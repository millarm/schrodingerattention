# V3 Block 1 final bounded draw-prefix correction

Only `PoolResult.draw_prefix` changed: `pool_family` now records at most the
first 16 eight-index rows (128 indices) while continuing all later trial draws,
rejections, RNG consumption, and pool outcomes exactly as before.

`test_pool_draw_audit_prefix_is_capped_without_changing_trials` injects 17
overlap rows and asserts all 17 trials/rejections occur, while the retained audit
is exactly the first 16 rows/128 indices. The prior four-trial branch evidence
remains covered by `test_pool_branch_order_and_independent_pcg64_draw_prefix`.

Command:

```
.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_data.py
```

Exit 0; 8 passed in 0.78s; full tool wall 0.930767833s, recorded as ledger UUID
`c58dcb6c-8a32-4ae7-9869-d2d5f9a08fb7`.

- Source SHA-256: `599c988fb3bbcff9ced5a7c7dadafc905641f8810c7e342fab56440c63253d09`
- Test SHA-256: `c221bf783bb99bad8639e158d09a962c8259ca98a5110ae0374b80001055e416`

No other code, production inventory, Block 2, or runner behavior changed.
