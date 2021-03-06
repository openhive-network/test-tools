from __future__ import annotations

from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING

from test_tools.__private.names import Names

if TYPE_CHECKING:
    from test_tools.__private.logger.logger_wrapper import LoggerWrapper


class Context:
    # Member _names should be private (__names), but when it is, Pylint crashes.
    # Issue is reported and can be tracked here: https://github.com/PyCQA/pylint/issues/6709.
    #
    # When issue will be resolved, make `_names` member private.

    DEFAULT_CURRENT_DIRECTORY = Path('./generated').absolute()

    def __init__(self, *, parent: Optional[Context]):
        self.__current_directory: Path

        self.__parent: Optional[Context] = parent

        if self.__parent is not None:
            self.__current_directory = self.__parent.get_current_directory()
            self.__logger = self.__parent.get_logger()
            self._names = Names(parent=self.__parent._names)  # pylint: disable=protected-access
            # Accessing another instance private member of the same class is not a privacy violation.
        else:
            self.__current_directory = self.DEFAULT_CURRENT_DIRECTORY
            self.__logger = None
            self._names = Names()

    def get_current_directory(self) -> Path:
        return self.__current_directory

    def set_current_directory(self, directory: Union[str, Path]):
        self.__current_directory = Path(directory)

    def get_logger(self) -> LoggerWrapper:
        return self.__logger

    def set_logger(self, logger: LoggerWrapper):
        self.__logger = logger

    def get_names(self) -> Names:
        return self._names
