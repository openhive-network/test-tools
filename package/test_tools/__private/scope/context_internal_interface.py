from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from loguru import Logger

    from test_tools.__private.names import Names
    from test_tools.__private.scope import ScopesStack
    from test_tools.__private.scope.context_definition import Context


class ContextInternalHandle:
    def __init__(self, scopes_stack: ScopesStack) -> None:
        self.__scopes_stack: ScopesStack = scopes_stack

    @property
    def __context(self) -> Context:
        return self.__scopes_stack.context

    @property
    def __current_directory(self) -> Path:
        return self.__context.get_current_directory()

    def get_current_directory(self) -> Path:
        if not self.__current_directory.exists():
            self.__current_directory.mkdir()
        return self.__current_directory

    def get_logger(self) -> Logger:
        return self.__context.logger

    @property
    def names(self) -> Names:
        return self.__context.get_names()
