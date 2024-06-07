import hab
from hab.errors import InvalidRequirementError
from Qt import QtWidgets

from .. import utils
from .alias_icon_button import AliasIconButton


class AliasButtonGrid(QtWidgets.QWidget):
    """Create a grid layout to hold buttons that are used to launch alias
    applications.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        button_wrap_length (int) Indicates the number of buttons per column/row.
        button_layout (int) Sets the button layout to be either a horizontal focus
            or a vertical focus.
        button_cls (QToolButton, optional): The button class that populates
            the grid.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(
        self,
        settings,
        button_wrap_length,
        button_layout,
        button_cls=AliasIconButton,
        parent=None,
    ):
        super().__init__(parent)
        self.settings = settings
        self.button_wrap_length = button_wrap_length
        self.button_layout = button_layout
        self.button_cls = button_cls

        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid_layout)

        # Update this widget any time settings are updated
        self.settings.uri_changed.connect(self.refresh)
        self.settings.verbosity_changed.connect(self.refresh)

    def refresh(self):
        self.clear()
        if self.settings.uri is None:
            return
        resolver = self.settings.resolver
        try:
            cfg = resolver.resolve(self.settings.uri)
        except InvalidRequirementError as error:
            msg = f"Error resolving URI: {self.settings.uri}"
            label = QtWidgets.QLabel()
            label.setText(f"{msg}\n\n{error}")
            label.setWordWrap(True)
            self.grid_layout.addWidget(label)
            raise

        with hab.utils.verbosity_filter(resolver, self.settings.verbosity):
            alias_list = list(cfg.aliases.keys())
            # So buttons show up in alphabetical order
            alias_list.sort()
        button_coords = utils.make_button_coords(
            alias_list, self.button_wrap_length, self.button_layout
        )
        for button_name, button_coord in button_coords.items():
            button = self.button_cls(cfg, button_name)
            self.grid_layout.addWidget(button, button_coord[0], button_coord[1])

    def clear(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.grid_layout.removeWidget(widget)
                self.grid_layout.removeItem(item)
