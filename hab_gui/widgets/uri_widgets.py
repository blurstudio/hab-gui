from Qt import QtCore, QtWidgets


class URIComboBox(QtWidgets.QComboBox):
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

    def uri(self):
        return self.currentText()

    def set_uri(self, uri):
        self.setEditText(uri)


class URILineEdit(QtWidgets.QLineEdit):
    uri_changed = QtCore.Signal(str)

    def __init__(self, resolver, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self.setPlaceholderText("Enter a URI...")

        self.textChanged.connect(self._emit_uri_changed)

    def _emit_uri_changed(self):
        print("Hello LineEdit")
        self.uri_changed.emit(self.uri())

    def uri(self):
        return self.text()

    def set_uri(self, uri):
        self.setText(uri)
