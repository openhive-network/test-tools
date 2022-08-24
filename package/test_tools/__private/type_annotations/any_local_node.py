from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from test_tools.__private.api_node import ApiNode
    from test_tools.__private.init_node import InitNode
    from test_tools.__private.raw_node import RawNode
    from test_tools.__private.witness_node import WitnessNode

    AnyLocalNode = Union[ApiNode, InitNode, RawNode, WitnessNode]
