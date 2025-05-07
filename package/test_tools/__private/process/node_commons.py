from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload

from beekeepy.interfaces import HttpUrl, P2PUrl, Url, WsUrl
from pydantic import Field

from schemas._preconfigured_base_model import PreconfiguredBaseModel

if TYPE_CHECKING:
    from typing_extensions import Self

if TYPE_CHECKING:
    BacktraceAllowedValues = Literal["yes", "no"]
    SinkAllowedValues = Literal["STDERR", "STDOUT", "WLOG", "ELOG", "DLOG", "ILOG"]
    ReportTypes = Literal["NONE", "MINIMAL", "REGULAR", "FULL"]
else:
    BacktraceAllowedValues = str
    SinkAllowedValues = str
    ReportTypes = str


class QuotedMarker:
    """Following string will be serialized with quotes and will be deserialized without them."""


StringQuoted = str | QuotedMarker
PathQuoted = Path | QuotedMarker
T = TypeVar("T")


class UniqueList(list[T]):
    def __init__(self, _obj: Iterable[T] | T = []) -> None:  # noqa: B006
        super().__init__(set(_obj) if isinstance(_obj, Iterable) else [_obj])
        self.sort()

    def append(self, __object: T) -> None:
        if __object not in self:
            super().append(__object)
            self.sort()

    def extend(self, __iterable: Iterable[T]) -> None:
        outcome = {*self, *__iterable}
        self.clear()
        super().extend(outcome)
        self.sort()

    def __iadd__(self, _: Any) -> Self:  # type: ignore[override]
        raise NotImplementedError

    def __add__(self, _: Any) -> Self:  # type: ignore[override]
        raise NotImplementedError


class ConfigurationCommonHived(PreconfiguredBaseModel):
    account_history_rocksdb_blacklist_ops: str | None = None
    account_history_rocksdb_path: PathQuoted | None = None
    account_history_rocksdb_track_account_range: str | None = None
    account_history_rocksdb_whitelist_ops: str | None = None
    backtrace: BacktraceAllowedValues | None = None
    block_data_export_file: Path | Literal["NONE"] | None = None
    block_data_skip_empty: bool | None = None
    block_log_compression_level: int | None = None
    block_log_info_print_file: SinkAllowedValues | Path | None = None
    block_log_info_print_interval_seconds: int | None = None
    block_log_info_print_irreversible: int | None = None
    block_log_split: int | None = None
    block_stats_report_output: SinkAllowedValues | None = None
    block_stats_report_type: ReportTypes | None = None
    blockchain_thread_pool_size: int | None = None
    cashout_logging_ending_block: int | None = None
    cashout_logging_log_path_dir: Path | None = None
    cashout_logging_starting_block: int | None = None
    checkpoint: UniqueList[tuple[int, str]] = Field(default_factory=UniqueList)
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
    p2p_seed_node: list[P2PUrl] = Field(default_factory=list)
    pacemaker_max_offset: int | None = None
    pacemaker_min_offset: int | None = None
    pacemaker_source: str | None = None
    plugin: UniqueList[str] = Field(default_factory=UniqueList)
    private_key: list[str] = Field(default_factory=list)
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
    witness: list[StringQuoted] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {Url: lambda u: u.as_string(with_protocol=False)}  # noqa: RUF012

    @classmethod
    def _require_quotation(cls, member_name_or_type: str | type) -> bool:
        return QuotedMarker.__name__ in (
            cls._member_annotation(member_name_or_type)
            if isinstance(member_name_or_type, str)
            else str(member_name_or_type)
        )

    @classmethod
    def _member_annotation(cls, member_name: str) -> str:
        return str(cls.__fields__[member_name].annotation)

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
