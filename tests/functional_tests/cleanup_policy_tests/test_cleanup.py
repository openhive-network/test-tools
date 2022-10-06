from typing import Optional

import pytest

import test_tools as tt
from test_tools.__private.scope import current_scope


def important_files_are_removed(node):
    paths_of_important_files = [
        '.',
        'config.ini',
        'stderr.txt',
    ]

    return all(not node.directory.joinpath(path).exists() for path in paths_of_important_files)


def unneeded_files_are_removed(node):
    paths_of_unneeded_files = [
        'blockchain/block_log',
    ]

    return all(not node.directory.joinpath(path).exists() for path in paths_of_unneeded_files)


def check_if_node_files_are_removed(
    policy: Optional[tt.constants.CleanupPolicy] = None, *, remove_important_files: bool, remove_unneeded_files: bool
):
    with current_scope.create_new_scope('test-scope'):
        init_node = tt.InitNode()
        init_node.run()

        if policy is not None:
            init_node.set_cleanup_policy(policy)

    assert important_files_are_removed(init_node) == remove_important_files
    assert unneeded_files_are_removed(init_node) == remove_unneeded_files


def check_if_everyone_files_are_removed(
    policy: Optional[tt.constants.CleanupPolicy] = None, *, remove_important_files: bool, remove_unneeded_files: bool
):
    with current_scope.create_new_scope('test-scope'):
        # Create some nodes outside of a network
        init_node = tt.InitNode()
        api_node = tt.ApiNode()

        # Create some nodes within a network
        network = tt.Network()
        tt.InitNode(network=network)
        tt.ApiNode(network=network)

        init_node.run()
        api_node.run(wait_for_live=False)
        network.run()

        if policy is not None:
            tt.cleanup_policy.set_default(policy)

    for node in [init_node, api_node]:
        assert important_files_are_removed(node) == remove_important_files
        assert unneeded_files_are_removed(node) == remove_unneeded_files

    assert all(important_files_are_removed(node) == remove_important_files for node in network.nodes)
    assert all(unneeded_files_are_removed(node) == remove_unneeded_files for node in network.nodes)


run_for_all_cases = pytest.mark.parametrize(
    'check_if_files_are_removed',
    [
        check_if_node_files_are_removed,
        check_if_everyone_files_are_removed,
    ],
)


@run_for_all_cases
def test_default_policy(check_if_files_are_removed):
    check_if_files_are_removed(remove_important_files=False, remove_unneeded_files=True)


@run_for_all_cases
def test_do_not_remove_files_cleanup_policy(check_if_files_are_removed):
    check_if_files_are_removed(
        tt.constants.CleanupPolicy.DO_NOT_REMOVE_FILES, remove_important_files=False, remove_unneeded_files=False
    )


@run_for_all_cases
def test_remove_only_unneeded_files_cleanup_policy(check_if_files_are_removed):
    check_if_files_are_removed(
        tt.constants.CleanupPolicy.REMOVE_ONLY_UNNEEDED_FILES, remove_important_files=False, remove_unneeded_files=True
    )


@run_for_all_cases
def test_remove_everything_cleanup_policy(check_if_files_are_removed):
    check_if_files_are_removed(
        tt.constants.CleanupPolicy.REMOVE_EVERYTHING, remove_important_files=True, remove_unneeded_files=True
    )
