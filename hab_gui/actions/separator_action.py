from Qt import QtWidgets


class SeparatorAction(QtWidgets.QAction):
    """A entry point used to add a separator to a menu using entry_points.

    Args:
        resolver (hab.Resolver): Ignored for this class.
        hab_widget (QWidget): Ignored for this class.
        verbosity (int, optional): Ignored for this class.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, resolver, hab_widget, verbosity=0, parent=None):
        super().__init__(parent)
        self.setSeparator(True)
