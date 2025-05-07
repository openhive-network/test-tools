from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.raw_node import RawNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class PreconfiguredNode(RawNode):
    """Only for internal use, user must never see it."""

    def __init__(self, name: str, network: Network | None = None, handle: NodeHandle | None = None) -> None:
        super().__init__(name=name, network=network, handle=handle)

        self._enable_api_plugins(
            plugins=[
                "app_status_api",
                "witness",
                "account_by_key",
                "account_by_key_api",
                "state_snapshot",
                "rc_api",
                "block_api",
                "database_api",
                "debug_node_api",
                "network_node_api",
                "wallet_bridge_api",
            ]
        )
        self.config.log_logger = (
            '{"name":"default","level":"debug","appender":"stderr"} '
            '{"name":"user","level":"debug","appender":"stderr"} '
            '{"name":"chainlock","level":"debug","appender":"p2p"} '
            '{"name":"sync","level":"debug","appender":"p2p"} '
            '{"name":"p2p","level":"debug","appender":"p2p"}'
        )
        self.config.shared_file_size = "128M"

    def _enable_api_plugins(self, *, plugins: list[str]) -> None:
        self.config.plugin.extend([plugin for plugin in plugins if plugin not in self.config.plugin])
