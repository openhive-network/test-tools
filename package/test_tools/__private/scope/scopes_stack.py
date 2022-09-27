import atexit
import inspect
from pathlib import Path
import pkgutil
from typing import List, Optional, TYPE_CHECKING
import warnings

from test_tools.__private.logger.logger_wrapper import LoggerWrapper
from test_tools.__private.raise_exception_helper import RaiseExceptionHelper
from test_tools.__private.scope.scope import Scope
from test_tools.__private.utilities.disabled_keyboard_interrupt import DisabledKeyboardInterrupt

if TYPE_CHECKING:
    from test_tools.__private.scope import ScopedObject


class ScopesStack:
    class __NamedScope(Scope):
        def __init__(self, name: str, parent: Optional[Scope]):
            super().__init__(parent)

            self.name = name

        def __repr__(self):
            return f"<Scope '{self.name}'>"

    class __ScopeContextManager:
        def __init__(self, scope):
            self.__scope = scope

        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.__scope.exit()

    def __init__(self):
        self.__scopes_stack: List[ScopesStack.__NamedScope] = []
        self.create_new_scope("root")

        root_scope = self.__current_scope
        logger = LoggerWrapper("root", parent=None)
        root_scope.context.set_logger(logger)

        atexit.register(self.__terminate)

        RaiseExceptionHelper.initialize()

    def __repr__(self):
        return f'<ScopesStack: {", ".join(repr(scope) for scope in self.__scopes_stack)}>'

    @property
    def __current_scope(self) -> Scope:
        def get_module_path(module_name: str) -> Path:
            module_path = pkgutil.get_loader(module_name).path  # type: ignore
            return Path(module_path).absolute()  # type: ignore

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

    def create_new_scope(self, name):
        new_scope = self.__NamedScope(name, parent=self.__current_scope)
        new_scope.enter()
        self.__scopes_stack.append(new_scope)
        return self.__ScopeContextManager(self)

    def register(self, scoped_object: "ScopedObject"):
        self.__current_scope.register(scoped_object)

    def exit(self):
        with DisabledKeyboardInterrupt():
            self.__current_scope.exit()
            self.__scopes_stack.pop()

    @property
    def context(self):
        return self.__current_scope.context

    def __terminate(self):
        with DisabledKeyboardInterrupt():
            if len(self.__scopes_stack) != 1:
                warnings.warn("You forgot to exit from some scope")

            while len(self.__scopes_stack) != 0:
                self.exit()
