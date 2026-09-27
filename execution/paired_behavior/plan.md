# Exploratory paired behavior continuation — 2026-09-19

User authorization: “Execute on that next experiment.” This explicitly replaces
the earlier baseline-first stop for this ONE paired seed. Astra specifies,
Terra implements additive analysis only, Sol independently reviews. No prior
implementation exception carries forward. No new models, data, seeds, optimizer
choices, test predictions or paid resources. Previous results remain unchanged.

## Fixed training and budget

Resume seed 1701 Schrödinger from its immutable 1,000-update checkpoint to 8,000
with the existing reviewed training command, same initial checkpoint, optimizer,
sampler/RNG and all frozen identities. Retain natural events at 2,000/4,000/8,000
and checkpoints every 100 updates. Reuse existing softmax results/checkpoints.
Validate initial shared-parameter digest, exact source/config/input identities,
resume hashes, and EVERY paired batch digest over updates 1–8,000. Mismatch
invalidates a paired comparison; do not silently retrain or repair history.

Starting debit: 1784.099195462031/7200 seconds. Prospective resource-only envelope
is 2200 seconds (parent approved before execution): development 80, resumed
training at most the existing B balance 1711.951495791 seconds, behavior analysis
300, independent reviews/audit 80, contingency 28.048504209. This replaces an
initial planning allocation of 1200, not a user/global budget increase. Existing
B/D balances suffice; the unchanged runner enforces its existing B deadline.
No resource wrapper or source changes are needed. Sol must review the exact
command/decision before training. All charges remain in the original ledger;
records here merely index them. One compute process, unique outputs, full
session results and explicit terminal exits; never relaunch on yield.

## Block 1: paired trajectories (existing reviewed runner)

One resume attempt, bounded by the existing B allowance. Preserve
all raw events and curves. At updates 1,000/2,000/4,000/8,000 compare full validation
512 problems: greedy and T1/K32 success, KL(q||p), Brier, CE, nonoptimal mass,
entropy_p and entropy_q; routine/challenge separately and frozen 80/20 mixture.
Report all training CE curves, gradient/update summaries, Schrödinger parameters
and existing local/dt0 mechanism probes. Teacher entropy is not error uncertainty.
Report cumulative measured core time and end-to-end cost separately. Equal-update
exposure is 64×updates; do not call this equal CPU time. Any displayed time-aligned
comparison uses latest existing scored checkpoint at/before a common cutoff,
with actual update counts and no interpolation or untrained extrapolation.

## Block 2: small additive behavior analysis

Prefer postprocessing stored full-validation records; no duplicate inference.
Use every saved problem in its original order, verify identifiers and q/row order.
At 1,000/4,000/8,000 report:

- Greedy problem outcomes: both solve, softmax only, Schrödinger only, neither.
  Separately pair sampled success fractions and pass@32; never treat samples as
  independent training replications.
- On identical saved states: TV=0.5 sum|pSA−pSM|, argmax disagreement with N/E/S/W
  tie order, split into both q-optimal, SM-only optimal, SA-only optimal, neither.
  Retain per-state/per-map values, mean and p50/p95, no signed cancellation.
- Per-problem valid route sets: intersection/union Jaccard (both-empty NA, report
  denominator), counts of SA-only/SM-only valid routes, distinct valid novel
  routes/signatures against the complete saved training support. Invalid route
  differences do not count as novelty. Report U_valid/K32, U_novel/K32,
  V_novel/K32 and quality together; retain raw sets/counts and equal-map summaries.
- Ambiguity-aware uncertainty: CE/KL/Brier versus exact completion-weighted q,
  predicted/oracle entropy and their signed/absolute difference. Optional simple
  distribution-reliability table uses fixed probability bins [0,.1,...,1] on
  legal actions, comparing mean p with mean q (not chosen-action probability
  versus binary validity). No epistemic or whole-route calibration claim.

At 8,000 only, predeclared modest quality control: use existing softmax T1 quality
as target and evaluate SA temperatures .75 and 1.25 in addition to retained T1.
Choose closest mixture Q, lower temperature breaks ties. A match requires |ΔQ|≤.02
AND routine and challenge |ΔQ|≤.03; otherwise explicitly unmatched. Report every
temperature and its quality/novelty, not only selected point. This is retrospective
validation-based descriptive control, not test confirmation or broad tuning.
Same K=32/common-uniform seed1701, replicate0, splitcode1. Any residual confounding
precludes novelty-advantage claims. No search beyond this three-point grid.

## Block 3: fixed transfer cohorts, no reconstruction

Read/hash-bind `execution/model_training_comparison/threeway-diagnosis-001/`
`matched_support.json` and existing softmax scores. Reuse exact saved A/B/C rows,
route order, q and quotas; do not rebuild, select or enlarge cohorts. Score only
SA at 1,000/4,000/8,000 using identical proper/greedy/T1K32 settings and A/B split0,
C split1. Report paired architecture differences within each cohort alongside
the prior residual geometry/multiplicity confounds. All24triplets,144routes and
768states/cohort remain frozen. No causal ranking of goal versus map bottlenecks.

## Acceptance and stop

Sol reviews this amendment and exact training authorization before SA continuation.
Terra supplies one compact additive analysis job, tests literal paired set/count
math (including both-empty), state alignment/TV/tie handling and frozen-cohort
loading; Sol reviews exact implementation before inference. No monolithic new
runner, no modification to accepted modules. Two correction cycles maximum.
If a technical/scientific gate fails, preserve completed evidence and stop the
affected block rather than changing models/cohorts. Audit results and identities,
then report architecture learning, trajectory differences, behavioral diversity,
uncertainty and transfer separately. One seed can demonstrate differences in
this run, not a statistically established architecture advantage or creativity.
