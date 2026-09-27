# Bounded residual fix — completed-run pair validation

Purpose: Sol revision2 identified the remaining pair comparator omission.
This specification narrows next work to a single-function correctness fix and
its regression. Scientific contract and accepted attention/data/model unchanged.

After Sol finishes review, Terra may edit only `schrodinger/experiment.py`,
`tests/test_experiment.py`, and new current logs/handoff/evidence/ledger records.
In pair_evaluate, load the final completed checkpoint or final artifact for
each run, require equal final update count, matching nonempty aggregate training
stream digest, and consistency with each run's raw stream digest. Do not use
empty step0 digest as completed-stream evidence. Preserve existing dataset,
seed/mode/config/source/initial checks. Emit verified final steps, stream digest,
config/source/initial/eval identities in pair result alongside selected equal-time
checkpoints/times/slack. Reject mismatch BEFORE evaluating endpoint models.

Add regressions for unequal final steps and mismatched completed training streams
despite identical step0/config/init/eval; assert rejection before evaluation.
Valid paired runs with equal stream must pass and emit actual identity evidence.
Run full suite, corrected pair evaluation on existing102-step evidence, and
full SHA256 current handoff including all checkpoint/JSONL/command artifacts.
No retraining needed because only evaluation-helper enforcement changes; label
training source hash versus new evaluator hash explicitly. <=120 additional
compute seconds; add Sol review2.1s and charge actual
commands/startup conservatively. Single complete handoff to Sol, no other changes.
