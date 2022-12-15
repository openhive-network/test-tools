class TestToolsException(Exception):
    """Base exception class for test-tools package."""


class CommunicationError(TestToolsException):
    def __init__(self, description, request, response):
        super().__init__(f"{description}.\nSent: {request}.\nReceived: {response}")
        self.request = request
        self.response = response


class InternalNodeError(TestToolsException):
    pass


class MissingBlockLogArtifactsError(TestToolsException):
    pass


class MissingPathToExecutable(TestToolsException):
    pass


class NameAlreadyInUse(TestToolsException):
    pass


class NodeIsNotRunning(TestToolsException):
    pass


class NotSupported(TestToolsException):
    pass


class ParseError(TestToolsException):
    pass


class ConfigError(TestToolsException):
    pass


class BlockWaitTimeoutError(TestToolsException):
    """Raised when the maximum amount of time to wait for a block on a blockchain is reached."""
