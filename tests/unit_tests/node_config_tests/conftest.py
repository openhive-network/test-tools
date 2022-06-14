import pytest

from test_tools.__private.node_config import NodeConfig


@pytest.fixture()
def config():
    return NodeConfig()
