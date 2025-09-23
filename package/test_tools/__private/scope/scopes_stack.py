from __future__ import annotations

import atexit
import importlib.util
import inspect
import warnings
from pathlib import Path
from typing import TYPE_CHECKING

from test_tools.__private.raise_exception_helper import RaiseExceptionHelper
from test_tools.__private.scope.scope import Scope
from test_tools.__private.utilities.disabled_keyboard_interrupt import DisabledKeyboardInterrupt

if TYPE_CHECKING:
    from types import TracebackType

    from test_tools.__private.scope import ScopedObject
    from test_tools.__private.scope.context_definition import Context


class ScopesStack:
    class NamedScope(Scope):
        def __init__(self, name: str, parent: Scope | None) -> None:
            super().__init__(parent)

            self.name = name

        def __repr__(self) -> str:
            return f"<Scope '{self.name}'>"

    class ScopeContextManager:
        def __init__(self, scope: Scope) -> None:
            self.__scope = scope

        def __enter__(self) -> None:
            """Does nothing."""

        def __exit__(self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None) -> None:
            self.__scope.exit_from_scope()

    def __init__(self) -> None:
        self.__scopes_stack: list[ScopesStack.NamedScope] = []
        self.create_new_scope("root")
        atexit.register(self.__terminate)
        RaiseExceptionHelper.initialize()

    def __repr__(self) -> str:
        return f'<ScopesStack: {", ".join(repr(scope) for scope in self.__scopes_stack)}>'

    @property
    def __current_scope(self) -> Scope | None:
        def get_module_path(module_name: str) -> Path:
            spec = importlib.util.find_spec(module_name)
            if spec is None or spec.origin is None:
                raise ImportError(f"Cannot find module '{module_name}'")
            return Path(spec.origin).absolute()

        scope_fixtures_definitions_path = get_module_path("test_tools.__private.scope.scope_fixtures_definitions")
        pytest_fixtures_caller_path = get_module_path("_pytest.fixtures")
        pytest_test_runner_path = get_module_path("_pytest.python")

        for frame in inspect.stack():
            if Path(frame.filename).absolute() == scope_fixtures_definitions_path:
                break  # We are in special TestTools fixtures, which handles scopes creation.

            if Path(frame.filename).absolute() == pytest_fixtures_caller_path:
                if frame.frame.f_locals["request"].scope == "package":
                    for scope in self.__scopes_stack:
                        if scope.name.startswith("package"):
                            # We are in fixture, which is NOT handled correctly with default behavior.
                            # When test requests fixture with package scope and fixture wasn't initialized earlier,
                            # TestTools' scopes stack thinks that we are in module scope and pass it to requests from
                            # package scope fixture. Here is workaround for this case.
                            return scope

                break  # We are in fixture, which is handled correctly with default behavior.

            if Path(frame.filename).absolute() == pytest_test_runner_path:
                break  # We are in test function.

        return self.__scopes_stack[-1] if self.__scopes_stack else None

    def create_new_scope(self, name: str) -> ScopeContextManager:
        new_scope = self.NamedScope(name, parent=self.__current_scope)
        new_scope.enter()
        self.__scopes_stack.append(new_scope)
        return self.ScopeContextManager(self)  # type: ignore[arg-type]

    def register(self, scoped_object: ScopedObject) -> None:
        assert self.__current_scope is not None  # mypy check
        self.__current_scope.register(scoped_object)

    def exit_from_scope(self) -> None:
        with DisabledKeyboardInterrupt():
            assert self.__current_scope is not None  # mypy check
            self.__current_scope.exit_from_scope()
            self.__scopes_stack.pop()

    @property
    def context(self) -> Context:
        assert self.__current_scope is not None  # mypy check
        return self.__current_scope.context

    def __terminate(self) -> None:
        with DisabledKeyboardInterrupt():
            if len(self.__scopes_stack) != 1:
                warnings.warn("You forgot to exit from some scope", stacklevel=1)

            while len(self.__scopes_stack) != 0:
                self.exit_from_scope()
