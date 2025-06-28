# fmt: off
# ruff: noqa
from __future__ import annotations

from pathlib import Path  # noqa: TCH003

from beekeepy._communication import HttpUrl, P2PUrl, WsUrl  # noqa: TCH002

from schemas._preconfigured_base_model import PreconfiguredBaseModel
from test_tools.__private.process.node_defaults import NodeDefaults


# All config items are automatically generated
class NodeCommon(PreconfiguredBaseModel):
    """Parameters used in command line and in config file."""

    account_history_rocksdb_blacklist_ops: list[str] = NodeDefaults.DEFAULT_ACCOUNT_HISTORY_ROCKSDB_BLACKLIST_OPS
    """
    Defines a list of operations which will be explicitly ignored.
    """

    account_history_rocksdb_path: Path = NodeDefaults.DEFAULT_ACCOUNT_HISTORY_ROCKSDB_PATH
    """
    The location of the rocksdb database for account history. By default it is $DATA_DIR/blockchain/account-history-
        rocksdb-storage
    """

    account_history_rocksdb_track_account_range: list[str] = NodeDefaults.DEFAULT_ACCOUNT_HISTORY_ROCKSDB_TRACK_ACCOUNT_RANGE
    """
    Defines a range of accounts to track as a json pair ["from","to"] [from,to] Can be specified multiple times.
    """

    account_history_rocksdb_whitelist_ops: list[str] = NodeDefaults.DEFAULT_ACCOUNT_HISTORY_ROCKSDB_WHITELIST_OPS
    """
    Defines a list of operations which will be explicitly logged.
    """

    alternate_chain_spec: str | None = NodeDefaults.DEFAULT_ALTERNATE_CHAIN_SPEC
    """
    Filepath for the alternate chain specification in JSON format
    """

    backtrace: str = NodeDefaults.DEFAULT_BACKTRACE
    """
    Whether to print backtrace on SIGSEGV
    """

    block_data_export_file: str = NodeDefaults.DEFAULT_BLOCK_DATA_EXPORT_FILE
    """
    Where to export data (NONE to discard)
    """

    block_data_skip_empty: bool = NodeDefaults.DEFAULT_BLOCK_DATA_SKIP_EMPTY
    """
    Skip producing when no factory is registered
    """

    block_log_compression_level: str = NodeDefaults.DEFAULT_BLOCK_LOG_COMPRESSION_LEVEL
    """
    Block log zstd compression level 0 (fast, low compression) - 22 (slow, high compression)
    """

    block_log_info_print_file: str = NodeDefaults.DEFAULT_BLOCK_LOG_INFO_PRINT_FILE
    """
    Where to print (filename or special sink ILOG, STDOUT, STDERR)
    """

    block_log_info_print_interval_seconds: str = NodeDefaults.DEFAULT_BLOCK_LOG_INFO_PRINT_INTERVAL_SECONDS
    """
    How often to print out block_log_info (default 1 day)
    """

    block_log_info_print_irreversible: bool = NodeDefaults.DEFAULT_BLOCK_LOG_INFO_PRINT_IRREVERSIBLE
    """
    Whether to defer printing until block is irreversible
    """

    block_log_split: str = NodeDefaults.DEFAULT_BLOCK_LOG_SPLIT
    """
    Whether the block log should be single file (-1), not used at all & keeping only head block in memory (0), or split
        into files each containing 1M blocks & keeping N full million latest blocks (N). Default 9999.
    """

    block_stats_report_output: str = NodeDefaults.DEFAULT_BLOCK_STATS_REPORT_OUTPUT
    """
    Where to put block stat reports: DLOG, ILOG, NOTIFY, LOG_NOTIFY. Default ILOG.
    """

    block_stats_report_type: str = NodeDefaults.DEFAULT_BLOCK_STATS_REPORT_TYPE
    """
    Level of detail of block stat reports: NONE, MINIMAL, REGULAR, FULL. Default FULL (recommended for API nodes).
    """

    blockchain_thread_pool_size: int = NodeDefaults.DEFAULT_BLOCKCHAIN_THREAD_POOL_SIZE
    """
    Number of worker threads used to pre-validate transactions and blocks
    """

    cashout_logging_ending_block: int | None = NodeDefaults.DEFAULT_CASHOUT_LOGGING_ENDING_BLOCK
    """
    Ending block for comment cashout log
    """

    cashout_logging_log_path_dir: Path | None = NodeDefaults.DEFAULT_CASHOUT_LOGGING_LOG_PATH_DIR
    """
    Path to log file
    """

    cashout_logging_starting_block: int | None = NodeDefaults.DEFAULT_CASHOUT_LOGGING_STARTING_BLOCK
    """
    Starting block for comment cashout log
    """

    checkpoint: list[str] = NodeDefaults.DEFAULT_CHECKPOINT
    """
    Pairs of [BLOCK_NUM,BLOCK_ID] that should be enforced as checkpoints.
    """

    colony_article: str | None = NodeDefaults.DEFAULT_COLONY_ARTICLE
    """
    Size and frequency parameters of article transactions.
    """

    colony_custom: str | None = NodeDefaults.DEFAULT_COLONY_CUSTOM
    """
    Size and frequency parameters of custom_json transactions. If no other transaction type is requested, minimal custom
        jsons will be produced.
    """

    colony_no_broadcast: bool = NodeDefaults.DEFAULT_COLONY_NO_BROADCAST
    """
    Disables broadcasting of produced transactions - only local witness will include them in block.
    """

    colony_reply: str | None = NodeDefaults.DEFAULT_COLONY_REPLY
    """
    Size and frequency parameters of reply transactions.
    """

    colony_sign_with: list[str] = NodeDefaults.DEFAULT_COLONY_SIGN_WITH
    """
    WIF PRIVATE KEY to be used to sign each transaction.
    """

    colony_start_at_block: int = NodeDefaults.DEFAULT_COLONY_START_AT_BLOCK
    """
    Start producing transactions when block with given number becomes head block (or right at the start if the block
        already passed).
    """

    colony_threads: int = NodeDefaults.DEFAULT_COLONY_THREADS
    """
    Number of worker threads. Default is 4
    """

    colony_transactions_per_block: int | None = NodeDefaults.DEFAULT_COLONY_TRANSACTIONS_PER_BLOCK
    """
    Max number of transactions produced per block. When not set it will be sum of weights of individual types.
    """

    colony_transfer: str | None = NodeDefaults.DEFAULT_COLONY_TRANSFER
    """
    Size and frequency parameters of transfer transactions.
    """

    colony_vote: str | None = NodeDefaults.DEFAULT_COLONY_VOTE
    """
    Size and frequency parameters of vote transactions.
    """

    debug_node_edit_script: list[str] = NodeDefaults.DEFAULT_DEBUG_NODE_EDIT_SCRIPT
    """
    Database edits to apply on startup (may specify multiple times)
    """

    enable_block_log_auto_fixing: bool = NodeDefaults.DEFAULT_ENABLE_BLOCK_LOG_AUTO_FIXING
    """
    If enabled, corrupted block_log will try to fix itself automatically.
    """

    enable_block_log_compression: bool = NodeDefaults.DEFAULT_ENABLE_BLOCK_LOG_COMPRESSION
    """
    Compress blocks using zstd as they're added to the block log
    """

    enable_stale_production: bool = NodeDefaults.DEFAULT_ENABLE_STALE_PRODUCTION
    """
    Enable block production, even if the chain is stale.
    """

    flush_state_interval: int | None = NodeDefaults.DEFAULT_FLUSH_STATE_INTERVAL
    """
    flush shared memory changes to disk every N blocks
    """

    log_appender: list[str] = NodeDefaults.DEFAULT_LOG_APPENDER
    """
    Appender definition JSON. Obligatory attributes: "appender" - name of appender "stream" - target stream, mutually
        exclusive with "file" "file" - target filename (including path), mutually exclusive with "stream" Optional
        attributes: "time_format" - see time_format enum values (default: "iso_8601_seconds") Optional attributes
        (applicable to file appender only): "delta_times" - whether times should be printed as deltas since previous message
        (default: false) "flush" - whether each log write should end with flush (default: true) "truncate" - whether to
        truncate the log file at startup (default: true) "rotate" - whether the log files should be rotated (default: true)
        "rotation_interval" - seconds between file rotation (default: 3600) "rotation_limit" - seconds before rotated file
        is removed (default: 86400)
    """

    log_console_appender: list[str] = NodeDefaults.DEFAULT_LOG_CONSOLE_APPENDER
    """

    """

    log_file_appender: list[str] = NodeDefaults.DEFAULT_LOG_FILE_APPENDER
    """

    """

    log_json_rpc: Path | None = NodeDefaults.DEFAULT_LOG_JSON_RPC
    """
    json-rpc log directory name.
    """

    log_logger: list[str] = NodeDefaults.DEFAULT_LOG_LOGGER
    """
    Logger definition JSON: "name" - name of logger "level" - level of reporting, see log_level enum values "appenders"
        - list of designated appenders
    """

    market_history_bucket_size: str = NodeDefaults.DEFAULT_MARKET_HISTORY_BUCKET_SIZE
    """
    Track market history by grouping orders into buckets of equal size measured in seconds specified as a JSON array of
        numbers
    """

    market_history_buckets_per_size: int = NodeDefaults.DEFAULT_MARKET_HISTORY_BUCKETS_PER_SIZE
    """
    How far back in time to track history for each bucket size, measured in the number of buckets (default: 5760)
    """

    max_mempool_size: str = NodeDefaults.DEFAULT_MAX_MEMPOOL_SIZE
    """
    Postponed transactions that exceed limit are dropped from pending. Setting 0 means only pending transactions that
        fit in reapplication window of 200ms will stay in mempool.
    """

    notifications_endpoint: list[P2PUrl] = NodeDefaults.DEFAULT_NOTIFICATIONS_ENDPOINT
    """
    list of addresses, that will receive notification about in-chain events
    """

    p2p_endpoint: P2PUrl | None = NodeDefaults.DEFAULT_P2P_ENDPOINT
    """
    The local IP address and port to listen for incoming connections.
    """

    p2p_max_connections: int | None = NodeDefaults.DEFAULT_P2P_MAX_CONNECTIONS
    """
    Maxmimum number of incoming connections on P2P endpoint.
    """

    p2p_parameters: str | None = NodeDefaults.DEFAULT_P2P_PARAMETERS
    """
    P2P network parameters. (Default: {"listen_endpoint":"0.0.0.0:0","accept_incoming_connections":true,"wait_if_endpoin
        t_is_busy":true,"private_key":"0000000000000000000000000000000000000000000000000000000000000000","desired_number_of_
        connections":20,"maximum_number_of_connections":200,"peer_connection_retry_timeout":30,"peer_inactivity_timeout":5,"
        peer_advertising_disabled":false,"maximum_number_of_blocks_to_handle_at_one_time":200,"maximum_number_of_sync_blocks
        _to_prefetch":20000,"maximum_blocks_per_peer_during_syncing":200,"active_ignored_request_timeout_microseconds":60000
        00} )
    """

    p2p_seed_node: list[str] = NodeDefaults.DEFAULT_P2P_SEED_NODE
    """
    The IP address and port of a remote peer to sync with.
    """

    pacemaker_max_offset: str = NodeDefaults.DEFAULT_PACEMAKER_MAX_OFFSET
    """
    maximum time of emission offset from block timestamp in milliseconds, default 20000ms (when exceeded, node will be
        stopped)
    """

    pacemaker_min_offset: str = NodeDefaults.DEFAULT_PACEMAKER_MIN_OFFSET
    """
    minimum time of emission offset from block timestamp in milliseconds, default -300ms
    """

    pacemaker_source: Path | None = NodeDefaults.DEFAULT_PACEMAKER_SOURCE
    """
    path to block_log file - source of block emissions
    """

    plugin: list[str] = NodeDefaults.DEFAULT_PLUGIN
    """
    Plugin(s) to enable, may be specified multiple times
    """

    private_key: list[str] = NodeDefaults.DEFAULT_PRIVATE_KEY
    """
    WIF PRIVATE KEY to be used by one or more witnesses or miners
    """

    queen_block_size: int = NodeDefaults.DEFAULT_QUEEN_BLOCK_SIZE
    """
    Size of blocks expected to be filled (or max allowed by witnesses). Default value 0 means max blocks.
    """

    queen_tx_count: int = NodeDefaults.DEFAULT_QUEEN_TX_COUNT
    """
    Number of transactions in block. Default value 0 means no limit.
    """

    rc_flood_level: str = NodeDefaults.DEFAULT_RC_FLOOD_LEVEL
    """
    Number of full blocks that can be present in mempool before RC surcharge is applied. 0-65535. Default 20 (one minute
        of full blocks).
    """

    rc_flood_surcharge: str = NodeDefaults.DEFAULT_RC_FLOOD_SURCHARGE
    """
    Multiplication factor for temporary extra RC cost charged for each block above flood level before transaction is
        allowed to enter and remain in pending. 0-10000. Default 10000 (100%).
    """

    rc_stats_report_output: str = NodeDefaults.DEFAULT_RC_STATS_REPORT_OUTPUT
    """
    Where to put daily RC stat reports: DLOG, ILOG, NOTIFY, LOG_NOTIFY. Default ILOG.
    """

    rc_stats_report_type: str = NodeDefaults.DEFAULT_RC_STATS_REPORT_TYPE
    """
    Level of detail of daily RC stat reports: NONE, MINIMAL, REGULAR, FULL. Default REGULAR.
    """

    required_participation: int = NodeDefaults.DEFAULT_REQUIRED_PARTICIPATION
    """
    Percent of witnesses (0-99) that must be participating in order to produce blocks
    """

    shared_file_dir: Path = NodeDefaults.DEFAULT_SHARED_FILE_DIR
    """
    the location of the chain shared memory files (absolute path or relative to application data dir)
    """

    shared_file_full_threshold: str = NodeDefaults.DEFAULT_SHARED_FILE_FULL_THRESHOLD
    """
    A 2 precision percentage (0-10000) that defines the threshold for when to autoscale the shared memory file. Setting
        this to 0 disables autoscaling. Recommended value for consensus node is 9500 (95%).
    """

    shared_file_scale_rate: str = NodeDefaults.DEFAULT_SHARED_FILE_SCALE_RATE
    """
    A 2 precision percentage (0-10000) that defines how quickly to scale the shared memory file. When autoscaling occurs
        the file's size will be increased by this percent. Setting this to 0 disables autoscaling. Recommended value is
        between 1000-2000 (10-20%)
    """

    shared_file_size: str = NodeDefaults.DEFAULT_SHARED_FILE_SIZE
    """
    Size of the shared memory file. Default: 24G. If running with many plugins, increase this value to 28G.
    """

    snapshot_root_dir: Path = NodeDefaults.DEFAULT_SNAPSHOT_ROOT_DIR
    """
    The location (root-dir) of the snapshot storage, to save/read portable state dumps
    """

    statsd_batchsize: int = NodeDefaults.DEFAULT_STATSD_BATCHSIZE
    """
    Size to batch statsd messages.
    """

    statsd_blacklist: list[str] = NodeDefaults.DEFAULT_STATSD_BLACKLIST
    """
    Blacklist of statistics to capture.
    """

    statsd_endpoint: P2PUrl | None = NodeDefaults.DEFAULT_STATSD_ENDPOINT
    """
    Endpoint to send statsd messages to.
    """

    statsd_whitelist: list[str] = NodeDefaults.DEFAULT_STATSD_WHITELIST
    """
    Whitelist of statistics to capture.
    """

    transaction_status_block_depth: int = NodeDefaults.DEFAULT_TRANSACTION_STATUS_BLOCK_DEPTH
    """
    Defines the number of blocks from the head block that transaction statuses will be tracked.
    """

    webserver_http_endpoint: HttpUrl | None = NodeDefaults.DEFAULT_WEBSERVER_HTTP_ENDPOINT
    """
    Local http endpoint for webserver requests.
    """

    webserver_https_certificate_file_name: str | None = NodeDefaults.DEFAULT_WEBSERVER_HTTPS_CERTIFICATE_FILE_NAME
    """
    File name with a server's certificate.
    """

    webserver_https_endpoint: HttpUrl | None = NodeDefaults.DEFAULT_WEBSERVER_HTTPS_ENDPOINT
    """
    Local https endpoint for webserver requests.
    """

    webserver_https_key_file_name: str | None = NodeDefaults.DEFAULT_WEBSERVER_HTTPS_KEY_FILE_NAME
    """
    File name with a server's private key.
    """

    webserver_thread_pool_size: int = NodeDefaults.DEFAULT_WEBSERVER_THREAD_POOL_SIZE
    """
    Number of threads used to handle queries. Default: 32.
    """

    webserver_unix_endpoint: P2PUrl | None = NodeDefaults.DEFAULT_WEBSERVER_UNIX_ENDPOINT
    """
    Local unix http endpoint for webserver requests.
    """

    webserver_ws_deflate: bool = NodeDefaults.DEFAULT_WEBSERVER_WS_DEFLATE
    """
    Enable the RFC-7692 permessage-deflate extension for the WebSocket server (only used if the client requests it).
        This may save bandwidth at the expense of CPU
    """

    webserver_ws_endpoint: WsUrl | None = NodeDefaults.DEFAULT_WEBSERVER_WS_ENDPOINT
    """
    Local websocket endpoint for webserver requests.
    """

    witness: list[str] = NodeDefaults.DEFAULT_WITNESS
    """
    name of witness controlled by this node (e.g. initwitness )
    """
