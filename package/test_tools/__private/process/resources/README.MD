## How to regenerate options (Argument and Config)

### 1. Generate dumps.json

```bash
hived --dump-options > /path/to/dumps.json
```

### 2. Run following script

```bash
python3 -m beekeepy._utilities.options_generator.update_options \
    --options-file /path/to/dumps.json \
    --source-dir test-tools/package/test_tools/__private/process/resources \
    --dest-dir test-tools/package/test_tools/__private/process \
    --prefix node
```
