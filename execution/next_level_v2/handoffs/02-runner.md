# V2 Stage 0 runner handoff

New `productive_diversity_runner.py` is the narrow integration layer only. No
earlier source was edited, and no production pool, model, or training run was
performed.

## Completed behavior

- A single v2-only parent `Attempt` owns O_EXCL lock, unique output, SIGALRM
  deadline, 900s/7200s prior-ledger budget reserve, exactly-once UUID ledger
  charge, failure attempt record, and cleanup.
- It composes each rung in frozen order: inventory, training/support/states,
  validation routine/challenge, then test routine/challenge. Completed files are
  written immediately within immutable A/B directories; every summary has
  explicit `NOT_EVALUATED` stages until reached.
- `ConstructionFailure` is retained as a successful scientific stop and permits
  B; unclassified technical exceptions propagate, finalize FAILED, and never
  start B. Parent summary retains both rung outcomes/evidence.
- Strict JSON serialization, support binary file hashing, recursive noncircular
  output hashes, source/config/runtime manifest, and final attempt-to-manifest
  SHA binding are implemented. Default paths are explicit v2 paths; tests pass
  isolated paths and do not mutate old globals or ledger.

## Test evidence

Final command:

```text
.venv/bin/python -m py_compile schrodinger/productive_diversity_runner.py && \
  .venv/bin/python -m pytest tests/test_productive_diversity_runner.py -q
```

It returned explicit exit code **0**, **4 passed in 0.46s** (external wall
0.580414417s). Tests cover injected CLI-style `main()` with A/B scientific
supply stops and output/manifest/attempt/one-ledger evidence; technical-no-B;
exhausted budget with failure record; existing output rejection; A-pass stopping;
and scientific A-fail/B-pass parent retention. No real pools were generated.

The v2 append-only verification ledger totals **6.900560377s**, below the
150-second development-test ceiling; its prior failed import-typo test run is
retained as a charged failure.

| SHA-256 | Path |
|---|---|
| `fe04e99aebf4eef284e068ab98a7241f8f1e0794f96baea4e2c3362adebe7588` | `schrodinger/productive_diversity_runner.py` |
| `3f7a2d9949a27305b7c6927f0aa91c2ce754afbc38caa5d48cc988227bc15679` | `tests/test_productive_diversity_runner.py` |
| `6c9c4099c1b98d486511087c3c50d72ab3b885e9b58ad019911b47741efb3ed5` | `schrodinger/productive_diversity_data.py` |
| `93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471` | `tests/test_productive_diversity_data.py` |
| `33ef1d90594060c57d3fc7d0d7de02f2df6e9b4a2957dc76ee05da68b758b494` | `execution/next_level_v2/ledger.jsonl` |
| `bbf31d38524c3a3c27922a06465860fa6c6ff4e5f204627cb81f38d2591821f2` | `execution/next_level_v2/specs/01-runner.md` |

Known limit: this is tested only against injected tiny inventories; production
dataset feasibility remains NOT EVALUATED and requires future Astra/Sol approval.

## Spec 01 acceptance checklist (current revision)

| Spec item | Implementation | Evidence / status |
|---|---|---|
| Frozen stage composition/order | `run_rung`, `execute` | Injected scientific A/B paths exercise rung order; real full-count composition **NOT EVALUATED**. |
| Exact default counts, map uniqueness, 16/map, quotas, q, predicates | pure engine functions called by `run_rung` | Pure-engine unit coverage exists; full production-count integration **NOT EVALUATED**. |
| Scientific-only B transition / technical no-B | `execute`, `run_rung` | `test_ladder_pass_stops_a_and_scientific_a_fail_b_pass_preserves_both`; `test_technical_failure_does_not_start_b_and_deadline_is_charged`. |
| One parent v2 lock/charge, fresh output, deadline/budget | `Attempt` | Existing output/lock and exhausted budget assertions; retained parent/rung artifact after deadline test. |
| Immutable A/B checkpoints and rung statuses | `run_rung` | Per-rung `inventory.json` and `summary.json` verified on injected scientific stop; unreached stage fields are `NOT_EVALUATED`. |
| Strict JSON/replayable tuple keys/support binary | `_json`, `_write`, `run_rung` | Tuple keys are explicit key/value arrays; support binary implementation present. Full successful support artifact path **NOT EVALUATED**. |
| Parent/rung/manifest linkage | `_manifest`, `Attempt.manifest_sha256` | Injected main test independently recomputes manifest hash; recursive output hashes asserted nonempty. |
| Exact provenance/runtime/config | `_manifest` | Engine/runner/old helper/tests/plan/specs/reviews, executable/runtime/thread environment included. |
| Failure log/cleanup/write resilience | `Attempt.persist`, `cleanup` | Deadline and rejection cleanup tested. Deliberate filesystem log-write fault injection **NOT EVALUATED**. |
| Actual injected CLI-style completion | `main` → injected `execute` | `test_injected_main_scientific_a_b_failure_persists_outputs_and_one_ledger`. |
| Production launch | intentionally absent | **NOT EVALUATED / not authorized.** |
