from __future__ import annotations

import pytest
import test_tools as tt
from test_tools.__private.names import Names


@pytest.fixture()
def names() -> Names:
    return Names()


def test_unique_name_registration(names: Names) -> None:
    names.register_unique_name("InitNode")
    assert names.get_names_in_use() == {"InitNode"}


def test_unique_name_double_registration(names: Names) -> None:
    names.register_unique_name("InitNode")
    with pytest.raises(tt.exceptions.NameAlreadyInUseError):
        names.register_unique_name("InitNode")


def test_single_numbered_name_registration(names: Names) -> None:
    name = names.register_numbered_name("ApiNode")

    assert name == "ApiNode0"
    assert names.get_names_in_use() == {"ApiNode0"}


def test_multiple_numbered_names_registration(names: Names) -> None:
    for name in ["ApiNode", "ApiNode", "ApiNode", "WitnessNode", "WitnessNode"]:
        names.register_numbered_name(name)

    assert names.get_names_in_use() == {"ApiNode0", "ApiNode1", "ApiNode2", "WitnessNode0", "WitnessNode1"}
