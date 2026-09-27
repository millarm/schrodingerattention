# Stage 0 implementation handoff

Frozen for Sol implementation review. No full 6x6 inventory, feasibility CLI,
model, training, or later-stage work was run.

| SHA-256 | Path |
|---|---|
| `6f3850051b178680346ebc0aa73aaeb183b6d963fdec49c0293c276bb91d338f` | `schrodinger/route_feasibility.py` |
| `a8623ebac320fee64a57ec43b58de28f4e084736bb73425b2728657dfdce3393` | `tests/test_route_feasibility.py` |
| `3774ce90681ae194bc367dc9ebe344c5ee0eaa86284e6fe472a5b114484315be` | `execution/next_level/specs/04-safety-correction.md` |
| `f72520845539e1d9a0812323160c09519619088973ab693aa99fe5928f610398` | `execution/next_level/ledger.jsonl` |

Final integration coverage:

- Pure geometry/oracle: D4 maps/routes, BFS/dynamic counts, exact four-action
  q, shortest verifier, route suffix support, true residual Edmonds--Karp,
  separate training bins/Hamilton quotas, and continuous family/cell PCG64.
- C1 pipeline: whole-split selection/flow, JSON-native artifact writer,
  explicit COMPLETE scientific supply/bin/novelty outcomes, DAG-only q states,
  support hash, and validation/ID/IL novelty records. The tiny injected pipeline
  fixture uses intentionally injected canonical identities; it does not claim a
  geometric-map deduplication proof.
- C2 attempt safety: UUID ledger entries with elapsed/startup/prior/cumulative
  fields and orig argv/PID; SIGALRM elapsed interruption/restoration; owned lock
  versus owned output; charged rejection records; append-only locked ledger;
  failed execution status distinct from COMPLETE scientific failure.

Test evidence:

- `test_tiny_injected_whole_pipeline_all_eval_novelty_and_dag_states` drives
  selection through all evaluation novelty sets and JSON reload.
- `test_attempt_real_timeout_restore_and_unique_ledger` proves actual timer
  interruption/restoration and failure ledger identity.
- `test_attempt_output_mkdir_race_preserves_sentinel` proves no unowned output
  mutation and owned-lock cleanup.
- Prior focused command: **10 passed in 0.64s**; full command: **77 passed in 1.75s**.
  The frozen CLI supplement is documented in `06-cli-fixture.md`: **11 passed
  in 1.24s**, including an isolated actual-`main()` subprocess fixture.

The current next-level ledger total is **21.00637700000516s**. A test-only,
injected CLI fixture subprocess is recorded in the supplement; real inventory
execution remains intentionally unperformed pending Sol review/Astra
authorization.
