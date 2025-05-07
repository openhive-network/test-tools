from __future__ import annotations

import pytest
from test_tools.__private.process.node_config import NodeConfig


@pytest.fixture
def config() -> NodeConfig:
    return NodeConfig()
