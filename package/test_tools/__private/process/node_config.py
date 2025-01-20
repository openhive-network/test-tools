from __future__ import annotations

from typing import Any

from helpy import HttpUrl, P2PUrl, WsUrl
from helpy._interfaces.config import Config
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
    def _convert_member_value_to_config_value(cls, member_name: str, member_value: Any) -> str:
        if cls._require_quotation(member_name):
            member_value = cls._apply_quotation(member_value)
        return super()._convert_member_value_to_config_value(member_name, member_value)

    @classmethod
    def default(cls) -> NodeConfig:
        return NodeConfig(
            webserver_http_endpoint=HttpUrl("0.0.0.0:0"),
            webserver_ws_endpoint=WsUrl("0.0.0.0:0"),
            p2p_endpoint=P2PUrl("0.0.0.0:0"),
        )
