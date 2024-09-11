from Qt import QtWidgets


class URILineEdit(QtWidgets.QLineEdit):
    """Create a QLineEdit to store a given list of URIs.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings

        self.setPlaceholderText("Enter a URI...")
        self.textChanged.connect(self._uri_changed)

    def _uri_changed(self):
        self.settings.uri = self.uri()

    def refresh(self):
        # Nothing to refresh on this widget
        pass

    def uri(self):
        return self.text().strip()

    def set_uri(self, uri):
        self.setText(uri)
