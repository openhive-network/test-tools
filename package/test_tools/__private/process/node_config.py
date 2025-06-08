from __future__ import annotations

from pathlib import Path
from typing import Any, Final, TypeGuard, overload

from beekeepy.handle.runnable import Config
from beekeepy.interfaces import HttpUrl, P2PUrl, Url, WsUrl
from msgspec import field

from test_tools.__private.process.node_commons import (
    BacktraceAllowedValues,
    PathQuoted,
    QuotedMarker,
    ReportTypes,
    SinkAllowedValues,
    StringQuoted,
    UniqueList,
)


class NodeConfig(Config):
    account_history_blacklist_ops: str | None = None
    account_history_track_account_range: str | None = None
    account_history_whitelist_ops: str | None = None
    edit_script: str | None = None
    flush_state_interval: str | None = None
    history_blacklist_ops: str | None = None
    history_whitelist_ops: str | None = None
    psql_first_block: int | None = None
    psql_index_threshold: int | None = None
    psql_operations_threads_number: int | None = None
    psql_transactions_threads_number: int | None = None
    psql_url: str | None = None
    psql_livesync_threshold: int | None = None
    rpc_endpoint: str | None = None
    seed_node: str | None = None
    track_account_range: str | None = None
    account_history_rocksdb_blacklist_ops: str | None = None
    account_history_rocksdb_path: PathQuoted | None = None
    account_history_rocksdb_track_account_range: str | None = None
    account_history_rocksdb_whitelist_ops: str | None = None
    backtrace: BacktraceAllowedValues | None = None
    block_data_export_file: str | None = None
    block_data_skip_empty: bool | None = None
    block_log_compression_level: int | None = None
    block_log_info_print_file: SinkAllowedValues | str | None = None
    block_log_info_print_interval_seconds: int | None = None
    block_log_info_print_irreversible: int | None = None
    block_log_split: int | None = None
    block_stats_report_output: SinkAllowedValues | None = None
    block_stats_report_type: ReportTypes | None = None
    blockchain_thread_pool_size: int | None = None
    cashout_logging_ending_block: int | None = None
    cashout_logging_log_path_dir: Path | None = None
    cashout_logging_starting_block: int | None = None
    checkpoint: UniqueList[tuple[int, str]] = field(default_factory=UniqueList)
    colony_article: str | None = None
    colony_custom: str | None = None
    colony_no_broadcast: bool | None = None
    colony_reply: str | None = None
    colony_sign_with: list[str] | None = None
    colony_start_at_block: int | None = None
    colony_threads: int | None = None
    colony_transactions_per_block: int | None = None
    colony_transfer: str | None = None
    colony_vote: str | None = None
    debug_node_edit_script: str | None = None
    enable_block_log_auto_fixing: bool | None = None
    enable_block_log_compression: bool | None = None
    enable_stale_production: bool | None = None
    log_appender: str | None = None
    log_console_appender: str | None = None
    log_file_appender: str | None = None
    log_json_rpc: Path | None = None
    log_logger: str | None = None
    market_history_bucket_size: str | None = None
    market_history_buckets_per_size: str | None = None
    p2p_endpoint: P2PUrl | None = None
    p2p_max_connections: int | None = None
    p2p_parameters: str | None = None
    p2p_seed_node: list[P2PUrl] = field(default_factory=list)
    pacemaker_max_offset: int | None = None
    pacemaker_min_offset: int | None = None
    pacemaker_source: str | None = None
    plugin: UniqueList[str] = field(default_factory=UniqueList)
    private_key: list[str] = field(default_factory=list)
    rc_stats_report_output: SinkAllowedValues | None = None
    rc_stats_report_type: ReportTypes | None = None
    required_participation: int | None = None
    shared_file_dir: PathQuoted | None = None
    shared_file_full_threshold: str | None = None
    shared_file_scale_rate: str | None = None
    shared_file_size: str | None = None
    snapshot_root_dir: PathQuoted | None = None
    statsd_batchsize: int | None = None
    statsd_blacklist: list[HttpUrl] | None = None
    statsd_endpoint: HttpUrl | None = None
    statsd_whitelist: list[HttpUrl] | None = None
    transaction_status_block_depth: int | None = None
    webserver_http_endpoint: HttpUrl | None = None
    webserver_https_certificate_file_name: Path | None = None
    webserver_https_endpoint: HttpUrl | None = None
    webserver_https_key_file_name: Path | None = None
    webserver_thread_pool_size: int | None = None
    webserver_unix_endpoint: Path | None = None
    webserver_ws_deflate: int | None = None
    webserver_ws_endpoint: WsUrl | None = None
    witness: list[StringQuoted] = field(default_factory=list)

    @classmethod
    def _convert_member_value_to_config_value(cls, member_name: str, member_value: Any) -> str | list[str]:
        if cls.is_checkpoint_type(member_value=member_value):
            return [f"[{item[0]}, {item[1]}]" for item in member_value]
        if cls._require_quotation(member_name):
            member_value = cls._apply_quotation(member_value)
        return super()._convert_member_value_to_config_value(member_name, member_value)

    @classmethod
    def default(cls, *, skip_address: bool = False) -> NodeConfig:
        return NodeConfig(
            webserver_http_endpoint=(None if skip_address else HttpUrl("0.0.0.0:0")),
            webserver_ws_endpoint=(None if skip_address else WsUrl("0.0.0.0:0")),
            p2p_endpoint=(None if skip_address else P2PUrl("0.0.0.0:0")),
        )

    @classmethod
    def is_checkpoint_type(cls, member_value: Any) -> TypeGuard[list[tuple[int, str]]]:
        checkpoint_item_length: Final[int] = 2

        return (
            isinstance(member_value, list)
            and len(member_value) > 0
            and isinstance(member_value[0], tuple)
            and len(member_value[0]) == checkpoint_item_length
        )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Url: lambda u: u.as_string(with_protocol=False)}  # noqa: RUF012

    @classmethod
    def _require_quotation(cls, member_name_or_type: str | type) -> bool:
        required_annotation = (
            cls._member_annotation(member_name_or_type)
            if isinstance(member_name_or_type, str)
            else str(member_name_or_type)
        )
        return "StringQuoted" in required_annotation or "PathQuoted" in required_annotation

    @classmethod
    def _member_annotation(cls, member_name: str) -> str:
        return str(cls.__annotations__[member_name])

    @overload
    @classmethod
    def _apply_quotation(cls, value: QuotedMarker | str | Path) -> str:
        ...

    @overload
    @classmethod
    def _apply_quotation(cls, value: list[str | Path]) -> list[str]:
        ...

    @classmethod
    def _apply_quotation(cls, value: QuotedMarker | str | Path | list[str | Path]) -> str | list[str]:
        if isinstance(value, list):
            return [cls._apply_quotation(item) for item in value]
        if isinstance(value, str):
            return f'"{value}"'
        if isinstance(value, Path):
            return cls._apply_quotation(value.as_posix())
        raise TypeError(f"Unsupported type: {value.__class__.__name__}")
