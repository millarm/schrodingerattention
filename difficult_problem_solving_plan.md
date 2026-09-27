# Investigation: useful variation on unfamiliar difficult problems

**PLAN ONLY — execution is not authorized by this document.** Date: 2026-09-19.
Astra plans/supervises; Terra implements only after future approval; Sol reviews
independently. No source changes, tests, training, inference or final-test access
in this planning turn. Preserve all prior plans, data, reviews and results.

## Question and evidence boundary

Does Schrödinger attention improve the probability of solving an unfamiliar hard
problem within a fixed sampling budget, beyond a fairly temperature-tuned softmax
baseline, without sacrificing ordinary correctness? Productive variation means
different **valid** solutions and broader problem success, not merely entropy,
errors, or absence of an action signature from training.

Fresh-four results motivate, but do not establish, this hypothesis: challenge
pass@32 +2.734 pp (3/4 pairs), single-draw challenge Q +0.092 pp, overall
U_valid/K −0.189 pp, unseen-map C Q −0.391 pp. All four early 1k Q differences
favored SA; the final primary mean did not. Training core cost was about 3.22×.
The challenge panel has only **8 maps ×16 problems**. A +3.90625 pp gain is five
extra solved problems, not hundreds of independent discoveries; repeated seeds
reuse those maps. These are post-hoc leads, not new confirmation.

This is a proposed new endpoint/authorization amendment, not a claim that the old
strict-novelty main-study gate passed. The reserved mixed population itself was
selected with Mnovel≥4 and novel fraction .25–.75; reusing it targets that selected
mixed-composition population, not representative difficult planning problems in
general. No silently regenerated test population or old-main authorization.

Keep the existing task: fully visible 12×12 state/goal, eight I/L components,
13 row tokens, learned next-action policy, at most 16 actions, exact legal
shortest-route verifier, no oracle-optimal mask or repair at deployment. This is
reactive sequential decision making, not an explicit search/planning algorithm.
Adding search, longer routes, new puzzles or a new architecture requires a new
plan and approval; none is silently introduced here.

## Stages and the smallest useful first block

|Block|Work proposed after approval|Exit / evidence type|
|---|---|---|
|D0|Retained-data diagnostic only, seeds 1702–1705; no inference|Audited post-hoc explanation or inconclusive diagnosis|
|D1|Validation-only symmetric temperature/control calibration; freeze hard-task support and runtime forecast|Go/no-go before any reserved-test predictions|
|D2|One sealed held-out evaluation of fixed checkpoints/decoding rules|Conditional confirmation on unseen maps, or prespecified failure|
|D3 optional|New training seeds / broader tasks|Separate approval and resource plan; not included below|

**Recommend approving D0 first.** It can establish whether the apparent coverage
gain comes from a few maps, broader success across problems, or more valid route
modes. It cannot establish architecture superiority. No training is needed.
Advancement from D0 is based on the fixed criteria below, not a favorable new
subgroup. D1/D2 require explicit user execution authorization; opening the final
test is an additional explicit release decision after the protocol is frozen.

## D0: retained-data diagnostic contract

Use hash-bound completed replication owners and ordered K32 route attempts at
1k/2k/4k/8k. Seed 1701 remains discovery-only. No repeated inference, new draws,
new cohorts or test-loader calls. Existing route-order caveat remains: raw rows
lack independent start/goal IDs, so bind producer/event hashes and exact dataset
order, corroborate validity, and retain the all-invalid permutation limitation.

For each problem, seed, architecture and checkpoint, compute success at
K={1,2,4,8,16,32}, empirical valid fraction c/32, distinct valid routes/K, distinct
valid routes/M, duplicate concentration conditional on at least one valid draw,
and number of valid routes per solved problem. Report zeros separately, never
silently condition all metrics on success. The main retained-bag estimate is
1−C(32−c,K)/C(32,K), with impossible binomial coefficients zero: chance that a
uniform K-subset of the saved 32 attempts contains at least one success. Expected
distinct valid routes is Σ_j[1−C(32−n_j,K)/C(32,K)], with n_j the count of valid
route j; report this divided by K and by M. At K32 these equal observed full-bag
metrics. Prefix curves are an order sensitivity analysis only. All curves reuse
the same draws, do not extrapolate beyond 32 and are not independent replications.

Make seed×map tables: both/SM-only/SA-only/neither solved, gains/losses by map,
per-problem c/32 distributions, and leave-one-map-out challenge contrasts.
Distinguish (a) success probability spread across more problems from (b) more
distinct valid routes on already solved problems. The same mean Q can produce
different pass@32 because its allocation across problems changes; between-model
route disagreement alone does not establish either form of productive diversity.

Report all predefined geometry bins, not only favorable failures: route length
14/15/16, mandatory detour d=shortest length−Manhattan distance (0 versus ≥2),
and exact shortest-path multiplicity M (1–8, 9–64, ≥65). Use these as descriptive
axes, not a claim they exhaust difficulty. Empty cells remain empty. Baseline-
failure subsets, if shown, are explicitly descriptive and cannot define D2.
Use the original equal-map aggregation within routine/challenge; do not combine
the two transfer settings C and mixed composition as interchangeable evidence.

D0 continuation criterion: artifact integrity passes, every single-map deletion
leaves a strictly positive four-seed mean challenge pass@32 difference (zero
fails), and positive
seed differences occur in at least 3/4 at 8k. These are prospective screening
rules on reused data, **not significance tests**. If a rule fails, stop with a
fragile/inconclusive diagnosis and recommend redesign rather than open the test.
No changing the threshold after seeing the map decomposition.
For each deletion remove the same map from both architectures and all four seeds,
recompute each seed's equal-map mean over the other seven maps, then average the
four contrasts. Do not choose separate favorable deletions per seed.

## D1: difficulty, fair decoding, and frozen confirmation contract

Primary population remains **all selected mixed-composition challenge problems**,
matching D0's motivating signal: 8 validation maps ×16 and, after explicit
release, 32 reserved test maps ×16. This probes unfamiliar obstacle composition,
not a claim every item is equally difficult. Equal weight to problems within
maps, then maps; no 80/20 dilution of the primary mixed-only endpoint.
Below, “hard Q/pass” is shorthand for this complete mixed-composition population,
not the detour-only subgroup.
Mandatory detour d≥2, length and M bins are fixed model-independent secondary
difficulty characterizations, not eligibility gates or “where SA wins.” Report
their full counts before predictions and retain empty/sparse bins without moving
boundaries. No new map generation or exclusion based on any model failure.

Routine controls are ALL original 24 validation and 96 reserved test homogeneous
maps, 16 problems each, both I/L families; equal problem weight within map and
equal map weight overall (families have equal map counts). Bind canonical map,
start, goal and original dataset/selection manifest hashes. Validate exact counts
before prediction; mismatches are integrity stops, not subset substitution.

Use all four fixed 8k checkpoints (1702–1705), no checkpoint selection. For each
architecture/seed, on the complete validation mixed/routine panels evaluate the **same** fixed
temperature grid {0.5,0.75,1,1.25,1.5}, K32, common uniforms; also retain greedy.
Both architectures receive the same search budget and immutable grid. Previously
retained matching-temperature runs can be reused only if input/seed/draw identities
are exact; missing softmax controls must not be inferred from SA's grid.

Shared validation eligibility floors: hard Q and routine Q must each be no more
than 2 pp below that seed's softmax T1 reference. Among eligible temperatures,
select maximum hard pass@32; ties within 1e−12 choose higher hard Q, then lower T.
SM T1 guarantees a softmax candidate; if SA has none, report control failure and
stop D2. Record every candidate, not only selected points. These common floors
are a correctness constraint, not proof of equal quality. Freeze chosen T values,
data/checkpoint/source hashes, seeds, all inclusion rules and analysis code before
test predictions. The repeated validation panel is tuning data, not confirmation.

## D2: one primary endpoint and decision rule

**Only primary endpoint:** paired SA−SM difference in held-out mixed-map
**pass@32**, at 8k and each architecture's validation-selected temperature. Each
seed contributes one equal-map contrast; four seed contrasts form the primary
mean. No pool of route draws substitutes for training-seed replication.
Before predictions bind problem IDs and sampling identities: per training seed,
both models and all temperatures use the same per-problem/per-draw/per-step
uniform arrays, with existing evaluator seed=training seed, splitcode=2 (test),
replicate=0 and K32. Validation remains splitcode=1. Different selected
temperatures do not change the uniform stream; arrays/digests and RNG construction
are retained. Fixed evaluation order SM-first for 1702/1704, SA-first for 1703/1705.

Report all seed differences, mean, SD, range and a small-n descriptive 95% paired-t
interval (df3). Separately cluster-bootstrap whole test maps, using the same map
resample for both architectures/all seeds, to show uncertainty conditional on
these trained models; freeze 2000 resamples and RNG seed 91703. Also report
leave-one-map-out sensitivity. The seed interval and map interval answer different
questions; neither alone represents all data/training uncertainty. No unbacked
power claim: D1 must report expected interval width from validation seed/map
variation and explicitly admit when four seeds cannot support a small effect.
Maps are new; training seeds are **not** new. Call D2 held-out map confirmation
conditional on these checkpoints, not an independent training-seed replication.

Practical evidence gate, fixed before test: mean pass@32 improvement ≥2 pp,
seed interval lower bound >0, and map-bootstrap interval lower bound >0.
Correctness guardrails: hard and routine single-draw Q each have mean Δ≥−2 pp
and their seed-interval lower bounds >−2 pp. Report conjunction failure rather
than cherry-pick one test. These demanding small-n gates may be inconclusive.
They are not a promise of power or a global multiplicity-corrected proof.

Secondary: prefix pass@K curve, greedy, Q, U_valid/K, unique_valid/M, duplicate
concentration, per-problem complementarity, q-relative KL/Brier and entropy versus
teacher entropy. A claim of **more productive route variation** additionally
requires positive mean U_valid/K with seed interval lower bound >0 on that same
hard population; otherwise a pass@32 gain supports broader problem coverage only.
Strict training-signature novelty is supplementary. No entropy-only creativity
claim. Report routine controls and all hard length/M bins, even if negative.

Reuse validation 1k/2k/4k/8k trajectories descriptively to investigate the early
effect. Do not release all test checkpoints or select the best test stage.

## Compute fairness, resources, and authority

Pass@K controls the number of sampled attempts, not elapsed inference cost.
Record actual model forward calls, generated action count, cache construction,
sampling, verification and total endpoint time separately. Reuse identical
batching/cache policy; no claiming a zero-cost cached policy. Report the measured
K32 endpoint latency and training cost alongside equal-update/attempt results.
Do not infer K-specific latency from rarefied or prefix curves: cache sharing and
batching are nonlinear. There is no equal-inference-time claim in this proposal;
dedicated timed K runs would require another prospective budgeted amendment.
An equal-training-time experiment would require a separate frozen
checkpoint-selection design; the 3.22× overhead is not removed by equal K.

Starting operational debit 4156.469097296/7200 s; remaining 3043.530902704 s.
Current stage caps A700/B3500/C400/D1300, used A466.802/B2286.766/C0/D479.898.
Proposed envelopes are maxima, not measured forecasts:

|Future block|Stage|Maximum charged seconds|
|---|---|---:|
|Narrow adapter/tests and failed attempts|A|100|
|D0 retained diagnostic|D|60|
|D1 validation controls + runtime/eligibility profile|D|180|
|D2 held-out scoring|D|420|
|Final audit/report|D|100|
|Unspent reserve (not authority to expand)|D|60|
|Total| |920|

This fits the current A and D headroom (D adds exactly 820 s versus ≈820.102 s
available); global remainder would be ≥2123.531 s. No stage transfer is assumed.
D1 must produce a measured 1.5× forecast of all remaining D2 operations, actual
counts, model/temperature calls, raw I/O, verification and finalization.
D2 includes 8 model endpoints, each 2048 problems (512 mixed+1536 routine) at
selected-temperature K32 plus greedy, and the accepted deterministic heldout
proper-score bank for the same panel. No repeated test-temperature grid, extra
training-stage checkpoints or conditional rescoring. D1's grid is 40 validation
model-temperature endpoints over 512 problems, less exact immutable reusable
calls; reused calls still count in the search budget. Profile bank construction
and selected-state counts as well as batched rollout work. This volume may fail
the envelope; it is a hard feasibility gate, not an assumed runtime guarantee.
If it exceeds 420 s or leaves inadequate audit reserve, stop before test scoring.
A prospective reviewed resource-only transfer within the original cap may be
proposed, not silently applied or used to extend a live deadline. No paid compute.

D3 is not budgeted: ≥8 genuinely new paired training seeds would cost roughly
8×(1805.993/4)×1.5≈5418 s for training alone using the measured replication cost,
already exceeding remaining resources before evaluation. Choose any fresh seed
count and power design prospectively under separate approval, not after outcomes.
Do not portray D2's four old checkpoints as a substitute for D3.
After D2, its panel is consumed for future model/hypothesis selection. Fresh seeds
on that same panel test seed robustness conditional on known maps, not new-map
confirmation after D2-informed tuning. Broader confirmation needs untouched maps
or a fully frozen no-adaptation continuation specified before D2 release.

Future execution requires Astra's bounded specs, Terra's additive implementation,
Sol exact-version PASS, one owned compute process, unique immutable outputs,
explicit command/session exits and append-only ledger accounting. At most two
review-correction cycles, then bounded respecification or blocker. No automatic
implementation follows this plan review. Release final-test eligibility/predictions
only under the explicit future authority described above.

Evidence: `execution/seed_replication/final_report.md`, `trajectories.md`,
`reviews/final-results-review.md`; accepted route data/evaluation/metrics modules.
