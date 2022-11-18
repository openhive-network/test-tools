from pathlib import Path
import re
from typing import Final, Optional

import pytest

import test_tools as tt
from test_tools.__private.logger.function_logger import FunctionLogger
from test_tools.__private.logger.levels import Level
from test_tools.__private.logger.module_logger import ModuleLogger
from test_tools.__private.logger.package_logger import PackageLogger
from test_tools.__private.scope import current_scope, ScopedCleanupPolicy, ScopedCurrentDirectory

__cleanup_policy_was_set_in_package_scope: bool = False
__DEFAULT_CLEANUP_POLICY: Final[tt.constants.CleanupPolicy] = tt.constants.CleanupPolicy.REMOVE_ONLY_UNNEEDED_FILES


@pytest.fixture(autouse=True, scope="function")
def function_scope(request):
    with current_scope.create_new_scope(f"function: {__get_function_name(request)}"):
        ScopedCurrentDirectory(__get_directory_for_function(request))
        ScopedCleanupPolicy(tt.cleanup_policy.get_default())

        current_logger = current_scope.context.get_logger()
        function_logger = current_logger.create_child_logger(__get_logger_name(request), child_type=FunctionLogger)
        function_logger.log_to_stdout()
        function_logger.log_to_file()
        current_scope.context.set_logger(function_logger)

        function_logger.set_file_handler_level(Level.TRACE)
        function_logger.trace("Entering function scope")
        yield
        function_logger.trace("Leaving function scope")


@pytest.fixture(autouse=True, scope="module")
def module_scope(request):
    with current_scope.create_new_scope(f"module: {__get_module_name(request)}"):
        ScopedCurrentDirectory(__get_directory_for_module(request))
        if not __cleanup_policy_was_set_in_package_scope:
            ScopedCleanupPolicy(__DEFAULT_CLEANUP_POLICY)

        current_logger = current_scope.context.get_logger()
        module_logger = current_logger.create_child_logger(__get_logger_name(request), child_type=ModuleLogger)
        module_logger.log_to_file()
        current_scope.context.set_logger(module_logger)

        # module_logger.set_file_handler_level(Level.TRACE)
        module_logger.trace("Entering module scope")
        yield
        module_logger.trace("Leaving module scope")


@pytest.fixture(autouse=True, scope="package")
def package_scope(request):
    global __cleanup_policy_was_set_in_package_scope  # pylint: disable=invalid-name, global-statement

    if not __is_run_in_package(request):
        # Fixtures with package scope are run also for tests which are not in any
        # package. If this is the case, package scope shouldn't be created.
        yield
    else:
        with current_scope.create_new_scope(f"package: {__get_package_name(request)}"):
            ScopedCurrentDirectory(__get_directory_for_package(request))
            ScopedCleanupPolicy(__DEFAULT_CLEANUP_POLICY)
            __cleanup_policy_was_set_in_package_scope = True

            current_logger = current_scope.context.get_logger()
            package_logger = current_logger.create_child_logger(__get_logger_name(request), child_type=PackageLogger)
            package_logger.log_to_file()
            current_scope.context.set_logger(package_logger)

            package_logger.trace("Entering package scope")
            yield
            package_logger.trace("Leaving package scope")


def __is_run_in_package(request) -> bool:
    return __get_pytest_package_object(request) is not None


def __get_package_name(request) -> str:
    return __get_pytest_package_object(request).name


def __get_directory_for_package(request) -> Path:
    return Path(__get_pytest_package_object(request).fspath).parent / "generated_by_package_fixtures"


def __get_directory_for_module(request):
    assert request.scope == "module"
    module_name = Path(request.module.__file__).stem
    module_directory = Path(request.module.__file__).parent
    return module_directory / f"generated_during_{module_name}"


def __get_module_name(request) -> str:
    assert request.scope == "module"
    return Path(request.module.__file__).stem


def __get_directory_for_function(request):
    assert request.scope == "function"
    directory_name = __convert_test_name_to_directory_name(request.node.name)
    return current_scope.context.get_current_directory() / directory_name


def __convert_test_name_to_directory_name(test_name: str) -> str:
    directory_name = []

    parametrized_test_match = re.match(r"([\w_]+)\[(.*)\]", test_name)
    if parametrized_test_match:
        test_name = f"{parametrized_test_match[1]}_with_parameters_{parametrized_test_match[2]}"

    for character in test_name:
        if character.isalnum() or character in "-_":
            pass
        else:
            character = f"-0x{ord(character):X}-"

        directory_name.append(character)

    return "".join(directory_name)


def __get_function_name(request) -> str:
    assert request.scope == "function"
    return request.node.name


def __get_pytest_package_object(request) -> Optional[pytest.Package]:
    assert request.scope == "package"

    if isinstance(request.node, pytest.Package):
        return request.node

    pytest_scope = request.node.items[0]
    while pytest_scope is not None:
        if isinstance(pytest_scope, pytest.Package):
            return pytest_scope

        pytest_scope = pytest_scope.parent

    return None


def __get_logger_name(request):
    if request.scope == "function":
        return request.node.name

    if request.scope == "module":
        path = Path(request.node.name)
        path_without_extension = str(path.parent.joinpath(path.stem))
        return path_without_extension.replace("/", ".")

    if request.scope == "package":
        return __get_package_name(request)

    assert False, "Shouldn't be ever reached"
