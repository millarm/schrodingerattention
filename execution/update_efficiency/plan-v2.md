# Fixed training-stage learning curves and updates to common quality

2026-09-27 — revised protocol for independent review. User clarified that
15/30/45/60/75% means fractions of TOTAL TRAINING UPDATES, not quality thresholds.
This supersedes `plan.md` before any new runtime. The old plan, draft code and
review remain historical. Astra specifies, Terra implements, Sol independently
reviews under `agent_execution_protocol.md`; no previous role exception applies.
User authorized writing and launching this separate study. Exact implementation
PASS remains mandatory before production.

Reference: `research/schrodinger_attention_research_paper.md`, SHA
`ed43f1705b0ea1dacf72b722dcb10c4a446e329f8a92375ec0ad0afbc15ed79e`.
Prior seed1701–1705 findings motivate this protocol but are NOT fresh evidence.
Compute, elapsed time, FLOPs and energy are NOT scientific endpoints. Runtime
records below are exclusively safety/accounting, not reasons to prefer a model.

## Fixed experiment

|Item|Prospective contract|
|---|---|
|Fresh pairs|2201,2202,2203,2204, no replacements; verify absence of prior owners|
|Models/data/optimizer|Unchanged accepted70,540-parameter RoutePolicy, training/validation bundles, map-balanced sampler, AdamW lr.001, batch64, clip1|
|Pairing|Same shared initial tensors and all8000 minibatch digests within each seed; seed varies initialization, data stream and decoding uniforms|
|Run order|2201 SM→SA;2202 SA→SM;2203 SM→SA;2204 SA→SM; one process|
|Horizon|Both architectures8000 updates, regardless observed quality/crossings|
|Primary scoring grid|0,1200,2400,3600,4800,6000,8000: baseline,15/30/45/60/75/100% of horizon|
|Checkpoint storage|Unchanged accepted trainer, every100 updates; no extra inference grid|
|Evaluation|All512 validation problems, T1/K32, split1/replicate0; accepted1024-state exact-q proper bank|
|Aggregation|Equal problems within map, equal maps per stratum, mixture.8routine+.2challenge; seeds equal|
|Excluded|No temperature tuning, new model/data/seed selection, final-test loader/payload, prepared JSON parsing, mechanism ablations, paid resources|

Loaders/model/optimizer/trainer/evaluator sources stay byte-identical. Train with
accepted `scheduled_training(validation=None)` then score the seven frozen saved
checkpoints inside the SAME owned attempt. No adaptive feedback or early stopping.
This removes old repeated initial/uniform/greedy/mechanism controls, not optimizer
steps. Save all curves/checkpoints; do not add supplementary scoring after seeing
results. Validation maps are reused: this is fresh-seed replication conditional
on the selected known population, not untouched-map confirmation.

## Main question: is the learning path materially different?

For each seed and scored update u, let ΔQ(u)=Q_SA(u)−Q_SM(u), in percentage points.
Report the complete per-seed paired Q trajectory, routine/challenge Q, exact-q
KL, Brier and teacher entropy. Do not treat checkpoints, maps, states or draws
as independent training replicates. Differences are about learned policies, not
quantum randomness or creativity.

The **primary nonlinear contrast** is fixed before results:

`C = ΔQ(3600) − [ΔQ(1200) + ΔQ(6000)] / 2`.

Those three stages are equally spaced. C measures departure of the architecture
gap from a straight line over15–75% training. A constant advantage or linearly
changing advantage yields C=0; positive C means a mid-stage bulge, not necessarily
overall superiority. This single contrast does not detect every possible curve
shape. Other plotted wiggles or maximum gaps are descriptive, not substitute tests.

Predeclared materiality is |mean C|≥1 percentage point. A **replicated nonlinear
screen** additionally requires the same sign in≥3/4 fresh pairs and a two-sided
95% paired t interval excluding0 (df3, multiplier3.182446, sampleSD ddof1).
These are small-n/normality-sensitive exploratory criteria, not proof. Report all
four C values, mean, SD, range and interval even if the screen fails. Missing pairs
preclude the four-pair screen; report the partial study without replacing seeds.

Secondary fixed stage contrast: mean ΔQ at4800/6000/8000 minus mean ΔQ at
1200/2400/3600. This measures a later-versus-earlier shift, which can be linear;
do not call it curvature. Report both contrasts without selecting whichever is
favorable. Endpoint8000 and all intermediate gaps remain visible. No separate
significance claims across a searched family of stages/metrics.

**Useful-learning guardrails:** a positive Q gap at a reported stage is accompanied
by the paired mean KL gap (SA−SM, lower better) and challenge-Q gap. If mean KL
is worse by>.02nat or challenge Q worse by>2pp at that stage, label the result
mixed, not an unqualified useful-learning gain. These descriptive practical
margins are not statistical equivalence proof. Negative/curved Q differences are
still reported regardless guardrail direction; no metric is suppressed.

## Secondary: updates to equivalent common quality

Report two common quality milestones for BOTH models:30% and38.198% overall Q.
The latter is the paper's rounded historical8k softmax mean, frozen as reference,
not a new-seed moving target. One-percentage-point lower tolerance gives common
thresholds.29 and.37198. This means at least reference-level route success within
tolerance, not formal two-sided equivalence or equivalence of the full policies.
Exact-threshold crossings are supplementary sensitivity, never replacements.

For each threshold use the first pair of consecutive scored checkpoints j,j+1
that both pass, j≥1. Report acquisition at grid[j], confirmation grid[j+1], and
interval(grid[j−1],grid[j]]. Record raw Q and proper/challenge metrics there.
Quality crossing is NOT silently delayed by a different metric's guard. To flag
fragile mastery separately, report whether acquisition KL>.40nat or challenge
Q<.08. These absolute diagnostic flags do not redefine the crossing estimator.
They are frozen pragmatic bands, not established safety or equivalence margins.

Initial0 passing is an anomaly that invalidates an update-saving claim for that
seed/threshold; keep the seed. Nonmonotonic/isolated passes remain visible.
No qualifying adjacent passes means right-censored/unconfirmed by8000. First
pass at8000 is explicitly unconfirmed, not imputed acquisition at8000. No
interpolation or monotonicity assumption. This coarse grid may leave mature
quality unresolved even when the final model reaches it.

For two confirmed crossings report SA−SM updates, SA/SM acquisition-grid ratio,
and conservative ratio bounds[La/Us,Ua/Ls],∞if Ls=0. For censored pairs show
censoring/bounds, not a fabricated8000 or complete-case headline mean. Table ALL
four seeds for each milestone, with earlier/same-grid/later/unresolved counts.
A descriptive20% update-saving screen requires allfour evaluable,≥3/4 earlier,
median grid ratio≤.8,≥3/4 interval upper bounds<1, and no initial anomaly. It is
secondary/exploratory and cannot override the nonlinear primary. Failed screens
do not establish equivalence or absence of an effect.

## Resources, minimal launch and stopping

Qualified inherited debit4764.416447001050/7200; remaining2435.583552998950.
Baseline central ledger SHA
`1340ee945d663e22c7a4fa7bd232c9832b90babe20d3d91662967116d232c3f9`.
Includes administrative300s historical uncertainty, not measured/proven bound.
Preserve the prefix; no reset, new carry or fictional reconciliation.

|New allocation|Maximum charged seconds|
|---|---:|
|A development/setup/tests/failures|100|
|B four paired8000-update owners|1800|
|D aggregation/audit/reporting|100|
|Total|2000|

Prospective resource-only transfer600 of unused D capacity to B establishes caps
A1000/B4100/C0/D800, global7200 unchanged. Current stage totalsA860.001000330,
B2286.766004918,D694.645844500 fit A+100,B+1800,D+100. Maximum qualified
global6764.416447001050 leaves435.58 unallocated, NOT extension authority.

One-owner external envelopes: SM200, SA250 seconds, including startup/cleanup/
finalization. First fixed pair2201≤450 is the minimal launch. Then continue the
other THREE fixed pairs only if1.5×observed complete SM/SA charged costs for all
remaining runs fit remaining B allocation and per-owner envelopes. This gate is
resources/integrity ONLY, never which model wins or hits a target. If forecast
fails, stop with an explicitly partial paired learning-path result. No reduction
of checkpoints, horizon, seeds or model to rescue completion. No automatic retry.

Historical complete8k runs cost169–171s SM and281–282s SA, including the repeated
controls/probes now removed. Thus the cheaper seven-endpoint protocol MAY fit,
but a full four-pair study is not guaranteed. First-pair actual cost decides
continuation prospectively, without using its outcomes. Runtime is not a science
endpoint, and no equal-time comparison is produced.

## Execution gates and output

New protocol/spec Sol PASS → Terra complete additive source/tests → exact static
safety PASS → externally bounded10s smoke then30s suite withinA100 → exact
implementation PASS/Astra acceptance → one owned2201pair → resource gate →
fixed remainder if feasible → independent results audit/report. Full command,
session, explicit exit, EOF accounting and permanent failure artifacts required.

Deliver: per-seed seven-point learning curves, primary C and secondary stage
contrast, both update-to-quality tables/censoring, proper/challenge guardrails,
limits and separate resource appendix. Do not portray15–75% as quality levels.
