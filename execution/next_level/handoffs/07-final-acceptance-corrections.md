# Stage 0 final-acceptance correction handoff

Frozen for Sol residual review. This correction made no full inventory, model,
or training invocation.

## Resolution map

1. **Owned enter-time failures and fallback records**
   - `test_enter_timer_exhaustion_persists_failed_attempt_manifest_and_charge`
     creates an already-exhausted cumulative ledger and exercises the real
     `Attempt.__enter__` timer path. It asserts `attempt.json`, one added
     charged `FAILED`/`FAILED` ledger entry, a `NOT_EVALUATED` manifest, lock
     release, and signal-handler restoration before the body can run.
   - `test_log_write_failure_falls_back_to_failed_charged_ledger` injects an
     `attempt.json` write failure on the real exit path and asserts the fallback
     ledger is `FAILED`/`FAILED`, charged, and cleaned up.
   - `test_attempt_output_mkdir_race_preserves_sentinel` now asserts the
     charged `REJECTED` record as well as preservation of externally-created
     sentinel output. `test_lock_o_excl_race_preserves_external_owner_and_charges_rejection`
     covers the literal O_EXCL owner-preservation path.

2. **Traceability and binding**
   - `_input_hashes()` includes module, test, plan, every Stage 0 spec, and
     every review record. `write_artifacts()` writes that table and output hashes
     excluding manifest/attempt self-references; `Attempt.bind_manifest()`
     stores the exact manifest SHA-256 and same output-hash table in final
     `attempt.json`.
   - `test_manifest_membership_and_attempt_binding_from_actual_written_output`
     writes real artifacts and asserts complete membership plus the binding.
     Enter-time failure test asserts explicit `NOT_EVALUATED` manifest state.

3. **Literal frozen acceptance fixtures**
   - `test_literal_nonuniform_hamilton_and_cross_family_global_flow` asserts
     exact nonuniform Hamilton quotas `{00:2,01:3,10:5,11:7}` for 17 and a
     global cross-family residual-flow success where a separated family quota
     fails.
   - `test_literal_novelty_255_256_and_15_16_map_gate` asserts failures at
     255 qualifying problems and 15 qualifying maps, and pass only at
     256/16.
   - `test_actual_pipeline_bin_match_infeasible_schema_retains_selection_and_stops`
     drives the real injected tiny `pipeline` to `BIN_MATCH_INFEASIBLE`, checks
     retained selection/capacity/flow evidence and later `NOT_EVALUATED`, then
     serializes/reloads the actual summary.

Commands and exits:

- `.venv/bin/python -m pytest tests/test_route_feasibility.py -q` — exit 0,
  **18 passed in 1.23s** (external wall 1.357s; before the final one-line
  rejection assertion).
- `.venv/bin/python -m pytest -q` — exit 0, **85 passed in 2.53s** (external
  wall 2.783s), including the final assertion.

| SHA-256 | Path |
|---|---|
| `74a7e0fe8b570d2bd58c3201aab4b950276ee1fbfce6a74f3847afd9c161ac84` | `schrodinger/route_feasibility.py` |
| `9a5ccef2e244526fe8d0fbdd9e9928772e0e336b62371740dc2e1bad0596aaa5` | `tests/test_route_feasibility.py` |
| `7003981706ee6b69f9f78dd9dddeac502ccae97f9fa8f77d1d02c97691dbcb1d` | `execution/next_level/ledger.jsonl` |
| `62e4e3ffcdaf07cf86eadb56263f0420a696ccaf7659757f65f2a47b2739f293` | `execution/next_level/specs/05-final-acceptance-corrections.md` |
| `bfe81241c265156cb8be62cc58917ec800940250a64e285789e88f62e2bd1c91` | `execution/next_level/reviews/04-feasibility-revision.md` |

The append-only next-level ledger totals **29.70637700000516s** after the
Sol review charge (1.7s), the corrected CLI-fixture allowance (2.0s), and this
conservative final-regression allowance (5.0s). No earlier ledger history was
rewritten.
