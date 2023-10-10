from __future__ import annotations

import pytest
import test_tools as tt
from test_tools.__private.exceptions import MissingPathToExecutableError

# Imported fixture is automatically used, so it's false positive.
from tests.unit_tests.key_generation_tests.local_tools import (
    ensure_that_key_generator_executable_is_missing,  # noqa: F401
)

# pylint: enable=unused-import


def test_if_account_object_can_be_created_without_key_generator() -> None:
    tt.Account("example")

    # Object is created, but public_key and private_key are not generated
    # yet, so missing key generator executable is not a problem.


def test_if_serialization_fails_due_to_missing_key_generator_executable() -> None:
    account = tt.Account("example")

    for key in ["private_key", "public_key"]:
        with pytest.raises(MissingPathToExecutableError):
            str(getattr(account, key))  # Run serialization, but it requires key generator, so should fail
