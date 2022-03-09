from test_tools.private.raw_node import RawNode


class PreconfiguredNode(RawNode):
    """Only for internal use, user must never see it."""

    def __init__(self, name: str):
        super().__init__(name=name)

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
