import test_tools as tt


def test_multiple_accounts_creation():
    accounts = tt.Account.create_multiple(3, "example")
    assert [f"example-{i}" for i in range(3)] == [account.name for account in accounts]
