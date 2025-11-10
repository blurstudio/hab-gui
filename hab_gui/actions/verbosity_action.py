from Qt import QtWidgets


class VerbosityAction(QtWidgets.QAction):
    """A QAction that allows the user to modify hab verbosity inside the gui.

    This action has a sub-menu that lists the available verbosity settings, the
    current setting and lets the user change the verbosity setting.

    You can customize the name of this widget and it's sub-menu names by adding
    a `verbosity_action` dictionary to your site config matching
    :py:attr:`default_config`'s structure.

    See :py:attr:`Settings.verbosity` for details on how this is saved to user_prefs.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    default_config = {
        "name": "Set Verbosity",
        "verbosity_map": {
            "Off": 0,
            "Low": 1,
            "Medium": 2,
            "High": 3,
        },
    }
    """dict: Default settings for this widget. `name` defines the name of the
    action containing the sub-menu. `verbosity_map` is a mapping of nice names
    for verbosity int value. This dict is used to build the sub-menu.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.settings.verbosity_changed.connect(self.refresh)
        self.setObjectName("edit_verbosity")

        self.load_config()
        self.setText(self.name)
        # Build a sub-menu letting the user view and update verbosity
        menu = QtWidgets.QMenu("Verbosity", self.settings.root_widget)
        menu.triggered.connect(self.menu_triggered)
        verbosity = self.settings.verbosity
        for key, value in self.verbosity_map.items():
            action = menu.addAction(key)
            action.setData(value)
            action.setCheckable(True)
            action.setChecked(verbosity == value)
        self.setMenu(menu)

    def load_config(self):
        site = self.settings.resolver.site
        settings = site.get("verbosity_action", {})
        self.name = settings.get("name", self.default_config["name"])
        self.verbosity_map = settings.get(
            "verbosity_map", self.default_config["verbosity_map"]
        )

    def menu_triggered(self, action):
        """Handles all actions selected by the user in the menu."""
        self.settings.verbosity = action.data()

    def refresh(self):
        """Updates currently checked item in the sub-menu"""
        verbosity = self.settings.verbosity
        for action in self.menu().actions():
            value = action.data()
            action.setChecked(verbosity == value)
