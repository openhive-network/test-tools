#!/usr/bin/env python3
import argparse
import os

from test_tools import logger, constants, Account, World, Asset, Wallet
from test_tools.private.prepared_block_log.block_log_utils import (
    all_witness_names, alpha_witness_names, beta_witness_names, block_log_file, timestamp_file
)


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def prepare_block_log(length):
    world = World()
    world.set_clean_up_policy(constants.WorldCleanUpPolicy.DO_NOT_REMOVE_FILES)

    # Create first network
    alpha_net = world.create_network('Alpha')
    beta_net = world.create_network('Beta')
    init_node = alpha_net.create_init_node()

    for i in range(4):
        first = int(i * len(alpha_witness_names) / 4)
        last = int((i+1) * len(alpha_witness_names) / 4)
        alpha_net.create_witness_node(witnesses=alpha_witness_names[first:last])
    api_node = alpha_net.create_api_node("ApiNode")

    for i in range(4):
        first = int(i * len(beta_witness_names) / 4)
        last = int((i+1) * len(beta_witness_names) / 4)
        beta_net.create_witness_node(witnesses=beta_witness_names[first:last])

    # Run
    alpha_net.connect_with(beta_net)

    logger.info('Running networks, waiting for live...')
    alpha_net.run()
    beta_net.run()

    logger.info('Attaching wallets...')
    wallet = Wallet(attach_to=api_node)
    # We are waiting here for block 43, because witness participation is counting
    # by dividing total produced blocks in last 128 slots by 128. When we were waiting
    # too short, for example 42 blocks, then participation equals 42 / 128 = 32.81%.
    # It is not enough, because 33% is required. 43 blocks guarantee, that this
    # requirement is always fulfilled (43 / 128 = 33.59%, which is greater than 33%).
    logger.info('Wait for block 43 (to fulfill required 33% of witness participation)')
    init_node.wait_for_block_with_number(43)

    # Prepare witnesses on blockchain
    create_accounts(wallet)
    make_transfers(wallet)
    make_transfers_to_vesting(wallet)
    update_witnesses(wallet)

    logger.info('Wait 21 blocks to schedule newly created witnesses')
    init_node.wait_number_of_blocks(21)

    active_witnesses_names = get_witnesses_state(api_node)
    logger.info("Witness state after voting")
    logger.info(active_witnesses_names)
    assert len(active_witnesses_names) == 21

    # Reason of this wait is to enable moving forward of irreversible block
    logger.info('Wait 21 blocks (when every witness sign at least one block)')
    init_node.wait_number_of_blocks(21)

    # Network should be set up at this time, with 21 active witnesses, enough participation rate
    # and irreversible block number lagging behind around 15-20 blocks head block number
    result = wallet.api.info()
    irreversible = result["last_irreversible_block_num"]
    head = result["head_block_num"]
    logger.info(f'Network prepared, irreversible block: {irreversible}, head block: {head}')

    assert irreversible + 10 < head

    while irreversible < length:
        init_node.wait_number_of_blocks(1)
        result = wallet.api.info()
        irreversible = result["last_irreversible_block_num"]
        head = result["head_block_num"]
        logger.info(f'Generating block_log of length: {length}')
        logger.info(f'Current irreversible: {irreversible}, current head block: {head}')

    timestamp = init_node.api.block.get_block(block_num = length)['block']['timestamp']

    return init_node.get_block_log(), timestamp


def create_accounts(wallet):
    with wallet.in_single_transaction():
        for name in all_witness_names:
            public_key = Account(name).public_key
            wallet.api.create_account_with_keys(
                'initminer', name, '',
                public_key, public_key, public_key, public_key
            )
    for name in all_witness_names:
        wallet.api.import_key(Account(name).private_key)


def make_transfers(wallet):
    with wallet.in_single_transaction():
        for name in all_witness_names:
            wallet.api.transfer("initminer", name, Asset.Test(1000), 'memo')


def make_transfers_to_vesting(wallet):
    with wallet.in_single_transaction():
        for name in all_witness_names:
            wallet.api.transfer_to_vesting("initminer", name, Asset.Test(1000))


def update_witnesses(wallet):
    with wallet.in_single_transaction():
        for name in all_witness_names:
            wallet.api.update_witness(
                name, "https://" + name, Account(name).public_key,
                {"account_creation_fee": Asset.Test(3), "maximum_block_size": 65536, "sbd_interest_rate": 0}
            )


def get_witnesses_state(api_node):
    response = api_node.api.database.list_witnesses(start=0, limit=100, order='by_name')
    active_witnesses = response["witnesses"]
    active_witnesses_names = [witness["owner"] for witness in active_witnesses]
    return active_witnesses_names


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--length', type=int, default=105, help='Desired block_log length')
    args = parser.parse_args()

    block_log, timestamp = prepare_block_log(args.length)
    logger.info(f'{Bcolors.OKGREEN}timestamp: {timestamp}{Bcolors.ENDC}')

    if os.path.exists(block_log_file):
        os.remove(block_log_file)
    block_log.truncate(block_log_file, args.length)

    if os.path.exists(timestamp_file):
        os.remove(timestamp_file)
    with open(timestamp_file, 'w') as f:
        f.write(f'{timestamp}')

    logger.info(f'{Bcolors.OKGREEN}files written to {block_log_file} and {timestamp_file}{Bcolors.ENDC}')
