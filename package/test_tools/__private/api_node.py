from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from test_tools.__private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class ApiNode(PreconfiguredNode):
    def __init__(
        self, *, name: str = "ApiNode", network: Optional[Network] = None, handle: Optional[NodeHandle] = None
    ):
        super().__init__(name=name, network=network, handle=handle)
        api_plugins = [
            plugin
            for plugin in self.get_supported_plugins()
            if plugin.endswith("_api") and plugin != "account_history_api"
        ]
        self._enable_api_plugins(plugins=api_plugins)
        self.config.plugin.remove("witness")
