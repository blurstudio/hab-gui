import logging

from Qt import QtCore, QtWidgets

logger = logging.getLogger(__name__)


class AliasButton(QtWidgets.QToolButton):
    """Create a QToolButton which will launch a specified alias via a subprocess.

    Args:
        cfg (hab.parsers.flat_config.FlatConfig): The config object which contains
        URI related data.
        alias_name (str): The alias name passed from AliasButtonGrid.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    button_pressed = QtCore.Signal(str)

    def __init__(self, cfg, alias_name, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.alias_name = alias_name

        self.alias_dict = self.cfg.aliases
        qsize_policy = QtWidgets.QSizePolicy
        size_policy = qsize_policy(qsize_policy.Minimum, qsize_policy.Preferred)
        self.setSizePolicy(size_policy)
        self.clicked.connect(self._button_action)
        self.refresh()

    def _button_action(self):
        """Launch the alias in a subprocess."""
        self.cfg.launch(self.alias_name)

    def refresh(self):
        alias = self.alias_dict[self.alias_name]
        label = alias.get("label", self.alias_name)
        self.setText(label)
