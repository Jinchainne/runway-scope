# Deployment

## Preflight

```bash
python -m pytest tests/test_contract_behavior.py -q
python -m py_compile contracts/runway_scope.py
python -m genvm_linter.cli check contracts/runway_scope.py
```

Deploy `contracts/runway_scope.py` without constructor arguments to `testnet-bradbury`. Require an accepted validator receipt, retrieve the public schema, and call `get_policy` plus `list_window_ids` before publishing the release manifest.
