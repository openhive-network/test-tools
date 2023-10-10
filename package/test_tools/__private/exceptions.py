from __future__ import annotations

from typing import Any


class TestToolsError(Exception):
    """Base exception class for test-tools package."""


class CommunicationError(TestToolsError):
    def __init__(self, description: str, request: Any, response: Any) -> None:
        super().__init__(f"{description}.\nSent: {request}.\nReceived: {response}")
        self.request = request
        self.response = response


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
