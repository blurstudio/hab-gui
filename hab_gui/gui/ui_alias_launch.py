import os

import hab
from Qt import QtCompat, QtCore, QtWidgets  # noqa: F401

from ..widgets.alias_button_grid import AliasButtonGrid
from ..widgets.uri_widgets import URIComboBox


class AliasLaunchWindow(QtWidgets.QMainWindow):
    def __init__(self, resolver, parent=None):
        super(AliasLaunchWindow, self).__init__(parent)
        self.resolver = resolver
        # Window properties
        self.setWindowTitle("Test UI")

        self.init_gui()
        self.setFixedWidth(400)

    def init_gui(self):
        self.window = QtWidgets.QWidget()
        self.hlayout = QtWidgets.QVBoxLayout()
        self.uri_widget = URIComboBox(self.resolver, parent=self)
        self.alias_button_grid = AliasButtonGrid(self.resolver, parent=self)
        self.setCentralWidget(self.window)
        self.hlayout.addWidget(self.uri_widget)
        self.uri_widget.uri_changed.connect(self.uri_changed)
        self.hlayout.addWidget(self.alias_button_grid)
        self.window.setLayout(self.hlayout)

    def uri_changed(self, uri):
        self.alias_button_grid.uri = uri
        self.alias_button_grid.refresh()


def main():
    os.environ["HAB_PATHS"] = "$HOME/code/hab/tests/site_main.json"

    app = QtWidgets.QApplication([])
    window = AliasLaunchWindow(hab.Resolver())
    window.show()
    app.exec_()

    os.environ.pop("HAB_PATHS")
