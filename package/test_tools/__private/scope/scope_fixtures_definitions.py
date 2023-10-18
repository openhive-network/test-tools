from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

import test_tools as tt
from test_tools.__private.scope import ScopedCleanupPolicy, ScopedCurrentDirectory, current_scope

if TYPE_CHECKING:
    from collections.abc import Iterator

__cleanup_policy_was_set_in_package_scope: bool = False
__DEFAULT_CLEANUP_POLICY: Final[tt.constants.CleanupPolicy] = tt.constants.CleanupPolicy.REMOVE_ONLY_UNNEEDED_FILES


@pytest.fixture(autouse=True)
def function_scope(request: pytest.FixtureRequest) -> Iterator[None]:
    with current_scope.create_new_scope(f"function: {__get_function_name(request)}"):
        function_dir = __get_directory_for_function(request)
        ScopedCurrentDirectory(function_dir)
        ScopedCleanupPolicy(tt.cleanup_policy.get_default())

        with current_scope.context.logger.contextualize(scope="function"):
            handler_id = current_scope.context.logger.add(
                function_dir / "test.log",
                enqueue=True,
                filter=lambda extras: extras["extra"].get("scope") == "function",
            )
            yield
            current_scope.context.logger.remove(handler_id=handler_id)


@pytest.fixture(autouse=True, scope="module")
def module_scope(request: pytest.FixtureRequest) -> Iterator[None]:
    with current_scope.create_new_scope(f"module: {__get_module_name(request)}"):
        module_dir = __get_directory_for_module(request)
        ScopedCurrentDirectory(module_dir)
        if not __cleanup_policy_was_set_in_package_scope:
            ScopedCleanupPolicy(__DEFAULT_CLEANUP_POLICY)

        with current_scope.context.logger.contextualize(scope="module"):
            handler_id = current_scope.context.logger.add(
                module_dir / "module.log", enqueue=True, filter=lambda extras: extras["extra"].get("scope") == "module"
            )
            yield
            current_scope.context.logger.remove(handler_id=handler_id)


@pytest.fixture(autouse=True, scope="package")
def package_scope(request: pytest.FixtureRequest) -> Iterator[None]:
    global __cleanup_policy_was_set_in_package_scope  # noqa: PLW0603

    if not __is_run_in_package(request):
        # Fixtures with package scope are run also for tests which are not in any
        # package. If this is the case, package scope shouldn't be created.
        yield
    else:
        with current_scope.create_new_scope(f"package: {__get_package_name(request)}"):
            package_dir = __get_directory_for_package(request)
            ScopedCurrentDirectory(package_dir)
            ScopedCleanupPolicy(__DEFAULT_CLEANUP_POLICY)
            __cleanup_policy_was_set_in_package_scope = True

            with current_scope.context.logger.contextualize(scope="package"):
                handler_id = current_scope.context.logger.add(
                    package_dir / "package.log",
                    enqueue=True,
                    filter=lambda extras: extras["extra"].get("scope") == "package",
                )
                yield
                current_scope.context.logger.remove(handler_id=handler_id)


def __is_run_in_package(request: pytest.FixtureRequest) -> bool:
    return __get_pytest_package_object(request) is not None


def __get_package_name(request: pytest.FixtureRequest) -> str:
    package = __get_pytest_package_object(request)
    assert package is not None
    return package.name


def __get_directory_for_package(request: pytest.FixtureRequest) -> Path:
    package = __get_pytest_package_object(request)
    assert package is not None
    return Path(package.fspath).parent / "generated_by_package_fixtures"


def __get_directory_for_module(request: pytest.FixtureRequest) -> Path:
    assert request.scope == "module"
    module_name = Path(request.module.__file__).stem
    module_directory = Path(request.module.__file__).parent
    return module_directory / f"generated_during_{module_name}"


def __get_module_name(request: pytest.FixtureRequest) -> str:
    assert request.scope == "module"
    return Path(request.module.__file__).stem


def __get_directory_for_function(request: pytest.FixtureRequest) -> Path:
    assert request.scope == "function"
    directory_name = __convert_test_name_to_directory_name(request.node.name)
    return current_scope.context.get_current_directory() / directory_name


def __convert_test_name_to_directory_name(test_name: str) -> str:
    directory_name = []

    parametrized_test_match = re.match(r"([\w_]+)\[(.*)\]", test_name)
    if parametrized_test_match:
        test_name = f"{parametrized_test_match[1]}_with_parameters_{parametrized_test_match[2]}"

    for character in test_name:
        character_to_append = character
        if not (character_to_append.isalnum() or character_to_append in "-_"):
            character_to_append = f"-0x{ord(character):X}-"

        directory_name.append(character_to_append)

    return "".join(directory_name)


def __get_function_name(request: pytest.FixtureRequest) -> str:
    assert request.scope == "function"
    result = request.node.name
    assert isinstance(result, str)
    return result


def __get_pytest_package_object(request: pytest.FixtureRequest) -> pytest.Package | None:
    assert request.scope == "package"

    if isinstance(request.node, pytest.Package):
        return request.node

    pytest_scope = request.node.items[0]
    while pytest_scope is not None:
        if isinstance(pytest_scope, pytest.Package):
            return pytest_scope

        pytest_scope = pytest_scope.parent

    return None
