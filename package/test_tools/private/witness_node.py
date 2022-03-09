from typing import List, Optional
import warnings

from test_tools.account import Account
from test_tools.private.preconfigured_node import PreconfiguredNode


class WitnessNode(PreconfiguredNode):
    def __init__(self, *, name: str = 'WitnessNode', witnesses: Optional[List[str]] = None):
        super().__init__(name=name)

        assert 'witness' in self.config.plugin

        if witnesses is None:
            warnings.warn(
                f'You are creating witness node without setting witnesses. Probably you forget to define them like:\n'
                f'\n'
                f'  {self.__class__.__name__}(witnesses=[\'witness0\', \'witness1\'])\n'
                f'\n'
                f'If you really want to create witness node without witnesses, then create node with explicit empty\n'
                f'list as argument, like this:\n'
                f'\n'
                f'  {self.__class__.__name__}(witnesses=[])'
            )
            witnesses = []

        for witness in witnesses:
            self.__register_witness(witness)

    def __register_witness(self, witness_name):
        witness = Account(witness_name)
        self.config.witness.append(witness.name)
        self.config.private_key.append(witness.private_key)
