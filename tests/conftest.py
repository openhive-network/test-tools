from __future__ import annotations

import contextlib
import logging

import pytest
import test_tools as tt
from loguru import logger
from test_tools.__private.scope.scope_fixtures import *  # noqa: F403

from schemas.policies.policy import set_policies
from schemas.policies.testnet_assets import TestnetAssetsPolicy


def _patch_database_api_for_dict_access() -> None:
    """Add dict-style access (__getitem__) to database_api Struct classes for backwards compatibility."""
    with contextlib.suppress(Exception):
        import msgspec
        from database_api import database_api_description

        def _getitem(self: msgspec.Struct, key: str) -> object:
            return getattr(self, key)

        for name in dir(database_api_description):
            obj = getattr(database_api_description, name)
            is_struct_subclass = isinstance(obj, type) and issubclass(obj, msgspec.Struct) and obj is not msgspec.Struct
            needs_getitem = not hasattr(obj, "__getitem__") or obj.__getitem__ is None
            if is_struct_subclass and needs_getitem:
                obj.__getitem__ = _getitem


_patch_database_api_for_dict_access()


@pytest.fixture(autouse=True)
def _disable_logging() -> None:
    logger.disable("helpy")


def pytest_sessionstart() -> None:
    # Turn off unnecessary logs
    logging.getLogger("urllib3.connectionpool").propagate = False
    tt.logger.enable("test_tools")


@pytest.fixture(autouse=True)
def _use_testnet_assets() -> None:
    set_policies(TestnetAssetsPolicy(use_testnet_assets=True))


@pytest.fixture(name="node")
def _node() -> tt.InitNode:  # noqa: PT005
    node = tt.InitNode()
    node.run()
    return node
