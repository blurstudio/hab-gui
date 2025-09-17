import logging
import sys

import click
from hab.cli import UriArgument
from hab.errors import InvalidAliasError
from hab.user_prefs import UriObj

from . import utils
from .widgets.splash_screen import SplashScreen

logger = logging.getLogger(__name__)


def get_application(settings=None, splash=True, **kwargs):
    """Returns the QApplication instance and SplashScreen, creating it if required.

    Args:
        settings (hab.cli.SharedSettings, optional): If settings is passed, then
            the `hab_gui.init` entry point is processed.
        splash (bool, optional): If enabled and the `splash_screen` property of
            the site config contains an image path. A SplashScreen is created
            shown and returned.
        **kwargs: Any other kwargs are passed to `cli_args` of
            `hab_gui.utils.entry_point_init`.

    Returns:
        app, splash: The first item is the QApplication instance. The second is
            the splash screen instance that was shown, or None.
    """
    from Qt.QtWidgets import QApplication

    global app

    if settings:
        utils.entry_point_init(settings.resolver, "launch", cli_args=kwargs)

    # Get the existing app if possible
    app = QApplication.instance()
    _splash = None
    if not app:
        # Otherwise create a new QApplication instance
        app = QApplication([])
        # Attempt to show a splash screen in case it takes a little while to
        # fully process the hab configuration
        if splash:
            splash_image = utils.get_splash_image(settings.resolver)
            if splash_image:
                _splash = SplashScreen(splash_image)
                _splash.show()

        # For a consistent UI, set the window icon for the application. All top
        # level widgets will inherit this automatically unless they override
        # it themselves.
        app.setWindowIcon(utils.Paths.icon("habihat.svg"))

    return app, _splash


def launch_alias(cli_settings, settings, alias_name, args=None):
    """Runs the requested alias.

    Args:
        alias_name (str): The alias name to run.
        args (list): Additional arguments for the command to be run by subprocess.
            This should be a list of each individual string argument. If a kwarg
            is being passed it should be passed as two items. ['--key', 'value'].
    """
    try:
        cli_settings.write_script(
            settings.uri, create_launch=True, launch=alias_name, exit=True, args=args
        )
    except InvalidAliasError as error:
        from Qt.QtWidgets import QMessageBox

        # No need to show the full traceback for this error, just show simple
        # message telling them the alias is invalid.
        logger.warning(str(error))
        QMessageBox.critical(None, "Invalid Alias Name", str(error))
        sys.exit(1)


@click.group()
@click.pass_context
def gui(ctx):
    """Run hab commands using gui mode"""


@gui.command(context_settings=dict(ignore_unknown_options=True))
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Show increasingly detailed output. Can be used up to 3 times.",
)
@click.argument("uri", cls=UriArgument, required=False, prompt=False)
@click.argument("alias", required=False)
# Pass all remaining arguments to the requested alias
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_obj
def launch(settings, verbosity, uri, alias, args):
    """Show a gui letting the user launch applications or choose URI's.

    If ALIAS is omitted then the Hab Launcher is shown. This lets the
    user choose URI's and quickly launch aliases.

    If you provide an AIAS instead of showing the HAB Launcher it will directly
    launch the requested alias without showing a UI. All trailing ARGS are passed
    to the launched alias. However, if the dash URI is passed it will use the URI
    stored in user preferences. If that URI has expired it will show the
    URI Picker allowing the user to choose the URI. If the shift key is pressed
    it will always show the URI Picker.
    """
    from .settings import Settings

    if isinstance(uri, click.UsageError):
        # Launch doesn't require a URI, but if its not passed a UsageError
        # is returned by UriArgument. Convert that to None.
        uri = None

    # If the user didn't pass the `-` URI, don't show the URI Picker
    is_dash = False
    if isinstance(uri, UriObj):
        uri = uri.uri
        is_dash = True

    app, splash = get_application(settings, uri=uri, verbosity=verbosity)

    settings.resolver._verbosity_target = "hab-gui"

    # The site file can specifically disable user_prefs for verbosity
    prefs_save_verbosity = settings.resolver.site.get("prefs_save_verbosity", True)
    # Handle loading verbosity from user_prefs if not explicitly specified.
    # Unfortunately click's `count` feature doesn't let the cli set verbosity
    # to zero. Then we could detect if the user wants to force verbosity to zero
    # or left it as default. For now this just means that you can force a
    # verbosity of 1 or higher to override the user pref but not zero.
    if prefs_save_verbosity and not verbosity:
        user_prefs = settings.resolver.user_prefs()
        user_prefs.load()
        if user_prefs.enabled:
            verbosity_settings = user_prefs.get("verbosity", {})
            if "hab-gui" in verbosity_settings:
                verbosity = verbosity_settings["hab-gui"]
                logger.info(f"Verbosity set to {verbosity} by user_prefs.")

    s = Settings(settings.resolver, verbosity, uri=uri)

    if alias:
        # If an alias was passed, launch it, possibly asking to update the URI
        from .dialogs.uri_picker_dialog import UriPickerDialog

        if not is_dash or not UriPickerDialog.should_show(s, alias=alias):
            launch_alias(settings, s, alias, args=args)
            if splash:
                splash.close()
            return

        logger.info("Showing the URI Picker dialog.")
        window = UriPickerDialog(s, alias=alias)
        window.accepted.connect(lambda: launch_alias(settings, s, alias, args=args))
    else:
        # Otherwise Show the alias launcher so the user can also choose aliases
        from .windows.alias_launch_window import AliasLaunchWindow

        window = AliasLaunchWindow(s)

    window.show()
    if splash:
        splash.finish(window)

    utils.exec_obj(app)


@gui.command()
@click.argument("uri", required=False)
@click.pass_obj
def set_uri(settings, uri):
    """Allows for saving a local URI default by passing
    a URI argument.  If no argument is passed uri-set
    will prompt you to enter and argument."""

    settings.log_context(uri)

    from Qt.QtWidgets import QInputDialog, QMessageBox

    # Create the QApplication, app.exec_ currently does not need called due
    # to this only using QInputDialog and QMessageBox.
    _ = get_application(settings, uri=uri, splash=False)

    if uri is not None:
        # If the uri was passed, no need to ask the user
        settings.resolver.user_prefs().uri = uri
        QMessageBox.information(
            None, "Hab URI default set", f"The hab URI default was set to {uri}"
        )
        return

    # Otherwise ask the user what uri to use.
    # TODO: Use fancy hab-gui widgets configured by site
    current_uri = settings.resolver.user_prefs().uri
    uris = list(settings.resolver.dump_forest(settings.resolver.configs, indent=""))
    if current_uri and current_uri not in uris:
        uris.append(current_uri)
    uris.sort(key=str.casefold)

    current_index = -1
    if current_uri:
        current_index = uris.index(current_uri)

    uri, ok = QInputDialog.getItem(
        None, "Set hab URI", "Set default hab URI to:", uris, current=current_index
    )
    if ok:
        settings.resolver.user_prefs().uri = uri
