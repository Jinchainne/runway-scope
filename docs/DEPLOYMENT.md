# Deployment

## Preflight

```bash
python -m pytest tests/test_contract_behavior.py -q
python -m py_compile contracts/runway_scope.py
python -m genvm_linter.cli check contracts/runway_scope.py
```

Deploy `contracts/runway_scope.py` without constructor arguments to `testnet-bradbury`. Require an accepted validator receipt, retrieve the public schema, and call `get_policy` plus `list_window_ids` before publishing the release manifest.

## Accepted release

- Contract: `0x0b45bb9a2d542C46FD4a615E32AB3107507f0DEc`
- Transaction: `0xc8299a66c4d358182c9e831d8d949900aa29b7f26c34ffc51c694a0d6a70fdc7`
- Source SHA-256: `89b8460bbeef6b882c22db40175a2961bda17e01d32a634640a37573cd8c906d`
