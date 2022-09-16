import pytest

from test_tools.__private.node_config_entry_types import String


@pytest.fixture
def entry():
    return String()


@pytest.fixture
def values():
    return [
        '"example"',
        "5JcCHFFWPW2DryUFDVd7ZXVj2Zo67rqMcvcq5inygZGBAPR1JoR",
        "0.0.0.0:51003",
        "56G",
    ]


def test_parsing(entry, values):
    # pylint: disable=duplicate-code
    for value in values:
        entry.parse_from_text(value)
        assert entry.get_value() == value
    # pylint: enable=duplicate-code


def test_serializing(entry, values):
    for value in values:
        entry.set_value(value)
        assert entry.serialize_to_text() == value
