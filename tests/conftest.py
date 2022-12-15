import logging

import pytest

import test_tools as tt
from test_tools.__private.scope.scope_fixtures import *  # pylint: disable=wildcard-import, unused-wildcard-import


def pytest_sessionstart() -> None:
    # Turn off unnecessary logs
    logging.getLogger("urllib3.connectionpool").propagate = False


@pytest.fixture(name="node")
def _node():
    node = tt.InitNode()
    node.run()
    return node
