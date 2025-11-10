import logging

from .. import utils
from .logging_exception import LoggingExceptionInit

logger = logging.getLogger(__name__)


class MessageBoxInit(LoggingExceptionInit):
    """Overrides `sys.excepthook` and handles any exceptions raised instead of
    raising them. This prevents Qt from closing when an exception is raised.
    It logs the traceback and then shows a QMessageBox with the exception raised.
    """

    def excepthook(self, cls, exception, tb):
        super().excepthook(cls, exception, tb)

        from ..dialogs.error_message_box import ErrorMessageBox

        box = ErrorMessageBox(cls, exception, tb, parent=None)
        utils.exec_obj(box)
