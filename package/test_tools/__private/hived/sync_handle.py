from __future__ import annotations

import math
from typing import TYPE_CHECKING, Generic

from beekeepy.handle.remote import AbstractSyncHandle, RemoteHandleSettings, RemoteSettingsT, SyncBatchHandle

from test_tools.__private.hived.api.api_collection import HivedSyncApiCollection
from test_tools.__private.hived.common_helpers import HiveHandleCommonHelpers
from wax.helpy._interfaces.time import Time
from wax.helpy.exceptions import BlockWaitTimeoutError

if TYPE_CHECKING:
    from datetime import datetime, timedelta

    from schemas.fields.basic import AccountName


class HivedTemplate(
    AbstractSyncHandle[RemoteSettingsT, HivedSyncApiCollection], HiveHandleCommonHelpers, Generic[RemoteSettingsT]
):
    def _construct_api(self) -> HivedSyncApiCollection:
        return HivedSyncApiCollection(owner=self)

    def _target_service(self) -> str:
        return self._hived_target_service_name()

    def get_dynamic_global_properties(self) -> HiveHandleCommonHelpers.GetDynamicGlobalPropertiesT:
        return self.api.database.get_dynamic_global_properties()  # type: ignore[return-value]

    def get_last_block_number(self) -> int:
        return self._get_last_block_number(self.get_dynamic_global_properties())

    def get_last_irreversible_block_number(self) -> int:
        return self._get_last_irreversible_block_number(self.get_dynamic_global_properties())

    def get_head_block_time(self) -> datetime:
        return self._get_head_block_time(self.get_dynamic_global_properties())

    def get_current_witness(self) -> AccountName:
        return self._get_current_witness(self.get_dynamic_global_properties())

    def wait_number_of_blocks(self, blocks_to_wait: int, *, timeout: float = math.inf) -> None:
        self._assert_non_negative_amount_of_blocks(blocks_to_wait)
        self.wait_for_block_with_number(self.get_last_block_number() + blocks_to_wait, timeout=timeout)

    def wait_for_block_with_number(self, block_number: int, *, timeout: float | timedelta = math.inf) -> None:
        def __is_block_with_number_reached() -> bool:
            last = self.get_last_block_number()
            return last >= block_number

        Time.sync_wait_for(
            __is_block_with_number_reached,
            timeout=timeout,
            timeout_error_message=f"Waiting too long for block {block_number}",
            poll_time=2.0,
        )

    def wait_for_irreversible_block(
        self, number: int | None = None, *, max_blocks_to_wait: int | None = None, timeout: float | timedelta = math.inf
    ) -> None:
        last_block_number = self.get_last_block_number()
        target_block_number = number or last_block_number
        max_wait_block_number = (last_block_number + max_blocks_to_wait) if max_blocks_to_wait is not None else None

        def __is_block_with_number_irreversible() -> bool:
            if max_wait_block_number is not None:
                self.__assert_block_with_number_reached_irreversibility_before_limit(
                    target_block_number, max_wait_block_number
                )

            last_irreversible_block_number = self.get_last_irreversible_block_number()
            return last_irreversible_block_number >= target_block_number

        Time.sync_wait_for(
            __is_block_with_number_irreversible,
            timeout=timeout,
            timeout_error_message=f"Waiting too long for irreversible block {target_block_number}",
            poll_time=2.0,
        )

    def __assert_block_with_number_reached_irreversibility_before_limit(
        self, block_number: int, max_wait_block_number: int
    ) -> None:
        response = self.get_dynamic_global_properties()
        last_block_number = response.head_block_number
        last_irreversible_block_number = response.last_irreversible_block_num

        def __expected_block_was_reached_but_is_still_not_irreversible() -> bool:
            return last_block_number >= max_wait_block_number and last_irreversible_block_number < block_number

        if __expected_block_was_reached_but_is_still_not_irreversible():
            raise BlockWaitTimeoutError(last_block_number, block_number, last_irreversible_block_number)

    def batch(self, *, delay_error_on_data_access: bool = False) -> SyncBatchHandle[HivedSyncApiCollection]:
        return SyncBatchHandle(
            url=self.http_endpoint,
            overseer=self._overseer,
            api=lambda o: HivedSyncApiCollection(o),
            delay_error_on_data_access=delay_error_on_data_access,
        )

    @property
    def network_type(self) -> str:
        return self._extract_network_type(self.api.database.get_version())


Hived = HivedTemplate[RemoteHandleSettings]
