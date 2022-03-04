from typing import Optional

import pytest

from test_tools import clean_up_policy
from test_tools.constants import CleanUpPolicy, NodeCleanUpPolicy


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


def check_if_node_files_are_removed(world,
                                    policy: Optional[CleanUpPolicy] = None,
                                    *,
                                    remove_important_files: bool,
                                    remove_unneeded_files: bool):
    init_node = world.create_init_node()
    init_node.run()

    if policy is not None:
        corresponding_clean_up_policy = {
            CleanUpPolicy.REMOVE_EVERYTHING: NodeCleanUpPolicy.REMOVE_EVERYTHING,
            CleanUpPolicy.REMOVE_ONLY_UNNEEDED_FILES: NodeCleanUpPolicy.REMOVE_ONLY_UNNEEDED_FILES,
            CleanUpPolicy.DO_NOT_REMOVE_FILES: NodeCleanUpPolicy.DO_NOT_REMOVE_FILES,
        }

        init_node.set_clean_up_policy(corresponding_clean_up_policy[policy])

    world.close()

    assert important_files_are_removed(init_node) == remove_important_files
    assert unneeded_files_are_removed(init_node) == remove_unneeded_files


def check_if_everyone_files_are_removed(world,
                                        policy: Optional[CleanUpPolicy] = None,
                                        *,
                                        remove_important_files: bool,
                                        remove_unneeded_files: bool):
    # Create some nodes outside of a network
    init_node = world.create_init_node()
    api_node = world.create_api_node()

    # Create some nodes within a network
    network = world.create_network()
    network.create_init_node()
    network.create_api_node()

    init_node.run()
    api_node.run(wait_for_live=False)
    network.run()

    if policy is not None:
        clean_up_policy.set_default(policy)

    world.close()

    assert all(important_files_are_removed(node) == remove_important_files for node in network.nodes())
    assert all(unneeded_files_are_removed(node) == remove_unneeded_files for node in network.nodes())

    for network in world.networks():
        assert all(important_files_are_removed(node) == remove_important_files for node in network.nodes())
        assert all(unneeded_files_are_removed(node) == remove_unneeded_files for node in network.nodes())


run_for_all_cases = pytest.mark.parametrize(
    'check_if_files_are_removed',
    [
        check_if_node_files_are_removed,
        check_if_everyone_files_are_removed,
    ]
)


@run_for_all_cases
def test_default_policy(world, check_if_files_are_removed):
    check_if_files_are_removed(
        world,
        remove_important_files=False,
        remove_unneeded_files=True
    )


@run_for_all_cases
def test_do_not_remove_files_clean_up_policy(world, check_if_files_are_removed):
    check_if_files_are_removed(
        world,
        CleanUpPolicy.DO_NOT_REMOVE_FILES,
        remove_important_files=False,
        remove_unneeded_files=False
    )


@run_for_all_cases
def test_remove_only_unneeded_files_clean_up_policy(world, check_if_files_are_removed):
    check_if_files_are_removed(
        world,
        CleanUpPolicy.REMOVE_ONLY_UNNEEDED_FILES,
        remove_important_files=False,
        remove_unneeded_files=True
    )


@run_for_all_cases
def test_remove_everything_clean_up_policy(world, check_if_files_are_removed):
    check_if_files_are_removed(
        world,
        CleanUpPolicy.REMOVE_EVERYTHING,
        remove_important_files=True,
        remove_unneeded_files=True
    )
