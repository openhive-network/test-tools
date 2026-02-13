# CLAUDE.md

> **⚠️ ARCHIVED REPOSITORY** — This repo is archived and read-only.
> All development has moved to [hive/wax](https://gitlab.syncad.com/hive/wax)
> under `python/test_tools/`.
>
> **Do not propose changes to this repository.**
> If asked to work on test-tools, direct all work to
> https://gitlab.syncad.com/hive/wax/-/tree/develop/python/test_tools

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

test-tools is a Python library for testing Hive blockchain software. It provides abstractions for creating testnets, managing hived nodes, executing wallet operations, and running blockchain-related tests.

**Repository (archived)**: https://gitlab.syncad.com/hive/test-tools
**Active development**: https://gitlab.syncad.com/hive/wax (monorepo — `python/test_tools/`)

## Development Commands

### Setup
```bash
# Install with dev dependencies (recommended)
python3.12 -m venv venv/
source venv/bin/activate
pip install poetry
poetry install

# Initialize git hooks
pre-commit install
```

### Testing
```bash
# Run unit tests (no hived executables required)
pytest -n auto -m "not requires_hived_executables" tests/unit_tests

# Run hived handle tests (requires HIVED_HTTP_ENDPOINT or local hived)
cd tests/hived_handle_tests
pytest -n auto --durations 0

# Run all functional tests (requires HIVE_BUILD_ROOT_PATH)
pytest -n auto tests/functional_tests

# Run single test
pytest tests/functional_tests/network_tests/test_network_startup.py::test_network_startup
```

### Code Quality
```bash
# Format code
ruff format .

# Lint with ruff
ruff check --fix .

# Type check
mypy package/test_tools/ tests/

# Run pre-commit hooks manually
pre-commit run --all-files
```

### Environment Variables
- `HIVE_BUILD_ROOT_PATH`: Path to hive build directory containing executables (hived, cli_wallet, etc.)
- `TEST_TOOLS_NODE_DEFAULT_WAIT_FOR_LIVE_TIMEOUT`: Default timeout for node startup (default: 30s)

## Architecture

### Core Components

**Node Hierarchy** (from base to specialized):
- `RawNode` - Unconfigured node with default settings (54GB shared file, minimal APIs)
- Base test nodes - Pre-configured for testing (128MB shared file, all APIs enabled):
  - `InitNode` - Network bootstrap, block production, API calls
  - `WitnessNode` - Block signing for registered witnesses
  - `ApiNode` - API calls (all except account_history)
  - `FullApiNode` - All APIs including account_history
- `RemoteNode` - Connect to existing remote hived instance

**Network Management**:
- `Network` - Container for nodes, handles p2p connections
- Nodes in same network auto-connect via p2p
- Multiple networks can be connected with `network1.connect_with(network2)`

**Wallet Integration**:
- `Wallet` (beekeeper-based, current) - Attach to any node for signing operations
- `OldWallet` (cli_wallet-based, legacy)

**State Management**:
- `Snapshot` - Save/restore node state to avoid replaying blockchain
- `BlockLog` - Manage block_log files for replay/testing

### Scope System

Critical architectural concept: TestTools uses a **scope-based resource management system** similar to pytest fixtures.

**Key Classes**:
- `Scope` - Context manager for resource lifecycle
- `ScopedObject` - Base class for managed resources (nodes, wallets, networks)
- `context` - Global scope manager (accessed via `tt.context`)

**Behavior**:
- Resources (nodes/wallets) register with current scope on creation
- Resources are cleaned up automatically when scope exits (in reverse creation order)
- Cleanup behavior controlled by `CleanupPolicy` (remove all files, keep logs, keep everything)
- Default pytest integration: scope created per test function

**Example**:
```python
# Nodes/wallets created in test are auto-cleaned when test exits
def test_example():
    node = tt.InitNode()  # Registers with current scope
    node.run()
    # node.exit_from_scope() called automatically at test end
```

### API Structure

**Node APIs** - Located in `package/test_tools/__private/hived/api/`:
- Each API has sync version (`sync_api.py`) and async wrapper
- Organized by API type: `block_api`, `database_api`, `condenser_api`, `wallet_bridge_api`, etc.
- Accessed via `node.api.<api_name>.<method>()` (e.g., `node.api.database.list_witnesses()`)
- API collection built at runtime from `api_collection.py`

**Handle Pattern**:
- User-facing classes are "handles" in `user_handles/handles/`
- Handles wrap internal implementation classes
- Implementation retrieved dynamically via `get_implementation()`
- Allows pytest mode vs. script mode behavior differences

### Key Modules

- `package/test_tools/__private/`:
  - `node.py` - Core Node class (runnable local nodes)
  - `network.py` - Network management and p2p connections
  - `account.py` - Key generation (public/private keys from account names)
  - `snapshot.py` - State save/restore functionality
  - `block_log.py` - Block log file management
  - `process/` - Node process management, config, arguments
  - `scope/` - Resource lifecycle management
  - `hived/api/` - All hived API wrappers

## Testing Patterns

### Basic Network Setup
```python
import test_tools as tt

# Single node
node = tt.InitNode()
node.run()
wallet = tt.Wallet(attach_to=node)

# Multi-node network
network = tt.Network()
init_node = tt.InitNode(network=network)
witness_node = tt.WitnessNode(witnesses=['alice', 'bob'], network=network)
api_node = tt.ApiNode(network=network)
network.run()
```

### Account Creation
```python
# Generate keys deterministically from account name
account = tt.Account('john')
print(account.private_key)  # 5K...
print(account.public_key)   # TST8...

# Bulk creation (optimized)
accounts = tt.Account.create_multiple(100_000, 'user')
```

### Snapshot Usage
```python
# Create snapshot from running node
snapshot = node.dump_snapshot()

# Start another node from snapshot
node2 = tt.ApiNode()
node2.run(load_snapshot_from=snapshot)
```

### Node Configuration
```python
node = tt.RawNode()
node.config.enable_stale_production = True
node.config.required_participation = 0
node.config.plugin.extend(['p2p', 'witness'])
node.run()
```

## Common Patterns

### Waiting for Conditions
- `node.wait_for_block_with_number(N)` - Wait until block N is produced
- `node.wait_number_of_blocks(N)` - Wait for N blocks from current head

### Batch Wallet Operations
```python
# Send multiple operations in single transaction
with wallet.in_single_transaction() as tx:
    wallet.api.create_account('initminer', 'alice', '{}')
    wallet.api.transfer('initminer', 'alice', tt.Asset.test(100), 'memo')

response = tx.get_response()
```

## Code Style

- **Formatting**: ruff format (line-length: 120)
- **Linting**: ruff with extensive ruleset (see pyproject.toml)
- **Type checking**: mypy in strict mode
- **Required import**: All files must have `from __future__ import annotations` (enforced by ruff)
- **Docstrings**: Required for public APIs (except in tests/)

## CI Pipeline

Pipeline runs on GitLab (`.gitlab-ci.yml`):

**Static Analysis Stage**:
- pre_commit_checks
- lint_code_with_ruff
- formatting_with_ruff_check
- type_check_with_mypy

**Tests Stage**:
- `unit_tests_launch` - Fast tests without hived (`-m "not requires_hived_executables"`)
- `test_hived_handle` - Integration tests with real hived endpoint

## Flaky Test Debugging

When tests are flaky (especially network/timing-related):
1. Check if test uses proper synchronization (`wait_for_block_with_number`, not sleep)
2. Verify cleanup between test runs (scope system should handle this)
3. Check for race conditions in node startup (use `node.wait_for_live()`)
4. For network tests, ensure p2p connections are fully established before assertions

## Dependencies

- **wax** (hiveio-wax): Blockchain transaction building, serialization
- **beekeepy**: Wallet/key management (beekeeper integration)
- **schemas**: API response schemas
- **abstractcp**: Process management
- **loguru**: Logging

Private GitLab package sources configured in pyproject.toml for Hive ecosystem packages.

## Dependency Management (Poetry)

The lockfile pins exact versions of all dependencies (direct and transitive). This prevents dependency mismatches between environments - if the lockfile is wrong or missing, builds may fail or behave differently. These rules keep it synchronized with pyproject.toml.

- **Dependency versions are specified in `pyproject.toml` and locked in `poetry.lock`**
- **Always use `poetry lock`** (without additional flags like `--regenerate`)
- **Always run `poetry lock` after changing `pyproject.toml`**
- **The `poetry.lock` file must be in the repository** - never add it to `.gitignore`
- **Never delete `poetry.lock`** - it ensures reproducible builds
- **Never edit `poetry.lock` manually** - always use poetry commands
- **Don't upgrade dependencies on your own** - only upgrade when explicitly requested
