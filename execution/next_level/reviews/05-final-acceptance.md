# Stage 0 final-acceptance review

## Verdict: CHANGES REQUIRED

The three scoped safety, traceability, and literal-fixture groups are substantially closed. However, the revision introduces or retains one critical scientific-output regression: `_novel_records` appends only after its input loop, so only the final problem in each split is retained. A full run would consequently evaluate the frozen IL novelty gate on at most one problem and must fail regardless of the true 512-problem inventory. Stage 0 execution is not authorized on this revision.

## Exact revision reviewed

- Final correction specification: `execution/next_level/specs/05-final-acceptance-corrections.md`, SHA-256 `62e4e3ffcdaf07cf86eadb56263f0420a696ccaf7659757f65f2a47b2739f293`
- Handoff: `execution/next_level/handoffs/07-final-acceptance-corrections.md`, SHA-256 `7edd510f8b1199c0e626948fd8e8cd8a6a7ba96896ea8eb251474ddd81fd253b`
- Module: `schrodinger/route_feasibility.py`, SHA-256 `74a7e0fe8b570d2bd58c3201aab4b950276ee1fbfce6a74f3847afd9c161ac84`
- Tests: `tests/test_route_feasibility.py`, SHA-256 `9a5ccef2e244526fe8d0fbdd9e9928772e0e336b62371740dc2e1bad0596aaa5`
- Prior review: `execution/next_level/reviews/04-feasibility-revision.md`, SHA-256 `bfe81241c265156cb8be62cc58917ec800940250a64e285789e88f62e2bd1c91`
- Ledger at review start: `execution/next_level/ledger.jsonl`, SHA-256 `7003981706ee6b69f9f78dd9dddeac502ccae97f9fa8f77d1d02c97691dbcb1d`

## Required correction

1. **Retain every evaluation problem in `_novel_records`.** At current module lines 181–186, route/signature computation is inside `for x in rows`, but `out.append(...)` is dedented outside it. Move the append into the loop. Add an end-to-end fixture asserting, for validation, ID, and IL separately, that novelty-record count and ordered `(map_id,start,goal)` identities exactly equal the selected split rows; each record's `M` equals the exact number of routes and the route/signature arrays both have that length. Assert that the novelty gate consumes this complete persisted IL list. The existing test's `all(result['novelty'].values())` proves only that each list is nonempty and allowed this cardinality loss to pass.

## Accepted scoped closure

- Owned-output enter-time deadline exhaustion now writes a charged `FAILED`/`FAILED` attempt and ledger record, marks manifest evaluation unavailable, restores signal state, and releases the owned lock.
- Required attempt-record write failure falls back to one charged ledger record with both status fields FAILED and unconditional cleanup.
- Lock and output-mkdir race fixtures preserve external ownership and record charged rejections.
- The generated manifest includes the module, tests, plan, Stage 0 specifications, and review records; the attempt binds the exact manifest digest and noncircular output-hash table.
- Literal nonuniform Hamilton, residual cross-family flow, 255/256 and 15/16 novelty boundaries, BIN_MATCH scientific-stop schema, and exhausted-budget paths now have direct fixtures.
- The previously accepted whole-split flow, RNG, DAG supervision, suffix support, JSON schemas, and scientific-stop mechanisms are otherwise unchanged.

## Independent checks

- Read the final correction specification, handoff, changed attempt/manifest paths, literal fixtures, and complete novelty-output function; traced their interaction with the primary gate.
- Ran `/usr/bin/time -p .venv/bin/python -m pytest -q tests/test_route_feasibility.py`: **18 passed in 1.19 s**, explicit exit; whole-command elapsed **1.42 s**. The pass demonstrates the stated coverage gap, not correctness of novelty cardinality.
- Conservatively charge **1.7 s** for this bounded review/test. The next-level ledger should advance from `29.70637700000516` to **`31.40637700000516` seconds** before any correction work.

## Not performed

- No full 6x6 inventory, feasibility outcome, model construction, pilot, training, or evaluation was run.
- The reported 85-test repository suite was not independently rerun; the critical defect is already demonstrated statically and is absent from its assertions.

