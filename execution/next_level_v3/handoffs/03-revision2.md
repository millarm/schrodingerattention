# Block 3 runner revision 2 handoff

Current runner SHA-256: `5ae71d4260123d9c6ca873a4f629d970c1159cab982c84eb848750fda1cadf09`.
Current test SHA-256: `0a10f9dd231bab835781e306e70578bea983cb1f185f968066e64a738bef887f`.

Focused verification: `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py`
exited 0, **11 passed in 1.03s** (full wall `1.139333167s`), charged at ledger EOF
as `08981b99-e580-4e88-8d39-51e7f5f39e4b`. No production invocation occurred.

Implemented revision2 source changes:

- PASS now requires the returned proposal be a retained ranking proposal; every
  wrapper has the exact expected family sequence and `OK` result before rows are
  flattened and validated.
- Effective manifest configuration records frozen family composition, pool/
  shortlist/split seed material, family codes, ranking semantics, audit reserve,
  runtime/thread facts, sources and output hashes.
- The CLI emits compact strict JSON only after `Attempt` closes:
  `{outcome,output,manifest_sha256}`; full scientific output remains `result.json`.
- Existing partial-deadline test covers error rethrow, FAILED attempt, partial
  output hash/manifest/summary and one ledger charge; existing attempt-log test
  covers mandatory log fault propagation and cleanup.

Existing focused tests exercising revision-relevant behavior are
`test_pipeline_deadline_after_pool_persists_partial_summary_and_failed_attempt`,
`test_real_eight_map_selection_writes_immutable_pipeline_artifacts`,
`test_real_tiny_pool_assemble_rank_capacity_failure`, and the Attempt lifecycle
tests. The source-level retained/wrapper guard is covered indirectly by the valid
eight-record result; dedicated mutation and stage-write-fault parameter tests are
not yet added, so this handoff intentionally does **not** claim Sol13 closure.
