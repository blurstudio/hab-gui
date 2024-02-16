import logging

from Qt import QtCore, QtWidgets

from ... import utils
from .file_tree_widget_item import FileTreeWidgetItem
from .variable_tree_widget_item import VariableTreeWidgetItem

logger = logging.getLogger(__name__)


class CustomVariableEditor(QtWidgets.QWidget):
    """A widget that can view and edit custom variables in hab configs/distros.

    This widget will only show config/distro files that have `variable_editor`
    set to `True` in the top level dict.

    Args:
        resolver (hab.Resolver): The resolver to change verbosity settings on.
        verbosity (int): Change the verbosity setting to this value. If None is passed,
            all results are be shown without any filtering.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
    """

    def __init__(self, resolver, verbosity=0, parent=None):
        super().__init__(parent)
        self._refresh_on_show = True
        self.resolver = resolver
        self.verbosity = verbosity
        utils.load_ui(__file__, self)
        self.setWindowIcon(utils.Paths.icon("habihat.svg"))

        self.uiAddVariableBTN.setIcon(utils.Paths.icon("plus-thick.svg"))
        self.uiEditCurrentItemBTN.setIcon(utils.Paths.icon("pencil-box-outline.svg"))
        self.uiResetBTN.setIcon(utils.Paths.icon("refresh.svg"))
        self.uiRemoveVariableBTN.setIcon(utils.Paths.icon("minus-thick.svg"))
        self.uiSaveBTN.setIcon(utils.Paths.icon("content-save.svg"))

        # Configure editing of widget items. _is_refreshing is used to only
        # prevent updating the model while refreshing, not other signals.
        self._is_refreshing = False
        self.uiVariableTREE.model().dataChanged.connect(self.editing_finished)

    def add_variable(self):
        """Add a new variable to the selected FileTreeWidgetItem"""
        item = self.uiVariableTREE.currentItem()
        if "Undefined" in item.parser.variables:
            QtWidgets.QMessageBox.information(
                self,
                "Variable already defined",
                "You already have a variable named Undefined. Change the name "
                "of that variable before adding a new one.",
            )
        else:
            item.parser.variables["Undefined"] = "Undefined"
            VariableTreeWidgetItem(item, "Undefined")
            # Mark the item as dirty
            item.dirty = True

    @property
    def dirty(self):
        """Generator that yields any FileTreeWidgetItem's that are modified."""
        for index in range(self.uiVariableTREE.topLevelItemCount()):
            child = self.uiVariableTREE.topLevelItem(index)
            if child.dirty:
                yield child

    def edit_cell(self):
        """Edit the currently selected cell"""
        index = self.uiVariableTREE.currentIndex()
        self.uiVariableTREE.edit(index)

    def editing_finished(self, top_left, bottom_right, roles):
        if self._is_refreshing:
            return

        if QtCore.Qt.EditRole in roles:
            item = self.uiVariableTREE.itemFromIndex(top_left)
            column = top_left.column()
            if column == 0:
                item.variable_name = item.text(column)
            elif column == 1:
                item.value = item.text(column)

    def current_changed(self, current=None, previous=None):
        """Enable buttons based on the current selection."""
        item = self.uiVariableTREE.currentItem()
        is_file = isinstance(item, FileTreeWidgetItem)
        self.uiAddVariableBTN.setEnabled(is_file)
        self.uiEditCurrentItemBTN.setEnabled(not is_file)
        self.uiRemoveVariableBTN.setEnabled(not is_file)

    @utils.cursor_override()
    def refresh(self):
        self._is_refreshing = True
        try:
            self.uiVariableTREE.clear()

            for forest in (self.resolver.configs, self.resolver.distros):
                for row in self.resolver.dump_forest(forest, attr=None):
                    parser = row.node
                    if parser.filename:
                        if parser.load(parser.filename).get("variable_editor", False):
                            FileTreeWidgetItem(self.uiVariableTREE, parser)

            self.uiVariableTREE.expandAll()
            self.uiVariableTREE.resizeColumnToContents(0)

            self.current_changed()
        finally:
            self._is_refreshing = False

    @property
    def refresh_on_show(self):
        """Should this automatically refresh when the widget is shown."""
        return self._refresh_on_show

    @refresh_on_show.setter
    def refresh_on_show(self, state):
        self._refresh_on_show = state

    def remove_variable(self):
        """Remove the currently selected variable"""
        item = self.uiVariableTREE.currentItem()
        item.remove_variable()
        parent = item.parent()
        idx = parent.indexOfChild(item)
        parent.takeChild(idx)
        parent.dirty = True

    def reset(self):
        """Revert any un-saved changes."""
        self.resolver.clear_caches()
        self.refresh()

    def save(self):
        """Save all changes to disk"""
        for parser in self.dirty:
            parser.save()

        # Re-display the saved data
        self.reset()

    def showEvent(self, event):  # noqa: N802
        super().showEvent(event)
        if self.refresh_on_show:
            self.refresh()

    @classmethod
    def create_dialog(cls, resolver, verbosity=0, title="Edit Variables", parent=None):
        """Create a simple standalone QDialog containing this widget.

        Args:
            resolver (hab.Resolver): The resolver to change verbosity settings on.
            verbosity (int): Change the verbosity setting to this value. If None is passed,
                all results are be shown without any filtering.
            title (str, optional): The window title of the created dialog.
            parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.
        """
        dlg = QtWidgets.QDialog(parent=parent)
        dlg.setWindowTitle(title)
        dlg.setWindowIcon(utils.Paths.icon("pencil-box-outline.svg"))
        layout = QtWidgets.QVBoxLayout(dlg)
        dlg.uiVariableWGT = cls(resolver, verbosity=verbosity, parent=dlg)
        layout.addWidget(dlg.uiVariableWGT)
        return dlg
