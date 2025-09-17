import logging

from Qt import QtWidgets

from .. import utils

logger = logging.getLogger(__name__)


class MenuButton(QtWidgets.QToolButton):
    """A button that gives the user access to a menu for the hab launcher.

    The menu is defined by a entry_point specification matching the
    `entry_point_name` property. If this entry point is not specified it will
    default to the value returned by `entry_point_default`.

    Each named entry_point will be added to the menu. See `hab_gui.actions` for
    some pre-built QActions. This is a dictionary, so if you want to re-use
    actions like `SeparatorAction`, make sure they all have unique names.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent=parent)
        self.settings = settings

        self.setText("Menu")
        self.setIcon(utils.Paths.icon("menu.svg"))
        self.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
        self.refresh()

    @property
    def entry_point_default(self):
        """The default entry point values used if self.entry_point_name is not
        defined in the site's entry_points.
        """
        return {
            "refresh": "hab_gui.actions.refresh_action:RefreshAction",
        }

    @property
    def entry_point_name(self):
        """The name of the entry point that defines what QActions are added to
        the menu.
        """
        return "hab_gui.uri.menu.actions"

    def populate_menu(self, menu):
        """Builds the menu by adding QActions defined by the entry_points."""
        eps = self.settings.resolver.site.entry_points_for_group(
            self.entry_point_name, default=self.entry_point_default
        )
        for ep in eps:
            cls = ep.load()
            act = cls(settings=self.settings, parent=self)
            menu.addAction(act)

    def refresh(self):
        """Rebuilds the menu shown when a user clicks on the button.
        See `populate_menu` for how the menu is populated.
        """
        menu = QtWidgets.QMenu(self)

        # Add actions and menus
        self.populate_menu(menu)

        self.setMenu(menu)
