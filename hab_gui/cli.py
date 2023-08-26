import click
from hab.cli import UriArgument, UriHelpClass


def get_application():
    """Returns the QApplication instance, creating it if required."""
    from Qt.QtWidgets import QApplication

    global app
    app = QApplication.instance()
    if not app:
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

    app = get_application()
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
    app = get_application()  # noqa: F841

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
