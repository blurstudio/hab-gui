import logging

from Qt import QtWidgets

from .. import utils

logger = logging.getLogger(__name__)


class RefreshButton(QtWidgets.QToolButton):
    """Create a QToolButton that forces hab to re-cache its data and update hab-gui.

    Args:
        resolver (hab.Resolver): The hab resolver to operate on.
        verbosity (int): Pass along a verbosity value for filtering of URIs
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, resolver, verbosity=0, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self.verbosity = verbosity

        self.setToolTip("Refresh hab to ensure you have the latest configuration.")
        self.setText("Refresh")
        self.setIcon(utils.Paths.icon("refresh.svg"))
