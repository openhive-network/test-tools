# Based on https://stackoverflow.com/a/21919644
from __future__ import annotations

import signal
from collections.abc import Callable
from types import FrameType
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import TracebackType

OldHandlerType = Callable[[int, FrameType | None], Any]


class DisabledKeyboardInterrupt:
    """
    Context manager to temporarily disable keyboard interrupt (SIGINT signal).

    Usage example with explanation:
    with DisabledKeyboardInterrupt():
        do_something()  # [1]
    # [2]

    If keyboard interrupt will be raised during [1], it will be ignored and reraised
    after exiting from covered scope [2].
    """

    def __init__(self) -> None:
        self.old_handler: OldHandlerType | None = None
        self.signal_received: tuple[int, FrameType | None] | None = None

    def __enter__(self) -> None:
        self.old_handler = signal.signal(signal.SIGINT, self.handler)  # type: ignore[assignment]

    def handler(self, sig: int, frame: FrameType | None) -> None:
        self.signal_received = (sig, frame)

    def __exit__(self, _: type[BaseException] | None, __: BaseException | None, ___: TracebackType | None) -> None:
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received is not None and self.old_handler is not None:
            self.old_handler(*self.signal_received)
