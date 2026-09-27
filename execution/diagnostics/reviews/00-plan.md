# Sol review — retained-checkpoint diagnostic plan

## Exact version inspected

- `checkpoint_diagnostic_plan.md` SHA-256
  `342ef3af2f9728188c0fd1f512d2a814a717eb482f98cbcef16726f53820e26f`.
- `execution/diagnostics/status.md` SHA-256
  `3d6bfdd85b1fc7acdabfc04836768c2a1ee8dfd98c749f6d972d2e6bc331d6a1`.

## Verdict

**PASS**

The plan is sufficiently frozen, scientifically interpretable, and bounded for
implementation. It directly distinguishes “attention barely changes” from
“attention changes locally but has little propagated downstream effect” without
retraining, parameter sweeps, regenerated data, or reuse of invalid timing
evidence.

## Required findings

None.

## Scientific-validity checks

- The primary direct comparison holds each layer's normalized hidden state,
  scores and values fixed and changes only exact evolution versus
  `softmax(S)`. In particular, layer 2 uses the normal evolved model's incoming
  hidden state for both local calculations, so it measures local attention
  change rather than accumulated intervention drift.
- The full-path comparison separately permits layer-2 inputs to diverge and
  labels attention/hidden changes propagated. Required layer-1 agreement and
  layer-2 input-difference evidence make accidental conflation detectable.
- Total variation, keywise maximum change, head/output-projection RMS changes,
  circular phase dispersion, and Hamiltonian evolution scale answer distinct
  aspects of local change without relying on signed cancellation or raw
  `dt`/`gamma` alone.
- Final probability, margin, disagreement, per-example loss, correctness, and
  signed benefit measurements are adequate to detect downstream changes that
  accuracy alone could hide. The sign convention `CE_dt0 - CE_normal` is
  explicit.
- All local/downstream/benefit thresholds and censoring language are frozen
  before diagnostic results. Seed-equal aggregation, unweighted within-cell
  quantiles, required stratification, boundary caution, and retrospective-only
  interpretation prevent these bands from being confused with the original
  research gate.
- “Uniformly small” requires every seed/condition/operation/layer/head cell,
  for both all-row and CLS summaries, to pass. Larger or mixed cells must be
  reported rather than averaged away.
- The intervention cannot establish useful interference or representational
  equivalence; the plan states both limitations and forbids causal claims from
  learned scalar magnitudes alone.

## Numerical and evidence checks

- Normal and all-layer `dt=0` traces must reproduce the existing public model
  API, retained accuracy, and retained CE under fixed tolerances.
- Direct `dt=0` identity, hand-calculated TV/quantile fixtures, RMS denominator
  behavior, nondegenerate detectability, row normalization, bounds, finiteness,
  shapes/counts, and correct/count calculations cover the main implementation
  failure modes.
- The optional `P(+t)=P(-t)` check is correctly restricted to a real,
  zero-phase complex128 sanity fixture and cannot be interpreted as evidence
  about trained checkpoints.
- Inputs are the retained per-seed step-2000 SA checkpoints and their stored
  evaluation arrays. Required hashes cover checkpoints, arrays, metadata,
  source, config, contract and plan before compute; regenerated data and
  independently trained baseline checkpoints are correctly excluded.
- Row/per-example arrays retain the identifiers needed to independently
  reconstruct every reported cell and detect pooling mistakes.

## Execution-safety checks

- The diagnostic has an independent 900-second CPU ceiling, 30-second
  upcoming-batch reserve, separate ledger, one-process rule, and success/failure
  whole-attempt logging.
- Atomic `O_EXCL` locking, fresh fail-if-present attempt directories, and
  supervisor-authorized stale-lock handling prevent overlap and overwrite.
- A yielded command remains running until an explicit exit code is observed;
  follow-up launch, lock clearing, or artifact-existence inference is expressly
  prohibited. This directly addresses the original provenance failure.
- Only additive diagnostic code/tests and fresh diagnostic artifacts are
  permitted. Original implementation, checkpoints, datasets, results and
  reports remain immutable.
- The sequence—bounded tests, independent code review, one authorized command,
  confirmed exit, result audit, then interpretation—is consistent with the
  approved agent protocol. User authorization already covers the bounded run;
  no redundant approval gate is introduced.

## Checks deferred to implementation/result review

- Exact hook/manual-trace equivalence and proof that direct branches share the
  same tensors.
- Complete shape/index coverage, batch64 aggregation, raw-array schemas, lock
  contention, failure logging and cap enforcement.
- Actual checkpoint hashes, numerical reproduction, cell classifications,
  figure provenance and final mechanistic interpretation.

Plan review used read-only hashing and full source inspection only; no
diagnostic compute was run. Charge **0.2 seconds conservatively** to the
diagnostic ledger for this review, including final review hashing.
