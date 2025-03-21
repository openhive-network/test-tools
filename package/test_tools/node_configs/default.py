from __future__ import annotations

import json

from test_tools.__private.node_config import NodeConfig


def create_default_config(*, skip_address: bool = False) -> NodeConfig:
    """
    Returns default node config.

    Returns
    -------
        NodeConfig: with default values.

    """
    hived_logger_settings = [
        {"name": "default", "level": "debug", "appenders": ["stderr"]},
        {"name": "user", "level": "debug", "appenders": ["stderr"]},
        {"name": "p2p", "level": "info", "appenders": ["p2p"]},
    ]

    return NodeConfig(
        **(
            {
                "p2p_endpoint": "0.0.0.0:0",
                "webserver_http_endpoint": "0.0.0.0:0",
                "webserver_ws_endpoint": "0.0.0.0:0",
            }
            if not skip_address
            else {}
        ),
        log_logger=" ".join(json.dumps(item) for item in hived_logger_settings),
    )
