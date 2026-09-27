# Stage 0 feasibility implementation review

## Verdict: CHANGES REQUIRED

The pure geometry, BFS/counting, route verification, D4/reversal signatures, suffix support helper, separate medians, continuous per-family RNG, Hamilton allocation, and residual Edmonds–Karp core are plausible and pass their small fixtures. The complete Stage 0 pipeline is not contract-compliant and is not runnable to a valid preserved outcome. No full inventory may be launched on this revision.

## Exact revision reviewed

- Frozen contract: `execution/next_level/specs/00-feasibility-contract.md`, SHA-256 `3b573fd5e67de97fd3ce9d0a4a4bfcf7b858ddcb65841638c6059f075ddcc0a3`
- Core-completion specification: `execution/next_level/specs/01-core-completion.md`, SHA-256 `4da537e20c0648a6e1754d949dc57c5c55836fb376e20ce3e3561be1c07ccc1d`
- Pipeline-completion specification: `execution/next_level/specs/02-pipeline-completion.md`, SHA-256 `ca8e8caccee56fa726d947c40ea83fa874e4bb78aa89ed09f050f50ef55be9a9`
- Complete-implementation handoff: `execution/next_level/handoffs/02-substep-b-pipeline.md`, SHA-256 `cbb2933583cb5403f2fcb47cefcada1dd5e7a02d10c77afc7fcdabf47861322c`
- Module: `schrodinger/route_feasibility.py`, SHA-256 `60684723ab541dba1e147c8f0286ed78978d7c04173214a1b98251815d39b9cd`
- Tests: `tests/test_route_feasibility.py`, SHA-256 `60915a1c8f7c5fce2776017a078f1d63db67ceb146c2562c9fc5f78a7657bc1c`
- Ledger at review start: `execution/next_level/ledger.jsonl`, SHA-256 `54ccaedc9b6bba021f88a8d53dba9901ce8df4bd8d19d33e8bc32674c5bebf50`

## Required corrections

1. **Implement the frozen training-derived joint-bin match.** `_evaluation_pairs` replaces the empirical training joint fractions with four hardcoded `0.25` values. It is called separately for II and LL, so it also enforces two family-specific flows rather than the contract's one quota/flow over every selected map in a split. Compute the four fractions from all 1,024 selected training problems after the frozen medians, allocate the required 128/256/512 split totals once, and solve one deterministic residual flow over all maps in that split. Preserve family labels, exact quotas, capacities, residual allocation, and selected pairs. Add a fixture with nonuniform training fractions and cross-family map capacities for which separate/uniform allocation gives a different or infeasible answer.

2. **Make every success and scientific-failure artifact serializable and complete.** A successful `feasibility()` result currently retains `frozenset` walls in training/validation/ID records and tuple keys in flow dictionaries. `json.dumps` cannot serialize tuple keys, while the supplied default returns unknown objects unchanged; the CLI will fail while writing `summary.json`. The BIN_MATCH_INFEASIBLE exception also attempts `json.dumps` on tuple-key dictionaries and can mask the intended evidence with a serialization error. Define stable JSON/NPZ schemas with string/cell records and test actual write/read round trips. Expected supply/bin/novelty failures must produce `execution_status: COMPLETE`, their exact evidence, and explicit `NOT_EVALUATED` later fields rather than raising into a compute-failure attempt with no gate summary.

3. **Produce the full oracle/support evidence required by the contract.** Persist deduplicated supervised `(map,current,goal)` states with their four-action `q`, not only selected training starts. Persist exact route/signature/`M`/`M_novel` records for validation and both test splits as required, rather than only IL `M_novel` summaries. Store the sorted length-prefixed support with an explicit digest and verify its decoded membership/count. Record per-map problem counts, bin counts, and gate arithmetic from the persisted artifacts. Add integration assertions that independently reconstruct these values.

4. **Complete manifests and attempt safety/provenance.** The current manifest contains only argv, executable, plan hash, and contract hash; it omits runtime identity, module/test/substep specification hashes, input/inventory identities, output hashes, and final status required by the contract. Attempt records generate `started_at_utc` at exit, omit an end timestamp and unique attempt ID, and do not preserve full source/output identities. If timer setup or another enter-time operation fails after this attempt creates its output, `__enter__` cleans resources but writes no failed attempt/ledger record. The prior interval timer is not restored. Implement exact start/end/runtime/identity records, unique IDs, deterministic output-manifest rules, unconditional owned cleanup and failure persistence for every entry path, and restoration of both prior signal handler and timer.

5. **Add the required complete-pipeline and safety regressions.** The submitted test file still contains only the six core/substep-A fixtures. It does not invoke `feasibility()` on an injected complete inventory or test required artifact schemas, scientific failure semantics, novelty threshold/map arithmetic, nonuniform bin flow, deadline interruption, lock/output races, enter-log failure cleanup, or cumulative stage/global accounting. Add bounded injected-inventory integration fixtures covering successful and each stopped outcome, plus the specified ownership/deadline/ledger cases. A passing repository-wide suite cannot substitute for absent acceptance tests.

## Independent checks

- Read the complete contract, both completion specifications, handoff, module, tests, and ledger; followed selection, flow, support, serialization, expected-failure, attempt, and CLI paths.
- Confirmed the residual network includes reverse edges and the core fixture requires reassignment; confirmed RNG objects are reused across maps/cells within each family.
- Ran `/usr/bin/time -p .venv/bin/python -m pytest -q tests/test_route_feasibility.py`: **6 passed in 0.45 s**, explicit exit; whole-command elapsed **0.69 s**. These are core fixtures only and do not cover the failed complete paths above.
- Conservatively charge **1.0 s** for this independent bounded test and static/hash audit. The next-level ledger should advance from 10.0 to **11.0 s** before further implementation work.

## Not performed

- No full 6x6 inventory, dataset generation, feasibility outcome, model construction, pilot, training, or evaluation was run.
- No source or test implementation was edited by the reviewer.

