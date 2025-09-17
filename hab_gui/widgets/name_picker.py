from hab.parsers import HabBase
from Qt import QtCore, QtWidgets

from .. import utils


class NamePicker(QtWidgets.QGroupBox):
    """A widget for selecting from a set of names with a description.

    Provides a list view of names the user can check. A description can be shown
    next to each name.
    """

    pref_name = None
    """Defines the name of the user_pref key used to store selected names. If not
    specified then saving is disabled for this class. If enabled then user_prefs
    are saved when the check state of any item in this tree is updated. The saved
    names are stored per modified URI, see :py:meth:`standardize_uri` for details.
    """

    def __init__(self, settings, title="Options", label="Distro", parent=None):
        super().__init__(parent=parent)
        self.settings = settings
        self.default_selection = set()
        utils.load_ui(__file__, self)
        self.setTitle(title)
        self.name_tree.setHeaderLabel(label)
        self.reset_to_default_btn.setIcon(utils.Paths.icon("arrow-left-top-bold"))
        self.name_tree.itemChanged.connect(self.item_changed)
        self.reset_to_default_btn.released.connect(self.reset_to_default)

    def item_changed(self, item, column):
        """Called when a item is modified, saves the user prefs when a checked
        state is updated."""
        if column != 0:
            return
        self.save_user_selection()

    def names(self):
        """Returns a dict of the current state of this widget.

        The key is the name shown in column 1. The value is a 2 item list containing
        the description shown to the user in column 2 and if name is checked by
        default.
        """
        ret = {}
        for index in range(self.name_tree.topLevelItemCount()):
            item = self.name_tree.topLevelItem(index)
            checked = item.checkState(0) == QtCore.Qt.CheckState.Checked
            ret[item.text(0)] = [item.text(1), checked]
        return ret

    def set_names(self, names, uri=None):
        self.name_tree.clear()
        # Reset the default selection
        self.default_selection = set()
        with utils.block_signals([self.name_tree]):
            for name, settings in names.items():
                item = QtWidgets.QTreeWidgetItem(self.name_tree, [name, settings[0]])
                item.setToolTip(1, settings[0])
                # Build the `default_selection` set for the current URI
                if len(settings) > 1 and settings[1]:
                    self.default_selection.add(name)
                item.setCheckState(0, QtCore.Qt.CheckState.Unchecked)

        self.name_tree.resizeColumnToContents(0)
        user_selection = self.user_selection(uri)
        if user_selection is None:
            self.set_selected(self.default_selection)
            self.reset_to_default_btn.setDisabled(True)
        else:
            self.set_selected(user_selection)
            self.reset_to_default_btn.setDisabled(False)

    def reset_to_default(self):
        """Reset the checked state of names to the default values, clearing
        saved user_prefs for the current URI.
        """
        self.set_selected(self.default_selection)
        self.save_user_selection(reset=True)

    def selected(self):
        """Returns the checked names as a list."""
        ret = set()
        for index in range(self.name_tree.topLevelItemCount()):
            item = self.name_tree.topLevelItem(index)
            if item.checkState(0) == QtCore.Qt.CheckState.Checked:
                ret.add(item.text(0))
        return ret

    def set_selected(self, selected):
        """Update the checked state to just these names."""
        with utils.block_signals([self.name_tree]):
            for index in range(self.name_tree.topLevelItemCount()):
                item = self.name_tree.topLevelItem(index)
                name = item.text(0)
                item.setCheckState(
                    0,
                    QtCore.Qt.CheckState.Checked
                    if name in selected
                    else QtCore.Qt.CheckState.Unchecked,
                )

    def sizeHint(self):  # noqa: N802
        return QtCore.QSize(0, 160)

    def standardize_uri(self, uri):
        """Modify the URI for saving in user_prefs. This implementation discards
        all but the top level item."""
        return uri.split(HabBase.separator)[0]

    def user_selection(self, uri):
        """Returns the names selected for the current URI saved in user_prefs
        as a dict or None if user_prefs are disabled.
        """
        if not self.pref_name:
            return None

        if uri is None:
            uri = self.settings.uri

        uri = self.standardize_uri(uri)
        return self.settings.user_pref(self.pref_name, {}).get(uri, None)

    def save_user_selection(self, reset=False):
        """Saves the currently selected names into user_prefs if enabled.

        Also always updates the enabled state of the reset button.
        """
        uri = self.standardize_uri(self.settings.uri)
        user_selections = self.settings.user_pref(self.pref_name, {})
        selected = self.selected()
        is_default = selected == self.default_selection
        if reset and is_default:
            # Only remove the URI from user_prefs if reset was pressed so we
            # can save having all optional dependencies disabled.
            if uri in user_selections:
                del user_selections[uri]
            self.reset_to_default_btn.setDisabled(True)
        else:
            user_selections[uri] = list(selected)
            self.reset_to_default_btn.setDisabled(False)

        if self.pref_name:
            self.settings.set_user_pref(self.pref_name, user_selections)
