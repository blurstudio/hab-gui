from Qt import QtWidgets

from .. import utils
from ..widgets.custom_variable_editor import CustomVariableEditor


class EditCustomVariablesAction(QtWidgets.QAction):
    """A QAction that allows the user to edit custom variables.

    Shows a dialog showing any config/distro json files that have editing enabled
    by setting the top level dict variable `variable_editor` to `True`. Users can
    then add or remove variables, and edit their keys and values.

    Args:
        resolver (hab.Resolver): The resolver used for settings.
        hab_widget (QWidget): The URI widget menu operations are performed on.
        verbosity (int, optional): The current verbosity setting.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, resolver, hab_widget, verbosity=0, parent=None):
        super().__init__(
            utils.Paths.icon("pencil-box-outline.svg"),
            "Edit Custom Variables",
            parent,
        )
        self.hab_widget = hab_widget
        self.resolver = resolver
        self.verbosity = verbosity
        self.setObjectName("edit_custom_variables")

        self.triggered.connect(self.edit_custom_variables)

    def edit_custom_variables(self):
        dlg = CustomVariableEditor.create_dialog(
            self.resolver, verbosity=self.verbosity, parent=self.parent()
        )
        dlg.exec_()

        # Ensure the hab_gui respects any changes the user may have made
        self.hab_widget.refresh_cache()
