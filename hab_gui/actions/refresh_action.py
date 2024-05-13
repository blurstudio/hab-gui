from Qt import QtWidgets

from .. import utils


class RefreshAction(QtWidgets.QAction):
    """A QAction that causes the root_widget to refresh the resolved hab and UI.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, settings, parent=None):
        super().__init__(
            utils.Paths.icon("refresh.svg"),
            "Refresh Hab Config",
            parent,
        )
        self.settings = settings
        self.setObjectName("refresh_hab_cfg")

        self.triggered.connect(self.settings.root_widget.refresh_cache)
