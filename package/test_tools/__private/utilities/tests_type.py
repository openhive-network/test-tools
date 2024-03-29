from __future__ import annotations

import sys


def is_automatic_test() -> bool:
    return __is_pytest_used()


def __is_pytest_used() -> bool:
    return "pytest" in sys.modules
