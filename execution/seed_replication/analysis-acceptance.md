# Analysis acceptance

Astra accepts corrected analysis only after Sol's exact-version PASS in
`reviews/analysis-review-01.md`. Source SHA-256:
`cbf8d19b31b429a91e48ad3dba2e2079ab0245d9811c92ad9e0e851bc8ffa3dd`.
Tests SHA-256: `e86471ce240f6548cc6b438880ba9db2821dc2e2c3f2b6b4e7625da877e9e76e`.
No scientific changes; all four fresh pairs remain fixed.

Authorized per-seed command, executed once only after both corresponding training
owners complete and no other compute process is running:

```
.venv/bin/python -m execution.seed_replication.analyze --seed SEED
```

SEED is respectively 1702, 1703, 1704, 1705. Each creates the unique original-root
`replication-SEED-analysis` owner with the frozen 120-second alarm plus four-second
allowances, charged D. Preserve full session/exit and raw outputs. No retry or
scientific adaptation is implied by this acceptance.
