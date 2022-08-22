import pytest

import test_tools as tt


@pytest.fixture(autouse=True)
def ensure_that_key_generator_executable_is_missing():
    try:
        previous_path = tt.paths_to_executables.get_path_of('get_dev_key')
    except tt.exceptions.MissingPathToExecutable:
        previous_path = None

    tt.paths_to_executables.set_path_of('get_dev_key', None)

    yield

    tt.paths_to_executables.set_path_of('get_dev_key', previous_path)
