import logging
import sys

from .base_init import BaseInit

logger = logging.getLogger(__name__)


class LoggingExceptionInit(BaseInit):
    """Overrides `sys.excepthook` and logs any exceptions raised instead of
    raising them. This prevents Qt from closing when an exception is raised.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sys.excepthook = self.excepthook

    def excepthook(self, cls, exception, tb):
        logger.exception("Captured Exception:", exc_info=(cls, exception, tb))
