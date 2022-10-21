from enum import Enum
import logging


class Level(Enum):
    NOTSET = logging.NOTSET
    TRACE = (logging.NOTSET + logging.DEBUG) // 2
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


assert Level.NOTSET.value < Level.TRACE.value < Level.DEBUG.value
