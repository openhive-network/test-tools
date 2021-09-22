def test_something_with_rc(world):
    init_node = world.create_init_node()
    init_node.config.webserver_ws_endpoint = '127.0.0.1:12345'
    init_node.run()
    wallet = init_node.attach_wallet()

    creator = "initminer"
    delegator = "delegator"
    wallet.api.create_account(creator, delegator, "{}", "true")
    wallet.api.transfer(creator, delegator, "10.000 TESTS", "", "true")
    wallet.api.transfer_to_vesting(creator, delegator, "0.010 TESTS", "true")
    wallet.api.transfer(creator, delegator, "1.000 TESTS", "", "true")

    idx=0
    # Create k x i of users
    for k in range (0,1):
        with wallet.in_single_transaction():
            for i in range (0,4):
                receiver = f'receiver{idx:04d}'
                wallet.api.create_account(creator, receiver, "{}")
                idx += 1
                i += 1

    k += 1

    # Delegate rc for k x i users
    i = 0
    k = 0
    idx = 0
    for k in range(0, 1):
        with wallet.in_single_transaction():
            for i in range (0,4):
                receiver = f'receiver{idx:04d}'
                wallet.api.delegate_rc(delegator, receiver, 1)
                idx += 1
                i += 1
    k += 1

    idx=0
    for idx in range (0, 4):
        receiver = f'receiver{idx:04d}'
        print(wallet.api.find_rc_accounts([receiver]))
        idx += 1

