import pytest

import test_tools as tt

# pylint: disable=unused-import
# Imported fixture is automatically used, so it's false positive.
from ..key_generation_tests.local_tools import ensure_that_key_generator_executable_is_missing

# pylint: enable=unused-import


@pytest.mark.parametrize("Key", [tt.PrivateKey, tt.PublicKey])
def test_if_key_object_can_be_created_without_key_generator(Key):  # pylint: disable=invalid-name
    Key("example")

    # Object is created, but key is not generated yet, so missing
    # key generator executable is not a problem.


@pytest.mark.parametrize("Key", [tt.PrivateKey, tt.PublicKey])
def test_if_serialization_fails_due_to_missing_key_generator_executable(Key):  # pylint: disable=invalid-name
    with pytest.raises(FileNotFoundError):
        str(Key("example"))  # Run serialization, but it requires key generator, so should fail
