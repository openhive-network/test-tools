import pytest

import test_tools as tt


def test_if_raise_when_parameters_are_bad(node: tt.InitNode):
    with pytest.raises(tt.exceptions.CommunicationError):
        node.api.database.list_accounts(limit="wrong-type", order="wrong-value")
