from enum import auto, Enum


class CleanupPolicy(Enum):
    REMOVE_EVERYTHING = auto()
    REMOVE_ONLY_UNNEEDED_FILES = auto()
    DO_NOT_REMOVE_FILES = auto()
