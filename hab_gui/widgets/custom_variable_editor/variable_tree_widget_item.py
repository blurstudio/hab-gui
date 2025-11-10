from Qt import QtCore, QtWidgets


class VariableTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """A QTreeWidgetItem used to view/edit a specific custom variable."""

    def __init__(self, parent, variable_name):
        super().__init__(parent)
        self.parser = parent.parser
        self._variable_name = variable_name
        self.setFlags(self.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)
        self.refresh()

    def remove_variable(self):
        del self.parser.variables[self.variable_name]

    @property
    def value(self):
        return self.parser.variables[self.variable_name]

    @value.setter
    def value(self, value):
        if self.value == value:
            return
        self.parser.variables[self.variable_name] = value
        self.parent().dirty = True

    @property
    def variable_name(self):
        return self._variable_name

    @variable_name.setter
    def variable_name(self, name):
        if self._variable_name == name:
            return
        # NOTE: This is called when data is changed by QTreeWidget's editor
        # so it's assumed that refresh does not need called here.
        value = self.parser.variables.pop(self._variable_name, "Undefined")
        self._variable_name = name
        self.parser.variables[name] = value
        self.parent().dirty = True

    def refresh(self):
        self.setText(0, self.variable_name)
        self.setText(1, self.value)
