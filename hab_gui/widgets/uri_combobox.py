from Qt import QtCore, QtWidgets


class URIComboBox(QtWidgets.QComboBox):
    """Create a QComboBox to store a given list of URIs.

    Args:
        resolver (hab.Resolver): The resolver to pull the URI data from Hab.
    """

    uri_changed = QtCore.Signal(str)

    def __init__(self, resolver, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self.setEditable(True)
        _translate = QtCore.QCoreApplication.translate
        self.setPlaceholderText(_translate("Launch_Aliases", "Select a URI..."))
        self.lineEdit().setPlaceholderText(self.placeholderText())
        self.refresh()

        self.currentTextChanged.connect(self.emit_uri_changed)

    def emit_uri_changed(self):
        self.uri_changed.emit(self.uri())

    def refresh(self):
        self.clear()
        items = self.resolver.dump_forest(self.resolver.configs, indent="")
        self.addItems(items)

        # Check for stored URI and set it as the default value
        local_stored_uri = str(self.resolver.user_prefs().uri_check())
        self.setCurrentText(local_stored_uri)

    def uri(self):
        return self.currentText()

    def set_uri(self, uri):
        self.setEditText(uri)
