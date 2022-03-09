from test_tools.private.preconfigured_node import PreconfiguredNode


class ApiNode(PreconfiguredNode):
    def __init__(self, *, name: str = 'ApiNode'):
        super().__init__(name=name)

        self.config.plugin.remove('witness')
