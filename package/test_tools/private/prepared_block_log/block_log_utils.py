from datetime import datetime, timezone
import os

from test_tools.private.block_log import BlockLog


directory = os.path.dirname(os.path.realpath(__file__))
block_log_file = directory + "/twenty_witnesses/block_log"
timestamp_file = directory + "/twenty_witnesses/timestamp"

alpha_witness_names = [f'witness{i}-alpha' for i in range(12)]
beta_witness_names = [f'witness{i}-beta' for i in range(8)]
all_witness_names = alpha_witness_names + beta_witness_names


def get_prepared_block_log() -> BlockLog:
    return BlockLog(None, block_log_file, include_index=False)


def get_prepared_time_offset() -> str:
    with open(timestamp_file, 'r', encoding='utf8') as file:
        timestamp = file.read()
    timestamp = timestamp.strip()
    current_time = datetime.now(timezone.utc)
    new_time = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
    startup_time = 10  # node needs some time to startup

    difference = round(new_time.timestamp() - current_time.timestamp()) - startup_time
    time_offset = str(difference) + 's'
    return time_offset
