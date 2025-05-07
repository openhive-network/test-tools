from __future__ import annotations

from typing import Any, Final, TypeGuard

from beekeepy.handle.runnable import Config
from beekeepy.interfaces import HttpUrl, P2PUrl, WsUrl

from test_tools.__private.process.node_commons import ConfigurationCommonHived


class NodeConfig(Config, ConfigurationCommonHived):  # type: ignore[misc]
    account_history_blacklist_ops: str | None = None
    account_history_track_account_range: str | None = None
    account_history_whitelist_ops: str | None = None
    edit_script: str | None = None
    flush_state_interval: str | None = None
    history_blacklist_ops: str | None = None
    history_whitelist_ops: str | None = None
    psql_first_block: int | None = None
    psql_index_threshold: int | None = None
    psql_operations_threads_number: int | None = None
    psql_transactions_threads_number: int | None = None
    psql_url: str | None = None
    rpc_endpoint: str | None = None
    seed_node: str | None = None
    track_account_range: str | None = None

    @classmethod
    def _convert_member_value_to_config_value(cls, member_name: str, member_value: Any) -> str | list[str]:
        if cls.is_checkpoint_type(member_value=member_value):
            return [f"[{item[0]}, {item[1]}]" for item in member_value]
        if cls._require_quotation(member_name):
            member_value = cls._apply_quotation(member_value)
        return super()._convert_member_value_to_config_value(member_name, member_value)

    @classmethod
    def default(cls, *, skip_address: bool = False) -> NodeConfig:
        return NodeConfig(
            webserver_http_endpoint=(None if skip_address else HttpUrl("0.0.0.0:0")),
            webserver_ws_endpoint=(None if skip_address else WsUrl("0.0.0.0:0")),
            p2p_endpoint=(None if skip_address else P2PUrl("0.0.0.0:0")),
        )

    @classmethod
    def is_checkpoint_type(cls, member_value: Any) -> TypeGuard[list[tuple[int, str]]]:
        checkpoint_item_length: Final[int] = 2

        return (
            isinstance(member_value, list)
            and len(member_value) > 0
            and isinstance(member_value[0], tuple)
            and len(member_value[0]) == checkpoint_item_length
        )
