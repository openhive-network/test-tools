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