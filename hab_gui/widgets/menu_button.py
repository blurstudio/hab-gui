import logging

from Qt import QtWidgets

from .. import utils

logger = logging.getLogger(__name__)


class MenuButton(QtWidgets.QToolButton):
    """A button that gives the user access to a menu for the hab launcher.

    Args:
        resolver (hab.Resolver): The resolver used for settings.
        hab_widget (QWidget): The URI widget menu operations are performed on.
            This likely is also the parent, but may not be.
        verbosity (int): Pass along a verbosity value for filtering of URIs
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, resolver, hab_widget, verbosity=0, parent=None):
        super().__init__(parent=parent)
        self.hab_widget = hab_widget
        self.resolver = resolver
        self.verbosity = verbosity

        self.setText("Menu")
        self.setIcon(utils.Paths.icon("menu.svg"))
        self.setPopupMode(self.InstantPopup)
        self.refresh()

    def populate_menu(self, menu):
        """Builds the menu by adding QActions with connected signals."""
        act = menu.addAction("Refresh Hab Config")
        act.setObjectName("refresh_hab_cfg")
        act.setIcon(utils.Paths.icon("refresh.svg"))
        act.triggered.connect(self.refresh_hab_config)

    def refresh(self):
        """Rebuilds the menu shown when a user clicks on the button.
        See `populate_menu` for how the menu is populated.
        """
        menu = QtWidgets.QMenu(self)

        # Add actions and menus
        self.populate_menu(menu)

        self.setMenu(menu)

    def refresh_hab_config(self):
        """Reset the refresh_timer if active and calls refresh_cache."""
        running = self.hab_widget.refresh_timer.isActive()
        if running:
            self.hab_widget.refresh_timer.stop()

        self.hab_widget.refresh_cache()

        if running:
            self.hab_widget.refresh_timer.start()
