def test_something_with_rc(world):
    init_node = world.create_init_node()
    init_node.run()
    wallet = init_node.attach_wallet()

    account_creator = wallet.api.find_rc_accounts("initminer")
    print(account_creator)



    # wallet.api.create_account()
    # wallet.api.

