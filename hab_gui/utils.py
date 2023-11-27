import datetime
import logging
import random
import time
from contextlib import contextmanager
from pathlib import Path

from Qt import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)


@contextmanager
def cursor_override(cursor=QtCore.Qt.BusyCursor):
    """Change the application cursor to wait while running the context/decorator.
    Ensures that the cursor is restored even if an exception is raised.
    """
    QtWidgets.QApplication.setOverrideCursor(cursor)
    try:
        yield
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()


def entry_point_init(resolver, cmd, cli_args=None, **kwargs):
    """Used to apply startup configuration via site config.

    Example of site config replicating the default:
        {
            "append": {
                "entry_points": {
                    "hab_gui.init": {
                        "init": "hab_gui.entry_points.message_box:MessageBoxInit"
                    }
                }
            }
        }

    This uses the site entry_point `hab_gui.init` to initialize a class using
    the interface defined by `hab_gui.entry_points.BaseInit`. Defaults to
    `hab_gui.entry_points.message_box:MessageBoxInit` which shows a QMessageBox if
    any exceptions are raised. This prevents Qt from closing the application due
    to unhanded exceptions. If you want to disable this entry point default set
    the object reference to a empty string.

    Example of disabling entry point:
        {"append": {"entry_points": {"hab_gui.init": {"init": ""}}}}`
    """
    if cli_args is None:
        cli_args = {}

    default = {"init": "hab_gui.entry_points.message_box:MessageBoxInit"}

    # NOTE: kwargs should be added to allow for future changes to this call
    eps = resolver.site.entry_points_for_group("hab_gui.init", default=default)
    for ep in eps:
        if not ep.value:
            # Passing an empty value disables processing this entry point
            continue

        # Evaluate the entry point and initialize it
        func = ep.load()
        func(resolver, cmd, cli_args=cli_args, **kwargs)


def interval(interval, fmt="%H:%M:%S"):
    """Convert interval string to seconds. Uses the `%H:%M:%S` format by default.
    Source: https://stackoverflow.com/a/10663851
    """
    x = time.strptime(interval, fmt)
    return datetime.timedelta(
        hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
    ).total_seconds()


def make_button_coords(button_list, wrap_length, arrangement):
    """Generates a dict that contains an alias_name key and a value that holds
    a 2D coordinate list.
    """
    array = dict()
    col = 0
    row = 0
    for i in range(0, len(button_list)):
        array[button_list[i]] = [row, col]
        if arrangement == 0:
            col += 1
            if col >= wrap_length:
                row += 1
                col = 0
        else:
            row += 1
            if row >= wrap_length:
                col += 1
                row = 0
    return array


class Paths:
    hab_gui = Path(__file__).parent
    resources = hab_gui / "resources"

    @classmethod
    def resource_path(cls, arg, *args):
        if isinstance(arg, str):
            return cls.resources.joinpath(arg, *args)
        return arg.joinpath(*args)

    @classmethod
    def icon(cls, arg, *args, **kwargs):
        path = cls.resource_path(arg, *args)
        return QtGui.QIcon(str(path), **kwargs)

    @classmethod
    def image(cls, arg, *args, **kwargs):
        path = cls.resource_path(arg, *args)
        return QtGui.QImage(str(path), **kwargs)


def get_splash_image(resolver):
    """
    Randomly grabs an image to use as a splash screen while starting Hab-Gui.

    A resolver object will be used to grab a site.json config that defines paths
    to any image or image directory.  Those will be distilled down to a list of
    valid images that can be used by the Hab-Gui SplashScreen class.  This method
    will then randomly choose an image from that list.
    """
    resolved_list = splash_paths(resolver)
    if not resolved_list:
        logger.debug("[Splash Image] No valid paths found to show.")
        return None
    return random.choice(resolved_list)


_splash_paths = None


def splash_paths(resolver, force=False):
    """Returns a list of all existing splash screen files found on disk.
    Uses the "splash_screen" list if defined in `resolver.site`. Any directories
    defined in this list will be expanded to include their direct children.
    Any file paths will also be included if they exist.

    The resolved list is cached, pass `force=True` to re-calculate the list.
    """
    global _splash_paths

    # Return the cached list if it was defined
    if not force and _splash_paths is not None:
        return _splash_paths

    paths = resolver.site.get("splash_screen", [])
    if not paths:
        # There are no paths to scan, just exit with an empty list
        _splash_paths = []
        return _splash_paths

    splash_paths = set()
    valid_extentions = set(
        [f".{x.data().decode()}" for x in QtGui.QImageReader.supportedImageFormats()]
    )

    for item in paths:
        item = Path(item)
        if item.is_dir():
            for scan_obj in item.iterdir():
                if scan_obj.is_file() and scan_obj.suffix in valid_extentions:
                    splash_paths.add(str(scan_obj))
        elif item.is_file() and item.suffix in valid_extentions:
            splash_paths.add(str(item))

    _splash_paths = list(splash_paths)
    return _splash_paths
