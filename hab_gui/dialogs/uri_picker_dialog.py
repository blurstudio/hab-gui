from Qt import QtCore, QtWidgets


class UriPickerDialog(QtWidgets.QDialog):
    """A dialog for asking the user to pick a URI only when required.

    This dialog is intended to be a front end for gui based methods of launching
    aliases. It is especially useful when using `user_prefs with timeout`_
    to only show the dialog if the timeout has expired.

    The intended workflow for this item is to create a desktop shortcut or other
    gui based method for generically launching a alias like maya. The shortcut
    would call `habw gui launch - maya`. If user prefs are enabled and the URI has
    not timed out, the maya app is launched without user interaction. However if
    the user prefs are disabled or URI has timed out, or the user is pressing the
    shift key or the user has checked the always ask checkbox for maya, it will
    show this dialog allowing the user to choose the URI they want to use.

    Args:
        settings (hab_gui.settings.Settings): Used to handle gui settings and
            facilitate emitting signals when settings change.
        alias (str, optional): The alias name the user want's to launch.
        expired (bool, optional): The text shown to the user indicates that it
            expired instead of simply asking the user to choose a URI.
        parent (Qt.QtWidgets.QWidget, optional): Define a parent for this widget.

    .. _user_prefs with timeout:
        https://github.com/blurstudio/hab?tab=readme-ov-file#user-prefs
    """

    template = {
        "label": [
            "Saved URI expired, please update with what you are currently working on.",
            "Choose the URI you would like to launch{_alias} with.",
        ],
        "title": [
            "Pick URI to launch {alias}",
            "Pick URI to launch",
        ],
    }
    """Templates for the text shown in this dialog. `str.format` is called passing
    the kwarg `alias` as `self.alias`. `_kwarg` is the alias with a leading space
    if specified otherwise an empty string.
    "label" is the informational label text, If the URI expired,
    index 0 is used, otherwise index 1. "title" is the window title, if an alias
    is provided index 0 is used, otherwise index 1.
    """

    def __init__(self, settings, alias=None, expired=False, parent=None):
        super().__init__(parent=parent)
        self.alias = alias
        self.expired = expired
        self.settings = settings
        self._cls_uri_widget = self.settings.load_entry_point(
            "hab_gui.uri.widget", "hab_gui.widgets.uri_combobox:URIComboBox"
        )
        self.init_gui()

    def accept(self):
        self.save_prefs()
        super().accept()

    def init_gui(self):
        self.info_label = QtWidgets.QLabel(self)
        self.uri_widget = self._cls_uri_widget(self.settings, parent=self)
        self.always_ask = QtWidgets.QCheckBox(
            "Ask on every launch (or hold shift when launching)", self
        )

        self.uiButtonsBOX = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Cancel, self
        )
        self.uiButtonsBOX.addButton("Launch", QtWidgets.QDialogButtonBox.AcceptRole)
        self.uiButtonsBOX.accepted.connect(self.accept)
        self.uiButtonsBOX.rejected.connect(self.reject)

        lyt = QtWidgets.QVBoxLayout(self)
        lyt.addWidget(self.info_label)
        lyt.addWidget(self.uri_widget)
        lyt.addWidget(self.always_ask)
        lyt.addWidget(self.uiButtonsBOX)
        self.refresh()

    @classmethod
    def prefs(cls, settings, alias):
        """Returns a dictionary of user preference information for this dialog.

        Returns:
            enabled (bool): If user prefs are enabled.
            user_prefs: The actual user_prefs object.
            ask (bool, optional): If the user want's to always ask for this alias.
        """
        user_prefs = settings.resolver.user_prefs()
        ret = dict(enabled=user_prefs.enabled, user_prefs=user_prefs)
        if not user_prefs.enabled:
            return ret
        user_prefs.load()
        ret["ask"] = user_prefs.get("uri_picker", {}).get(alias, False)
        return ret

    def save_prefs(self):
        """Save hab user_prefs."""
        user_prefs = self.settings.resolver.user_prefs()
        if user_prefs.enabled:
            user_prefs.setdefault("uri_picker", {})[
                self.alias
            ] = self.always_ask.isChecked()
            # Calling this setter triggers saving of user prefs
            user_prefs.uri = self.uri_widget.uri()

    def refresh(self):
        fkwargs = {
            "_alias": " " + self.alias if self.alias else "",
            "alias": self.alias,
        }

        title = self.template["title"][0 if self.alias else 1]
        title = title.format(**fkwargs)
        self.setWindowTitle(title)

        text = self.template["label"][0 if self.expired else 1]
        text = text.format(**fkwargs)
        self.info_label.setText(text)

        if self.settings.uri is not None:
            self.uri_widget.set_uri(self.settings.uri)

        prefs = self.prefs(self.settings, self.alias)
        self.always_ask.setVisible(prefs["enabled"])
        if prefs["enabled"]:
            self.always_ask.setChecked(prefs["ask"])

    @classmethod
    def should_show(cls, settings, alias=None):
        """Checks if this dialog should be shown.

        Checks for and returns True if any of the following are true:

        - If user_prefs are disabled.
        - If the user is pressing the shift key.
        - If the user has checked the always ask checkbox for this alias.
        - If the uri has timed out.
        """
        prefs = cls.prefs(settings, alias)
        # If prefs are disabled, always show the dialog
        if not prefs["enabled"]:
            print("no prefs")
            return True

        # The shift key is pressed
        # Note: Not using `keyboardModifiers` because it is not updated when
        # calling this from the cli module.
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            return True

        # always_ask is checked for this alias
        if prefs["ask"]:
            return True

        # finally check if the uri has expired
        uri_check = prefs["user_prefs"].uri_check()
        return uri_check.timedout
