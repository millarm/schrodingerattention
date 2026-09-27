# Checkpoint diagnostic revision 1 handoff

Status: frozen for Sol re-review. This record covers the accepted trace plus
the six required review corrections. No full diagnostic command, training, or
modification of any original experimental artifact occurred.

## Current reviewed identities

| SHA-256 | Path |
|---|---|
| `cc79222d106248dedf27106141f3656024dfceb87e961a70572b26a681fc73fd` | `schrodinger/checkpoint_diagnostic.py` |
| `eb3636f9a3f2b9c7f53bd15bd2885b8e049bc4ff3b4879a3127a83d206b9048e` | `tests/test_checkpoint_diagnostic.py` |
| `b160517e6a6c8d707fe50d392b3953dac447b99d74eeda2893a53c15dfd66b16` | `checkpoint_diagnostic_plan.md` |
| `a9a50cd426048d0ee5cdd31a12767a179f15c6a8022a08425cfe20df0e4b3453` | `execution/diagnostics/specs/01-review-corrections.md` |
| `9961ce9c450eb613df10256d1d638f38f5fe16f0fba422744a7fda087f229b1b` | `execution/diagnostics/reviews/01-implementation.md` |
| `daa27192b758d35c9535c056a056e3c538dfd46f5549f39ed2c95f5ea79618b3` | `execution/diagnostics/ledger.jsonl` |

## Six-group resolution map

1. **Downstream tails and flags:** NPZ examples now contain `disagreement` and
   `absolute_loss_change`; summaries include probability maximum, margin
   mean/p95/maximum, absolute-loss mean/p95/maximum, and signed-benefit
   median/p05/p95. `frozen_flags` reports every direct local-small cell result
   and seed-equal test-condition/op benefit rule (mean >= .01 plus 2/3 positive).
2. **Strict numerical rejection:** every numeric raw array must be finite;
   attention/output probabilities are checked for finite values, [0,1] bounds,
   and row sums; direct/propagated TV is bounded with 2e-4 tolerance. Schema
   zeros are documented as inapplicable fields for `head=-1`, rather than
   accepted NaNs. Layer-1 normalized inputs and trace API identities are
   asserted on every batch.
3. **Immutable identity/content validation:** before any trace, retained seed,
   mode, step, semantic checkpoint path, config/source/initial identity, stored
   evaluation manifest/final digests, condition keys/shapes/domains/balance and
   data validation are checked. Real seed-11 validation passed after resolving
   the legitimate ROOT-relative `final_checkpoint` declaration semantically;
   no immutable mismatch was found or rewritten.
4. **Aggregation/cap:** raw lists convert once to reusable arrays; cached
   detached dt/gamma values avoid row-loop parameter construction. Guards run
   before/after trace, aggregation, compression, JSON/CSV serialization, and
   plotting, leaving the 30-second reserve and preserving explicit failed
   attempt status.
5. **Attempt/runtime provenance:** records include exact executable/argv/lock,
   PID, UTC start/end, whole-command elapsed time, prior/cumulative charge.
   Runtime artifact separates actual Python/platform/Torch/NumPy/thread/hardware
   identity from frozen experiment config. Existing-output/lock rejections write
   an external rejection record and ledger entry without touching the owned lock
   or output. Attempt-record write failure writes a failed ledger record.
6. **Focused regressions:** added malformed checkpoint/evaluation identity,
   NaN/TV/probability-row rejection, selected retained-checkpoint trace,
   cumulative and post-processing cap, exact provenance/rejection, failed
   record persistence, lock contention/cleanup, final schema/count rejection,
   direct dt0 identity, phase/time, and full manual trace fixtures.

## Commands and outcomes

- `.venv/bin/python -m pytest tests/test_checkpoint_diagnostic.py -q`
  — exit 0, **14 passed in 0.75s**.
- `.venv/bin/python -m pytest -q` — exit 0, **62 passed in 1.53s**.

No process yielded; there is no active session ID. The only read-only retained
check was selected seed-11 input identity/API validation. The one all-seed
diagnostic CLI remains prohibited pending Sol PASS and Astra authorization.

## Ledger

`execution/diagnostics/ledger.jsonl` totals **16.7s**: prior 11.7s,
supervisor hash allowance 1.0s, and conservative Terra revision-test allowance
4.0s. This is separate from the original experiment ledger and far below the
diagnostic 900-second cap.
