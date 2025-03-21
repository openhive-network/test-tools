from __future__ import annotations

import pytest
import test_tools as tt

from schemas.fields.basic import PrivateKey, PublicKey


@pytest.mark.requires_hived_executables
def test_if_same_accounts_have_same_keys() -> None:
    assert tt.Account("alice") == tt.Account("alice")


@pytest.mark.requires_hived_executables
def test_if_different_accounts_have_different_keys() -> None:
    assert tt.Account("alice") != tt.Account("bob")


@pytest.mark.requires_hived_executables
@pytest.mark.parametrize("key", [PrivateKey, PublicKey])
def test_check_of_key_presence_in_set_of_keys(key: type[PrivateKey | PublicKey]) -> None:
    assert key("bob") in {key(name) for name in ["alice", "bob", "carol"]}


@pytest.mark.requires_hived_executables
@pytest.mark.parametrize("key", [PrivateKey, PublicKey])
def test_check_of_key_presence_in_set_of_strings(key: type[PrivateKey | PublicKey]) -> None:
    assert key("bob") in {str(key(name)) for name in ["alice", "bob", "carol"]}
