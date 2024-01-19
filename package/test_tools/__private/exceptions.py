from __future__ import annotations

from helpy.exceptions import RequestError


class TestToolsError(Exception):
    """Base exception class for test-tools package."""


CommunicationError = RequestError


class InternalNodeError(TestToolsError):
    pass


class MissingBlockLogArtifactsError(TestToolsError):
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


class BlockLogUtilError(TestToolsError):
    pass
