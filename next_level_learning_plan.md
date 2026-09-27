# Next-level test: learned, correct, diverse solutions

Status: EXECUTION AUTHORIZED — user requested a goal to execute this plan on
2026-09-15. Astra supervises; Terra implements; Sol independently reviews.
Prior reports remain unchanged. Execute the gated design within7,200 CPU seconds;
stop at a reviewed feasibility/learning failure rather than relaxing the gates.
Sol plan review: PASS, [review record](execution/next_level/reviews/01-plan-revision.md).
This status-only authorization update does not certify empirical feasibility.

## Hypothesis and evidential boundary

Test whether Schrödinger attention learns a distribution over **different correct
solutions** that generalizes better than matched softmax attention, at comparable
solution quality and sampling budget. This operationalizes useful diversity, not
human creativity. A novel wrong answer earns zero credit.

The earlier diagnostic inspired this hypothesis post hoc: attention changed,
some predictions changed in opposite directions, and no consistent benefit was
established. Those results are not evidence of originality or useful uncertainty.
For fixed weights and input, this attention implementation is deterministic;
Born-rule conversion does not introduce quantum randomness. Randomness here
comes from explicitly controlled action sampling.

Three claims must remain distinct:

1. **Usable learning:** training improves verified solution quality and proper
   distribution scores on unseen problems over untrained/random controls.
2. **Architecture advantage:** at matched quality, Schrödinger attention yields
   more distinct correct, structurally novel solutions than a decoding-controlled
   softmax model, or learns useful behavior with fewer examples.
3. **Mechanistic dependence:** removing evolution from the same trained weights
   reduces that advantage after decoding is re-matched. This is evidence of
   dependence, not proof of uniquely quantum interference or creativity.

## One task: shortest routes through compositional obstacle layouts

A 6x6 grid has six blocked cells forming two disconnected components. Each
component is either an I-triomino (three straight cells) or L-triomino (three
cells forming a corner); components cannot touch orthogonally. The learner
sees the whole obstacle map, current cell and goal, and chooses one of four
cardinal moves. Grid coordinates are explicit. A conventional state encoder
with an action head preserves bidirectional attention; there are no future
answer tokens, causal-Hamiltonian modifications or language-model pretraining.

Training and in-distribution evaluation use II and LL layouts. The compositional
test uses IL layouts: both primitives were seen, their combination was not.
Keep shortest distance 4–10 and the number of shortest solutions M in [4,64].
This deliberately ensures several correct answers without an enormous oracle.
Enumerate the finite shortest-path DAG using BFS distances and dynamic counts.
Reachability, collision freedom, goal arrival and exact shortest length are
verified independently of the model. Report the two training families separately.

The future generator must inventory enough cases before any training. If the
fixed geometry cannot supply the counts below, report a feasibility failure and
propose a revised plan; do not quietly change the board, filters or test sizes.

### Frozen proposed split sizes

| Split | Canonical obstacle maps | Start/goal problems per map | Problems |
| --- | ---: | ---: | ---: |
| Training, balanced II/LL | 64 | 16 | 1,024 |
| Validation, balanced II/LL | 8 | 16 | 128 |
| Unseen-map ID test, balanced II/LL | 16 | 16 | 256 |
| Unseen-composition IL test | 32 | 16 | 512 |

Maps are disjoint after canonicalization under the eight square symmetries.
All starts/goals, intermediate states and routes inherit their map's split;
reversing a route or changing its start cannot cross splits. Deduplicate model
input states within each split. Fixed generation seeds are 41001–41004 in table
order, with deterministic lexicographic tie-breaking and hashed arrays. Match
test/validation/training distance and log2(M) bins using fixed equal-frequency
training-bin boundaries; report any infeasible bin rather than resampling based
on model outcomes. No test item is selected using either model's predictions.

## Teach multiple valid solutions, not one reference answer

For every state on a training problem's shortest-path DAG, let C(s) be the number
of shortest suffixes to its goal. The teacher target is

`q(a|s) = C(next(s,a))/C(s)` for moves reducing distance by one, and zero otherwise.

This generates a uniform distribution over complete shortest routes for a fixed
problem; local uniform choice among optimal actions generally does not. Train
cross-entropy to q using the same locally legal-move-masked, renormalized policy
p used for rollout, not a sampled single canonical route. Illegal moves have
zero p and q; nonoptimal but locally legal moves remain possible and penalized.
Deduplicate state/goal inputs before deterministic shuffled training epochs.
Weight training states equally; report unique states, repeated exposures and
full-route support separately. Teacher distributions and distance labels are
training targets/audit data, never encoder inputs.

During rollout, mask only moves that leave the board or enter a visibly blocked
cell. Never mask nonoptimal moves, use oracle guidance, beam reranking, search,
repair, rejection-resampling, or verifier feedback. The same local-legality
mask is used for every policy. Stop at first goal arrival or ten moves; accept
only a shortest solution. An invalid or overlong rollout consumes its sample.

## Novelty that is not just a new problem ID

Represent a route by its displacement/action sequence; canonicalize under the
eight square symmetries and path reversal, and ignore absolute translation.
Enumerate the **entire shortest-suffix support of every supervised training
state/goal**, including every intermediate DAG state, not just full routes from
original starts or sampled routes. A test route is structurally novel only if its canonical
signature is absent from that support. Distinctness within a problem uses its
exact visited-cell sequence, so two equivalent spellings are not two solutions.
Encode cardinal actions as bytes N=0,E=1,S=2,W=3. Apply each square symmetry
to displacement vectors; reversal reverses the sequence and negates every
displacement. The lexicographically least of the resulting16 byte strings is
the route signature (length is retained). Hash the sorted exclusion set and
independently test transform invariance and suffix membership before training.

For each test problem, record M and M_novel (number of its distinct shortest
routes with novel signatures). Reserve the complete test set and label this
oracle-derived novelty stratum before model training. The primary novelty
analysis requires at least 256/512 IL problems with M_novel >=4, spread over
at least16 test maps. If unavailable,
the novelty claim is not testable in this domain; report feasibility failure,
not a revised novelty definition. Report all 512 IL problems as well, including
zero-novel-support cases, so the stratum is not mistaken for general performance.

This is modest combinatorial originality, not semantic originality, invention,
or a test of creative writing. A different route need not be more useful than
another; correctness and measured coverage establish its limited utility.

## Models and fair training

Use the same two-layer, d_model32, two-head, feed-forward64 encoder and exact
Schrödinger attention mechanism as the prior work. Replace only task embeddings
and classifier: 36 cell tokens plus CLS; cell features encode wall/current/goal,
and explicit row/column positional embeddings are shared across architectures.
No pretrained weights. The output has four action logits.

- Paired comparison seeds: 101,202,303,404,505; separate softmax-only pilot seed909.
- Identical corresponding initialization, state ordering, minibatch64, AdamW,
  lr3e-4, weight decay0.01, clip norm1, no dropout or scheduler. No architecture-
  specific optimizer search. If these fail in the pilot, stop and re-plan.
- Exact dt/gamma parameterization and initialization remain as previously
  reviewed. Schrödinger adds eight active scalars. The primary softmax control
  also gets eight active scalars: per-head score scale exp(alpha) and value scale
  exp(beta), initialized to one. This is a capacity-matched softmax control,
  not eight inert dummy parameters. Report its parameterization explicitly.
- The baseline-only pilot and main comparison both use this capacity-matched
  softmax control; a separate ordinary-softmax training arm is deferred. Initial
  distributions are not identical because Schrödinger starts with nonzero dt;
  matched corresponding weights do not mean identical functions.
- Save checkpoints at updates50,100,250,500,1000,2000 up to the frozen budget.
  Compare equal state exposures; also report actual compute/throughput. Make
  no equal-FLOP, energy or speed claim from equal updates.

## Decoding controls and exact measurements

Use K=32 independent categorical rollouts per problem per operating point,
with common recorded uniform variates for paired models and dt0. No best-of-K
oracle reranking is used to create the primary score. Check K=8 and16 using
prefixes of the same samples; K=32 is the sole primary sampling budget.
Draw inverse-CDF categorical actions in order N,E,S,W. Use independent PCG64
streams seeded by SeedSequence([51001, model_pair_seed, split_id, map_id,
problem_id, sample_id]); IDs are assigned lexicographically in frozen manifests.
Pre-draw ten uniforms per rollout, one per step, even if termination is early.
Reuse the exact arrays across models, dt0, temperature settings and controls;
states may diverge, so common random numbers do not imply identical paths.

Cache logits for every unblocked current-state/goal combination needed by a
problem, including off-shortest states. Caching is not oracle guidance: the
model sees only the legal state, and each rollout still uses its unfiltered
policy. Record both logical action evaluations and actual cache/model time.

Report the quality–diversity curve at T={0.5,0.75,1,1.25,1.5,2}; greedy decoding
is a separate quality reference. Temperature selection uses validation only.
Additionally fit a validation temperature in [0.25,3] by at most eight bisection
steps to target 90% valid-shortest rollout quality (within0.5pp), separately for
each model/seed. Verify monotonicity on the fixed grid; if it fails, use the
grid point nearest the target with deterministic lower-T tie-break and label
the match unsuccessful if outside tolerance. No test-driven temperature search.

Primary test comparison requires both policies' quality >=88% and absolute
paired mean quality difference <=1pp **on the same frozen M_novel>=4 IL stratum
used for primary novelty coverage**; otherwise no same-quality diversity claim
is made. Repeat quality reporting on all IL problems and the ID test, without
substituting those averages for the primary stratum's match.
Always show the full predeclared curve, so a temperature-only tradeoff
cannot masquerade as an architecture gain. As a secondary decoding control,
match each softmax policy's mean entropy to Schrödinger at T=1 on the same
fixed validation state bank using the same bounded search, and report test
quality/diversity. Entropy matching alone is not quality matching.

For each problem, count valid rollouts V, distinct valid routes U, and distinct
valid structurally novel routes U_novel. Invalid outputs never enter diversity
numerators. Main score on the frozen novel-support IL stratum is

`normalized novel coverage = U_novel / min(K, M_novel)`.

Also report valid rate V/K, U/min(K,M), U/K, U_novel/K, pass@32, and concentration
among valid routes. Count all sampled attempts in cost, including duplicates
and failures. U_novel/K is the budget-normalized yield; oracle-normalized
coverage must not conceal the count of useful outputs. Report paired differences,
not only ratios, and stratify distance/M/obstacle family.
Here pass@32 is the indicator V>0, averaged over problems. Concentration is
the pair-collision rate sum_r n_r(n_r-1)/(V(V-1)) among valid routes; report NA
when V<2, together with that exclusion count. For all-problem descriptive
novel coverage, set coverage to0 when M_novel=0 and explicitly label the
structurally unavailable cases; the primary stratum has no zero denominator.
M>=4 and K>0 elsewhere. Never treat an undefined ratio as an infinite gain.

### Learned ambiguity is not error uncertainty

Before training, build each test state bank from all deduplicated goal-reachable,
nonterminal (map,current,goal) states associated with reserved goals; unreachable
states and terminal goals are excluded with counts. Use the same locally legal
masked/renormalized p as rollout and training for every proper score. Compute
masked log-softmax stably; nonfinite logits or zero legal probability mass are
numerical failures, not permission to silently inject a uniform policy.
On this fixed oracle-labeled test state bank, report cross-entropy and Brier score
to the exact q distribution, KL(q||p), oracle entropy H(q), predicted H(p), and
probability mass assigned to nonoptimal actions. Distinguish diversity *within*
valid support from probability wasted outside it. Use untempered T=1 scores
for the learning claim, plus separately labeled decoding-calibrated scores.

Do not compare probability of one chosen action with a binary "any valid action"
label: several actions can be simultaneously correct. Do not call valid-action
mass versus self-sampled validity an independent calibration discovery. Without
a separate held-out correctness predictor, this test establishes distribution
fit/learned ambiguity, not calibrated whole-route success or epistemic uncertainty.

## Stages and limits — user authorized gated execution

Proposed total ceiling: two elapsed CPU device-hours, no paid resources. Allocate
10min oracle/tests, 10min baseline learnability/profile pilot, 60min paired
training, 30min cached evaluation, 5min audit and 5min reserve. Unused allocations
can move only within this ceiling before comparison; caps are ceilings, not targets.

1. **Dataset/oracle feasibility:** inventory split/novelty counts, independently
   verify BFS/counts/q and symmetry deduplication on exhaustive small fixtures.
   Check q sums, valid-action support, rollout verifier and count-normalization.
2. **Baseline-only pilot:** use seed909 and training/validation only, maximum
   2,000 updates/10min. Require greedy validation optimal completion >=80%,
   T=1 valid rollout rate >=60%, and validation Brier improvement >=20% over
   initial weights. The pilot must also attain90% validation quality within
   0.5pp using the declared temperature selection/fallback. If that operating
   point is unavailable, stop/re-plan before comparison. Require diversity
   headroom: at that successfully matched quality-target operating
   point, mean normalized valid-route coverage at K32 <0.90. If learning fails,
   or valid diversity is already saturated, the proposed comparison is
   INCONCLUSIVE/uninformative; stop rather than claiming a negative mechanism result.
3. **Freeze the comparison contract:** choose the smallest listed checkpoint
   budget meeting pilot criteria, with a floor500 updates; profile a short
   untrained Schrödinger batch for feasibility only, not comparative quality.
   If five paired runs plus full evaluation cannot fit the ceiling, stop and
   request revised resources/design. Freeze every hash, budget, checkpoint,
   sampling seed and operating-point selection before any paired quality result.
   Use a conservative projection from measured batch/state/rollout costs:
   1.5 times the sum of all five paired trainings, scheduled checkpoint
   validation, initial/random/dt0 controls, complete state-logit caches,
   temperature/RNG rollouts and summaries/bootstrap/audit, plus300s reserve.
   Already charged tests/pilot time plus this projection must fit7,200s. Include
   failures in the same ledger; a cumulative interrupting deadline stops work
   with failed/partial status, preserves artifacts and releases owned locks.
4. **Five paired seeds and held-out evaluation:** no per-seed early stopping,
   failed-seed replacement, hyperparameter tuning, or favorable checkpoint choice.
   Evaluate initial policies and uniform locally legal random-action control
   with the same K/step caps. Evaluate learned Schrödinger dt0 on the same saved
   inputs/random variates; refit its validation temperature by the same rule.
5. **Independent audit:** regenerate all tables from immutable per-rollout and
   per-state records; include learning curves and quality–diversity frontiers.

The eventual execution must retain Astra specification/acceptance, Terra code,
Sol review, exclusive lock, fresh immutable attempt directories, exact original
argv/source/data/runtime hashes, cumulative deadline and complete ledger.
The caller must print/store the **entire** command result, retain a yielded
session ID and poll it to explicit exit before dependent work. No file-existence
completion inference, no automatic relaunch, no ledger reordering.

## Predeclared interpretation and go/no-go

These are new proposed screening thresholds, not changes to the prior experiment's
gate. For rollout metrics, first average problems within each canonical map,
then maps within each seed, then the five seed means equally. For the primary
novelty stratum, include only qualifying problems and their nonempty maps;
freeze those memberships before training. For proper scores, average unique
states equally within each map, then maps and seeds equally. Report simple
pooled counts additionally, never as a replacement for the primary estimand.

For paired seed effects d_i, use mean(d) +/- t_(.975,4)*sd(d)/sqrt(5).
The quality noninferiority lower bound is mean(d_quality) minus
t_(.95,4)*sd(d_quality)/sqrt(5), and must exceed -0.01. Complement this with
2,000 percentile bootstrap replicates of canonical maps, resampled with
replacement within each seed/stratum, preserving all conditions and paired
model records for each sampled map. Use PCG64 seed61001; average the five
resampled seed means equally, then report2.5/97.5 percentiles. This is a
conditional map-sampling interval, not additional independent training seeds.
No routes or repeated draws from one map count as independent experiments.

**Usable learning gate:** at T=1 on both test sets, trained mean valid-shortest
rate >=70%, at least20pp above both initial-model and random controls, and mean
Brier loss at least20% lower than initial weights, with positive improvements
in at least4/5 seeds. Failure is a learning/benchmark failure, not evidence about
creativity. The pilot uses separate thresholds and no test outcomes.
These magnitude gates apply to equal-seed means for each trained architecture
separately; all required improvement directions must hold in at least4/5 seeds.

**Primary architecture gate:** usable learning passes; quality-match eligibility
above passes; primary normalized novel coverage improves by >=0.05 absolute
and >=10% relative over capacity-matched softmax, with positive effect in >=4/5
seeds and a95% paired seed-level t interval excluding zero. Test quality is
noninferior within1pp using a one-sided95% paired seed-level bound. No ID quality
regression >2pp is allowed. Magnitude/quality gates apply to equal-seed means
on their stated strata; the4/5 rule applies to paired primary coverage effects.
Relative improvement is (mean_coverage_SA-mean_coverage_softmax) divided by
mean_coverage_softmax. If the denominator is zero, report the absolute gain and
classify this relative-gain gate INCONCLUSIVE rather than inventing infinity.
These are deliberately demanding small-screen gates;
five seeds may yield wide intervals. Insufficient precision is INCONCLUSIVE,
not proof of equivalence. Report map-cluster intervals as complementary, not a
substitute for the seed-level architecture interval.

**Evolution-dependence check:** if the architecture gate passes, define per-seed
g_i=C_SA,i-C_softmax,i and g0_i=C_dt0,i-C_softmax,i, using the same primary
stratum, frozen hierarchy and validation-selected quality-matched decoders.
For mean(g)>0, removal fraction is (mean(g)-mean(g0))/mean(g). Require >=0.5
and C_SA,i>C_dt0,i in at least4/5 seeds for active inference-time evolution
dependence. If mean(g)<=0 the fraction is undefined and no dependence claim
is made. dt0 must pass the same primary-stratum quality eligibility and
noninferiority checks before an isolated diversity comparison is interpreted.
If quality cannot be re-matched, report changed overall behavior, not isolated
diversity dependence. If the gain persists under dt0, useful learning and even
an architecture gain can still hold; training-mediated effects remain possible.
This check cannot prove or disprove those training mechanisms and does not
invalidate usable learning. It is secondary, not an alternative primary gate.

**Learning efficiency, secondary:** record state exposures to80% greedy validation
completion and20% Brier improvement, using only scheduled checkpoints and right-
censoring non-crossers. A >=20% exposure reduction in >=4/5 seeds is supporting
evidence only; it cannot rescue a failed primary diversity gate. Report both
unique-state and repeated-example counts plus wall-clock cost.

- Pass: justify an independently replicated, second-domain study of **productive
  diversity**, not a claim of proven general creativity or usable language-model
  originality. No expansion is automatically authorized.
- Quality drops, only invalid uniqueness rises, or softmax temperature/entropy
  control erases the gain: no architecture-specific productive-diversity evidence.
- Poor baseline learning, insufficient novelty/headroom, budget shortfall or wide
  intervals: INCONCLUSIVE; preserve results and stop.

## Methodological motivation

[Zhang et al. (2021)](https://aclanthology.org/2021.humeval-1.3/) motivates examining
quality–diversity tradeoffs and decoding controls rather than one diversity score.
[Alihosseini et al. (2019)](https://aclanthology.org/W19-2311/) motivates evaluating
quality and diversity together. [Guo et al. (2017)](https://proceedings.mlr.press/v70/guo17a.html)
distinguishes calibrated confidence from raw uncertainty. These papers motivate
measurement discipline; none validates this attention architecture or establishes
that quantum-inspired phases cause creativity.
