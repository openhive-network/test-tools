import time
import threading

from test_tools import Account

def thread_body(wallet, creator, delegator):
    with wallet.in_single_transaction():
        for i in range (4):
            receiver = f'receiver{i:04d}'
            wallet.api.create_account(creator, receiver, "{}")
            wallet.api.delegate_rc(delegator, receiver, 1)



def test_something_with_rc(world):
    init_node = world.create_init_node()
    init_node.config.webserver_ws_endpoint = '127.0.0.1:12345'
    init_node.run()
    wallet1 = init_node.attach_wallet()
    wallet2 = init_node.attach_wallet()

    creator = "initminer"
    delegator = "delegator"
    delegator_key = Account(delegator).public_key

    wallet1.api.set_password('password')
    wallet1.api.unlock('password')
    wallet1.api.create_account_with_keys(creator, delegator, "{}", delegator_key, delegator_key, delegator_key, delegator_key)

    wallet1.api.import_key(Account(delegator).private_key)
    wallet1.api.transfer(creator, delegator, "10.000 TESTS", "", "true")
    wallet1.api.transfer_to_vesting(creator, delegator, "0.010 TESTS", "true")
    wallet1.api.transfer(creator, delegator, "1.000 TBD", "", "true")


    wallet2.api.import_key(Account(delegator).private_key)

    thread = threading.Thread(target=thread_body, args=(wallet2, creator, delegator))
    thread.start()

    with wallet1.in_single_transaction():
        for i in range(4):
            receiver = f'receiverrr{i:04d}'
            wallet1.api.create_account(creator, receiver, "{}")
            wallet1.api.delegate_rc(delegator, receiver, 1)













