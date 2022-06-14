Purpose of configuration:
- Replace environmental variables based configuration with file based

Use https://www.dynaconf.com/

Actual use cases:
- Paths to executables
  - On CI, are defined in .test_tools_based
  - On users' setups are defined in `/etc/environment` or passed to process during run
- In `message_format_tests` `SIGN_TRANSACTION_PATH`
  - On CI is defined in dedicated job
  - On users' setups must be defined manually
- Node's default wait for live timeout
  - On CI is increased in .test_tools_based
  - *Nothing to do* -- On users' setups is unchanged
- Schemas validation
  - On CI is set in `message_format_tests`
  - On users' setups must be defined manually


Future use cases:
- Configuration accessible for testers with `tt.config['TIME_OF_SOMETHING']` and configurable via local
  `test_tools_config.toml` files.
  ```toml
  [custom]
  TIME_OF_SOMETHING = 5
  ```


class Config:
  class Node:
    def __init():
      self.TIME_OF_SOMETHING: Annotated[int, 'in milliseconds'] = 20

  def __init__():
    self.node = Node()


int(tt.config['TIME_OF_SOMETHING'])

Solution:
On CI config is edited with `python -m test_tools.config.edit "HIVED_PATH" "$CI_PATH_ROOT/..."`
Or with entry points something like this: `test_tools configure HIVED_PATH $CI_PATH_ROOT/...`

```toml
[common]
BUILD_ROOT_PATH = "..."
HIVED_PATH = "this.common.BUILD_ROOT_PATH + ..."
```

- Should be supported config in home dir

- `test_tools_config.toml` -- ignored by git
- `test_tools_default_config.toml` -- tracked by git


- Config structure (below overrides above)
  - Hardcoded default inside TestTools
  - User home directory
  - Hierarchical configs within current package
    - test_tools_default_config.toml
    - test_tools_config.toml
