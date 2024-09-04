from __future__ import annotations

from test_tools.__private.node_config import NodeConfig


def create_default_config(*, skip_address: bool = False) -> NodeConfig:
    """
    Returns default node config.

    Returns
    -------
        NodeConfig: with default values.
    """
    return NodeConfig(
        **(
            {"p2p_endpoint": "0.0.0.0:0", "webserver_http_endpoint": "0.0.0.0:0", "webserver_ws_endpoint": "0.0.0.0:0"}
            if not skip_address
            else {}
        ),
    )
