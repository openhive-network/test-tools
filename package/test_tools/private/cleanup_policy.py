from test_tools.constants import CleanupPolicy


# This is default value only when pytest is not used (e.g. in manual tests).
# For pytest there are registered autouse-fixtures which sets default cleanup
# policy to removing only unneeded files.
__default_cleanup_policy: CleanupPolicy = CleanupPolicy.DO_NOT_REMOVE_FILES


def set_default(policy: CleanupPolicy) -> None:
    global __default_cleanup_policy  # pylint: disable=invalid-name, global-statement
    __default_cleanup_policy = policy


def get_default() -> CleanupPolicy:
    return __default_cleanup_policy
