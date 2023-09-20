import logging

import click
from hab.cli import UriArgument, UriHelpClass

import hab_gui.utils

logger = logging.getLogger(__name__)


def get_application(settings=None, **kwargs):
    """Returns the QApplication instance, creating it if required.

    If settings is passed, then the `hab_gui_init` entry point is processed, any
    other kwargs are passed to `cli_args` of `hab_gui.utils.entry_point_init`.
    """
    from Qt.QtWidgets import QApplication

    global app

    if settings:
        hab_gui.utils.entry_point_init(settings.resolver, "launch", cli_args=kwargs)

    # Get the existing app if possible
    app = QApplication.instance()
    if not app:
        # Otherwise create a new QApplication instance
        app = QApplication([])

    return app


@click.group()
@click.pass_context
def gui(ctx):
    """Run hab commands using gui mode"""


@gui.command(cls=UriHelpClass)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
    help="Show increasingly detailed output. Can be used up to 3 times.",
)
@click.argument("uri", cls=UriArgument, required=False)
@click.pass_obj
def launch(settings, verbosity, uri):
    """Show a gui letting the user launch applications."""
    from .windows.alias_launch_window import AliasLaunchWindow

    if isinstance(uri, click.UsageError):
        # Launch doesn't require a URI, but if its not passed a UsageError
        # is returned by UriArgument. Convert that to None.
        uri = None

    app = get_application(settings, uri=uri, verbosity=verbosity)

    settings.resolver._verbosity_target = "hab-gui"
    window = AliasLaunchWindow(settings.resolver, uri=uri, verbosity=verbosity)
    window.show()

    app.exec_()


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
    app = get_application(settings, uri=uri)  # noqa: F841

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
    if current_uri not in uris:
        uris.append(current_uri)
    uris.sort()
    current = uris.index(current_uri)

    uri, ok = QInputDialog.getItem(
        None, "Set hab URI", "Set default hab URI to:", uris, current=current
    )
    if ok:
        settings.resolver.user_prefs().uri = uri
