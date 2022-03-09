from test_tools.private.witness_node import WitnessNode


class InitNode(WitnessNode):
    """Node which is ready to produce blocks"""

    def __init__(self, *, name: str = 'InitNode'):
        super().__init__(name=name, witnesses=['initminer'])

        self.config.enable_stale_production = True
        self.config.required_participation = 0
