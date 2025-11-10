from Qt import QtWidgets

from .. import utils
from ..widgets.custom_variable_editor import CustomVariableEditor


class EditCustomVariablesAction(QtWidgets.QAction):
    """A QAction that allows the user to edit custom variables.

    Shows a dialog showing any config/distro json files that have editing enabled
    by setting the top level dict variable `variable_editor` to `True`. Users can
    then add or remove variables, and edit their keys and values.

    Args:
        settings (hab_gui.settings.Settings): Used to access shared hab settings.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, settings, parent=None):
        super().__init__(
            utils.Paths.icon("pencil-box-outline.svg"),
            "Edit Custom Variables",
            parent,
        )
        self.settings = settings
        self.setObjectName("edit_custom_variables")

        self.triggered.connect(self.edit_custom_variables)

    def edit_custom_variables(self):
        dlg = CustomVariableEditor.create_dialog(self.settings, parent=self.parent())
        utils.exec_obj(dlg)

        # Ensure the hab_gui respects any changes the user may have made
        self.settings.root_widget.refresh_cache()
