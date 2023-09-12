from Qt import QtCore, QtWidgets

from . import ICON_PATH  # noqa: F401


class AliasButton(QtWidgets.QToolButton):
    button_pressed = QtCore.Signal(str)

    def __init__(self, cfg, alias_name, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setText(alias_name)
        qsize_policy = QtWidgets.QSizePolicy
        size_policy = qsize_policy(qsize_policy.Minimum, qsize_policy.Preferred)
        self.setSizePolicy(size_policy)
        self.clicked.connect(self.button_action)

    def button_action(self):
        print(f"hab launch {self.text()} {self.cfg.uri}")
