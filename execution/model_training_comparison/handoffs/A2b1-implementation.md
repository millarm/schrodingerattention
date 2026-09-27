# A2b1 safety and paired-training-core handoff

Status: final A2b1-01 bounded correction implemented; Sol exact-version PASS
remains required. No A2b2, production command, profile, pilot, evaluator or
bank artifact has been added.

## Exact bindings

- Frozen plan unchanged: `model_training_comparison_plan.md`
  `5ece45cdb11f860ae64933225f284297cff59aa544c6730b247138c660cc8ff0`.
- Core: `schrodinger/route_policy_experiment.py`
  `7cbe387948f18ce3edab488d3a0f4f8af79ed2e8865765443019052d7c043603`.
- Tests: `tests/test_route_policy_experiment.py`
  `7583d975590469d6760aec3e8e9af152f9d818e3c4fd95f4774a8e00ab85d03c`.

## A2b1-01 residual-to-assertion map

1. **Core timing and checkpoint accumulation.** Core lines 143–164 define
   `training_core_seconds = materialize_seconds + neural_seconds`, excluding
   scheduled summary extraction. Test lines 72–88 literally asserts that exact
   sum and writes update-2 `training_seconds` as the sum of steps 1 and 2; line
   97 asserts the restored payload preserves that cumulative sum.
2. **Frozen controls and preclip groups.** Core lines 123–142 freeze the five
   disjoint groups: `embedding`, `attention`, `feedforward`,
   `normalization_head`, `controls`; all parameter names are classified or fail.
   The preclip group norms are extracted only on scheduled summaries. Controls
   retain two values per layer/head: softmax alpha/beta; Schrodinger effective
   `0.5*sigmoid(raw_dt)` and `pi*tanh(raw_gamma)`. Test lines 73–87 captures
   preclip gradients, asserts the exact five keys and hand-computes each norm;
   lines 82 and 105–106 assert distinct head values and the effective SA
   formulas.
3. **Exact Schrodinger replay.** Test lines 99–106 saves a truthful SA initial
   checkpoint, captures the uninterrupted post-step tensors, restores, takes the
   same next step, and asserts `torch.equal` for every parameter, not merely the
   scalar losses.
4. **Every acquired timer stage and canonical fsync failure.** Core lines 62–75
   sets `timer_acquired` immediately after cancelling the prior timer and
   restores handler/timer plus removes the owned lock on any setup failure.
   Test lines 50–58 injects the arming failure and asserts restoration/cleanup.
   Core lines 76–105 durably appends one neutral `attempt_charge` row before any
   success artifact. Post-write fsync failure never retries the UUID, leaves that
   canonical row `FINALIZATION_UNCERTAIN`, and writes canonical `attempt.json`
   / sidecar `FAILED_LEDGER`; it cannot be interpreted as COMPLETE. Test lines
   43–49 literally asserts no ledger COMPLETE and a FAILED_LEDGER attempt.
   Successful completion is only the output `attempt.json` written after the
   charge append/fsync succeeds; A2b2 must consume that successful artifact.

## Charged commands

- UUID `a436bcb9-c8c8-4d15-a328-89aeeb1dd5fd`, failed direct focused run,
  `3 failed, 2 passed in 2.34s`; charged `2.800000000` is a conservative
  rounded outer tool-wall allowance, not a claimed precise test duration.
- UUID `7029a15f-d62d-48df-9703-242d0ea4a2e4`, failed direct focused run,
  `1 failed, 4 passed in 2.33s`; charged `2.800000000` is the same conservative
  rounded outer tool-wall allowance.
- UUID `f9a863ae-6c0c-4a25-88bc-6b62d24ccac3`, passed direct focused run,
  `5 passed in 2.40s`; charged `2.800000000` is the conservative rounded outer
  tool-wall allowance.
- UUID `d148a0f7-24ac-498e-93cb-743e26031988`, passed direct focused run,
  `5 passed in 2.34s`; charged `2.800000000` is the conservative rounded outer
  tool-wall allowance.

All are `.venv/bin/python -m pytest -q tests/test_route_policy_experiment.py`,
direct exits and no sessions. Before the final post-handoff check, the
append-only ledger is A `91.657762043`, global `1014.661359296` seconds; carry
remains `923.003597253`. No production activity occurred.
