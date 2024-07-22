from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from pydantic import BaseModel, ConstrainedStr, Field, validator

if TYPE_CHECKING:
    from typing_extensions import Self


class StringQuotedMarker(ConstrainedStr):
    """Following string will be serialized with quotes and will be deserialized without them."""


StringQuoted = StringQuotedMarker | str
T = TypeVar("T")


class UniqueList(list[T]):
    def __init__(self, _obj: Iterable[T] | T = []) -> None:  # noqa: B006
        super().__init__(set(_obj) if isinstance(_obj, Iterable) else [_obj])

    def append(self, __object: T) -> None:
        if __object not in self:
            super().append(__object)

    def extend(self, __iterable: Iterable[T]) -> None:
        for item in __iterable:
            self.append(item)

    def __iadd__(self, _: Any) -> Self:  # type: ignore[override]
        raise NotImplementedError

    def __add__(self, _: Any) -> Self:  # type: ignore[override]
        raise NotImplementedError


class NodeConfig(BaseModel, validate_assignment=True):
    log_appender: str | None = None
    log_console_appender: str | None = None
    log_file_appender: str | None = None
    log_logger: str | None = None
    backtrace: str | None = None
    plugin: UniqueList[str] = Field(default_factory=UniqueList)
    account_history_track_account_range: str | None = None
    track_account_range: str | None = None
    account_history_whitelist_ops: str | None = None
    history_whitelist_ops: str | None = None
    account_history_blacklist_ops: str | None = None
    history_blacklist_ops: str | None = None
    account_history_rocksdb_path: StringQuoted | None = None
    account_history_rocksdb_track_account_range: str | None = None
    account_history_rocksdb_whitelist_ops: str | None = None
    account_history_rocksdb_blacklist_ops: str | None = None
    block_data_export_file: str | None = None
    block_data_skip_empty: bool | None = None
    block_log_info_print_interval_seconds: str | None = None
    block_log_info_print_irreversible: str | None = None
    block_log_info_print_file: str | None = None
    shared_file_dir: StringQuoted | None = None
    shared_file_size: str | None = None
    shared_file_full_threshold: str | None = None
    shared_file_scale_rate: str | None = None
    checkpoint: str | None = None
    flush_state_interval: str | None = None
    cashout_logging_starting_block: str | None = None
    cashout_logging_ending_block: str | None = None
    cashout_logging_log_path_dir: str | None = None
    debug_node_edit_script: str | None = None
    edit_script: str | None = None
    log_json_rpc: str | None = None
    market_history_bucket_size: str | None = None
    market_history_buckets_per_size: str | None = None
    notifications_endpoint: str | None = None
    p2p_endpoint: str | None = None
    p2p_max_connections: str | None = None
    seed_node: str | None = None
    p2p_seed_node: list[str] = Field(default_factory=list)
    p2p_parameters: str | None = None
    rc_stats_report_type: str | None = None
    rc_stats_report_output: str | None = None
    block_log_split: int | None = None
    snapshot_root_dir: StringQuoted | None = None
    statsd_endpoint: str | None = None
    statsd_batchsize: str | None = None
    statsd_whitelist: str | None = None
    statsd_blacklist: str | None = None
    tags_start_promoted: str | None = None
    tags_skip_startup_update: str | None = None
    transaction_status_block_depth: str | None = None
    webserver_http_endpoint: str | None = None
    webserver_unix_endpoint: str | None = None
    webserver_ws_endpoint: str | None = None
    webserver_ws_deflate: bool | None = None
    rpc_endpoint: str | None = None
    webserver_thread_pool_size: str | None = None
    enable_stale_production: bool | None = None
    required_participation: int | None = None
    witness: list[StringQuoted] = Field(default_factory=list)
    private_key: list[str] = Field(default_factory=list)
    psql_url: str | None = None
    psql_index_threshold: int | None = None
    psql_operations_threads_number: int | None = None
    psql_transactions_threads_number: int | None = None
    psql_first_block: int | None = None
    enable_block_log_compression: bool | None = None
    enable_block_log_auto_fixing: bool | None = None
    block_log_compression_level: int | None = None
    blockchain_thread_pool_size: int | None = None
    block_stats_report_type: str | None = None
    block_stats_report_output: str | None = None
    webserver_https_certificate_file_name: str | None = None
    webserver_https_key_file_name: str | None = None
    colony_sign_with: list[str] | None = None
    colony_threads: int | None = None
    colony_transactions_per_block: int | None = None
    colony_start_at_block: int | None = None
    colony_no_broadcast: bool | None = None
    colony_article: str | None = None
    colony_reply: str | None = None
    colony_vote: str | None = None
    colony_transfer: str | None = None
    colony_custom: str | None = None
    pacemaker_source: str | None = None
    pacemaker_min_offset: int | None = None
    pacemaker_max_offset: int | None = None

    @validator("witness", "private_key", "p2p_seed_node", pre=True, always=True)
    @classmethod
    def _transform_lists(cls, value: Any) -> list[Any]:
        if value is None:
            return []
        if not isinstance(value, list):
            return [value]
        return value

    @validator("plugin", pre=True)
    @classmethod
    def _transform_to_uniquelist(cls, value: Any) -> UniqueList[str]:
        if value is None or value == [] or value == UniqueList():
            return UniqueList()
        return UniqueList(value)

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, NodeConfig)
        return len(self.get_differences_between(other)) == 0

    def get_differences_between(
        self, other: NodeConfig, stop_at_first_difference: bool = False
    ) -> dict[str, tuple[Any, Any]]:
        differences = {}
        for name_of_entry in self.dict(by_alias=True):
            mine = getattr(self, name_of_entry)
            his = getattr(other, name_of_entry)

            if mine == his or (isinstance(mine, list) and sorted(mine) == sorted(his)):
                continue

            differences[name_of_entry] = (mine, his)
            if stop_at_first_difference:
                break

        return differences

    @classmethod
    def __is_member_quoted(cls, member_name: str) -> bool:
        return "StringQuoted" in str(NodeConfig.__fields__[member_name].annotation)

    def write_to_lines(self) -> list[str]:
        def __serialize_depending_on_type(member_name: str, value: str | list[str] | bool | int) -> list[str]:
            def quote_on_demand(value: str) -> str:
                return f'"{value}"' if self.__is_member_quoted(member_name) else value

            def format_list(list_to_format: list[str]) -> list[str]:
                return [f"{member_name.replace('_', '-')} = {item}" for item in list_to_format]

            if isinstance(value, str):
                return format_list([quote_on_demand(value)])
            if isinstance(value, list):
                return format_list([quote_on_demand(item) for item in value])
            if isinstance(value, bool):
                return format_list(["1" if value else "0"])
            if isinstance(value, int):
                return format_list([str(value)])
            raise TypeError(member_name, value, type(value))

        result = []
        for member_name, member_value in self.dict(by_alias=True).items():
            if not (member_value is None or (isinstance(member_value, list) and len(member_value) == 0)):
                result.extend(__serialize_depending_on_type(member_name, member_value))
        return result

    def write_to_file(self, file_path: str | Path) -> None:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with file_path.open("w", encoding="utf-8") as file:
            file.write("\n".join(self.write_to_lines()))

    def load_from_lines(self, lines: list[str]) -> None:
        assert isinstance(lines, list)

        def parse_entry_line(line: str) -> tuple[str, str] | None:
            result = re.match(r"^\s*([\w\-]+)\s*=\s*(.*?)\s*$", line)
            return (result[1], result[2]) if result is not None else None

        def is_entry_line(line: str) -> bool:
            return parse_entry_line(line) is not None

        self.__clear_values()
        for line in lines:
            if is_entry_line(line):
                parsed = parse_entry_line(line)
                if parsed is None:
                    continue
                raw_key, value = parsed
                self.__check_if_key_from_file_is_valid(raw_key)
                key = raw_key.replace("-", "_")

                def strip_item(member_name: str, item: str) -> str:
                    return item.strip('"') if self.__is_member_quoted(member_name) else item

                if value != "":
                    if isinstance(attr := getattr(self, key), list):
                        attr.extend(strip_item(key, item) for item in value.split(" "))
                    else:
                        setattr(self, key, strip_item(key, value))

    def __check_if_key_from_file_is_valid(self, key_to_check: str) -> None:
        """Keys from file have hyphens instead of underscores."""
        valid_keys = [key.replace("_", "-") for key in self.dict(by_alias=True)]

        if key_to_check not in valid_keys:
            raise KeyError(f'Unknown config entry name: "{key_to_check}".')

    def __clear_values(self) -> None:
        for entry in self.dict():
            setattr(self, entry, None)

    def load_from_file(self, file_path: str | Path) -> None:
        if isinstance(file_path, str):
            file_path = Path(file_path)
        with file_path.open(encoding="utf-8") as file:
            self.load_from_lines(file.readlines())
