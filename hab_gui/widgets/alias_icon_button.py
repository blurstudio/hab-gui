import logging
import os

from Qt import QtCore, QtGui

from .alias_button import AliasButton

logger = logging.getLogger(__name__)


class AliasIconButton(AliasButton):
    """Create a AliasButton that also shows a icon for each alias.

    Args:
        cfg (hab.parsers.flat_config.FlatConfig): The config object which contains
        URI related data.
        alias_name (str): The alias name passed from AliasButtonGrid.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    button_pressed = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

    def refresh(self):
        alias = self.alias_dict[self.alias_name]
        icon = QtGui.QIcon()
        icon_path = alias.get("icon", "")
        if os.path.exists(icon_path):
            icon.addPixmap(QtGui.QPixmap(icon_path))
        elif icon_path:
            logger.debug(
                f"The specified icon file {icon_path} does not exist for {self.alias_dict}"
            )
        self.setIcon(icon)

        super().refresh()
