# Block 3 runner — implementation handoff

Current runner implementation is
`3d0278cf01f6de41e34e6447104c2fc5b63fae8deb2786b778ad4ab6b0a37a61`;
its focused tests are
`b7bf635f2e7d1999da72e54bd9f4854d4295afd3f0bfaa87f43ddae474d45db8`.

Focused verification command (exit 0):

```
.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py
9 passed in 0.69s (full wall 0.783042416s)
```

The runner owns a v3-local O_EXCL lock/output lifecycle, exact-once UUID ledger
entry, local rejection artifact, SIGALRM timer restoration, and mandatory attempt
log failure propagation. `_prior` rejects duplicate IDs, non-finite/negative
debits, and missing/duplicate/non-frozen carry entries for the production ledger;
the carry is global-only while later charges and allowances count against stage.

`execute_pipeline` persists each pool, assembled inventory, full ranking, each
completed proposal-stage callback, result, manifest and compact summary before
the `Attempt` closes. It validates PASS support hashing, split identity isolation,
per-stage map counts and quota lengths. The CLI remains only `--output` and uses
the production v3 data functions; it was not invoked here.

Test evidence:

- `test_prior_carry_is_global_only_and_duplicate_ids_rejected` verifies carry,
  duplicate IDs, non-finite/negative fields and required-carry failure.
- `test_deadline_uses_stage_global_and_tightening_override` and
  `test_deadline_cleanup_restores_previous_handler` verify immutable cap math,
  tightening-only override and timer restoration.
- `test_output_and_lock_rejections_are_local_and_charged_once`,
  `test_postlock_output_race_cleans_only_owned_lock_and_charges`, and
  `test_log_failure_charges_once_cleans_lock_and_propagates` exercise ownership,
  rejection isolation, one charge and cleanup.
- `test_real_eight_map_selection_writes_immutable_pipeline_artifacts` passes the
  accepted eight-record fixture through real `run_ranked_proposals` and actual
  artifact callbacks; only pool/assemble/rank inputs are internal test seams.
- `test_raw_capacity_failure_persists_truthful_result` verifies a no-retained
  ranking writes a truthful `RAW_JOINT_CAPACITY_FAILED` result/summary.

No production pool, inventory, ranking, or dataset CLI invocation occurred.
Ledger EOF rows `ad3b42d5-59fd-4c80-a1be-9b80f2de903a`,
`b8abdbdc-cd76-414e-999a-ddf929f0e17f`, and
`50cab268-344a-4499-916c-a39f336581ff` record the latest observed focused-command
wall times; earlier safety rows remain retained without alteration.
