from __future__ import annotations

import datetime
import math
from typing import NoReturn, Optional, TYPE_CHECKING

from test_tools.__private import exceptions
from test_tools.__private.logger.logger_internal_interface import logger
from test_tools.__private.scope import context
from test_tools.__private.time.time import Time
from test_tools.__private.user_handles.implementation import Implementation as UserHandleImplementation
from test_tools.node_api.node_apis import Apis

if TYPE_CHECKING:
    from test_tools.__private.user_handles.handles.node_handles.node_handle_base import NodeHandleBase as NodeHandle


class BaseNode(UserHandleImplementation):
    def __init__(self, *, name, handle: Optional[NodeHandle] = None):
        super().__init__(handle=handle)

        self.api = Apis(self)
        self.__name = context.names.register_numbered_name(name)
        self._logger = logger.create_child_logger(self.get_name())

    def __str__(self):
        return self.__name

    def __repr__(self) -> str:
        return str(self)

    def get_name(self):
        return self.__name

    def get_last_block_number(self):
        response = self.api.database.get_dynamic_global_properties()
        return response["head_block_number"]

    def get_last_irreversible_block_number(self) -> int:
        response = self.api.database.get_dynamic_global_properties()
        return response["last_irreversible_block_num"]

    def get_head_block_time(self) -> datetime.datetime:
        response = self.api.database.get_dynamic_global_properties()
        return Time.parse(response["time"])

    def get_current_witness(self) -> str:
        response = self.api.database.get_dynamic_global_properties()
        return response["current_witness"]

    def wait_number_of_blocks(self, blocks_to_wait, *, timeout=math.inf):
        assert blocks_to_wait > 0
        self.wait_for_block_with_number(self.get_last_block_number() + blocks_to_wait, timeout=timeout)

    def wait_for_block_with_number(self, number, *, timeout=math.inf):
        Time.wait_for(
            lambda: self.__is_block_with_number_reached(number),
            timeout=timeout,
            timeout_error_message=f"Waiting too long for block {number}",
            poll_time=2.0,
        )

    def wait_for_irreversible_block(
        self, number: Optional[int] = None, *, max_blocks_to_wait: Optional[int] = None, timeout=math.inf
    ) -> None:
        def __is_number_param_given() -> bool:
            return number is not None

        def __is_max_blocks_to_wait_param_given() -> bool:
            return max_blocks_to_wait is not None

        last_block_number = self.get_last_block_number()
        target_block_number = number if __is_number_param_given() else last_block_number
        max_wait_block_number = (
            last_block_number + max_blocks_to_wait if __is_max_blocks_to_wait_param_given() else None
        )

        log_message = f"Waiting for block with number `{target_block_number}` to become irreversible..."

        if __is_max_blocks_to_wait_param_given():
            log_message += f" (max wait block number: `{max_wait_block_number}`)"

        self._logger.info(log_message)

        Time.wait_for(
            lambda: self.__is_block_with_number_irreversible(target_block_number, max_wait_block_number),
            timeout=timeout,
            timeout_error_message=f"Waiting too long for irreversible block {target_block_number}",
            poll_time=2.0,
        )

    def __is_block_with_number_reached(self, number):
        last = self.get_last_block_number()
        return last >= number

    def __is_block_with_number_irreversible(self, number: int, max_wait_block_number: Optional[int]) -> bool:
        if max_wait_block_number is not None:
            self.__assert_block_with_number_reached_irreversibility_before_limit(number, max_wait_block_number)

        last_irreversible_block_number = self.get_last_irreversible_block_number()
        return last_irreversible_block_number >= number

    def __assert_block_with_number_reached_irreversibility_before_limit(
        self, number: int, max_wait_block_number: int
    ) -> Optional[NoReturn]:
        def __expected_block_was_reached_but_is_still_not_irreversible() -> bool:
            return last_block_number >= max_wait_block_number and last_irreversible_block_number < number

        response = self.api.database.get_dynamic_global_properties()  # to avoid 2 calls to the node
        last_block_number = response["head_block_number"]
        last_irreversible_block_number = response["last_irreversible_block_num"]

        if __expected_block_was_reached_but_is_still_not_irreversible():
            raise exceptions.BlockWaitTimeoutError(
                f"Block with number `{last_block_number}` was just reached but expected `{number}` is still not"
                f" irreversible.\n"
                f"Last irreversible block number is `{last_irreversible_block_number}`."
            )
