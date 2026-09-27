# Productive-diversity v2 Astra recovery review

## Verdict: PASS

The user-authorized Astra recovery closes every blocker recorded in review 06 without changing the frozen scientific criteria. The reviewed Stage 0 engine/runner is safe for **one** frozen production dataset-ladder invocation under the accepted lock, deadline, budget, immutability, and audit rules. This PASS does not establish dataset feasibility and does not authorize model construction, pilots, or training before the resulting dataset attempt receives independent review.

## Exact versions reviewed

- Recovery handoff: `execution/next_level_v2/handoffs/05-astra-recovery.md`, SHA-256 `e448cef2bd9ae557fccfdf75d421d171e3fa3e4aa6d87c0fb137ee8c663a287a`
- Runner: `schrodinger/productive_diversity_runner.py`, SHA-256 `567cb0ceff9107ca9fd2a3999d6126b9ec0c94559db860e73dbdd91670e4d98f`
- Runner tests: `tests/test_productive_diversity_runner.py`, SHA-256 `b62bd8f2bbfc94d2ec114579de4f8a5e0addf4d59d490f3955b32b2f238f6f9e`
- Unchanged pure engine: `schrodinger/productive_diversity_data.py`, SHA-256 `e2e2b93a72afac114f68c1add3881aaa89898dbeb1f6a22c2ac00cf3a8faae09`
- Unchanged pure tests: `tests/test_productive_diversity_data.py`, SHA-256 `93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471`
- Prior blocker audit: `execution/next_level_v2/reviews/06-final-implementation-blocker.md`, SHA-256 `9603aea680689c37de8def37bcd805a6edf43a64e9a8cf7dc75467c248007902`
- Protocol: `agent_execution_protocol.md`, SHA-256 `8e6b0c8834d5ec5efa9ec2033a3c04577c1d0635a04f0c17fdaf784f6d299a89`
- Current accepted plan: `productive_diversity_v2_plan.md`, SHA-256 `c603fec5d64314514bb971afa41b84344e8e3ff81f4fcf0c3d7e1ade14ceefc9`
- Specifications 00/01/02/03: SHA-256 respectively `67d28a6d6884da6cfa4980a320534774e9a87ee523cbec56d4258b49f47588de`, `bbf31d38524c3a3c27922a06465860fa6c6ff4e5f204627cb81f38d2591821f2`, `666388fbd5f9a0f693930204a1ef9fc6fb134700e8d823333479d7dc5c2c8fd2`, and `6783b451f47a77438d2b8e5b051c81d04bd8208f4aaee0242d119f466390933e`
- Post-review-test v2 ledger: `execution/next_level_v2/ledger.jsonl`, SHA-256 `811282f456dc19154323b0c36f999406e0ea25d88551a4e0c2ac78a332bfbf97`

## Blocker closure

1. **Genuine composed success — PASS.** The test-only fixture injects bounded selection, not a replacement `run_rung`. It uses genuine 8×8 geometry, canonical identities, orientation coverage, BFS completion counts, q states, all-DAG suffix support, and `novelty_for`. Its validation/test routine rows have zero novel routes and its challenge rows genuinely satisfy `M_novel >= 4` and ratio `[.25,.75]`. All four stages complete in the frozen order, serialize strict artifacts, preserve the support hash, and report the injected exact counts. Production defaults remain three/four components, 16 problems/map, and `16 <= M <= 256`; the fixture is not labeled production feasibility.

2. **Independent returned-stage invariants — PASS.** The runner recomputes canonical identity, BFS length/count, enumerated route count, novelty count, family/map counts, per-map unique ordered problems, cross-split identity exclusion, and exact length quotas. It validates training states/q to absolute `1e-12`, orientation coverage, and support order/hash. Wrong family, duplicate/total/map count, cross-split reuse, quota, M, fabricated novelty, routine novelty, challenge zero/below-four, and both ratio-bound violations are explicit technical negative cases. Technical failures cannot start B.

3. **Truthful immutable statuses — PASS.** Each rung records RUNNING then COMPLETE, SCIENTIFIC_FAILURE, TECHNICAL_FAILURE, or DEADLINE with later stages NOT_EVALUATED; its summary is written in `finally` before re-raising technical failures. The real deadline-after-inventory test preserves the A inventory and rung summary, parent FAILED outcome/count linkage, manifest, one failed attempt charge, and no B. Completed scientific two-rung failure and selected-rung PASS produce explicit parent status/outcome, attempted-rung summaries, observed/required counts, and immutable artifacts.

4. **Ownership, deadline, and charge safety — PASS.** Output/artifact writes use exclusive creation. Existing output/lock and the post-lock mkdir race preserve foreign ownership and charge one rejection in the injected rejection directory. A mandatory `attempt.json` write failure appends exactly one FAILED charge, propagates to a nonzero command path, releases the owned lock, and restores the prior SIGALRM handler/timer. Ledger accounting includes the conservative historical allowance separately from measured elapsed time.

5. **Manifest provenance — PASS.** The manifest binds protocol, current engine/runner/helper/tests, plan, every Stage 0 specification, and all reviews. Effective config includes `n=8`, pool seed/trials/limit, per-rung index/family codes/families/lengths/split seeds, exact train/evaluation allocations, problems/map, multiplicity bounds, stage order, and budget constants. Tests independently recompute every recorded input and noncircular output hash.

6. **Bounded cache reuse — PASS.** One `OracleCache` instance is passed across all four held-out stages. The composed fixture asserts object identity, and an independent call counter proves repeated signature lookup hits the cache without repeated route enumeration. Cache bounds and scientific selection semantics are unchanged.

## Independent execution and budget charge

I independently ran:

```text
.venv/bin/python -m pytest tests/test_productive_diversity_data.py tests/test_productive_diversity_runner.py -q
```

The command returned explicit exit code **0**, with **32 passed in 0.98s** and full command wall **1.074367625s**. It did not yield or require polling. Ledger entry `b80b4bb2-9e95-4a5f-b848-b70c4b1ce5a8` appends that exact full wall once. The post-entry conservative v2 debit is **168.705074252s**, including the separately identified 150-second historical allowance; it remains below the 900-second Stage 0 and 7,200-second global ceilings.

No production pool, dataset, model, pilot, or training command was run during this review.

## Gate consequence

The earlier implementation BLOCKED status is resolved for these exact hashes. Astra may launch only the single accepted default Stage 0 ladder command into a fresh immutable output while preserving complete tool exit/session evidence. The resulting scientific PASS or construction failure must be audited before any later stage.
