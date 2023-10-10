from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from test_tools.__private.names import Names

if TYPE_CHECKING:
    from loguru import Logger


class Context:
    DEFAULT_CURRENT_DIRECTORY = Path("./generated").absolute()

    def __init__(self, *, parent: Context | None) -> None:
        self.__current_directory: Path

        self.__parent: Context | None = parent
        self.__names: Names
        self.__logger: Logger | None

        if self.__parent is not None:
            self.__current_directory = self.__parent.get_current_directory()
            self.__names = Names(parent=self.__parent.__names)
            self.__logger = self.__parent.logger.bind(context_parent=self.__parent, context_names=self.__names)
        else:
            self.__current_directory = self.DEFAULT_CURRENT_DIRECTORY
            self.__logger = logger
            self.__names = Names()

    def get_current_directory(self) -> Path:
        return self.__current_directory

    def set_current_directory(self, directory: str | Path) -> None:
        self.__current_directory = Path(directory)

    @property
    def logger(self) -> Logger:
        assert self.__logger is not None  # mypy check
        return self.__logger

    def get_names(self) -> Names:
        return self.__names
