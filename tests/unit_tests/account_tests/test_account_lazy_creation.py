import pytest

import test_tools as tt

# pylint: disable=unused-import
# Imported fixture is automatically used, so it's false positive.
from ..key_generation_tests.local_tools import ensure_that_key_generator_executable_is_missing

# pylint: enable=unused-import


def test_if_account_object_can_be_created_without_key_generator():
    tt.Account("example")

    # Object is created, but public_key and private_key are not generated
    # yet, so missing key generator executable is not a problem.


def test_if_keys_can_be_accessed_without_generator():
    account = tt.Account("example")
    _ = account.keys.public, account.keys.private

    # Generation of public_key and private_key is postponed even more, until
    # value will be really required (e.g. to compare with something, to send
    # public key to node, and so on...), so missing key generator executable
    # is not a problem.


def test_if_serialization_fails_due_to_missing_key_generator_executable():  # pylint: disable=invalid-name
    account = tt.Account("example")

    for key in ["private", "public"]:
        with pytest.raises(FileNotFoundError):
            str(getattr(account.keys, key))  # Run serialization, but it requires key generator, so should fail
