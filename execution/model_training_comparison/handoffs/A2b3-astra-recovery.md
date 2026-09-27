# A2b3 implementation handoff — 2026-09-19

Astra's user-approved narrow exception implements only the combined runner and
its tests. Sol reviews independently. Scientific model/data/metrics/evaluator
modules are unchanged; earlier rejected handoffs/reviews remain historical.

Exact files frozen for review:

- `schrodinger/route_policy_experiment.py`: `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b`
- `tests/test_route_policy_experiment.py`: `588236b87c7cbc03d4617f97dd62be6e4e3a7de58f8d8a90450e63f691cd06c4`
- `tests/test_route_policy_runner_recovery.py`: `ac1332ac3af04caff5d149c345b9f5f0a87157b971aa669173678633a3ebc64a`

## Former blocker to executable evidence

1. `test_real_cli_profile_full_work_and_artifacts` executes real prepare/profile:
   5 warmup + 20 measured updates per model, six maps/96 problems, all five
   evaluation/control operations per family/model, both full probe banks, real
   checkpoints, JSON serialization and owned finalization. No model/evaluator
   mocks. Data loader monkeypatches only reuse already verified immutable loaded
   objects to avoid repeated fixture setup; production profile measures loaders.
2. It asserts ordered nonoverlapping phase intervals and exclusive sums, actual
   supplied ledger path/append cost, retained per-operation timings/artifacts.
   Nested evaluator timing is diagnostic evidence, not added again. The copied
   ledger fixture has zero charge; the actual owner appends one charge and records
   its measured append time before finalizing the forecast/output manifest.
3. It checks separate identified training64/validation128 probe artifacts and
   retained numerical results. Production selectors remain fixed.
4. It verifies all output file hashes, checkpoint hashes/counts, source inventory
   and governing resource-review provenance. Model-bearing final test inference
   is explicitly prohibited by this pilot harness.
5. `test_real_cli_paired_compressed_training_resume_and_authorization` runs both
   real CLI training paths on a declared temporary fixture with test-only
   2-update schedule and third-update resume. It checks paired shared tensors and
   batch digests, initial FILE hash, durable events/curves, same own-initial route
   control after resume, exact uninterrupted state/digest replay, wrong seed/mode/
   target/fresh-resume authorization and substituted initial-model rejection.
   Production constants are asserted before test-only monkeypatching. No fixture
   score is a scientific result.

## Verification and accounting

Focused: 14 passed in 37.31 seconds, session89496 explicit exit0; charged39.31
including2 seconds disclosed startup allowance. Full:221 passed in51.35 seconds,
session66234 explicit exit0; charged53.35 including2 seconds allowance. Full
command/session/poll records retained in the conversation; ledger rows unique.
Operational total1304.663835837; A381.660238584, leaving318.339761416 of A700 and
5895.336164163 overall. No production prepare/profile or paired training yet.

Future main-seed framework is deliberately deferred; the acceptance request is
the approved initial paired/profile/validation/resume boundary only. The runtime
forecast already reserves conservative costs for conditional later decoding work.
