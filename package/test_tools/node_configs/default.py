from __future__ import annotations

from test_tools.__private.node_config import NodeConfig


def create_default_config(*, skip_address: bool = False) -> NodeConfig:
    """
    Returns default node config.

    Returns
    -------
        NodeConfig: with default values.
    """
    return NodeConfig(
        log_appender=(
            '{"appender":"stderr","stream":"std_error","time_format":"iso_8601_microseconds"} '
            '{"appender":"p2p","file":"logs/p2p/p2p.log","time_format":"iso_8601_milliseconds"}'
        ),
        log_logger=(
            '{"name":"default","level":"info","appenders":["stderr"]} '
            '{"name":"user","level":"debug","appenders":["stderr"]} '
            '{"name":"p2p","level":"warn","appenders":["p2p"]}'
        ),
        backtrace="yes",
        plugin=["witness", "account_by_key_api", "account_by_key", "state_snapshot"],
        account_history_rocksdb_path="blockchain/account-history-rocksdb-storage",
        block_data_export_file="NONE",
        block_data_skip_empty=False,
        block_log_info_print_interval_seconds="86400",
        block_log_info_print_irreversible="1",
        block_log_info_print_file="ILOG",
        shared_file_dir="blockchain",
        shared_file_size="24G",
        shared_file_full_threshold="0",
        shared_file_scale_rate="0",
        market_history_bucket_size="[15,60,300,3600,86400]",
        market_history_buckets_per_size="5760",
        rc_stats_report_type="REGULAR",
        rc_stats_report_output="ILOG",
        block_log_split=-1,
        snapshot_root_dir="snapshot",
        statsd_batchsize="1",
        transaction_status_block_depth="64000",
        webserver_thread_pool_size="32",
        enable_stale_production=False,
        required_participation=33,
        enable_block_log_auto_fixing=True,
        block_log_compression_level=15,
        blockchain_thread_pool_size=8,
        block_stats_report_type="FULL",
        block_stats_report_output="ILOG",
        webserver_ws_deflate=False,
        enable_block_log_compression=True,
        colony_threads=4,
        colony_start_at_block=0,
        colony_no_broadcast=False,
        pacemaker_min_offset=-300,
        pacemaker_max_offset=20000,
        **(
            {"p2p_endpoint": "0.0.0.0:0", "webserver_http_endpoint": "0.0.0.0:0", "webserver_ws_endpoint": "0.0.0.0:0"}
            if not skip_address
            else {}
        ),
    )
