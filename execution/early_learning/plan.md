# Dense early-learning diagnostic

2026-09-27. Astra successor plan. The user stopped the 200k extension and
directed an early-learning focus after PR #1's critique. The 200k hold remains
in force. This first block uses existing checkpoints only: no training,
optimizer steps, final-test access, temperature fitting, LR sweep or ablations.
Astra plans/accepts; GPT-6 Luna implements/operates; GPT-6 Sol independently
reviews methodology and exact implementation before inference.

## Question and fixed observations

How do route success and teacher-relative proper scores change during the
first 3,000 updates, and is an apparent early architecture gap stable across
nearby checkpoints? Evaluate seeds 2201 and 2202, both modes, every 100 updates
from 0 through 3,000 (31 checkpoints per owner). These are the existing two training
pairs, not new replications. Preserve all source models, checkpoints and reports.

Reuse the reviewed Q/proper scores at 0, 1,200, 2,000 and 2,400 with explicit
hash-bound lineage; evaluate the other 27 checkpoints per owner. Use the same
512 validation problems and exact 1,024-state proper bank. Route evaluation
uses temperature 1, 32 samples, split 1 and replicate 0, with the original
seeded uniforms and 0.8 routine / 0.2 challenge aggregation. At all 31 points
obtain deterministic greedy route success, policy and teacher entropy, KL, Brier, sampled
route Q, and challenge Q. Greedy success is invariant to temperature scaling
of fixed logits; it is a useful companion, not a complete causal decomposition
of sampled Q into representation learning and confidence.

Read learned per-layer/head dt = 0.5 * sigmoid(raw_dt) and gamma = pi * tanh(raw_gamma)
for both SA owners at all 31 points. At the fixed 0, 500, 1,000, 1,500, 2,000,
2,500 and 3,000 points call the accepted local mechanism probe on its deterministic 128-state
validation subset. Retain attention TV from same-score softmax, CLS TV,
spectral norm of dt H, and full-policy TV/greedy disagreement under dt = 0,
with numerical checks.
This is inference-only dependence on evolution at fixed weights, not a trained
ablation or causal proof. Softmax dt/gamma and SA-specific TV are not applicable,
not estimated as numerical zero. Use per-head/stratum summaries with clear
denominators; no independence claim from states, heads, rows or checkpoints.

## Frozen descriptive summaries

Primary diagnostic window is 800–2,000 inclusive (13 equally spaced points).
For each owner report arithmetic window mean and ordinary least-squares slope
against update/1000 for Q, KL and Brier. Compute SA−softmax paired differences
within each seed for each mean and slope, then equal-seed average and range.
KL/Brier lower is better; Q higher is better. No joint winner if these disagree.
Report entropy and greedy success alongside those summaries. These endpoints
are fixed before the new dense scores but chosen after prior results and the
critique; they are exploratory, not preregistered confirmatory evidence.

Secondary fixed windows 0–1,000, 1,000–2,000 and 2,000–3,000 use the same summaries and
retain overlapping boundaries explicitly. Plot every raw point; show slopes
only as local linear summaries. Do not impose monotonicity or a saturating fit.
Report grid minima of KL/Brier, all ties within 1e−12, and endpoints of their
contiguous tied intervals. Describe them as sampled minima; no interpolation
or claim of exact continuous onset. 1,200 was the earliest previously scored
nonzero checkpoint, so previous results do not locate the true minimum.

Report SD of raw paired checkpoint gaps within each fixed window and SD of
residuals after its descriptive linear fit. Distinguish trend from residual
variation; neither estimates independent replication variance. Do not bootstrap
checkpoints or treat maps/rollouts as training seeds. With two pairs, provide no
p-values, population confidence intervals, sign-test claim or power claim.

Increasing Q together with worse KL/Brier and lower policy entropy is consistent
with sharpening/overfitting but cannot prove that all Q gains are confidence
artifacts. Q measures valid-route fraction, not agreement with the oracle's
full distribution. Discuss greedy success, proper scores and local mechanism
together without claiming that any alone resolves the mechanism.

## Resources and gates

Fresh independent local cap: 1,800 seconds, allocated as stage A 120 seconds for
development checks, stage B 1,440 seconds for inference and stage D 240 seconds
for audit. No historical or revoked 200k budget carry. Historical
ledger remains at SHA ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2.
No paid resources. One compute process, two CPU threads; order: 2201 softmax,
2201 SA, 2202 SA, 2202 softmax. External complete owner envelopes are 300 seconds
for softmax and 360 seconds for SA, totaling 1,320 seconds.
All startup, scoring, probe, serialization, cleanup and failure costs count.
Stop on resource/integrity failure and report missing cells; no automatic retry,
selective checkpoint removal, changed panel/K or outcome-adaptive expansion.

Actual prior proper-score plus Q evaluation averaged 6.43–6.49 seconds for softmax
and 7.24–7.26 seconds for SA; the maximum was 7.405 seconds. The 108 new score
cells forecast about 740 seconds; greedy/probes and startup fit
the additional headroom provisionally. The cap is modest and does not guarantee
completion. Require 2 GiB free; preserve durable per-checkpoint output and timing.

Gates: Sol methodology PASS, bounded implementation, Sol static safety PASS,
one 10-second smoke and one 60-second targeted suite within stage A's 120 seconds,
exact implementation PASS,
Astra acceptance, then sequential inference and independent result audit.
No neural imports or scoring before their gate. Read-only stdlib inspection of
existing JSON/checkpoint hashes does not consume inference budget.

## Successor work, not authorized by this block

Use these curves to design a new preregistered fresh-seed confirmation with a
fixed window and proper-score companion endpoint. Any calibration or tuning
requires a separate training-side held-out panel and independent assessment;
do not fit temperatures or choose best checkpoints on this reused scoring
panel and call the result calibrated generalization. Choose seed count using
an honest uncertainty/precision design; do not accept PR #1's power table without
checking its assumptions. Final-test release requires a separate frozen gate.
