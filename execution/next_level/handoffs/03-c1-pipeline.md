# Stage 0 C1 pipeline correction — partial handoff

This is C1 only, not Stage-0 readiness: Attempt/safety remediation remains
explicitly reserved for C2 and no full inventory was executed.

| SHA-256 | Path |
|---|---|
| `61a4c2bf250ab37f9146a125d9049565208375ba90c3462be209347e40cb92b2` | `schrodinger/route_feasibility.py` |
| `c080755c17d10f6acb30dc2ba2b02d88a479868a9fbd3e348ded2ae791d038ec` | `tests/test_route_feasibility.py` |
| `d49f1bce7d6344deeb0c74f8992fdeab1e391c2108a2c7e66c4af30d7324e938` | `execution/next_level/specs/03-pipeline-correction.md` |
| `266c44d8ef4696030fcdc6566dc44f57832c4a020b8cacd4a41a7e79a8b33936` | `execution/next_level/ledger.jsonl` |

C1 changes implement whole-split training-derived joint histogram/fractions and
one split-wide flow/quota allocation, JSON-native flow/capacity records,
explicit `execution_status: COMPLETE` scientific selection/bin/novelty outcomes
with `NOT_EVALUATED` later fields, deduplicated training state/q vectors,
support binary/hash, and validation/ID/IL novelty records. The artifact writer
emits the independent C1 file schema and round-trippable manifest/output hashes.

Evidence: `test_json_native_writer_scientific_failure_and_artifacts` constructs
an injected failure result, writes every required JSON artifact, reloads each,
and asserts the explicit COMPLETE/NOT_EVALUATED schema. Prior focused oracle/
flow/RNG fixtures remain. Command results: focused **7 passed in 0.47s**;
full **74 passed in 1.71s**. Next-level ledger total is **14.0s**. No CLI
inventory, model, or training run occurred.
