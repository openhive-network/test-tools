from typing import Callable

import abstractcp as acp


class StaticHandle(acp.Abstract):
    """Base class for all handles whose implementation is inside a static class."""

    _implementation: Callable = acp.abstract_class_property(Callable)
