from typing import Final, Union

from test_tools.__private.asset.token import Token
from test_tools.__private.exceptions import ParseError


class Asset:
    class Hbd(Token):
        token: Final[str] = "HBD"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000013"

    class Tbd(Token):
        token: Final[str] = "TBD"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000013"

    class Hive(Token):
        token: Final[str] = "HIVE"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000021"

    class Test(Token):
        token: Final[str] = "TESTS"
        precision: Final[int] = 3
        nai: Final[str] = "@@000000021"

    class Vest(Token):
        token: Final[str] = "VESTS"
        precision: Final[int] = 6
        nai: Final[str] = "@@000000037"

    @classmethod
    def from_(cls, data: Union[str, dict], *, treat_dict_as_testnet_currencies: bool = True) -> Token:
        """
        This function allows you to convert an asset from string or JSON format to the appropriate object of Asset type.

        * In case of dict:
            Nai dictionary does not hold the information about token type.

            By default, treat_dict_as_testnet_currencies parameter is set to True. As a result, an Asset object will be
            created in the testnet format. If you want to create an object in mainnet form, set it to False.
        """
        if isinstance(data, str):
            return cls.__from_sting(data)
        if isinstance(data, dict):
            return cls.__from_dict(data, testnet_currencies=treat_dict_as_testnet_currencies)
        raise ParseError(f"Can't convert `{type(data)}` to Asset object.")

    @classmethod
    def __from_sting(cls, asset_as_string: str) -> Token:
        amount, token = asset_as_string.split()
        assets = [cls.Hbd, cls.Hive, cls.Vest, cls.Tbd, cls.Test]
        for asset in assets:
            if token == asset.token:
                return asset(float(amount))
        raise ParseError(
            f"Asset with token `{token}` does not exist.\n"
            f"Supported tokens are: {[asset.token for asset in assets]}."
        )

    @classmethod
    def __from_dict(cls, asset_as_dict: dict, *, testnet_currencies: bool = True) -> Token:
        if "nai" not in asset_as_dict:
            raise ParseError("Asset dictionary has no nai.")

        assets = [cls.Vest]
        assets += [cls.Tbd, cls.Test] if testnet_currencies else [cls.Hbd, cls.Hive]

        for asset in assets:
            if asset_as_dict["nai"] == asset.nai:
                # When it will be implemented according to the Handle's practice  should be removed
                return asset._from_dict(asset_as_dict)  # pylint: disable=protected-access
        raise ParseError(
            f"Asset with nai `{asset_as_dict['nai']}` does not exist.\n"
            f"Supported nai's are: {[asset.nai for asset in assets]}."
        )
