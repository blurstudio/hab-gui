import traceback

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from Qt import QtCore, QtWidgets


class ErrorMessageBox(QtWidgets.QMessageBox):
    """QMessageBox that shows a manageable, highlighted python traceback.

    If the traceback is longer than the short version, then the full traceback
    is shown in more details section. It also adds a button to easily copy the
    full raw traceback text.
    """

    def __init__(self, etype, value, tb, parent=None):
        super().__init__(parent=parent)
        self._raw_traceback = None
        self.etype = etype
        self.value = value
        self.tb = tb
        # Limit the length of the traceback to the last X results.
        self.stack_limit = -5

        self.setWindowTitle("Exception")
        self.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        # Using detailedText seems to disable the close button, enable it
        self.setEscapeButton(QtWidgets.QMessageBox.StandardButton.Ok)

        # Create a button allowing the user to copy the non-highlighted text
        copy_btn = self.addButton("Copy", QtWidgets.QMessageBox.ButtonRole.ActionRole)
        copy_btn.setToolTip("Copy the full traceback for error reporting.")
        # Disconnect the QMessageBox signals that would cause the box to close
        # when this button is pressed and add our own signal connection
        copy_btn.disconnect()
        copy_btn.released.connect(self.copy_traceback)

        self.setDefaultButton(QtWidgets.QMessageBox.StandardButton.Ok)
        self.refresh()

    @QtCore.Slot()
    def copy_traceback(self):
        """Copy the raw traceback into the copy paste buffer."""
        text = self._raw_traceback
        QtWidgets.QApplication.clipboard().setText(text)

    def highlight(self, text):
        """Syntax highlight the traceback to make it more readable."""
        fhtml = HtmlFormatter()
        body = highlight(text, PythonLexer(), fhtml)
        style = fhtml.get_style_defs()
        return f"<head><style>{style}</style></head>{body}"

    def refresh(self):
        short = None
        full = traceback.format_exception(self.etype, self.value, self.tb)
        # If the traceback is longer than stack_limit, then show a short tb
        # in the message box and include the full traceback in detailed text
        if len(full) - 2 > abs(self.stack_limit):
            # Subtract two to account for first and last line of a traceback.
            # Each file line in the list includes the python code on the next line.
            short = traceback.format_exception(
                self.etype, self.value, self.tb, limit=self.stack_limit
            )
            short = "".join(short)

        self._raw_traceback = "".join(full)
        if short:
            self.setText(self.highlight(short))
            self.setDetailedText(self._raw_traceback)
        else:
            self.setText(self.highlight(self._raw_traceback))
            self.setDetailedText("")
