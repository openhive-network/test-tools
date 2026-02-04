from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

import pytest
from beekeepy.exceptions import CommunicationError, NothingToSendError, ResponseNotReadyError
from beekeepy.interfaces import SuppressApiNotFound
from msgspec import ValidationError  # TODO: new msgspec refactor should encapsulate schemas !!!

if TYPE_CHECKING:
    from test_tools.__private.hived.sync_handle import Hived


@pytest.mark.skip  # TODO: any change in config.hpp guarantees that test will fail - it should not be here but in hived and it should use local node, not api.hive.blog
def test_batch_node(sync_node: Hived) -> None:
    try:
        with sync_node.batch() as node:
            dynamic_properties = node.api.database.get_dynamic_global_properties()
            config = node.api.database.get_config()

        assert len(dynamic_properties.dict()) != 0, "Dynamic global properties should not be empty"
        assert len(config.dict()) != 0, "Config should not be empty"

    except ValidationError as ex:
        repr(ex).index("Object missing required field `HIVE_CUSTOM_OP_BLOCK_LIMIT")


def test_batch_node_response_not_ready(sync_node: Hived) -> None:
    with sync_node.batch() as node:
        dynamic_properties = node.api.database.get_dynamic_global_properties()

        with pytest.raises(ResponseNotReadyError):
            _ = dynamic_properties.head_block_id


def test_batch_node_error_response(sync_node: Hived) -> None:
    with pytest.raises(CommunicationError, match="Invalid cast"):  # noqa: SIM117
        with sync_node.batch() as node:
            node.api.database.find_accounts(accounts=123)


def test_batch_node_error_response_delayed(sync_node: Hived) -> None:
    with sync_node.batch(delay_error_on_data_access=True) as node:
        response = node.api.database.find_accounts(accounts=123)

    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = response.accounts[0].name


@pytest.mark.parametrize("order", ["first_good", "first_bad"])
def test_batch_node_mixed_request_delayed(sync_node: Hived, order: Literal["first_good", "first_bad"]) -> None:
    with sync_node.batch(delay_error_on_data_access=True) as node:
        if order == "first_good":
            good_response = node.api.database.get_dynamic_global_properties()
            bad_response = node.api.database.find_accounts(accounts=123)
        else:
            bad_response = node.api.database.find_accounts(accounts=123)
            good_response = node.api.database.get_dynamic_global_properties()

    assert good_response.head_block_number > 0
    with pytest.raises(CommunicationError, match="Invalid cast"):
        _ = bad_response.accounts[0].name


def test_batch_node_nothing_to_send(sync_node: Hived) -> None:
    with pytest.raises(NothingToSendError):  # noqa: SIM117
        with sync_node.batch():
            pass


def test_batch_node_with_suppress_api_not_found(sync_node: Hived) -> None:
    # ARRANGE
    missing_api: Final[str] = "debug_node_api"
    amount_of_requests: Final[int] = 3

    with SuppressApiNotFound(missing_api) as suppress, sync_node.batch() as bnode:
        for _ in range(amount_of_requests):
            bnode.api.debug_node.debug_get_head_block()

    # ASSERT
    assert len(suppress.errors) == amount_of_requests, "there should be exactly 2 suppressed errors"
    assert all(item.api == missing_api for item in suppress.errors), f"suppressed for: {suppress.errors}"
