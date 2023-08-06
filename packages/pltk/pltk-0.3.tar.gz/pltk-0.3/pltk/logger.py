"""Logging support."""
import sys
import logging
import logging.handlers

logging.root.setLevel(logging.DEBUG)

facility = logging.handlers.SysLogHandler.LOG_LOCAL4

address = '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log'
handler = logging.handlers.SysLogHandler(facility=facility, address=address)

handler.setFormatter(logging.Formatter(logging.BASIC_FORMAT, None))
logging.root.addHandler(handler)

IGNORED_LOGGERS = ['beaker', 'suds']
for logger in IGNORED_LOGGERS:
    logging.getLogger(logger).setLevel(logging.ERROR)


def get(name):
    """Return a logger handler.

    >>> from pltk import logger
    >>> logger = logger.get(__file__)
    >>> logger.debug('Something for debug')
    """
    return logging.getLogger(name)
