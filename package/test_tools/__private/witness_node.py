from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

from test_tools.__private.account import Account
from test_tools.__private.preconfigured_node import PreconfiguredNode

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.network_handle import NetworkHandle as Network
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class WitnessNode(PreconfiguredNode):
    def __init__(
        self,
        *,
        name: str = "WitnessNode",
        witnesses: list[str] | None = None,
        network: Network | None = None,
        handle: NodeHandle | None = None,
    ):
        super().__init__(name=name, network=network, handle=handle)
        assert "witness" in self.config.plugin

        if witnesses is None:
            warnings.warn(
                f"You are creating witness node without setting witnesses. Probably you forget to define them like:\n"
                f"\n"
                f"  {self.__class__.__name__}(witnesses=['witness0', 'witness1'])\n"
                f"\n"
                f"If you really want to create witness node without witnesses, then create node with explicit empty\n"
                f"list as argument, like this:\n"
                f"\n"
                f"  {self.__class__.__name__}(witnesses=[])",
                stacklevel=1,
            )
            witnesses = []

        for witness in witnesses:
            self.__register_witness(witness)

    def __register_witness(self, witness_name: str) -> None:
        witness = Account(witness_name)
        self.config.witness.append(witness.name)
        self.config.private_key.append(witness.private_key)
