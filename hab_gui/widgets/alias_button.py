import logging
import subprocess  # noqa: F401

from Qt import QtCore, QtGui, QtWidgets

logger = logging.getLogger(__name__)


class AliasButton(QtWidgets.QToolButton):
    """Create a QToolButton which will launch a specified alias via a subprocess.

    Args:
        cfg (hab.Resolver.resolve): The config dict which contains URI related data.
        alias_name (str): The alias name passed from AliasButtonGrid.
    """

    button_pressed = QtCore.Signal(str)

    def __init__(self, cfg, alias_name, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.alias_name = alias_name

        self.alias_dict = self.cfg.aliases
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        qsize_policy = QtWidgets.QSizePolicy
        size_policy = qsize_policy(qsize_policy.Minimum, qsize_policy.Preferred)
        self.setSizePolicy(size_policy)
        self.clicked.connect(self.button_action)
        self.refresh()

    def button_action(self):
        print(f"cmd {self.alias_dict[self.alias_name]['cmd']}")
        # TODO Need to enable the launch command once the Hab code is ready
        # cmd = cfg.launch(alias_name)

    def refresh(self):
        self.refresh_icon()
        self.refresh_text()

    def refresh_icon(self):
        try:
            icon_path = self.alias_dict[self.alias_name]["icon"]
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path))
            self.setIcon(icon)
        except Exception as e:
            # TODO Needs proper exception handling
            return e

    def refresh_text(self):
        try:
            self.setText(self.alias_dict[self.alias_name]["label"])
        except Exception as e:
            self.setText(self.alias_name)
            # TODO Needs proper exception handling
            return e
