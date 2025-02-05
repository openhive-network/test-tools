from __future__ import annotations


class TestToolsError(Exception):
    """Base exception class for test-tools package."""


class WalletError(TestToolsError):
    """Base exception class for Wallet."""


class InternalNodeError(TestToolsError):
    pass


class MissingPathToExecutableError(TestToolsError):
    pass


class NameAlreadyInUseError(TestToolsError):
    pass


class NodeIsNotRunningError(TestToolsError):
    pass


class NotSupportedError(TestToolsError):
    pass


class ConfigError(TestToolsError):
    pass


class BlockWaitTimeoutError(TestToolsError):
    """Raised when the maximum amount of time to wait for a block on a blockchain is reached."""


class BlockLogError(TestToolsError):
    """Base class for BlockLog exceptions."""


class MissingBlockLogArtifactsError(BlockLogError):
    pass


class BlockLogUtilError(BlockLogError):
    pass


class AccountNotExistError(WalletError):
    """Raised when the account with the specified name does not exist on the blockchain."""


class DelegatorIsNotRightError(WalletError):
    """Raised when the provided delegator is incorrect."""


class DelegateeIsNotRightError(WalletError):
    """Raised when the provided delegatee is incorrect."""


class DelegatorOrDelegateeNotExistError(WalletError):
    """Raised when either the delegator or delegatee does not exist."""


class ThresholdOutOfRangeError(WalletError):
    """Raised when the provided threshold has an invalid value."""

    def __init__(self, message="Threshold out of range. The threshold must be greater than 0."):  # type: ignore[no-untyped-def]
        super().__init__(message)


class WeightOutOfRangeError(WalletError):
    """Raised when the provided weight exceeds the valid range."""

    def __init__(self, message="Weight out of range. The weight must be in the range 0 to 100."):  # type: ignore[no-untyped-def]
        super().__init__(message)


class MethodDeprecatedInBeekeeperWalletError(WalletError):
    """Raised when the called method is deprecated in the Beekeeper wallet. Use OldWallet or a similar method from another API."""


class PrivateKeyInMemoError(WalletError):
    """Raised when a private key is found in the memo field."""


class BroadcastDuringTransactionBuildingError(WalletError):
    """Raised when the broadcast parameter is set to True during transaction building."""

    def __init__(  # type: ignore[no-untyped-def]
        self,
        message="You cannot broadcast api call during transaction building.\n"
        "\n"
        "Replace broadcast parameter with value False or better -- remove it\n"
        "completely, because it is default value during transaction building.",
    ):
        super().__init__(message)
