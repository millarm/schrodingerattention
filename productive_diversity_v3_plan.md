# Productive diversity v3 — larger spatial composition, feasible shared lengths

Status: user authorized planning and execution on2026-09-16 using Terra
implementation and Sol independent review. Astra supervises/specifies only;
the v2 implementation-role exception has ended. Scientific plan FROZEN / ACCEPTED
after Sol00-plan-contract PASS, before any v3 data outcome.
No v3 data/model result exists. Preserve all prior code behavior and artifacts.

## Question and unchanged scientific targets

Can Schrödinger attention learn usable predictions and yield a small reliable
increase in distinct correct structurally novel routes, while most valid outputs
remain known and quality is comparable to capacity-matched softmax?

This is a toy-domain productive-diversity test, not proof of human creativity,
quantum randomness, epistemic uncertainty or a general architecture advantage.
Fixed-input attention is deterministic; sampling randomness is controlled.
The v2 result motivates this redesign post hoc: length quotas failed before any
model was trained, so neither architecture has a result from that iteration.

The v2 learning/decoding/inference protocol is retained, except for the explicit
v3 dataset/representation/seeds/budget changes below. In particular:

- K32 attempts/problem; primary endpoint weighted distinct valid novel routes/K.
  Invalid and duplicate attempts remain in the denominator. Required main gain
  >=.01 absolute, two-sided95% paired-seed CI above0, and >=8/10 positive seeds.
- Deployment mixture80% routine/20% challenge. At least80% of each model's
  weighted valid output mass must be known. The5–15% novel-mass target is a
  design implication of the oracle challenge mixture, not an assumed result
  or a required5% minimum model mass. Use weighted known-valid attempt mass
  divided by weighted valid attempt mass, not average conditional ratios.
- Routine quality equivalence:90% paired CI inside[-.01,.01]. Overall quality
  noninferiority margin1pp and challenge-specific margin2pp, each one-sided95%
  paired lower bound. Failure of any quality gate cannot be rescued by novelty.
- Validation-only temperature fitting to90% mixture quality within.5pp, T in
  [.25,3], at most8 bisections with bracket/monotonicity checks and the same
  predeclared fixed-grid fallback; unmatched policies ineligible. Both main
  policies >=88% test mixture quality; mean absolute paired quality difference
  <=1pp. Fixed T curve {.5,.75,1,1.25,1.5,2}, greedy/T1 and entropy-matched
  softmax controls remain; no test-temperature selection.
- Teacher completion-count q, proper CE/Brier/KL(q||p), entropy versus oracle
  entropy, and nonoptimal-action mass distinguish learned ambiguity from errors.
  No chosen-action confidence-versus-any-valid-action calibration claim.
- Same-weight all-layer dt0 with identical uniforms and validation quality
  rematching remains secondary. If main support holds, >=50% removal of the
  gain and reductions in8/10 seeds support active-evolution dependence; a
  surviving gain may be training-mediated, not absence of usable learning.

All remaining metric definitions, zero-denominator rules, sampling indexing,
map/problem/stratum weighting, two-thousand paired map-cluster bootstrap,
sample-efficiency censoring and interpretation limits are inherited explicitly
from productive_diversity_v2_plan.md. No secondary metric rescues primary failure.

## One larger task and a compact shared representation

Use12x12 grids with exactly eight separated I/L-triomino obstacle components:
24/144 cells occupied (~16.7%). Components cannot overlap or touch orthogonally.
Training and routine maps are homogeneous I^8 or L^8; challenge maps are I^4L^4.
All component orientations must occur in selected training maps. Canonical D4
map identities are disjoint across training/validation/test, including symmetry.

Encode CLS plus12 row tokens (13 tokens). Each row uses a shared linear
projection of36 numeric wall/current/goal indicators,12 of each, plus learned
row position. Column slots are compositional numeric features, never a lookup
embedding for whole rows. Two pre-norm layers, d_model64, two heads, FF128,
four-action CLS head. Both architectures have identical input/data/base weights.
SA retains reviewed dt/gamma initialization and eight active scalars; softmax
has the same eight active score/value scale controls as v2. CPU float32/complex64,
two intra-op threads, one inter-op; no paid resources.

The state/goal is fully visible. Only locally legal actions are masked; no
oracle-optimal mask, repair, search, rejection-resampling or verifier guidance
at generation. Stop at first goal or selected maximum route length. Teacher
q(a|s)=C(next)/C(s) for distance-decreasing actions and0 otherwise, with every
nonterminal shortest-path-DAG state supervised and deduplicated.

## Joint map/length feasibility before models

Increasing spatial/compositional complexity does not require forcing a long,
nearly uniform tail of route lengths. V3 deliberately narrows length variety to
three shared lengths; this change is explicit, not a claim that every notion of
complexity increases. Candidate windows are (12,13,14), (14,15,16), (16,17,18),
(18,19,20). Every selected map contributes16 problems with one of the shared
length quotas (6,5,5), (5,6,5), or (5,5,6). Thus every split has exactly the same
length proportions, and every selected training length has >=16 examples.

The deterministic bounded algorithm is frozen before generation:

1. Generate one fixed pool of at most256 canonical maps per family, at most
   200,000 placement trials/family. Enumerate individual shapes directly:
   I horizontal/vertical placements and four L missing-corner placements.
   Do not repeatedly enumerate all C(144,3) triples. Inventory exact BFS shortest
   lengths/counts for pairs in12..20 with16<=M<=256. Fixed independent streams
   produce a shortlist of at most64 candidate pairs/map/length.
2. For each window and quota permutation, count maps per family whose raw
   shortlist supplies that complete16-problem quota. Required raw joint map
   counts are92 I^8,92 L^8,40 I^4L^4 (all splits together). Reject proposals
   not meeting these necessary raw counts. Rank proposals by minimum normalized
   family supply, then deterministic enumeration-cost and lexical ties specified
   in the contract. Keep the best quota per window and at most three distinct
   windows. Save every proposal score and rank before any support/novelty result.
3. For each retained proposal in fixed order, select32 raw-quota-eligible maps
   per homogeneous family using frozen permutations; take its quota of pairs.
   Construct exact q data and complete nonempty shortest-suffix signature
   support from every supervised DAG state. Signatures identify D4, translation
   and reversal and preserve length. Support is rebuilt for each proposal; it
   cannot be treated as independent of the chosen training problems.
4. With that exact support fixed, lazily scan held-out maps in frozen order.
   Accept a map only if its shortlists supply the entire same length quota
   under the relevant novelty predicate. Routine requires M_novel=0; challenge
   requires M_novel>=4 and .25<=M_novel/M<=.75. Enumerate routes exactly; stop
   scanning a length once its quota is filled, and skip a map if it cannot fill
   a length within its frozen64-pair shortlist. Never weaken predicates.
5. Select validation routine12 maps/family and challenge8 mixed maps; then test
   routine48/family and challenge32 mixed maps, excluding all earlier identities.
   Every map supplies16 problems: train1024, validation384+128, test1536+512.
   This is a sufficient joint-feasibility construction, not a globally optimal
   integer solver. No map is committed to a split before its full quota passes.
6. First proposal passing all strata becomes the frozen dataset. An ordinary
   finite-supply/orientation failure may advance to the next pre-ranked proposal.
   A bug, count mismatch, deadline or resource failure stops without using
   another proposal as a technical fallback. Three scientific failures (or no
   raw-feasible proposal) end the iteration with a reviewed construction stop.

No new pool, length window, quota, map permutation or shortlist is selected
after these bounded outcomes. Failure means this sampled/shortlisted construction
failed, not that no feasible12x12 dataset exists. Oracle uniform challenge
sampling implies5–15% mixture novel mass; actual model mass is measured.

## Learnability, power and runtime gates

Only after a reviewed dataset PASS may the model/harness be built. AdamW lr1e-3,
weight_decay.01, batch64, clipping1, no dropout/schedule/search, shared optimizer
and minibatches. Baseline seed1701 first; checkpoints500/1000/2000/4000/8000.
Select earliest checkpoint >=1000 meeting all v2 learnability gates: validation
greedy>=80%, T1>=70%, Brier>=20% improvement over initial, quality>=20pp above
initial AND uniform locally legal policies, reachable90% decoding point, and
challenge normalized K32 coverage<.90 (headroom). Otherwise stop, without tuning.
Complete five pilot pairs1701–1705 at frozen exposure, reusing1701 baseline;
baseline mean must pass and at least4/5 seeds improve quality/Brier. Main pairs
2101–2110 are fresh. Held-out test model scores are not inspected in pilots.

Use the unchanged corrected v2 variance gate: four independent paired K32
replicates per pilot seed; sbar² between five replicate means, vwithin mean
within-seed variance; upper bounds4*sbar²/chi2(.20,4) and15*vwithin/chi2(.20,15),
s_main_upper=sqrt(sbar_upper²+.75*vwithin_upper). Require single-K32 paired
Monte Carlo SD sqrt(vwithin_upper)<=.002 and
(t(.975,9)+z(.80))*s_main_upper/sqrt(10)<=.01. Pilot mean advantage does not
choose eligibility. This noisy planning proxy does not guarantee combined-gate
power; failure stops, not raises the effect size or substitutes puzzle counts
for independently trained seeds.

Before main pairs, freeze the1.5× measured-cost forecast for every remaining
training, checkpoint validation, cache, operating point, Python rollout,
signature/uniqueness aggregation, proper scoring, serialization, bootstrap and
independent audit plus reserve. Cache inference alone is not the forecast.
Dataset stage reports exact route-enumeration calls/routes and elapsed cost;
bounded lazy scans/caches are necessary, not an assumption of free oracle work.

Architecture support still requires all v2 main gates, including usable learning
on both test strata for both architectures, primary effect, quality matching,
routine equivalence, overall/challenge noninferiority and known-valid majority.
A wide interval is INCONCLUSIVE, not equivalence; one toy domain is not broad proof.

## Budget and process

The total ceiling remains7,200 elapsed CPU seconds across v2+v3. Carry forward
v2 conservative debit443.384519002s once, including its disclosed150s historical
allowance; do not grant a new budget or double-charge recovered old durations.
Remaining6,756.615480998s allocation: dataset/tests/audit1,600s; pilot1,500s;
main training2,200s; evaluation/audit1,100s; reserve356.615480998s. These are
ceilings, not targets. Profile before training. Resource-only redistribution
inside the total cap requires a recorded prospective decision and Sol review;
it must not alter scientific criteria or silently extend a running deadline.

Astra specifies/accepts; Terra implements/tests; Sol independently reviews plan,
contract, exact implementation and results. At most two revision cycles before
bounded respecification or a concrete blocker; no silent role/model switch.
Stage0 is dataset-only, implemented in small complete blocks using proven
helpers with explicit n=12 everywhere; no model scaffold before dataset PASS.
All new artifacts live under execution/next_level_v3, unique immutable attempts,
exact source/config/input/output/runtime hashes, owned lock, one compute process,
interrupting deadlines and append-once chronological UUID ledger. Record full
tool command result and yielded session ID; poll to explicit exit before another
launch, never relaunch a yielded process. Tests use isolated temporary ledgers.

Primary method motivation remains the verified v2 references on joint quality/
diversity and decoding controls (Zhang2021; Alihosseini2019) and calibration versus
entropy (Guo2017). None establishes an advantage for this attention mechanism.
