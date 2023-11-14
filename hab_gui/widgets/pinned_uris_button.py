import logging

from Qt import QtWidgets

from .. import utils

logger = logging.getLogger(__name__)


class PinnedUriButton(QtWidgets.QToolButton):
    """A widget that gives users quick access to URI's used regularly. When the
    user clicks on this tool button, it opens a menu allowing the user to choose
    from previously saved URI's or add/remove a URI to saved user_prefs.

    Args:
        resolver (hab.Resolver): The resolver used for settings.
        uri_widget (QWidget): The URIComboBox like widget used to get/set the
            current URI from.
        verbosity (int): Pass along a verbosity value for filtering of URIs
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    _text_main = "\U0001F4CC"
    _text_pin_selected = "Pin selected URI"
    _text_remove_uri = "Remove pin"

    def __init__(self, resolver, uri_widget, verbosity=0, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self.uri_widget = uri_widget
        self.verbosity = verbosity

        self.setToolTip("Select and manage quick access to commonly used URI's.")
        self.setText(self._text_main)
        self.setIcon(utils.Paths.icon("pin-outline.svg"))
        self.setPopupMode(self.InstantPopup)
        self.refresh()

    def add_uri(self, uri):
        """Add this uri to `self.uris()` and save that change to user_prefs."""
        uris = self.uris()
        uris.add(uri)
        self.set_uris(uris)

    def menu_triggered(self, action):
        """Handles all actions selected by the user in the menu."""
        uri = action.text()
        tag = action.data()
        if tag == "pin":
            # This option uses the URI from the uri_widget not the action
            uri = self.uri_widget.uri()
            self.add_uri(uri)
            self.refresh()
        elif tag == "choose":
            self.uri_widget.set_uri(uri)
        elif tag == "remove":
            # Remove this URI from user_prefs
            uris = self.uris()
            if uri in uris:
                uris.remove(uri)
                self.set_uris(uris)
            self.refresh()

    def refresh(self):
        """Rebuilds the menu shown when a user clicks on the button."""
        menu = QtWidgets.QMenu(self)
        menu.triggered.connect(self.menu_triggered)

        # Add management actions and menus
        act = menu.addAction(self._text_pin_selected)
        act.setIcon(utils.Paths.icon("pin-outline.svg"))
        act.setData("pin")
        remove_menu = menu.addMenu(self._text_remove_uri)
        remove_menu.setIcon(utils.Paths.icon("pin-off-outline.svg"))
        menu.addSeparator()

        # Add existing pinned URI's to both menus
        for uri in sorted(self.uris(), key=str.casefold):
            # Selects this URI in self.uri_widget
            act = menu.addAction(uri)
            act.setData("choose")

            # Removes the URI from saved user_prefs
            act = remove_menu.addAction(uri)
            act.setData("remove")

        self.setMenu(menu)

    def uris(self):
        """Returns the pinned_uris saved in preferences as a set. It will only do
        that if prefs are enabled. Returns `set()` otherwise. This will call load
        to ensure the preference file has been loaded.
        """
        prefs = self.resolver.user_prefs()
        if prefs.enabled:
            # Ensure the preferences are loaded.
            prefs.load()
            return set(prefs.get("pinned_uris", []))
        return set()

    def set_uris(self, uris):
        """Saves URIS to pinned_uris in user_prefs. It will only do that if prefs
        are enabled. This will call load to ensure the preference file has been loaded.
        """
        prefs = self.resolver.user_prefs()
        if prefs.enabled:
            # Ensure the preferences are loaded.
            prefs.load()

            prefs["pinned_uris"] = sorted(uris, key=str.casefold)
            prefs.save()
            logger.debug(f"Pinned URI's saved {prefs.filename}")
