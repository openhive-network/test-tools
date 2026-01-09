from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from database_api.database_api_description import GetDynamicGlobalPropertiesResponse as GetDynamicGlobalProperties

if TYPE_CHECKING:
    from typing import TypeAlias

    from database_api.database_api_description import GetVersionResponse as GetVersion

    from schemas.fields.basic import AccountName


class HiveHandleCommonHelpers:
    GetDynamicGlobalPropertiesT: TypeAlias = GetDynamicGlobalProperties

    def _get_last_block_number(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> int:
        return dynamic_global_properties.head_block_number

    def _get_last_irreversible_block_number(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> int:
        return dynamic_global_properties.last_irreversible_block_num

    def _get_head_block_time(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> datetime:
        time_value = dynamic_global_properties.time
        if isinstance(time_value, str):
            return datetime.fromisoformat(time_value.replace("Z", "+00:00"))
        return time_value

    def _get_current_witness(self, dynamic_global_properties: GetDynamicGlobalPropertiesT) -> AccountName:
        return dynamic_global_properties.current_witness

    def _hived_target_service_name(self) -> str:
        return "hived"

    def _extract_network_type(self, get_version: GetVersion) -> str:
        return get_version.node_type

    def _assert_non_negative_amount_of_blocks(self, amount_of_blocks: int) -> None:
        assert amount_of_blocks > 0, "Can't wait for negative or zero amount of blocks"
