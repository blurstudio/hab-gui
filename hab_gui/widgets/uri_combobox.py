import hab
from Qt import QtCore, QtWidgets


class URIComboBox(QtWidgets.QComboBox):
    """Create a QComboBox to store a given list of URIs.

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
        self.setEditable(True)
        _translate = QtCore.QCoreApplication.translate
        self.setPlaceholderText(_translate("Launch_Aliases", "Select a URI..."))
        self.lineEdit().setPlaceholderText(self.placeholderText())
        self.refresh()

        self.currentTextChanged.connect(self._emit_uri_changed)

    def _emit_uri_changed(self):
        self.uri_changed.emit(self.uri())

    def refresh(self):
        current = self.uri()
        self.clear()
        if self.uri is None:
            return
        with hab.utils.verbosity_filter(self.resolver, self.verbosity):
            items = self.resolver.dump_forest(self.resolver.configs, indent="")
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
