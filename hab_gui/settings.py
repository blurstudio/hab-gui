import logging

from Qt.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class Settings(QObject):
    """A collection shared hab gui settings passed to widgets.

    Args:
        resolver (hab.Resolver): The hab resolver to get information from.
        verbosity (int): Change the verbosity setting to this value. If None is
            passed, all results are be shown without any filtering.
        uri (str, optional): Use this as the current URI.
        root_widget (Qt.QtWidgets.QWidget, optional): The main Qt widget, likely
            a top level widget. For example `AliasLaunchWindow`.
    """

    verbosity_changed = Signal(int)
    """Signal emitted any time the verbosity property is updated, passing the new value."""
    uri_changing = Signal(str)
    """Signal emitted just before the URI will be updated, passing the new URI."""
    uri_changed = Signal(str)
    """Signal emitted just after the URI has been updated, passing the new URI."""

    def __init__(self, resolver, verbosity, uri=None, root_widget=None, parent=None):
        super().__init__(parent=parent)
        self._verbosity = verbosity
        self._uri = uri
        self.resolver = resolver
        self.root_widget = root_widget

    def load_entry_point(self, name, default, allow_none=False):
        """Work function that loads the requested entry_point defined in site."""

        default = {"default": default}
        eps = self.resolver.site.entry_points_for_group(name, default=default)
        if allow_none and (not eps or eps[0].value is None):
            return None
        if not eps:
            raise ValueError(f"A valid entry_point for {name} must be defined")
        return eps[0].load()

    @property
    def verbosity(self):
        """The verbosity setting used by hab_gui.

        This can be passed using `hab gui launch -v`. If the site configuration
        variable `prefs_save_verbosity` is set to `true`(the default) and user_prefs
        are enabled, then when this variable is modified, its state will be saved
        in the user_prefs.
        """
        return self._verbosity

    @verbosity.setter
    def verbosity(self, value):
        self._verbosity = value
        self.verbosity_changed.emit(value)

        # If enabled save the user preference for verbosity
        if not self.resolver.site.get("prefs_save_verbosity", True):
            return

        user_prefs = self.resolver.user_prefs()
        if user_prefs.enabled:
            user_prefs.load()
            user_prefs.setdefault("verbosity", {})["hab-gui"] = value
            user_prefs.save()
            logger.debug(f"User prefs verbosity saved to {user_prefs.filename}")

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, uri):
        self.uri_changing.emit(uri)
        self._uri = uri
        self.uri_changed.emit(uri)
