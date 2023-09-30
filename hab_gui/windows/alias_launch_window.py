import hab
from Qt import QtWidgets

from ..widgets.alias_button_grid import AliasButtonGrid
from ..widgets.pinned_uris_button import PinnedUriButton
from ..widgets.uri_combobox import URIComboBox


class AliasLaunchWindow(QtWidgets.QMainWindow):
    """Create a window that can launch applications relevant to a project URI

    Contains a custom QComboBox (URIComboBox) and a QGridlayout (AliasButtonGrid)
    The ComboBox is populated with a list of available URIs. The GridLayout is
    filled with buttons that represent application aliases.

    Args:
        resolver (hab.Resolver): The resolver to change verbosity settings on.
        uri (str, optional): If passed, use this as the current uri. Otherwise
            the value stored in the users prefs is used.
        verbosity (int): Change the verbosity setting to this value. If None is passed,
            all results are be shown without any filtering.
        button_wrap_length (int) Indicates the number of buttons per column/row.
        button_layout (int) Sets the button layout to be either a horizontal focus
            or a vertical focus.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(
        self,
        resolver,
        uri=None,
        verbosity=0,
        button_wrap_length=3,
        button_layout=0,
        parent=None,
    ):
        super(AliasLaunchWindow, self).__init__(parent)
        self.resolver = resolver
        self.verbosity = verbosity
        self.button_wrap_length = button_wrap_length
        self.button_layout = button_layout

        self.init_gui(uri)

        # Window properties
        self.setWindowTitle("Hab Launch Aliases")
        self.setFixedWidth(400)
        self.center_window_position()

    def init_gui(self, uri=None):
        self.window = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout()

        self.uri_widget = URIComboBox(
            self.resolver, verbosity=self.verbosity, parent=self
        )

        # If prefs are enabled, insert the Pinned URI widget
        column_uri_widget = 0
        prefs_enabled = self.resolver.user_prefs().enabled
        if prefs_enabled:
            self.pinned_uris = PinnedUriButton(
                self.resolver, self.uri_widget, verbosity=self.verbosity, parent=self
            )
            self.layout.addWidget(self.pinned_uris, 0, 0)
            column_uri_widget = 1
            self.pinned_uris.uri_widget = self.uri_widget

        self.alias_button_grid = AliasButtonGrid(
            self.resolver,
            self.button_wrap_length,
            self.button_layout,
            self.verbosity,
            parent=self,
        )

        self.setCentralWidget(self.window)
        self.layout.addWidget(self.uri_widget, 0, column_uri_widget)
        self.uri_widget.uri_changed.connect(self.uri_changed)
        self.layout.addWidget(self.alias_button_grid, 1, 0, 1, -1)
        self.window.setLayout(self.layout)

        # Check for stored URI and apply it as the current text
        if uri is None:
            uri = str(self.resolver.user_prefs().uri_check())
        if uri:
            self.uri_widget.set_uri(uri)
            self.uri_changed(uri)

        # Ensure the URI widget has focus by default
        self.uri_widget.setFocus()

        # Ensure the tab order is intuitive. This doesn't come for free because
        # we need to pass uri_widget as an argument to pinned_uris which requires
        # creating it first and that breaks the default tab ordering.
        if prefs_enabled:
            self.setTabOrder(self.pinned_uris, self.uri_widget)
            self.setTabOrder(self.uri_widget, self.alias_button_grid)
            self.setTabOrder(self.alias_button_grid, self.pinned_uris)

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
