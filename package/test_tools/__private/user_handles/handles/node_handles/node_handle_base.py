from __future__ import annotations

import datetime
import math
import typing
from typing import TYPE_CHECKING

from test_tools.__private.base_node import BaseNode
from test_tools.__private.node import Node
from test_tools.__private.user_handles.get_implementation import get_implementation
from test_tools.__private.user_handles.handle import Handle

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Dict, List, Literal, Optional, Tuple, Union

    from test_tools.__private.block_log import BlockLog
    from test_tools.__private.cleanup_policy import CleanupPolicy
    from test_tools.__private.node_config import NodeConfig
    from test_tools.__private.snapshot import Snapshot
    from test_tools.node_api.node_apis import Apis


class NodeHandleBase(Handle):
    # pylint: disable=too-many-public-methods
    DEFAULT_WAIT_FOR_LIVE_TIMEOUT = Node.DEFAULT_WAIT_FOR_LIVE_TIMEOUT

    @property
    def __implementation(self) -> BaseNode:
        return typing.cast(BaseNode, get_implementation(self))

    @property
    def api(self) -> Apis:
        """
        Returns grouped all node's APIs.

        Should be used in following way:
          node.api.<API>.<METHOD>()
        e.g.:
          node.api.database.get_version()
        """
        return self.__implementation.api

    def get_last_block_number(self) -> int:
        """Returns number of the newest block known to node."""
        return self.__implementation.get_last_block_number()

    def get_last_irreversible_block_number(self) -> int:
        """Returns number of the last irreversible block known to node."""
        return self.__implementation.get_last_irreversible_block_number()

    def get_head_block_time(self) -> datetime.datetime:
        """Returns head block time."""
        return self.__implementation.get_head_block_time()

    def get_current_witness(self) -> str:
        """Returns current witness."""
        return self.__implementation.get_current_witness()

    def is_running(self) -> bool:
        """Returns True if node's process is running, False if process is closed."""
        return self.__implementation.is_running()

    def wait_number_of_blocks(self, blocks_to_wait: int, *, timeout: float = math.inf) -> None:
        """
        Blocks program execution until number of new blocks specified by `blocks_to_wait` will be produced. For example
        if node's newest block is 10th and `blocks_to_wait` is set to 3, program execution will be resumed when node's
        newest block will be 13th. Maximum wait time can be limited with `timeout` parameter.

        :param blocks_to_wait: Number of blocks produced, after which execution will be resumed.
        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.

        See also similar method: `wait_for_block_with_number`.
        """
        return self.__implementation.wait_number_of_blocks(blocks_to_wait, timeout=timeout)

    def wait_for_block_with_number(self, number: int, *, timeout: float = math.inf) -> None:
        """
        Blocks program execution until block with specified `number` is produced. If specified block number is already
        produced, program execution is immediately resumed. Maximum wait time can be limited with `timeout` parameter.

        :param number: Block's number produced, after which execution will be resumed.
        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.

        See also similar method: `wait_number_of_blocks`.
        """
        return self.__implementation.wait_for_block_with_number(number, timeout=timeout)

    def wait_for_irreversible_block(
        self, number: Optional[int] = None, *, max_blocks_to_wait: Optional[int] = None, timeout: float = math.inf
    ) -> None:
        """
        Blocks program execution until current head block or block with specified `number` is considered as irreversible

        If the irreversible block is not reached within the specified maximum number of blocks, or if the timeout is
        reached, an exception is raised.

        :param number: The number of the irreversible block to wait for. If not specified, the function will wait for
            the current head block to become irreversible.
        :param max_blocks_to_wait: The maximum number of blocks to wait for the irreversible block to be reached. If
            specified, an exception is raised if the block is not irreversible after this number of blocks.
        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.
        """
        return self.__implementation.wait_for_irreversible_block(
            number, max_blocks_to_wait=max_blocks_to_wait, timeout=timeout
        )

    def wait_for_live_mode(self, timeout: float = math.inf) -> None:
        """
        Blocks program execution until node is in live mode. It's detected by waiting for `hive_status` notification

        :param timeout: Time limit for wait. When timeout is reached, `TimeoutError` exception is thrown. Expressed in
            seconds.
        """
        self.__implementation.wait_for_live_mode(timeout=timeout)

    def get_version(self) -> dict:
        """Returns output from hived for --version flag"""
        return self.__implementation.get_version()

    @property
    def http_endpoint(self) -> str:
        """
        Returns opened HTTP endpoint. Blocks program execution if HTTP endpoint is not ready. When endpoint is
        configured with special values like 0.0.0.0 address or 0 port, special values are replaced with actually
        selected by node.
        """
        return self.__implementation.get_http_endpoint()

    @property
    def ws_endpoint(self) -> str:
        """
        Returns opened WS endpoint. Blocks program execution if WS endpoint is not ready. When endpoint is configured
        with special values like 0.0.0.0 address or 0 port, special values are replaced with actually selected by node.
        """
        return self.__implementation.get_ws_endpoint()

    @property
    def p2p_endpoint(self) -> str:
        """
        Returns opened P2P endpoint. Blocks program execution if WS endpoint is not ready. When endpoint is configured
        with special values like 0.0.0.0 address or 0 port, special values are replaced with actually selected by node.
        """
        return self.__implementation.get_p2p_endpoint()
