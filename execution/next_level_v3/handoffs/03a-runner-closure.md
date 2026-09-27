# 03a runner closure handoff

Runner SHA-256: `06b941f169e6186df60d72544b0e2b311ffd9c4c869a8e457efc6f832af66041`.
Test SHA-256: `cd2d0c044c9dfa664136b0dec0f9bfbbfbf3d8956057f08f670e5176ad8dea9d`.

Focused command exited 0: `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py` —
**28 passed in 2.76s**, full wall `2.866879750s`. No production invocation.

03a closures:

1. `execute_pipeline` records callback-derived per-stage states. Exact assertions in
   `test_post_training_callback_deadline_preserves_stage_artifact_and_failed_attempt`
   require training COMPLETE, faulting validation routine FAILED and all later stages
   NOT_EVALUATED. Successful full PASS produces COMPLETE stages; the first unobserved
   stage remains NOT_COMPLETED_UNKNOWN only when no callback/write outcome establishes it.
2. `_source_hashes` now requires and hashes runner/data/route helper, both v3 test
   files, plan, protocol, fixed contract/spec plus every sorted current v3 spec/review.
   `test_success_manifest_recomputes_artifacts_and_serializes_science_fields` recomputes
   manifest output hashes and attempt binding.
3. `test_real_pipeline_stage_or_result_write_fault_truthful_state` parameterizes real
   eight-map pipeline writes at `proposal-12-training.json` and `result.json`. It asserts
   original write error, FAILED attempt, one charge, released owned lock, absent failed
   artifact, exact completed output hashes, and respectively stage FAILED/future
   NOT_EVALUATED versus all scientific stages COMPLETE with TECHNICAL_FAILED persistence.

EOF ledger records preserve all observed closure runs: failed `c05f3cea-3670-486c-8b34-f45e61e037a2`,
`d1c346b5-79e8-4e8e-a0a9-0702c8c47858`; passing `7de616d6-62cf-4754-ad52-97d648c76b46`,
`f041dd9d-a63a-4f5f-97f5-5c62efa50ebd`.
