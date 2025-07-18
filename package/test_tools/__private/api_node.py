from __future__ import annotations

from typing import TYPE_CHECKING

from test_tools.__private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class ApiNode(PreconfiguredNode):
    def __init__(
        self, *, name: str = "ApiNode", network: Network | None = None, handle: NodeHandle | None = None
    ) -> None:
        super().__init__(name=name, network=network, handle=handle)
        excluded: set = {"account_history_api", "rewards_api"}
        api_plugins = [
            plugin for plugin in self.get_supported_plugins() if plugin.endswith("_api") and plugin not in excluded
        ]
        self._enable_api_plugins(plugins=api_plugins)
        self.config.plugin.remove("witness")
