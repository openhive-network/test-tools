from enum import IntEnum
import logging


class UserLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Level(IntEnum):
    TRACE = (logging.NOTSET + logging.DEBUG) // 2
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


assert logging.NOTSET < Level.TRACE < Level.DEBUG

logging.addLevelName(Level.TRACE, "TRACE")
