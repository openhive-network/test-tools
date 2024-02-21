from __future__ import annotations

import ast
import subprocess
from typing import TYPE_CHECKING

from pydantic import BaseModel

from schemas.fields.basic import AccountName, PrivateKey, PublicKey
from test_tools.__private import paths_to_executables

if TYPE_CHECKING:
    from pathlib import Path


class KeyGeneratorItem(BaseModel):
    private_key: PrivateKey
    public_key: PublicKey
    account_name: AccountName


class KeyGenerator:
    @staticmethod
    def generate_keys(
        account_name: str,
        *,
        number_of_accounts: int = 1,
        secret: str = "secret",
        executable_path: Path | None = None,
    ) -> list[KeyGeneratorItem]:
        assert number_of_accounts >= 1

        if account_name == "initminer":
            assert number_of_accounts == 1
            return [
                KeyGeneratorItem(
                    private_key=PrivateKey("5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n"),
                    public_key=PublicKey("STM6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4"),
                    account_name=account_name,
                )
            ]

        if executable_path is None:
            executable_path = paths_to_executables.get_path_of("get_dev_key")

        if number_of_accounts != 1:
            account_name += f"-0:{number_of_accounts}"

        output = subprocess.check_output([str(executable_path), secret, account_name]).decode("utf-8")
        parsed_output = ast.literal_eval(output)
        assert isinstance(parsed_output, list)
        return [KeyGeneratorItem(**item) for item in parsed_output]
