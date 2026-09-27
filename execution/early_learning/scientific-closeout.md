# Accepted early-learning diagnostic

2026-09-27. Astra accepts the bounded inference-only study after Sol's exact
results PASS in reviews/07-results.md, SHA-256
0aa15af3aac3d4850cb4da60aa4a54a28822a65e1d8fd4abdeb0393771211394.
The review binds results.md, source identities, raw outputs, paired summary and
accounting. Historical reports remain unchanged.

## Findings

The fixed 800–2,000 window does not establish an SA early-learning advantage.
Mean SA-minus-softmax Q is −0.052 percentage points; KL is +0.001042 and Brier
is +0.000300. Each mean difference has opposite signs across the two seeds.
Q slope differences favor softmax in both pairs; Brier slope differences favor
SA in both, while KL slope differences are mixed. These are descriptive
observations on two existing seed pairs, not a population result.

Dense scoring corrects the sparse-grid impression: unique sampled KL and Brier
minima occur at 900 updates for seed 2201 softmax, 700 for seed 2201 SA, and
2,600 for both seed 2202 models. These are minima on the observed 0–3,000 grid,
not universal optimal stopping points or continuous minima.

For the prespecified 800→2,000 contrast, conditional divergence within oracle
support (B) increases in all four owners. Support-mass loss (A) improves in both
seed 2201 owners but worsens in both seed 2202 owners. For seed 2201 SA, A
improves enough that total KL improves despite increasing B. Mean outside-support
mass falls in all four contrasts. The behavior cannot be reduced to uniform
transfer of probability onto wrong actions or a blanket claim of increasingly
overconfident policies. The four exhaustive argmax-transition groups retain every
state and reconstruct aggregate changes in the audited summary.

Q is valid-route fraction, not full oracle-distribution agreement. Neither these
decompositions nor local fixed-weight dt=0 probes establish causal mechanism,
calibration, or that route gains are purely confidence artifacts.

## Completion and limits

All four owners completed in fixed order: 124 checkpoints, 108 new and 16 reused
proper/Q cells, 124 greedy evaluations and 14 SA probes. The bounded audit and
Sol's independent raw checks passed. Actual debit was 842.3533415840939 seconds
of the separate 1,800-second allocation: A 18.360494249965996;
B 820.0813823339995; D 3.9114650001283735. Owned processes were cleaned up;
no reservation lock remains. Legacy provisional charge labels were resolved
using matching COMPLETE artifacts and driver evidence, not ledger rewriting or
waiving uncertainty.

No training, final-test access or calibration was performed. The 200k run remains
HOLD—USER REQUEST with zero debit. This block is complete; unused allocation
does not authorize further work. Confirmation should be preregistered on fresh
seed pairs, with an independent tuning/calibration split before calibrated claims.
No replacement experiment is launched or authorized by this closeout.
