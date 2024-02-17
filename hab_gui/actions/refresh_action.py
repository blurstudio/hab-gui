from Qt import QtWidgets

from .. import utils


class RefreshAction(QtWidgets.QAction):
    """A QAction that causes the hab_widget to refresh the resolved hab setup and UI.

    Args:
        resolver (hab.Resolver): The resolver used for settings.
        hab_widget (QWidget): The URI widget menu operations are performed on.
        verbosity (int, optional): The current verbosity setting.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, resolver, hab_widget, verbosity=0, parent=None):
        super().__init__(
            utils.Paths.icon("refresh.svg"),
            "Refresh Hab Config",
            parent,
        )
        self.hab_widget = hab_widget
        self.resolver = resolver
        self.verbosity = verbosity
        self.setObjectName("refresh_hab_cfg")

        self.triggered.connect(self.hab_widget.refresh_cache)
