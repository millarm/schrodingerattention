# Stage 0 feasibility revision review

## Verdict: CHANGES REQUIRED

The revised scientific pipeline now implements whole-split training-derived quotas, a single residual flow, continuous family RNG streams, exact DAG-state supervision, full suffix support, validation/ID/IL novelty records, JSON-native artifacts, and COMPLETE scientific failure outcomes. Those parts are accepted. A small but material safety/traceability closure remains before the full 6x6 invocation.

## Exact revision reviewed

- Frozen contract: `execution/next_level/specs/00-feasibility-contract.md`, SHA-256 `3b573fd5e67de97fd3ce9d0a4a4bfcf7b858ddcb65841638c6059f075ddcc0a3`
- Core completion: `execution/next_level/specs/01-core-completion.md`, SHA-256 `4da537e20c0648a6e1754d949dc57c5c55836fb376e20ce3e3561be1c07ccc1d`
- Pipeline completion: `execution/next_level/specs/02-pipeline-completion.md`, SHA-256 `ca8e8caccee56fa726d947c40ea83fa874e4bb78aa89ed09f050f50ef55be9a9`
- C1 pipeline correction: `execution/next_level/specs/03-pipeline-correction.md`, SHA-256 `d49f1bce7d6344deeb0c74f8992fdeab1e391c2108a2c7e66c4af30d7324e938`
- C2 safety correction: `execution/next_level/specs/04-safety-correction.md`, SHA-256 `3774ce90681ae194bc367dc9ebe344c5ee0eaa86284e6fe472a5b114484315be`
- Implementation handoff: `execution/next_level/handoffs/05-stage0-implementation.md`, SHA-256 `f7aa30f12e1ff98a8cc0a4a31e7d1d2deea730403a2f0e3210e70933517e79c8`
- CLI supplement: `execution/next_level/handoffs/06-cli-fixture.md`, SHA-256 `8abb29436725815797aee1b0961d0be42ab9bb5fa0134f427e16f1ec7a86bbaa`
- Module: `schrodinger/route_feasibility.py`, SHA-256 `6f3850051b178680346ebc0aa73aaeb183b6d963fdec49c0293c276bb91d338f`
- Tests: `tests/test_route_feasibility.py`, SHA-256 `a8623ebac320fee64a57ec43b58de28f4e084736bb73425b2728657dfdce3393`
- Ledger at review start: `execution/next_level/ledger.jsonl`, SHA-256 `f72520845539e1d9a0812323160c09519619088973ab693aa99fe5928f610398`

## Remaining required corrections

1. **Persist and charge every enter-time failure.** If `_timer()` raises after this attempt has created its output—for example because cumulative Stage 0 budget is already exhausted—`Attempt.__enter__` currently performs cleanup and re-raises without writing `attempt.json` or appending a charged failed ledger entry. The C2 specification explicitly covers this path. Record an owned-output enter failure as `execution_status: FAILED` exactly once, protect cleanup with an outer `finally`, and test exhausted cumulative budget/deadline at entry with output evidence, nonzero charge, restored timer, and released lock.

2. **Do not retain COMPLETE execution status when required logging fails.** In `__exit__`, failure to write `attempt.json` appends `{status: "failed"}` but inherits `execution_status: "COMPLETE"` from the successful body record. Both status fields must say FAILED and the error must identify the required-record failure. Add an injected write-failure regression proving one failed ledger record, no success record, and unconditional descriptor/lock/timer cleanup. Also add the specified atomic lock-race test and strengthen the output-mkdir race test to verify a unique charged external rejection record rather than sentinel preservation alone.

3. **Finish traceability and the missing acceptance cases.** The manifest currently hashes the module, tests, plan, and original contract only. Add both completion specifications, C1/C2 correction specifications, and the prior implementation reviews/handoffs required to identify the accepted pipeline; bind the output manifest from the attempt record without creating a circular hash. Add literal assertions for nonuniform training fractions and one cross-family whole-split flow, exact 256-problem/16-map novelty arithmetic, BIN_MATCH scientific-failure serialization, and cumulative stage/global exhaustion. The existing tiny pipeline is useful but does not explicitly prove these frozen thresholds and failure schemas.

## Accepted revision behavior

- The four joint fractions are computed from selected training problems; Hamilton quotas are allocated once per complete validation, ID, or IL split; one deterministic residual flow spans all selected maps; and per-family RNG streams remain continuous during within-cell choice.
- Deduplicated training states are restricted to the exact shortest-path DAG and carry four-action `q`; support contains every nonterminal shortest suffix and has an exact binary digest.
- Validation, ID, and IL records retain exact routes, canonical signatures, `M`, and `M_novel`; the novelty gate uses the frozen 256/512 and 16-map thresholds without selection feedback.
- Artifacts are JSON-native, scientific selection/bin/novelty failures are COMPLETE outcomes with unavailable downstream fields distinguished from zeroes, and the isolated CLI fixture reaches the real writer/attempt path with an observed subprocess exit code.
- The real timeout test establishes signal interruption and handler restoration; output ownership is separate from lock ownership; successful and ordinary body-failure records use UUIDs and charged cumulative accounting.

## Independent checks

- Read the full contract, four completion/correction specifications, current module, all focused tests, handoffs, and shared ledger; followed successful, scientific-stop, timeout, rejection, entry-failure, and record-write paths.
- Ran `/usr/bin/time -p .venv/bin/python -m pytest -q tests/test_route_feasibility.py`: **11 passed in 1.19 s**, explicit exit; whole-command elapsed **1.44 s**.
- Conservatively charge **1.7 s** for this bounded review/test. The shared next-level ledger should advance from `21.00637700000516` to **`22.70637700000516` seconds** before further work.

## Not performed

- No full 6x6 inventory, feasibility outcome, model construction, pilot, training, or evaluation was run.
- The prior 77-test repository result was not independently rerun because the remaining failures are uncovered acceptance paths, not regressions detectable by that suite.

