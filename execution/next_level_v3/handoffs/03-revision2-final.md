# Block 3 runner revision 2 final evidence

Runner SHA-256: `f63bbf942625b37ffca6f48e3694c7e68c26a63be116d4ab57d4cb49ead19c12`.
Tests SHA-256: `02f2a7c50ddbc7e92c35a28853b65b5991c2ce74a7c00e6f6a6a69427fed90ef`.

Focused command: `.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_runner.py`
returned exit 0: **26 passed in 2.47s**, full wall `2.568162750s`. No production
pool/inventory/CLI command was invoked.

Sol13 resolution map:

1. Primary pipeline errors survive manifest/summary finalization errors via
   exception chaining, with one Attempt charge and cleanup. Assertions:
   `test_pipeline_write_fault_keeps_primary_error_charged_once` (manifest and
   summary parameter cases), `test_rejection_artifact_write_failure_charges_once_and_cleans`,
   and `test_log_failure_charges_once_cleans_lock_and_propagates`.
2. `test_post_training_callback_deadline_preserves_stage_artifact_and_failed_attempt`
   interrupts after the real training callback and checks training q/profile,
   completed-stage artifact, structured future NOT_EVALUATED list, FAILED attempt,
   one charge and lock cleanup.
3. `test_success_manifest_recomputes_artifacts_and_serializes_science_fields`
   recomputes manifest output hashes and attempt binding, and asserts seeds,
   effective selected quota, runtime/source fields and strict serialized artifacts.
   Source now includes platform/CPU and frozen pool/shortlist/split/family metadata.
4. `test_validate_pass_rejects_literal_corruptions` parameterizes retained proposal,
   stage outcome, wrapper family, row quota, length/inventory, n/identity, M,
   Mnovel and support-hash corruption against a deep-copied genuine eight-record
   result.
5. `test_cli_prints_exact_compact_success_and_no_success_on_failure` asserts exact
   post-context compact JSON `{outcome,output,manifest_sha256}` and no success
   stdout on failure.
6. `test_success_manifest_recomputes_artifacts_and_serializes_science_fields`
   verifies training support/profile with live cache omitted and held-out evidence/profile;
   output byte hashes are recomputed from the manifest.

Observed preceding failed test commands are preserved at EOF (not erased):
`445917d0-4680-4894-9cf0-2a4023288cf8` and
`1834c214-4955-43d1-986f-2a1e27e14fc6`; final passing command is
`80c47124-8a57-42b3-9456-c3708aa297c4`.
