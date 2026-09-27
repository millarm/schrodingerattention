# Exact Schrödinger attention: initial research decision

## Decision: INCONCLUSIVE — do not scale on this evidence

The reference implementation passed independent numerical and harness review.
The retained checkpoints show no qualifying modelling advantage, and only one
of three paired seeds reliably learned XOR. Both architectures fall below the
frozen mean-validation-XOR adequacy threshold of 80%. Separately, execution
provenance invalidates the controlled timing/equal-time comparison. This is
not a negative scientific verdict on amplitude evolution.

## Retained equal-update results

Each retained endpoint is at 2,000 updates / 128,000 examples. Values are accuracy
percentages, mean ± sample SD across seeds 11, 22, and 33. Sol verified that current
checkpoints, continuous raw logs, shared initialization, input streams, fixed
evaluation data, and integer metric counts are internally consistent. Earlier
duplicate-attempt versions are not recoverable, so these are descriptive
results from retained artifacts rather than an unqualified clean six-run study.

| Endpoint | Softmax | Exact | Mean paired difference |
| --- | ---: | ---: | ---: |
| Validation XOR |71.88 ±25.05|73.70 ±23.43|+1.82 pp|
| Held-out-pair XOR, 4 distractors (primary) |70.90 ±22.27|72.92 ±21.55|+2.02 pp|
| Seen-pair XOR, 8 distractors (secondary) |67.19 ±24.55|68.82 ±25.81|+1.63 pp|

Primary paired differences are +2.34, +2.54, +1.17 percentage points (sample
SD 0.74 pp). Secondary differences are +2.93, −1.56, +3.52 pp. Neither mean reaches
the prespecified 3 pp threshold. COPY passes the material-regression check:
mean changes are +0.59 pp on held-out/d4 and +0.72 pp on seen/d8.

Only seed 33 reaches the 90% and 95% validation-XOR targets. Both models first
reach 90% at 51,200 examples; softmax first reaches 95% at 57,600, exact at 64,000.
The other seeds are right-censored at 128,000 examples. The three-pair 20%
sample-efficiency gate therefore cannot qualify. Target resolution is 6,400
examples; no interpolation or favorable checkpoint selection was used.

Disabling evolution does not remove the small retained gains. Mean
normal-minus-dt0 XOR change is −0.065 pp on the primary endpoint and +0.065 pp
on the secondary, far below the required 1 pp intervention effect. This does
not support attributing the differences to Schrödinger evolution, and would
not establish useful interference even if the intervention were larger.

## Numerical and resource evidence

The exact module implements row-state evolution `psi0 @ U.T`, complex64 exact
matrix exponentiation, and no probability renormalization. Independent tests
covered Hermiticity/unitarity, norm preservation, dt0 softmax equivalence,
double-precision gradients, finite gradients, and optimization. In retained
normal validation/final evaluations, maximum Hermiticity error is 0 and maximum
unitarity/Born-row error is 1.20e-6, below the 2e-3 training guard. Learned effective
dt spans approximately 0.0458–0.0883. Exact has 18,506 parameters versus 18,498 for
softmax; the eight extra scalars were disclosed before training.

Hardware: Apple M4 Mac mini, 10 cores, 24 GB; CPU, two Torch threads, one inter-op
thread; PyTorch 2.14.0 / Python 3.12.14. MPS was unavailable. Recorded checkpoint
process RSS spans roughly 305–331 MB; this is a process proxy, not tensor-only
memory or a verified final-evaluation peak. No accelerator-memory value exists.

## Execution limitation: timing and equal-time results INVALID

The ledger contains eight training attempts and five pair evaluations (four
successful, one failed), rather than the intended six training jobs. Follow-up
commands were issued after 30-second tool yields without confirming earlier
process exit. Seed 22 softmax and seed 33 exact reused output directories;
earlier checkpoints/log versions may have been overwritten. Non-overlap and
attempt-specific timing cannot be reconstructed reliably. The seed 22 pair
failure detected raw logs extending beyond a saved checkpoint.

All surviving timing/equal-time artifacts are retained with invalid-comparison
labels. They must not support claims about wall-clock efficiency, overhead,
energy, or FLOP matching. Training and failed-attempt charges remain counted;
the four-hour cap was not approached. Final charged compute is 393.95 seconds
(6.57 minutes / 0.1094 CPU-hours), including explicit historical overhead
allowances. This is a conservative budget account, not recovered actual device
wall time; see the current status/ledger.
No reruns were made to conceal or repair this provenance gap.

## Recommendation and reproducibility

Stop this initial screen without scaling to language models or approximations.
If a new experiment is authorized, first ensure unique attempt directories and
confirmed process exit, then predeclare a diagnostic that makes both models
learn XOR consistently across seeds. Do not select a favorable seed or extend
this run after inspecting its results. No further training is authorized here.

Reproduce descriptive aggregation with `.venv/bin/python -m schrodinger.summarize`.
See [machine-readable summary](results/summary.json), [CSV](results/summary.csv),
[learning curves](results/learning_curves.png), [raw retained runs](results/measured/),
[contract](experiment_contract.md), [numerical review](reviews/01-attention.md),
[harness review](reviews/02-harness.md), and [execution audit](reviews/03-comparison.md).
The Block 4 review and completion status are linked from [status](status.md).
