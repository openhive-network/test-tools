import pytest

from test_tools.private.node_config import NodeConfig


@pytest.fixture
def config():
    return NodeConfig()
