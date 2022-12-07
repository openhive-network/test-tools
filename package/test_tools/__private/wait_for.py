import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from threading import Event


def wait_for_event(
    event: "Event",
    deadline: Optional[float] = None,
    exception_message: str = "The event didn't occur within given time frame",
) -> None:
    """
    Blocks current thread execution until `event` is set. Optionally raises `exception`, when
    `deadline` is reached.

    :param event: Awaited event. When event is set functions stops blocking.
    :param deadline: Time point before which event must occur. Can be counted from the formula:
                     deadline = now + timeout
    :param exception_message: When deadline is reached, TimeoutError with message specified by
                              this parameter will be raised.
    """
    timeout = deadline - time.time()
    if not event.wait(timeout):
        raise TimeoutError(exception_message)
