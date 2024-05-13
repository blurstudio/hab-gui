from Qt import QtWidgets


class SeparatorAction(QtWidgets.QAction):
    """A entry point used to add a separator to a menu using entry_points.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.setSeparator(True)
