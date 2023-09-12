import hab
from Qt import QtWidgets

from ..widgets.alias_button_grid import AliasButtonGrid
from ..widgets.uri_combobox import URIComboBox


class AliasLaunchWindow(QtWidgets.QMainWindow):
    """Create a window that can launch applications relevant to a project URI

    Contains a custom QComboBox (URIComboBox) and a QGridlayout (AliasButtonGrid)
    The ComboBox is populated with a list of available URIs. The GridLayout is
    filled with buttons that represent application aliases.

    Args:
        resolver (hab.Resolver): The resolver to change verbosity settings on.
        verbosity (int): Change the verbosity setting to this value. If None is passed,
            all results are be shown without any filtering.
        button_wrap_length (int) Indicates the number of buttons per column/row.
        button_layout (int) Sets the button layout to be either a horizontal focus
            or a vertical focus.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(
        self, resolver, verbosity=0, button_wrap_length=3, button_layout=0, parent=None
    ):
        super(AliasLaunchWindow, self).__init__(parent)
        self.resolver = resolver
        self.verbosity = verbosity
        self.button_wrap_length = button_wrap_length
        self.button_layout = button_layout

        self.init_gui()

        # Window properties
        self.setWindowTitle("Hab Launch Aliases")
        self.setFixedWidth(400)
        self.center_window_position()

    def init_gui(self):
        self.window = QtWidgets.QWidget()
        self.hlayout = QtWidgets.QVBoxLayout()
        self.uri_widget = URIComboBox(
            self.resolver, verbosity=self.verbosity, parent=self
        )
        self.alias_button_grid = AliasButtonGrid(
            self.resolver,
            self.button_wrap_length,
            self.button_layout,
            self.verbosity,
            parent=self,
        )

        self.setCentralWidget(self.window)
        self.hlayout.addWidget(self.uri_widget)
        self.uri_widget.uri_changed.connect(self.uri_changed)
        self.hlayout.addWidget(self.alias_button_grid)
        self.window.setLayout(self.hlayout)

        # Check for stored URI and apply it as the current text
        local_stored_uri = str(self.resolver.user_prefs().uri_check())
        if local_stored_uri:
            self.uri_widget.set_uri(local_stored_uri)
            self.uri_changed(local_stored_uri)

    def uri_changed(self, uri):
        self.alias_button_grid.uri = uri
        self.alias_button_grid.refresh()

    def center_window_position(self):
        # Place window onto screen center
        qt_rectangle = self.frameGeometry()
        app = QtWidgets.QApplication.instance()
        primary = app.primaryScreen()
        center_point = primary.availableGeometry().center()
        qt_rectangle.moveCenter(center_point)
        self.move(qt_rectangle.topLeft())


def main():
    app = QtWidgets.QApplication([])
    window = AliasLaunchWindow(hab.Resolver(target="hab-gui"), verbosity=1)
    window.show()
    app.exec_()
