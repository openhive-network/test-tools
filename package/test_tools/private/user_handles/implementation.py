class Implementation:
    """Base class for all objects pointed by handles. Contains handle by which is pointed."""

    def __init__(self, *args, handle, **kwargs):
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self.__handle = handle  # pylint: disable=unused-private-member; It is used in `user_handles.get_handle`.
