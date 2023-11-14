from Qt import QtCore, QtWidgets


class URILineEdit(QtWidgets.QLineEdit):
    """Create a QLineEdit to store a given list of URIs.

    Args:
        resolver (hab.Resolver): The resolver to pull the URI data from Hab.
        verbosity (int): Pass along a verbosity value for filtering of URIs
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    uri_changed = QtCore.Signal(str)

    def __init__(self, resolver, verbosity=0, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self.verbosity = verbosity

        self.setPlaceholderText("Enter a URI...")
        self.textChanged.connect(self._emit_uri_changed)

    def _emit_uri_changed(self):
        self.uri_changed.emit(self.uri())

    def refresh(self):
        # Nothing to refresh on this widget
        pass

    def uri(self):
        return self.text()

    def set_uri(self, uri):
        self.setText(uri)
