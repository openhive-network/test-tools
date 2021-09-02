from pathlib import Path

from test_tools.private.scope.scope_singleton import context, current_scope
from test_tools.private.scope.scoped_current_directory import ScopedCurrentDirectory


def test_getting_value_set_in_same_scope():
    with current_scope.create_new_scope('test-scope'):
        ScopedCurrentDirectory('scoped-directory')
        assert context.get_current_directory() == Path('scoped-directory')


def test_value_is_popped_after_exit_from_scope():
    directory_before = current_scope.context.get_current_directory()

    with current_scope.create_new_scope('test-scope'):
        ScopedCurrentDirectory('scoped-directory')

    assert context.get_current_directory() == directory_before