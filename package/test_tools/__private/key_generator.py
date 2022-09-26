from __future__ import annotations

import ast
import subprocess
from typing import TYPE_CHECKING

from test_tools.__private import paths_to_executables

if TYPE_CHECKING:
    from typing import Dict, List, Optional
    from pathlib import Path


class KeyGenerator:
    @staticmethod
    def generate_keys(
        account_name: str,
        *,
        number_of_accounts: int = 1,
        secret: str = "secret",
        executable_path: Optional[Path] = None,
    ) -> List[Dict[str, str]]:
        assert number_of_accounts >= 1

        if account_name == "initminer":
            assert number_of_accounts == 1
            return [
                {
                    "private_key": "5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n",
                    "public_key": "TST6LLegbAgLAy28EHrffBVuANFWcFgmqRMW13wBmTExqFE9SCkg4",
                    "account_name": account_name,
                }
            ]

        if executable_path is None:
            executable_path = paths_to_executables.get_path_of("get_dev_key")

        if number_of_accounts != 1:
            account_name += f"-0:{number_of_accounts}"

        output = subprocess.check_output([str(executable_path), secret, account_name]).decode("utf-8")
        return ast.literal_eval(output)
