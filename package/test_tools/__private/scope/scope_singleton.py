from test_tools.__private.scope.context_internal_interface import ContextInternalHandle
from test_tools.__private.scope.scopes_stack import ScopesStack
from test_tools.__private.utilities.tests_type import is_automatic_test

current_scope = ScopesStack()
context = ContextInternalHandle(current_scope)

if not is_automatic_test():
    # Break import-cycle; ScopedObject depends on current_scope, which is already defined
    # pylint: disable=cyclic-import
    from test_tools.__private.scope.scoped_current_directory import ScopedCurrentDirectory

    ScopedCurrentDirectory(current_scope.context.get_current_directory())

    root_logger = current_scope.context.get_logger()
    root_logger.log_to_stdout()
    root_logger.log_to_file(context.get_current_directory() / "last_run.log")
