from __future__ import annotations

from helpy.exceptions import RequestError


class TestToolsError(Exception):
    """Base exception class for test-tools package."""


class WalletError(TestToolsError):
    """Base exception class for Wallet."""


CommunicationError = RequestError


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
    pass


class DelegatorIsNotRightError(WalletError):
    pass


class DelegateeIsNotRightError(WalletError):
    pass


class DelegatorOrDelegateeNotExistError(WalletError):
    pass


class TresholdOutOfRangeError(WalletError):
    pass


class WeightOutOfRangeError(WalletError):
    pass


class MethodDeprecatedInBeekeeperWalletError(WalletError):
    pass


class PrivateKeyInMemoError(WalletError):
    pass
