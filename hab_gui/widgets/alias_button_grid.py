import hab
from Qt import QtWidgets

from .. import utils
from .alias_icon_button import AliasIconButton


class AliasButtonGrid(QtWidgets.QWidget):
    """Create a grid layout to hold buttons that are used to launch alias
    applications.

    Args:
        resolver (hab.Resolver): The resolver to change verbosity settings on.
        button_wrap_length (int) Inidicates the number of buttons per column/row.
        button_layout (int) Sets the button layout to be either a horizontal focus
            or a vertical focus.
        verbosity (int): Change the verbosity setting to this value. If None is passed,
            all results are be shown without any filtering.
        uri (string, optional) The project uri that specifies the button aliases.
        button_cls (QToolButton, optional): The button class that populates
            the grid.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(
        self,
        resolver,
        button_wrap_length,
        button_layout,
        verbosity,
        uri=None,
        button_cls=AliasIconButton,
        parent=None,
    ):
        super().__init__(parent)
        self.resolver = resolver
        self.button_wrap_length = button_wrap_length
        self.button_layout = button_layout
        self.verbosity = verbosity
        self.uri = uri
        self.button_cls = button_cls

        self.grid_layout = QtWidgets.QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.grid_layout)

    def refresh(self):
        self.clear()
        if self.uri is None:
            return
        cfg = self.resolver.resolve(self.uri)
        with hab.utils.verbosity_filter(self.resolver, self.verbosity):
            alias_list = list(cfg.aliases.keys())
            # So buttons show up in alphabetical order
            alias_list.sort()
        button_coords = utils.make_button_coords(
            alias_list, self.button_wrap_length, self.button_layout
        )
        for button_name, button_coord in button_coords.items():
            button = self.button_cls(cfg, button_name)
            self.grid_layout.addWidget(button, button_coord[0], button_coord[1])
        self.spacer_item = QtWidgets.QSpacerItem(
            20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.grid_layout.addItem(self.spacer_item, self.grid_layout.rowCount(), 0, 1, 1)

    def clear(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.grid_layout.removeWidget(widget)
                self.grid_layout.removeItem(item)
