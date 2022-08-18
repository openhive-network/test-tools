from test_tools.__private.key_generator import KeyGenerator


class Account:
    def __init__(self, name, secret='secret', with_keys=True):
        self.__name = name
        self.__secret = secret
        self.private_key = None
        self.public_key = None

        if with_keys:
            output = KeyGenerator.generate_keys(name, secret=secret)[0]
            self.private_key = output['private_key']
            self.public_key = output['public_key']

    @property
    def name(self) -> str:
        return self.__name

    @property
    def secret(self) -> str:
        return self.__secret

    @staticmethod
    def create_multiple(number_of_accounts, name_base='account', *, secret='secret'):
        accounts = []
        for generated in KeyGenerator.generate_keys(name_base, number_of_accounts=number_of_accounts, secret=secret):
            account = Account(generated['account_name'], secret=secret, with_keys=False)
            account.private_key = generated['private_key']
            account.public_key = generated['public_key']

            accounts.append(account)

        return accounts
