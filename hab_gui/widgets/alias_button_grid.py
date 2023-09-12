from Qt import QtWidgets

from .. import utils
from .alias_button import AliasButton


class AliasButtonGrid(QtWidgets.QWidget):
    def __init__(
        self,
        resolver,
        uri=None,
        button_cls=AliasButton,
        wrap_length=3,
        arrangement="col",
        parent=None,
    ):
        super().__init__(parent)
        self.resolver = resolver
        self.uri = uri
        self.button_cls = button_cls
        self.wrap_length = wrap_length
        self.arrangement = arrangement
        self.grid_layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.grid_layout)

    def refresh(self):
        self.clear()
        cfg = self.resolver.resolve(self.uri)
        print(cfg)
        alias_list = list(cfg.aliases.keys())
        button_coords = utils.make_button_coords(
            alias_list, self.wrap_length, self.arrangement
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
