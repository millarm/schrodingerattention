# Block 3 runner revision 1 handoff

Current hashes: runner `9ebfec7e2999e7b18f6f8054038a1bd9a3778b517faa763ab752429ef744e9bd`,
tests `0a10f9dd231bab835781e306e70578bea983cb1f185f968066e64a738bef887f`.

Focused command: `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py`
exited 0: **11 passed in 1.06s** (full final wall `1.169871167s`). No production command ran.

Sol12 finding map:

1. `execute_pipeline` has try/except/finally finalization: completed artifacts are
   hashed, partial `manifest.json`/`summary.json` bind reached files and original
   error, then the original exception is re-raised. Verified by
   `test_pipeline_deadline_after_pool_persists_partial_summary_and_failed_attempt`.
2. `_source_hashes` and manifest bind runner/data/helper/tests/plan/contract/spec/review,
   runtime, thread environment, budget/carry priors, frozen family/ranking/support settings
   and all discovered output hashes. The real writer test asserts manifest/attempt binding.
3. `_validate_pass` now uses the returned selected window/quota, not placeholder
   configuration, and checks source linkage, n/map/canonical identity, exact per-map quota,
   training family counts, M inventory membership, support hash, split leakage and novelty.
4. `test_real_tiny_pool_assemble_rank_capacity_failure` calls real
   `assemble_global_inventory` and real `rank_proposals` on tiny pools and asserts the genuine
   capacity outcome; `test_real_eight_map_selection_writes_immutable_pipeline_artifacts`
   remains the permitted genuine eight-record selection seam.
5. Partial deadline after one pool proves FAILED attempt log, exactly one ledger row,
   lock cleanup, original error and partial manifest/summary. Existing tests cover O_EXCL
   races and mandatory attempt-log fault charging/propagation.
6. `main` prints strict compact JSON only after successful pipeline completion; normal
   result remains immutable on disk.

The deadline formula now reserves 2s startup + 30s finalization + 120s independent audit
inside existing caps; `test_deadline_uses_stage_global_and_tightening_override` asserts it.
New EOF ledger records are `96ed5039-2048-4358-8d3c-a6fdc0be38da`,
`d19ac69e-6615-4918-8131-37bb7e20475e`, and
`63246ad1-75a6-4aa1-b2d5-dc6d0e684d23`.
