from __future__ import annotations

from pathlib import Path

from test_tools.__private.scope.scope_singleton import current_scope
from test_tools.__private.scope.scoped_object import ScopedObject


class ScopedCurrentDirectory(ScopedObject):
    """
    Scoped object which.

        - on creation -- creates directory and sets it as current directory
        - at exit from scope -- restores previous directory and removes self if is empty.
    """

    def __init__(self, path: str | Path) -> None:
        super().__init__()

        self.__path = Path(path)
        self.__create_directory()

        self.__previous_path = current_scope.context.get_current_directory()
        current_scope.context.set_current_directory(self.__path)

    def at_exit_from_scope(self) -> None:
        self.__remove_directory_if_empty()
        current_scope.context.set_current_directory(self.__previous_path)

    def __create_directory(self) -> None:
        self.__path.mkdir(parents=True, exist_ok=True)

    def __remove_directory_if_empty(self) -> None:
        if self.__is_empty():
            self.__path.rmdir()

    def __is_empty(self) -> bool:
        return not any(self.__path.iterdir())
