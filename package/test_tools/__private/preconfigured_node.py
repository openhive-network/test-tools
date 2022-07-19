from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from test_tools.__private.raw_node import RawNode

if TYPE_CHECKING:
    from test_tools.__private.network import Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class PreconfiguredNode(RawNode):
    """Only for internal use, user must never see it."""

    def __init__(self, name: str, network: Optional[Network] = None, handle: Optional[NodeHandle] = None):
        super().__init__(name=name, network=network, handle=handle)

        self.__enable_all_api_plugins()
        self.config.log_logger = '{"name":"default","level":"info","appender":"stderr"} ' \
                                 '{"name":"user","level":"debug","appender":"stderr"} ' \
                                 '{"name":"chainlock","level":"debug","appender":"p2p"} ' \
                                 '{"name":"sync","level":"debug","appender":"p2p"} ' \
                                 '{"name":"p2p","level":"debug","appender":"p2p"}'
        self.config.shared_file_size = '128M'

    def __enable_all_api_plugins(self) -> None:
        self.config.plugin.append('account_history_rocksdb')  # Required by account_history_api

        all_api_plugins = [plugin for plugin in self.get_supported_plugins() if plugin.endswith('_api')]
        self.config.plugin.extend([plugin for plugin in all_api_plugins if plugin not in self.config.plugin])
