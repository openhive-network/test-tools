from abc import ABC
from typing import Any, Callable, NoReturn, Optional

from test_tools.__private.user_handles.handle import Handle
from test_tools.__private.user_handles.implementation import Implementation


class InsideStaticHandle(Handle, ABC):
    """
    Base class which should be used in classes derived from `StaticHandle` class, when some of their methods are
    returning implementation object of its internal class. Like `Asset.from_` method.
    This class is used to disable the `__init__` method when the `__implementation` keyword argument is passed.

    Inspired by: https://stackoverflow.com/a/45268946
    """

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        """
        This method is called before __init__.
        Used to instantiate a handle object when an implementation has been already created and needs to be assigned.

        Objects of this class hold a reference to its implementation and are referenced by it.
        All this is done by passing the `__implementation` keyword argument when creating the object
        like `child = Child(__implementation=existing_object_reference)`.
        In this way the `__implementation` attribute is set with skipping the `__init__` method
        (which creates implementation object by itself, and we don't want that).
        """
        instance = object.__new__(cls)

        implementation = kwargs.pop("__implementation", None)
        if not implementation:
            return instance

        cls.__assert_implementation_type(implementation)
        implementation: Implementation

        cls.__init__ = cls.__new_init(cls.__init__)
        instance._Handle__implementation = implementation  # pylint: disable=invalid-name
        implementation._Implementation__handle = instance
        return instance

    @classmethod
    def __assert_implementation_type(cls, implementation: Any) -> Optional[NoReturn]:
        if not isinstance(implementation, Implementation):
            raise TypeError(
                f"Object `{implementation!r}` of type `{type(implementation)}` does not inherit from `{Implementation}`"
            )

    @classmethod
    def __new_init(cls, init: Callable) -> Callable:
        def __disabled_init(*args, **kwargs) -> None:  # pylint: disable=unused-argument
            cls.__init__ = init

        return __disabled_init
