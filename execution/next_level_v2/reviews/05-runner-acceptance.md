# Productive-diversity v2 corrected-runner review

## Verdict: CHANGES REQUIRED

The shared-cache plumbing is present, but the submitted block does not close four of the five prior findings and does not test cache reuse. Most importantly, the composed fixture can label challenge data with zero novelty as `DATASET_PASS`. No production invocation is authorized.

## Exact versions reviewed

- Dataset contract: `execution/next_level_v2/specs/00-dataset-contract.md`, SHA-256 `67d28a6d6884da6cfa4980a320534774e9a87ee523cbec56d4258b49f47588de`
- Runner specification: `execution/next_level_v2/specs/01-runner.md`, SHA-256 `bbf31d38524c3a3c27922a06465860fa6c6ff4e5f204627cb81f38d2591821f2`
- Correction specification: `execution/next_level_v2/specs/02-runner-correction.md`, SHA-256 `666388fbd5f9a0f693930204a1ef9fc6fb134700e8d823333479d7dc5c2c8fd2`
- Handoff: `execution/next_level_v2/handoffs/04-runner-final-corrections.md`, SHA-256 `17399b591895324592915041ed2ef8d931789d2fd6fdcb70b7a05f5e72f003b3`
- Pure engine: `schrodinger/productive_diversity_data.py`, SHA-256 `e2e2b93a72afac114f68c1add3881aaa89898dbeb1f6a22c2ac00cf3a8faae09`
- Runner: `schrodinger/productive_diversity_runner.py`, SHA-256 `628aa0e784b4712cae3d8c81cb79f5aacb877b6d4edb3c7dac9e9fb54adac73f`
- Pure tests: `tests/test_productive_diversity_data.py`, SHA-256 `93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471`
- Runner tests: `tests/test_productive_diversity_runner.py`, SHA-256 `eba489e559b3c0344c3d03c86ab81190733c35952dcd7edd9b43fa08970f66eb`
- Ledger inspected: `execution/next_level_v2/ledger.jsonl`, SHA-256 `85365eca0ef71b23996ec78513673cf4cc443af96f81835040a2b6524201d5de`

## Remaining blockers

1. **The composed fixture can falsely pass invalid challenge data.** `run_rung` accepts injected `counts`, then overwrites them with production `_counts(spec)` before the strata. The test replaces `stratum` and returns the same real-oracle `M_novel=0` routine row for routine and challenge calls; `run_rung` performs no independent predicate/cardinality check and returns `DATASET_PASS`. Preserve the permitted selection/allocation seam, but make its counts effective and validate every returned stratum: exact requested family/map/problem identities and counts, 16 unique problems/map under production defaults, length quotas, `M_novel=0` for routine, and `M_novel>=4` with ratio `[.25,.75]` for challenge. The fixture may use predetermined records, but real `novelty_for` must produce valid challenge evidence; alternatively an invalid callback must be proven to fail technically. Required negative fixtures are: routine `M_novel>0`; challenge `M_novel=0` or `<4`; challenge ratio below `.25` and above `.75`; duplicate start/goal rows or wrong per-map/total count; wrong family; cross-split canonical identity reuse; and observed length histogram differing from the recorded quota. Each must raise a specific technical invariant failure, never return `DATASET_PASS` or start B. Do not claim production feasibility.

2. **Rung/parent status finalization is still absent.** `run_rung` still catches only `ConstructionFailure`; a technical error or deadline writes no rung `summary.json` with reached stages. `execute` then writes only a generic parent failure. Successful/scientific parent summaries still omit explicit `execution_status`, parent outcome, and consolidated observed/required gate counts. Implement and test immutable rung technical finalization plus complete parent scientific/PASS/failure status and linkage.

3. **Ownership and write-failure safety remain incomplete.** `Attempt.reject` still writes to the global `REJECTIONS`, so injected fixture paths are not isolated. More seriously, an `attempt.json` write failure is converted to a FAILED ledger row but suppressed by `__exit__`; `execute` returns normally and the CLI can exit zero despite the missing mandatory completion record. Propagate a logging failure after exactly-once charging and cleanup so the command exits nonzero. Inject the rejection directory, preserve foreign race output/lock bytes, and assert timer/handler restoration and one charge.

4. **Manifest configuration is incomplete and weakly tested.** The default effective config omits explicit board size 8, pool seed 80000, rung family codes, exact train/validation/test family allocations, and the correction specification from input hashes. The tests do not independently assert the complete config or every recorded input/output hash. Add these exact fields and hash verification while retaining the noncircular rule.

5. **Cache implementation needs the requested regression.** One `OracleCache` is now passed to all four `stratum` calls, which is the correct implementation direction. The test only accepts arbitrary `**kwargs`; it never asserts that the same cache object reaches all four stages or that an overlapping signature/BFS fact is reused. Add a same-identity/call-count regression without changing cache bounds or selection semantics.

## Retained acceptance

The pure orientation, q/support, and novelty helpers remain accepted. The corrected engine exposes a cache parameter without changing default scientific behavior. The post-lock output race is now charged while preserving the foreign output and owned lock cleanup. Frozen rung order and scientific-versus-technical taxonomy remain correct.

## Independent checks and charge

I statically traced the complete submitted runner and tests and recomputed all listed hashes. The blockers are directly observable in current source/tests, so I did not run pytest or any data command. Independent charged compute: **0 seconds**. Terra's reported **14 focused passes** and cumulative `10.071845336s` charge were inspected but do not exercise the missing assertions above.

Production dataset feasibility and every model outcome remain **NOT EVALUATED**.
