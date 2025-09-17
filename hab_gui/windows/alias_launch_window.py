import logging
import math
from functools import partial

import hab
from Qt import QtCore, QtWidgets

from .. import utils

logger = logging.getLogger(__name__)


class AliasLaunchWindow(QtWidgets.QMainWindow):
    """Create a window that can launch applications relevant to a project URI

    Contains a custom QComboBox (URIComboBox) and a QGridlayout (AliasButtonGrid)
    The ComboBox is populated with a list of available URIs. The GridLayout is
    filled with buttons that represent application aliases.

    Args:
        settings (hab_gui.settings.Settings): Used to handle gui settings and
            facilitate emitting signals when settings change.
        uri (str, optional): If passed, use this as the current uri. Otherwise
            the value stored in the users prefs is used.
        button_wrap_length (int) Indicates the number of buttons per column/row.
        button_layout (int) Sets the button layout to be either a horizontal focus
            or a vertical focus.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    window_title = "Hab Launch - {uri}"
    """The title of this window. Use a `str.format` style string with the kwarg
    `uri` to include the currently selected URI.
    """

    def __init__(
        self,
        settings,
        uri=None,
        button_wrap_length=3,
        button_layout=0,
        parent=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.settings.root_widget = self
        self.button_wrap_length = button_wrap_length
        self.button_layout = button_layout

        self.process_entry_points()
        self.init_gui(uri)

        # Window properties
        self.setFixedWidth(400)
        self.center_window_position()

        # Create a auto-refresh timer by default that forces a refresh of hab.
        # This can be disabled by setting the site config setting to an empty string.
        self.refresh_timer = QtCore.QTimer(self)
        refresh_time = self.settings.resolver.site.get(
            "hab_gui_refresh_inverval", ["00:30:00"]
        )
        refresh_time = refresh_time[0]
        if refresh_time:
            self.refresh_timer.timeout.connect(partial(self.refresh_cache, False))
            refresh_time = math.ceil(utils.interval(refresh_time))
            logger.debug(f"Setting auto-refresh interval to {refresh_time} seconds")
            self.refresh_timer.start(refresh_time * 1000)

    def _update_window_title(self, uri):
        """Updates the window title with a `str.format` style string with the
        kwarg `uri` to include the currently selected URI.
        """
        self.setWindowTitle(self.window_title.format(uri=uri))

    def apply_layout(self):
        """Configures the layout of all widgets in this interface."""
        column_uri_widget = 1 if self.prefs_enabled else 0
        self.setCentralWidget(self.main_widget)
        self.layout.addWidget(self.uri_widget, 0, column_uri_widget)
        if self._cls_menu_button:
            self.layout.addWidget(self.menu_button, 0, column_uri_widget + 1)
        self.layout.addWidget(self.alias_buttons, 1, 0, 1, -1)

        # Add the footer_widget if used, otherwise add a spacer
        if self._cls_footer_widget:
            self.layout.addWidget(self.footer_widget, 2, 0, 1, -1)
        else:
            self.spacer_item = QtWidgets.QSpacerItem(
                0,
                0,
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Expanding,
            )
            self.layout.addItem(self.spacer_item, self.layout.rowCount(), 0, 1, -1)

        self.main_widget.setLayout(self.layout)

        # Ensure the tab order is intuitive. This doesn't come for free because
        # we need to pass uri_widget as an argument to pinned_uris which requires
        # creating it first and that breaks the default tab ordering.
        if self.prefs_enabled:
            self.setTabOrder(self.pinned_uris, self.uri_widget)
            if self._cls_menu_button:
                self.setTabOrder(self.uri_widget, self.menu_button)
                self.setTabOrder(self.menu_button, self.alias_buttons)
                self.setTabOrder(self.alias_buttons, self.pinned_uris)
            else:
                self.setTabOrder(self.uri_widget, self.pinned_uris)

    def process_entry_points(self):
        """Loads the classes defined by the site entry_point system.
        These are later initialized by init_gui to create the UI.
        """
        # Used to launch a specific alias by `_cls_aliases_widget`
        self._cls_alias_widget = self.settings.load_entry_point(
            "hab_gui.alias.widget", "hab_gui.widgets.alias_icon_button:AliasIconButton"
        )
        # Used to display alias launch widgets
        self._cls_aliases_widget = self.settings.load_entry_point(
            "hab_gui.aliases.widget",
            "hab_gui.widgets.alias_button_grid:AliasButtonGrid",
        )
        # Allows the user to refresh hab configuration in case it has changed.
        self._cls_menu_button = self.settings.load_entry_point(
            "hab_gui.uri.menu.widget",
            "hab_gui.widgets.menu_button:MenuButton",
            allow_none=True,
        )
        # Allows the user to pin commonly used URI's
        self._cls_uri_pin_widget = self.settings.load_entry_point(
            "hab_gui.uri.pin.widget",
            "hab_gui.widgets.pinned_uris_button:PinnedUriButton",
            allow_none=True,
        )
        # Interface the user uses to view and change the current URI.
        self._cls_uri_widget = self.settings.load_entry_point(
            "hab_gui.uri.widget", "hab_gui.widgets.uri_combobox:URIComboBox"
        )
        # A footer widget shown under the aliases widget
        self._cls_footer_widget = self.settings.load_entry_point(
            "hab_gui.footer.widget",
            None,
            allow_none=True,
        )

    def init_gui(self, uri=None):
        self.main_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout()

        self.uri_widget = self._cls_uri_widget(self.settings, parent=self)

        # If prefs are enabled, insert the Pinned URI widget
        self.prefs_enabled = self.settings.resolver.user_prefs().enabled
        if self._cls_uri_pin_widget is None:
            # The pinning widget can be disabled by setting the entry point to null
            self.prefs_enabled = False

        # Create a refresh button
        if self._cls_menu_button:
            self.menu_button = self._cls_menu_button(self.settings)

        if self.prefs_enabled:
            self.pinned_uris = self._cls_uri_pin_widget(
                self.settings, self.uri_widget, parent=self
            )
            self.layout.addWidget(self.pinned_uris, 0, 0)
            self.pinned_uris.uri_widget = self.uri_widget

        self.alias_buttons = self._cls_aliases_widget(
            self.settings,
            self.button_wrap_length,
            self.button_layout,
            button_cls=self._cls_alias_widget,
            parent=self,
        )

        # If specified add a footer widget under the aliases widget
        if self._cls_footer_widget:
            self.footer_widget = self._cls_footer_widget(self.settings)

        self.apply_layout()

        # If URI is not specified use the one defined in settings
        if uri is None:
            uri = self.settings.uri
        if uri:
            # This QTimer allows the gui to stay open even if the URI can't
            # be resolved. For example if the URI depends on a distro that is
            # no longer installed.
            QtCore.QTimer.singleShot(0, partial(self.uri_widget.set_uri, uri))

        # Ensure the URI widget has focus by default
        self.uri_widget.setFocus()

        # Ensure the window title always shows the currently selected URI
        self.settings.uri_changed.connect(self._update_window_title)

    @utils.cursor_override()
    def refresh_cache(self, reset_timer=True):
        """Refresh the resolved hab and re-display.

        Args:
            reset_timer (bool, optional): Stop and restart the refresh_timer if
                its currently active.
        """
        logger.debug(f"Refreshing cache with reset_timer: {reset_timer}")
        running = self.refresh_timer.isActive()
        try:
            if reset_timer and running:
                self.refresh_timer.stop()

            self.settings.resolver.clear_caches()
            self.uri_widget.refresh()
            self.alias_buttons.refresh()
        finally:
            if reset_timer and running:
                self.refresh_timer.start()

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
    utils.exec_obj(app)
