from test_tools.constants import CleanUpPolicy


# This is default value only when pytest is not used (e.g. in manual tests).
# For pytest there are registered autouse-fixtures which sets default clean
# up policy to removing only unneeded files.
__default_clean_up_policy: CleanUpPolicy = CleanUpPolicy.DO_NOT_REMOVE_FILES


def set_default(policy: CleanUpPolicy) -> None:
    global __default_clean_up_policy  # pylint: disable=invalid-name, global-statement
    __default_clean_up_policy = policy


def get_default() -> CleanUpPolicy:
    return __default_clean_up_policy
