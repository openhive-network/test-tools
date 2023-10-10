from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from helpy._handles.abc.handle import RequestError

if TYPE_CHECKING:
    import test_tools as tt


def test_if_raise_when_parameters_are_bad(node: tt.InitNode) -> None:
    with pytest.raises(RequestError):
        node.api.database.list_accounts(name=[])  # type: ignore[call-arg]
