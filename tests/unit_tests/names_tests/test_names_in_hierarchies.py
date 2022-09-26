from test_tools.__private.names import Names


def test_if_child_registers_new_name_without_collision_with_parent():
    parent = Names()
    parent.register_numbered_name("Numbered")

    child = Names(parent=parent)
    child.register_numbered_name("Numbered")

    assert child.get_names_in_use() == {"Numbered0", "Numbered1"}


def test_name_registration_in_parent_when_child_already_exists():
    parent = Names()
    child = Names(parent=parent)

    parent.register_numbered_name("Numbered")
    child.register_numbered_name("Numbered")

    assert parent.get_names_in_use() == {"Numbered0"}
    assert child.get_names_in_use() == {"Numbered0", "Numbered1"}  # Child knows about name registered in parent


def test_if_names_registered_in_first_child_do_not_affect_second_child():
    parent = Names()

    first_child = Names(parent=parent)
    first_child.register_numbered_name("Numbered")

    second_child = Names(parent=parent)
    second_child.register_numbered_name("Numbered")

    assert second_child.get_names_in_use() == {"Numbered0"}
