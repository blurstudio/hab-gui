import hab
from Qt import QtCore, QtWidgets


class URIComboBox(QtWidgets.QComboBox):
    """Create a QComboBox to store a given list of URIs.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setEditable(True)
        _translate = QtCore.QCoreApplication.translate
        self.setPlaceholderText(_translate("Launch_Aliases", "Select a URI..."))
        self.lineEdit().setPlaceholderText(self.placeholderText())
        self.refresh()

        self.currentTextChanged.connect(self._uri_changed)

    def _uri_changed(self):
        self.settings.uri = self.uri()

    def refresh(self):
        current = self.uri()
        self.clear()
        if self.uri is None:
            return
        resolver = self.settings.resolver
        with hab.utils.verbosity_filter(resolver, self.settings.verbosity):
            items = resolver.dump_forest(resolver.configs, indent="")
            self.addItems(items)
        self.set_uri(current)

    def uri(self):
        return self.currentText()

    def set_uri(self, uri):
        # If the uri is already an item in the combo box, select it
        index = self.findText(uri)
        if index > -1:
            self.setCurrentIndex(index)
        else:
            # Otherwise update the text of the combo box to match
            self.setEditText(uri)
