# Productive-diversity v2 Stage 0 runner review

## Verdict: CHANGES REQUIRED

The runner has the correct high-level rung order and ordinary scientific/technical transition, but its evidence does not exercise a composed successful rung and several required failure/provenance behaviors are incomplete. The corrections below are bounded to the runner integration and a semantics-preserving shared cache seam. No production inventory, model, pilot, or training work is authorized.

## Exact versions reviewed

- Runner specification: `execution/next_level_v2/specs/01-runner.md`, SHA-256 `bbf31d38524c3a3c27922a06465860fa6c6ff4e5f204627cb81f38d2591821f2`
- Initial runner handoff: `execution/next_level_v2/handoffs/02-runner.md`, SHA-256 `bf6230e93381782aea53427093df9c2f1ce86ce4740b9b4bdaf2968b576ff947`
- Hardening handoff: `execution/next_level_v2/handoffs/03-runner-acceptance-hardening.md`, SHA-256 `75967f45eb7826956f05c59261e5629e4d0f70404e2ef0de5bd65eb4c8381e08`
- Runner: `schrodinger/productive_diversity_runner.py`, SHA-256 `99a2b8d67f0dcc3ab8b367ba7ec02f8b8b2caa1320a408fe7ff71188938ce72d`
- Runner tests: `tests/test_productive_diversity_runner.py`, SHA-256 `8914532f1447db1aa660a94501e990ab5151ef8101e7a9d8b514a92ecf927b74`
- Accepted pure engine: `schrodinger/productive_diversity_data.py`, SHA-256 `6c9c4099c1b98d486511087c3c50d72ab3b885e9b58ad019911b47741efb3ed5`
- Pure-engine acceptance: `execution/next_level_v2/reviews/03-pure-acceptance.md`, SHA-256 `df7a0c70271df6e81204418ec348cf8aab796b27c507340e1f53c939a6e7209c`

## Required corrections

1. **Exercise one genuinely composed successful rung.** Every current path that reports `DATASET_PASS` monkeypatches `run_rung` wholesale. The only real `run_rung` invocation stops at empty-inventory `MAP_SUPPLY_FAILED`; therefore training selection/orientation coverage, q/states/support serialization, all four ordered strata, exact family/map/problem cardinalities, novelty predicates, length quotas, tuple-key records, and the successful support/manifest path are not integration evidence. Add an internal test-only fixture configuration or callable seam—never a CLI option and never a production-default change—then run the real runner composition through a complete small success. Assert order, exact injected expected/observed counts, no cross-split identities, 16-per-map production invariant where applicable (or the explicitly injected fixture capacity), q tolerance, orientation evidence, support digest/file hash, all four artifacts, strict JSON, and recursive output hashes. Keep production pools prohibited.

2. **Persist truthful rung and parent completion state on every path.** A technical exception or deadline inside `run_rung` bypasses its `ConstructionFailure` handler, so no rung `summary.json` records the completed stage statuses or error; `execute` writes only a generic parent failure and loses which rung/stages completed. Make each rung finalize an immutable technical summary with reached stages and explicit failure class before re-raising. A scientific two-rung stop and a selected-rung PASS also need an explicit parent `execution_status=COMPLETE`, parent scientific outcome, and exact observed/required gate counts; do not make auditors infer completion or cardinality from nested files. Extend the interruption test to check the rung summary, parent linkage, stage statuses, and manifest hashes, not merely file existence.

3. **Close ownership, rejection isolation, and write-failure safety.** After O_EXCL lock acquisition, a racing `output.mkdir` failure occurs while `owned` is false: the lock is cleaned, but the attempt is neither charged nor logged. Handle this without writing into or deleting the foreign output. Inject the rejection-record directory with the fixture lock/ledger paths; current tests using isolated ledgers still write rejection JSON into the workspace-global `execution/next_level_v2/rejections`. Add exact tests for the output-creation race, existing lock/output preservation, timer/handler restoration, and deliberate attempt-log failure. Every attempted invocation must append at most and exactly one UUID charge when its ledger remains writable, and cleanup must occur even when failure logging itself fails.

4. **Bind the frozen effective configuration in the manifest.** `_manifest` hashes relevant source/documents but contains no explicit effective dataset/runtime configuration despite the specification and handoff claim. Record and assert board size, pool seed/trials/limit, both rung family codes/families/lengths/split seeds, map/problem allocations, frozen stage order, cap/global cap/startup/reserve, and the exact imported engine/runner/helper/test/plan/spec/review hashes. Keep the noncircular output-hash rule and independently verify all manifest hashes in the composed-success fixture.

5. **Share the bounded oracle/signature cache across strata.** Each `stratum` currently creates its own `OracleCache`; the runner therefore repeats route enumeration for maps reconsidered between validation/test within a family. Expose a cache argument and pass one bounded rung cache across held-out strata (and selected-record novelty), preserving exact eligibility/selection semantics. Add a small call-count or cache-identity regression proving reuse. This is required execution feasibility plumbing, not a new scientific gate or a request for unbounded caching.

## Static behavior accepted and retained

- The frozen order is inventory, training, validation routine/challenge, then test routine/challenge; counts computed by `_counts` match rung A/B family allocations.
- Only typed `ConstructionFailure` is converted to a scientific completed rung; technical exceptions otherwise propagate and prevent B. A PASS stops at A, while a scientific A failure may start B.
- The parent owns one O_EXCL lock and one charge; the SIGALRM deadline clamps overrides to remaining 900/7,200-second budgets with startup/reserve, and normal cleanup restores the prior handler/timer.
- Per-stage files use fresh rung directories and strict JSON; tuple-key dictionaries become explicit key/value records, support uses two-byte length prefixes, manifest hashing is recursive and noncircular, and the attempt binds the manifest hash.
- The final accepted taxonomy remains exhaustive: bounded supply, frozen novelty-qualified selection, length flow, and missing selected-training orientation coverage are scientific/B-eligible; malformed components, identity collision, BFS/enumeration M mismatch, q/count/cardinality invariant failure, runtime/deadline/budget/serialization, and unclassified errors are technical/not-B.

## Independent evidence and charge

I recomputed the listed hashes and traced every runner/test path against the accepted engine and runner specification. I did not execute pytest or any data command because the missing composed-success path and failure-path defects are statically decisive. Independent charged compute: **0 seconds**. Terra's reported **5 passed** and cumulative `8.745575544s` development charge were inspected but not independently rerun.

Production dataset feasibility, actual runtime, and all model outcomes remain **NOT EVALUATED**.
