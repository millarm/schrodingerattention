# Audited compute-ledger reconciliation

`execution/compute_ledger.jsonl` is retained intact, including its historical
non-monotonic `cumulative_seconds` fields. The canonical total is the sum of
`charged_seconds`, not those stale display fields.

| Component | Seconds |
| --- | ---: |
| Measured/previously charged records retained in JSONL | 50.3793099170 |
| Conservative historical overhead allowance | 129.6206900830 |
| Canonical pre-comparison preparation charge | 180.0000000000 |

The allowance explicitly includes Sol revision-2 review time (3.1 seconds),
failed-command startup, and unmetered test/setup overhead. It is conservative
accounting, not a claim of exact measured elapsed time. The appended JSONL
allowance record establishes the monotonic audited total while preserving all
original records.
