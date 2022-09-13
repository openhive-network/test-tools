## Installation

To use TestTools you have to install them and specify location of hive executables. Whole process is described below.

### 1. Install package

<details>
<summary>Full installation (recommended for testers and developers)</summary>

#### A. Select one of following methods:

- <details>
  <summary>Install with PyCharm</summary>

  Create virtual environment in the `~/hive/tests/` directory using PyCharm project-specific isolated virtual
  environment ([read more](https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html)).

  With opened project, select tab `Python Packages` at the bottom of window, click `Add Package` and then `From Disk`.

  ![Installation instructions](./documentation/installation_in_pycharm0.png)

  Select TestTools directory, mark `Install as editable` option, specify extra `[dev]` for additional dependencies and
  click OK.

  ![Installation instructions](./documentation/installation_in_pycharm_dev.png)
  </details>

- <details>
  <summary>Install in virtual environment manually</summary>

  ```bash
  cd ~/hive/tests/          # Go to tests/ directory of hive repository
  python3.8 -m venv venv/   # Create virtual environment in venv/ directory
  source venv/bin/activate  # Activate it
  pip install poetry        # Install poetry
  cd test_tools/            # Go to TestTools directory
  poetry install            # Install TestTools with dev-dependencies
  ```

  To deactivate virtual environment run:
  ```bash
  deactivate
  ```
  </details>

- <details>
  <summary>Install in your operating system scope (not recommended)</summary>

  Enter following command in terminal:
  ```bash
  python3.8 -m pip install poetry  # Install poetry
  cd ~/hive/tests/test_tools/      # Go to TestTools directory
  python3.8 -m poetry install      # Install TestTools with dev-dependencies
  ```
  </details>

#### B. Initialize git hooks

Installation will include additional tools for code quality checking and `pre-commit` framework for git hooks managing.

You can initialize it with the following line:

```bash
source ~/hive/tests/venv/bin/activate  # Active the previously created virtual environment
cd ~/hive/tests/test_tools/            # Go to TestTools directory
pre-commit install                     # Install the pre-commit script
```

:information_source: **Hint**: If for some reason you want to bypass the pre-commit hooks, use the `--no-verify` flag.
This will skip all analysis, so you will be able to trigger CI/CD pipeline (e.g. to run tests on WIP code) without the
need to ensure the production quality of the code.

```bash
git commit --no-verify
```

#### C. [Optionally] Install script which will automatically activate virtual environment

:information_source: **Hint**: When using an IDE-integrated terminal, you shouldn't have the problems described in this
section, as most IDEs support automatic activation of venv.

This tool can be useful if you have encountered one of the following errors:
<details>
<summary>Click to expand error messages</summary>

##### pre-commit is not installed

```bash
`pre-commit` not found.  Did you forget to activate your virtualenv?
```

##### ModuleNotFoundError: No module named xyz

```bash
$ git commit
check for added large files..............................................Passed
check for merge conflicts................................................Passed
check yaml...........................................(no files to check)Skipped
check json...........................................(no files to check)Skipped
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
fix double quoted strings............................(no files to check)Skipped
pretty format json...................................(no files to check)Skipped
lint all sources with pylint.............................................Failed
- hook id: pylint-sources
- exit code: 1

Traceback (most recent call last):
  File "/home/dev/.local/bin/pylint", line 5, in <module>
    from pylint import run_pylint
ModuleNotFoundError: No module named 'pylint'

lint user handles documentation with pylint..............................Failed
- hook id: pylint-handles
- exit code: 1

Traceback (most recent call last):
  File "/home/dev/.local/bin/pylint", line 5, in <module>
    from pylint import run_pylint
ModuleNotFoundError: No module named 'pylint'
```

</details>

The errors above were caused by omitted activation of venv. The `pre-commit` hooks for their checks require additional
dependencies (e.g. `pylint`) installed in a virtual
environment. It is easy to forget to activate it manually every time. This script activates the virtual environment
automatically every time you enter the directory containing it.

Follow the instructions below:

1. Get the script:

    ```bash
    curl -s -o ~/.virtualenv-autodetect.sh https://raw.githubusercontent.com/egilewski/virtualenv-autodetect/29c814f4e5b6f32a7b1952727cf112a13f34327d/virtualenv-autodetect.sh
    ```

2. Add the following line to the end of your `.bashrc`, `.bash-profile` or `.zshenv` file:

    ```bash
    source ~/.virtualenv-autodetect.sh
    ```

3. Restart your terminal.

</details>

<details>
<summary>Lightweight installation (if you want only to run tests, without contributing)</summary>

#### Select one of following methods:

- <details>
  <summary>Install with PyCharm</summary>

  With opened project, select tab `Python Packages` at the bottom of window, click `Add Package` and then `From Disk`.

  ![Installation instructions](./documentation/installation_in_pycharm0.png)

  Select TestTools directory, mark `Install as editable` option and click OK.

  ![Installation instructions](./documentation/installation_in_pycharm1.png)
  </details>

- <details>
  <summary>Install in virtual environment manually</summary>

  ```bash
  cd ~/hive/tests/test_tools/             # Go to repository root directory
  python3.8 -m venv venv/                 # Create virtual environment in venv/ directory
  source venv/bin/activate                # Activate it
  pip install -e ~/hive/tests/test_tools  # Install TestTools
  ```

  To deactivate virtual environment run:
  ```bash
  deactivate
  ```
  </details>

- <details>
  <summary>Install in your operating system scope (not recommended)</summary>

  Enter following command in terminal:
  ```bash
  python3.8 -m pip install -e ~/hive/tests/test_tools/  # Install TestTools
  ```
  </details>

</details>

### 2. Define path to hive executables

Define environment variable `HIVE_BUILD_ROOT_PATH` with path to hive build directory (containing _hived_, _cli_wallet_
and other executables). Add entry `HIVE_BUILD_ROOT_PATH="/home/dev/hive/build"` to `/etc/environment` and restart
computer.

<details>
<summary>If you don't want to modify content of your `/etc/environment` file...</summary>

...then you have to set this variable locally before every run of script, which uses TestTools. It can be done as in
examples below:

```bash
HIVE_BUILD_ROOT_PATH="/home/dev/hive/build" pytest
HIVE_BUILD_ROOT_PATH="/home/dev/hive/build" python3 your_script.py
```

</details>

## Tutorials

- [Snapshot](documentation/tutorials/snapshot.md) -- What is snapshot? How to create and use it?
- [Replay](documentation/tutorials/replay.md) -- What is replay? How to do it?

## Features

### Easy testnet creation

You can run testnet with node configured for blocks production and attached wallet with such simple script:

```python
import test_tools as tt

if __name__ == '__main__':
    node = tt.InitNode()
    node.run()

    wallet = Wallet(attach_to=node)
```

### Node and wallet APIs

Node and wallet has `api` member which allows for communication with them. You can communicate with node and wallet with
following syntax:

```python
# Example node calls
node.api.condenser.get_key_references(['TST5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW'])
node.api.database.list_witnesses(start=None, limit=100, order='by_name')

# Example wallet calls
wallet.api.create_account('initminer', 'john', '{}')
wallet.api.get_account('john')
```

Use your IDE's code completion to get hints for wallet api calls like below. IDE should help you to write method names,
but also parameters.

![Wallet api code completion example](./documentation/wallet_code_completion.png)

### Node types

Creation and initialization of nodes are simplified by predefined node types. Node types hide a lot of configuration
stage and make tests more readable, because node purpose is directly expressed in
code ([read more](documentation/node_types.md)). Following node types are supported:

- init node,
- witness node,
- api node,
- raw node.

This is how network consisting of init, witness and api node can be defined:

```python
network = tt.Network()
init_node = tt.InitNode(network=network)
witness_node = tt.WitnessNode(witnesses=[f'w{i}' for i in range(10)], network=network)
api_node = tt.ApiNode(network=network)
```

### Node configuration

Node has `config` member which allow for editing _hived_ _config.ini_ file. You can configure node in following way:

```python
node.config.enable_stale_production = True
node.config.required_participation = 0
node.config.plugin.extend(['p2p', 'witness'])
```

> :warning: Type support is not completed yet. Not all config entries types are set correctly. At the moment most of
> them are treated as strings. So you have to write like:
> ```python
> # Note that all are strings
> node.config.market_history_bucket_size = '[15,60,300,3600,86400]'
> node.config.webserver_thread_pool_size = '32'
> node.config.witness_skip_enforce_bandwidth = '1'
> ```

Provides support for Python types. You can write:

```python
if node.config.enable_stale_production and node.config.required_participation < 20:
    ...
```

because type of `node.config.enable_stale_production` is `bool` and type of `node.config.required_participation`
is `int`.

### Select which executables should library use

You can select them in python script, via command line arguments, environment variables or by executables
installation ([read more](documentation/paths_to_executables.md)).

### Configure which files should be removed after test

During tests nodes generates a lot of files. In most cases some of these files are unneeded and are automatically
removed by library. You can configure this behavior for your needs ([read more](documentation/clean_up_policies.md)).

### Generate public and private keys

Some tests requires multiple accounts creation. To perform operations on them keys are required. TestTools provides
support for key generation with `Account` class. You only need to provide account name. Generated account contains
member variables `private_key` and `public_key`, which can be used in tests. Optionally you can specify `secret`
parameter, which affects generated keys.

```python
# Simple account creation example
account = tt.Account('John')
print(account.private_key)  # Prints: 5KSJQHSBh4vxZVaY2fi3vbhDbkkg7C74pE4S3bigEQyct2RqMDf
print(account.public_key)  # Prints: TST8FukVPod6riKr2mg94hhDanCzCYvivJtPdpcUVnEChaJ5N9QbC

# Inline usage example
print(tt.Account('initminer').private_key)  # Prints: 5JNHfZYKGaomSFvd4NUdQ9qMcEAC43kujbfjueTHpVapX1Kzq2n
```

If you need to create many accounts, (e.g. more than 10 000), it might be slow using method described above. For
multiple accounts creation use method showed below:

```python
tt.Account.create_multiple(100_000, 'example')  # Optimized version of: [Account('example-{i}') for i in range(100_000)]
```

### Send multiple operations in single wallet transaction

TestTools provides support for sending single transaction containing multiple operations. It is helpful for optimizing
scripts which send multiple transactions and wait 3 seconds for every transaction confirmation. When sending these
operations in one transaction, you wait for only one confirmation, so your script executes much faster. You can do it
with following syntax:

```python
with wallet.in_single_transaction():
    wallet.api.create_account('initminer', account, '{}')
    wallet.api.transfer('initminer', account, amount, 'memo')
```

In above example operations `create_account` and `transfer` are sent in single transaction during exiting from "with"
statement.

Implementation is very flexible and allows for using python control statements (ifs, loops), functions which sends
wallet api calls and so on. See example below showing for-loop use case during transaction preparation.

```python
accounts_and_balances = {
    'first': tt.Asset.Test(100),
    'second': tt.Asset.Test(200),
    'third': tt.Asset.Test(300),
}

with wallet.in_single_transaction():
    for account, amount in accounts_and_balances.items():
        wallet.api.create_account('initminer', account, '{}')
        wallet.api.transfer('initminer', account, amount, 'memo')
```

If you want to read response, you can name a returned context manager and call its `get_response` method after
exiting `with` context, like this:

```python
with wallet.in_single_transaction() as transaction:
    ...

response = transaction.get_response()
```
