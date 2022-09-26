import pytest

import test_tools as tt


@pytest.mark.requires_hived_executables
@pytest.mark.parametrize("Key", [tt.PrivateKey, tt.PublicKey])
def test_if_same_accounts_have_same_keys(Key):  # pylint: disable=invalid-name
    assert Key("alice") == Key("alice")


@pytest.mark.requires_hived_executables
@pytest.mark.parametrize("Key", [tt.PrivateKey, tt.PublicKey])
def test_if_different_accounts_have_different_keys(Key):  # pylint: disable=invalid-name
    assert Key("alice") != Key("bob")


@pytest.mark.requires_hived_executables
@pytest.mark.parametrize("Key", [tt.PrivateKey, tt.PublicKey])
def test_check_of_key_presence_in_set_of_keys(Key):  # pylint: disable=invalid-name
    assert Key("bob") in {Key(name) for name in ["alice", "bob", "carol"]}


@pytest.mark.requires_hived_executables
@pytest.mark.parametrize("Key", [tt.PrivateKey, tt.PublicKey])
def test_check_of_key_presence_in_set_of_strings(Key):  # pylint: disable=invalid-name
    assert Key("bob") in {str(Key(name)) for name in ["alice", "bob", "carol"]}
