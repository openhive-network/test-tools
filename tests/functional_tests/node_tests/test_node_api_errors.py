import pytest

import test_tools as tt


@pytest.fixture
def node():
    init_node = tt.InitNode()
    init_node.run()

    return init_node


def test_if_raise_when_parameters_are_bad(node):
    with pytest.raises(tt.exceptions.CommunicationError):
        node.api.database.list_accounts(limit="wrong-type", order="wrong-value")

def test_if_not_raise_when_parameters_are_bad_but_flag_is_provided(node):
    result = node.api.database.list_accounts(
        limit="wrong-type",
        order="wrong-value",
        options=tt.RequestOptions(allow_error=True)
    )
    assert "error" in result
