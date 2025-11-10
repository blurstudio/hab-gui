import json

import hab.utils
from Qt import QtCore, QtWidgets

from .variable_tree_widget_item import VariableTreeWidgetItem


class FileTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """A QTreeWidgetItem used to show a given config/distro and its custom variables."""

    def __init__(self, parent, parser):
        super().__init__(parent)
        self.parser = parser
        # Add a tracking variable to tell if the parser is dirty
        if not hasattr(self.parser, "dirty"):
            self.parser.dirty = False

        # Add a child item that shows the filename. It should not be editable.
        self.filename_item = QtWidgets.QTreeWidgetItem(self)
        self.filename_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)

        self.refresh()

    @property
    def dirty(self):
        return self.parser.dirty

    @dirty.setter
    def dirty(self, state):
        changed = state != self.parser.dirty
        self.parser.dirty = state
        if changed:
            self.setText(0, self.name)

    @property
    def name(self):
        name = self.parser.name
        if self.dirty:
            return f"{name}*"
        return name

    def refresh(self):
        self.setText(0, self.name)
        self.filename_item.setText(0, "Filename")
        self.filename_item.setText(1, str(self.parser.filename))

        for index, variable_name in enumerate(self.parser.variables):
            # Get the existing variable item if possible. Index 0 is the
            # filename item.
            item = self.child(index + 1)
            if item:
                item.variable_name = variable_name
                item.refresh()
            else:
                # Otherwise add a new item
                VariableTreeWidgetItem(self, variable_name)

        # If any variables were removed, remove their tree widget items
        variable_count = len(self.parser.variables) + 1
        for _ in range(variable_count, self.childCount() + 1):
            self.removeChild(self.child(variable_count))

    def save(self):
        """Save the variable changes to disk.

        NOTE: This saves the data as regular json data not json5. Any comments,
        etc will be cleared by calling this method.

        Returns:
            bool: Returns if this was dirty and updated data was saved to disk.
        """
        if not self.dirty:
            return False

        # Reload data from disk
        raw_data = hab.utils.load_json_file(self.parser.filename)

        # Update the variables section with the changes.
        raw_data["variables"] = self.parser.variables

        # Save changes over top of the existing file.
        with self.parser.filename.open("w") as fle:
            json.dump(raw_data, fle, indent=4, cls=hab.utils.HabJsonEncoder)

        return True
