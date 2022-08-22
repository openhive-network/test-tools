import pytest

import test_tools as tt
from test_tools.__private.node_config_entry_types import PrivateKey as PrivateKeyEntry


@pytest.fixture
def entry():
    return PrivateKeyEntry()


@pytest.fixture
def values():
    return [
        '5JcCHFFWPW2DryUFDVd7ZXVj2Zo67rqMcvcq5inygZGBAPR1JoR',
    ]


def test_parsing(entry, values):
    for value in values:
        entry.parse_from_text(value)
        assert entry.get_value() == value


def test_serializing_from_string(entry, values):
    for value in values:
        entry.set_value(value)
        assert entry.serialize_to_text() == value


@pytest.mark.requires_hived_executables
def test_serializing_from_private_key_object(entry):
    private_key = tt.PrivateKey('example')
    entry.set_value(private_key)
    assert entry.serialize_to_text() == str(private_key)


def test_different_type_assignments(entry):
    for incorrect_value in [True, 123, 2.718]:
        with pytest.raises(ValueError):
            entry.set_value(incorrect_value)
