from enum import auto, Enum


class NodeCleanUpPolicy(Enum):
    REMOVE_EVERYTHING = auto()
    REMOVE_ONLY_UNNEEDED_FILES = auto()
    DO_NOT_REMOVE_FILES = auto()


class NetworkCleanUpPolicy(Enum):
    REMOVE_EVERYTHING = auto()
    REMOVE_ONLY_UNNEEDED_FILES = auto()
    DO_NOT_REMOVE_FILES = auto()


class WorldCleanUpPolicy(Enum):
    REMOVE_EVERYTHING = auto()
    REMOVE_ONLY_UNNEEDED_FILES = auto()
    DO_NOT_REMOVE_FILES = auto()

class LoggingOutgoingRequestPolicy(Enum):
    DO_NOT_LOG = auto()
    BASIC_LOGGING = auto()
    LOGGING_AS_CURL_REQUEST = auto()
