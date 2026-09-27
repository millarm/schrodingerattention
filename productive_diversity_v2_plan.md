# Productive diversity v2 — a small reliable gain in a mostly routine task

Status: user authorized revised planning AND gated execution on2026-09-15;
FROZEN / ACCEPTED after Sol review01-plan-contract before data generation. No previous source,
checkpoint, dataset or report is replaced. New cumulative ceiling7,200 elapsed
CPU seconds, including sizing, pilots, failures, tests and audits; no paid resources.

## Claim and primary endpoint

Test a modest hypothesis: most valid outputs remain familiar and routine-task
quality remains equivalent to capacity-matched softmax, while Schrödinger
attention generates a small but statistically reliable excess of **distinct,
correct, structurally novel** solutions at the same quality and sampling budget.
The earlier failed benchmark established insufficient novel support in its
frozen6x6 construction, not a model failure. It motivates this redesign post hoc.

Primary effect: at K=32 attempts/problem, a >=0.01 absolute increase in
`distinct valid novel routes / 32`, with paired-seed95% CI above zero. This is
one extra distinct novel correct output per100 attempts, not a5pp normalized
coverage gain or a requirement that half the problems be novel. Count invalid
and repeated outputs in the denominator; repeating one novel route is not
repeated originality. A1pp effect is a proposed minimum useful screening effect,
not a promised outcome. A power-feasibility gate must support it before testing.

This is combinatorial productive diversity, not proof of human creativity,
quantum randomness or calibrated epistemic uncertainty. The attention remains
deterministic for fixed input/weights; generation randomness is controlled.

## One task, efficiently increased complexity

Use8x8 shortest-route problems with disconnected I/L-triomino obstacles, full
state visibility, cardinal moves and an exact BFS/counting verifier. Components
cannot overlap or touch orthogonally. Training/routine problems use homogeneous
III or LLL compositions; novelty-challenge problems use IIL or ILL. Both primitive
shapes and all rotations appear in training, but mixed compositions do not.

There is one **dataset-only sizing ladder**, tried in this exact order:

| Rung | Components | Training families | Challenge families | Shortest length |
| --- | ---: | --- | --- | --- |
| A | 3 | III, LLL | IIL, ILL | 6–14 |
| B, only if A fails dataset feasibility | 4 | IIII, LLLL | IILL | 8–18 |

Both use8x8 and16<=M<=256 exact shortest routes/problem. Pick the first rung
passing all dataset gates. No model is built while sizing; no model outcome,
temperature or architecture score may influence rung selection. Preserve both
attempts if B is needed. If neither passes within the dataset budget, stop with
a reviewed feasibility result rather than inventing another rung.

Encode the map in **nine tokens**, CLS plus eight row tokens, rather than65
dense cell tokens. Each row is a shared linear projection of24 numeric features:
eight wall indicators, eight current-position indicators and eight goal indicators,
plus a learned row-position embedding. Column slots are fixed compositional
features, not a lookup embedding for whole row bit patterns. Both architectures
use identical features, two pre-norm layers, d_model64, two heads, FF128 and a
four-action CLS head. This keeps the matrix exponential9x9 while representing
a larger state space. Compact representation may make learning harder; the
baseline pilot must test this instead of assuming feasibility.

## Dataset construction, novelty and majority-routine mix

Generate a bounded finite pool of canonical maps per family using seeded
component placement, not exhaustive8x8 enumeration. All D4-equivalent maps
share one identity. Freeze pool size, seeds, placement/rejection order and
problem-selection ties in the Stage0 contract before generation. Maximum
100,000 placement attempts/family; collect at most256 canonical maps/family.
Inventory failure is failure of this fixed candidate construction, not a proof
that the domain contains no feasible dataset.

Select64 training maps balanced across homogeneous families,16 problems/map
(1,024 problems). Deduplicate supervised DAG states. As before, teach
`q(a|s)=C(next)/C(s)` for distance-decreasing moves and zero otherwise: all valid
shortest completions are supported, not a single canonical answer. Use the same
locally legal-move-masked policy for training, scoring and rollout. No oracle
optimal-action mask, repair, search, rejection-resampling or verifier guidance
during model generation. Stop at first goal or the rung's maximum route length.

Enumerate **all shortest suffixes from every supervised training DAG state**.
Canonical route signatures preserve length and identify D4 transforms,
translation and reversal; exact visited-cell sequences define distinct solutions
within a problem. Use explicit board size in every reused oracle helper—never
the old6x6 default. Hash the complete exclusion support.

From disjoint held-out maps, build validation and test strata using oracle-only
criteria, never model outputs:

| Split | Routine maps/problems | Challenge maps/problems |
| --- | ---: | ---: |
| Validation | 24 / 384 | 8 / 128 |
| Final test | 96 / 1,536 | 32 / 512 |

Each map contributes16 unique ordered start/goal problems. Routine problems
have M_novel=0. Challenge problems have M_novel>=4 and
0.25<=M_novel/M<=0.75. These are deliberately targeted challenge strata, not an
estimate of novelty prevalence in arbitrary maps. Fix all IDs before training;
maps, starts/goals, intermediate states and reversals cannot cross map splits.

The primary deployment mixture is **80% routine,20% challenge**, with maps and
problems averaged within each stratum and the explicit0.8/0.2 weights applied
afterward. Thus oracle-uniform valid sampling would allocate5–15% of output
mass to novel routes. Actual model novelty mass is measured, not assumed.
Report unweighted raw counts as well; the physical3:1 evaluation sample ratio
is not the estimand's4:1 mixture.

Match the exact shortest-length histogram between routine/challenge evaluation
strata to the training length histogram by predeclared integer quotas/flow.
Training must contain at least16 selected problems at every allowed integer
length; challenge lengths must be inside that same support. If quota/map supply
is infeasible, the rung fails—no novelty merely from longer test paths, no
post-outcome bin merging. Report M and length distributions, signatures by
length, and all strata separately. Exact pool/selection/flow details are frozen
in a Sol-reviewed implementation contract before either rung is generated.

## What “most should match softmax” means

Do not require identical sampled routes, which can differ harmlessly under the
same solution distribution. Operational requirements are:

1. At least80% of **valid generated output mass** is structurally known for
   each model in the fixed mixture; report actual novel mass and the5–15%
   design target separately. The lower5% is not a success requirement.
2. On routine problems, the paired mean valid-shortest rate is equivalent
   within +/-1pp: the two-sided90% seed-level CI lies inside[-.01,.01]. Failure
   to detect a difference is not evidence of equivalence.
3. Overall fixed-mixture valid-shortest quality is noninferior within1pp using
   a one-sided95% paired bound. Challenge-stratum quality must independently
   be noninferior within2pp using a one-sided95% paired bound. A challenge
   failure cannot be hidden by routine mass or rescued by novelty gains.

These gates test a mostly-conventional useful-output regime. A large novelty
gain that violates them does not support the user's specific modest-effect claim.

## Matched learning, decoding and uncertainty controls

Softmax gets eight active capacity-control scalars: per-head exp(alpha) score
scale and exp(beta) value scale, initialized1. Schrödinger retains the reviewed
dt/gamma parameterization/initialization, eight active scalars total. All other
initial weights, minibatches, states and optimizer settings are paired. Use
AdamW lr1e-3, weight_decay0.01, batch64, clip_norm1, no dropout/scheduler or
architecture-specific optimizer tuning. CPU float32/complex64, two intra-op
threads and one inter-op. Report unequal initial functions and actual cost.

Pilot checkpoints: updates500,1000,2000,4000,8000. First use baseline seed701
only; choose the earliest checkpoint >=1000 satisfying the learnability gates
below. Freeze that exposure budget for all later models; no per-seed selection.
Then complete paired validation-only pilot seeds701–705, reusing baseline701
at that frozen checkpoint; comparison seeds1101–1110 are fresh independent
paired initializations. Neither test logits nor test scores are inspected in
any pilot. No comparative mean is used to change dataset, effect size or model.

At each operating point sample K32 categorical rollouts with common independent
uniform arrays indexed by seed/map/problem/sample/step and fixed N,E,S,W action
order. Invalid/duplicate/overlong attempts all count. K8/K16 prefixes are secondary.
Cache logits for all reachable current states at each reserved map/goal, including
off-shortest states, without exposing oracle labels to the model. Cache/model
cost and logical action evaluations are reported separately.

Show fixed quality–diversity curves for T={.5,.75,1,1.25,1.5,2}. Fit a separate
validation temperature in[.25,3] with <=8 bisections to90% fixed-mixture quality,
tolerance0.5pp; require a bracket and monotonicity, otherwise use the nearest
fixed-grid point with lower-T ties. Unmatched policies are ineligible for the
matched-quality claim. Fit an entropy-matched softmax control against SA T1
on the same frozen validation state bank, with the same bounded search.
Entropy matching is secondary, not a substitute for quality matching.

On the final test, both matched policies must achieve>=88% weighted quality
and mean absolute paired quality difference<=1pp, in addition to the CI gates.
Temperature selection never uses test data. Report greedy/T1 quality and the
full fixed curves so the primary result cannot hide a temperature-only advantage.

Measure U_novel/K (primary), V_novel/K (novel probability mass), U_valid/K,
pass@32, exact-support coverage, and conditional-valid duplicate concentration.
V counts every valid attempt including repeats; U counts distinct exact valid
routes within a problem. Average counts/K over problems in each map, then maps
within stratum, then apply0.8/0.2. Known-valid fraction is weighted known-valid
attempt mass divided by weighted valid attempt mass, never an average of local
conditional ratios. Zero weighted valid mass fails the majority/usefulness gate
and gives NA conditional fractions. Valid support coverage is U_valid/M;
novel support coverage is U_novel/M_novel and is NA for M_novel=0. Duplicate
concentration is sum_r(n_r/V)^2 within valid outputs, NA when V=0; report its
eligible denominator rather than converting missing values to zero.
Measure T1 CE/Brier/KL(q||p), H(p), H(q), and nonoptimal-action mass on the fixed
goal-reachable nonterminal state bank; use equal state/map/stratum/seed weighting.
These measure learned ambiguity/distribution fit, not epistemic uncertainty or
calibration of a single chosen action against “any action was valid”.

## Learning, power and resource gates

Proposed allocation under the7,200s hard cumulative cap:900s dataset/tests,
1,500s pilot/validation/power,3,000s comparison training,1,200s evaluation/audit,
600s reserve. Profiling before comparison may redistribute unused time within
the cap, never increase it. Limits are ceilings, not targets.

**Baseline usability:** on validation at a saved checkpoint, greedy shortest
completion>=80%, T1 quality>=70%, and Brier at least20% lower than initial
weights; quality improves>=20pp over both initial and uniform-legal random
controls. The90% decoding operating point must be attainable and normalized
valid-route coverage at K32 must remain<.90 on the challenge stratum (headroom).
If seed701 cannot pass by8,000 updates or its pilot allocation, stop: this
representation/task has not demonstrated usable learning. Do not tune it here.
The completed pilot baseline mean must also meet those gates and at least4/5
baseline pilot seeds must improve quality/Brier over initial weights.

**Power feasibility:** use five validation-only pilot paired differences in
the primary fixed-mixture U_novel/K endpoint, with4 independent K32 sampling
replicates per pilot seed (average four K32 scores, not one K128 uniqueness score).
Let sbar² be the sample variance of five seed means and vwithin the mean of
five within-seed sample variances over four paired K32 replicates. Freeze
`sbar_upper²=4*sbar²/chi2_quantile(.20,4)` and
`vwithin_upper=15*vwithin/chi2_quantile(.20,15)`. Use
`s_main_upper=sqrt(sbar_upper²+.75*vwithin_upper)` to restore the Monte Carlo
variance of the single K32 main endpoint (not a four-replicate main mean).
Require `(t_quantile(.975,9)+normal_quantile(.80))*s_main_upper/sqrt(10)<=.01`
and `sqrt(vwithin_upper)<=.002` for single-K32 paired Monte Carlo SD. Report
every replicate and variance component. These separate80% variance upper
bounds are a normal random-effects planning approximation, not a joint80%
confidence guarantee. This is a planning proxy for detecting1pp versus zero, not a power
guarantee or80% probability of passing every combined gate; five pilot seeds
remain noisy. If it fails, stop as insufficient power at this budget, without
increasing the effect threshold or claiming equivalence. Pilot mean advantage
is not an eligibility criterion, and is reported transparently.

**Runtime feasibility:** before main seeds, freeze a conservative forecast
1.5× measured costs of all remaining20 trainings, checkpoint validation, caches,
all fixed/matched/entropy/dt0 operating points, Python rollout traversal and
uniqueness/signature aggregation, proper-score banks, bootstrap, serialization,
independent audit and remaining reserve. Include any unfinished four-replicate
pilot work. Cached inference alone is not a rollout/evaluation forecast.
Charged work plus forecast must fit7,200s. If not, stop before main results;
no dropping difficult seeds, shrinking test sizes or unreviewed paid resources.

## Main inference and stop/continue decision

Replication units are ten independently trained paired seeds, not thousands
of routes. For each seed average problems within maps, maps within stratum,
then apply0.8/0.2 mixture weights. Primary paired effect d_i is SA minus softmax
U_novel/K at validation-selected quality-matched temperatures. Report mean(d)
and mean(d)+/-t_(.975,9)*sd(d)/sqrt(10); at least8/10 effects must be positive.
Report2,000 paired map-cluster percentile bootstrap intervals conditionally
within seed/stratum as complementary uncertainty, not extra seed replication.

Architecture support requires all: usable-learning gate on both test strata
for both architectures (same quality/Brier improvements, using>=70% T1 quality
and>=20pp over controls); mean primary gain>=.01 with95%CI>0 and8/10 positive;
matched-quality eligibility; routine equivalence, overall and challenge noninferiority;
>=80% known valid mass. Interpret no secondary metric as a rescue if primary
fails. Also show same-temperature and entropy-controlled results descriptively.

Evaluate same-weight SA with all-layer dt0 using identical inputs and random
arrays. Refit its validation quality temperature by the same rule. If the primary
gate passed and dt0 quality is eligible, define removal=(G-G0)/G using equal-seed
primary gains against the same softmax comparator. >=50% removal and reduction
in8/10 seeds supports active evolution dependence. Otherwise the main learned
benefit may persist through training-mediated effects; do not equate a dt0 null
with no usable learning. No parameter sweeps are authorized.

Report sample exposures to80% greedy validation quality and20% Brier improvement
with scheduled-checkpoint censoring, plus actual runtime. Efficiency is secondary;
equal-update comparisons are not equal FLOPs or energy.

A passed result supports only a small productive-diversity advantage on this
verified toy domain. A dataset, learning, power or runtime gate failure is a
reviewed planned stopping outcome, not broad falsification of the hypothesis.
Wide/overlapping main intervals are INCONCLUSIVE, not proof of equivalence.

## Execution discipline

Astra specifies/accepts and, by explicit user role-switch authorization on
2026-09-16, owns implementation/tests for this cycle; Terra is inactive. Sol independently
reviews each complete small block. Reuse verified pure helpers additively, with
explicit8x8 size, and preserve old modules/results/ledgers. New artifacts live
under execution/next_level_v2, unique immutable attempts and a separate UUID/
timestamped append-only ledger. One compute process and owned O_EXCL lock;
interrupting stage/global deadlines; exact source/data/config/runtime/output
hashes. Print/store full command results with `text(r)`, keep yielded session_id
and poll to explicit exit before another launch. Never relaunch on yield.
No later model scaffold before a reviewed dataset feasibility PASS.
