from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import test_tools as tt

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def ensure_that_key_generator_executable_is_missing() -> Iterator[None]:
    try:
        previous_path = tt.paths_to_executables.get_path_of("get_dev_key")
    except tt.exceptions.MissingPathToExecutableError:
        previous_path = None

    tt.paths_to_executables.debug_set_path_of("get_dev_key", None)

    yield

    tt.paths_to_executables.debug_set_path_of("get_dev_key", previous_path)
