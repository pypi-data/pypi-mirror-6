"""
Logs handling.
"""
import logging


class _Logger(object):
    """
    Simple logger. Supports only info and debug. Uses NullHandler by default.
    """
    def __init__(self, name=__name__, level=logging.DEBUG, handler=None, formatter=None):
        # Default handler does nothing (a logger must have at least one handler).
        if handler is None:
            handler = logging.NullHandler()

        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        # Setting handler (a logger must have at least one handler attached to it)
        self._handler = handler
        self._handler.setLevel(level)

        # Setting formatter
        if formatter is not None:
            self._handler.setFormatter(formatter)
        self._logger.addHandler(self._handler)

    def __del__(self):
        # If we don't remove the handler and a call to logging.getLogger(...) will be made with
        # the same name as the current logger, the handler will remain.
        self._logger.removeHandler(self._handler)

    def info(self, msg):
        self._logger.info(msg)

    def debug(self, msg):
        self._logger.debug(msg)


class StdoutLogger(_Logger):
    """
    Simple logger for printing to STDOUT.
    """
    def __init__(self, name="eyes", level=logging.DEBUG):
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        super(StdoutLogger, self).__init__(name, level, handler, formatter)


class NullLogger(_Logger):
    """
    Simple logger class which does nothing.
    """
    def __init__(self, name="eyes", level=logging.DEBUG):
        super(NullLogger, self).__init__(name, level)


# No logger by default
_logger = None


def set_logger(logger=None):
    global _logger
    _logger = logger


def info(msg):
    if _logger is not None:
        _logger.info(msg)


def debug(msg):
    if _logger is not None:
        _logger.debug(msg)

