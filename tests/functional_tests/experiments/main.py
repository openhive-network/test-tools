import time
import threading


def thread_body(a, b):
    # wallet = node.attach_wallet()
    # wallet.api.delegate_rc(delegator, receiver, 1)
    while True:
        print(f'In thread, {a}, {b}')
        time.sleep(1)


def test_something_with_rc(world):
    thread = threading.Thread(target=thread_body, args=(5, 12))
    thread.start()

    while True:
        print('In main')
        time.sleep(1)


    init_node = world.create_init_node()
    init_node.config.webserver_ws_endpoint = '127.0.0.1:12345'
    init_node.run()
    wallet = init_node.attach_wallet()

    creator = "initminer"
    delegator = "delegator"
    receiver = "receiver"

    wallet.api.create_account(creator, delegator, "{}", "true")
    wallet.api.transfer(creator, delegator, "10.000 TESTS", "", "true")
    wallet.api.transfer_to_vesting(creator, delegator, "0.010 TESTS", "true")
    wallet.api.transfer(creator, delegator, "1.000 TESTS", "", "true")
    wallet.api.delegate_rc(delegator, receiver,1)
    print(wallet.api.find_rc_accounts([receiver]))


# def rc_trans2()
#     creator = "initminer"
#     delegator = "delegator2"
#     receiver = "receiver2"
#
#     wallet.api.create_account(creator, delegator, "{}", "true")
#     wallet.api.transfer(creator, delegator, "10.000 TESTS", "", "true")
#     wallet.api.transfer_to_vesting(creator, delegator, "0.010 TESTS", "true")
#     wallet.api.transfer(creator, delegator, "1.000 TESTS", "", "true")
#     wallet.api.delegate_rc(delegator, receiver,1)
#     print(wallet.api.find_rc_accounts([receiver]))
#     return