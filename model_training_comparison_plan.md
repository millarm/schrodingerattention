# Model training comparison: usability, learning dynamics and useful novelty

Status: **PLAN ONLY — execution not authorized by the 2026-09-19 request.**
Astra specifies; Terra would implement additive code after approval; Sol reviews
the plan, exact implementation and results. No training or implementation starts
in this planning turn. Historical plans, sources, datasets and results stay intact.

### Execution overview, if approved

| Stage | Concrete result | Continue only if |
|---|---|---|
| Build and profile | Reviewed route-policy harness and measured cost | Both initial 1,000-update runs plus evaluation fit |
| First paired result | Seed 1701: softmax and SA at 0, 500 and 1,000 updates | Baseline subsequently passes frozen usability gates |
| Five pilot pairs | Learning curves, operating points and variance estimate | Usability, quality matching, power and full cost forecast pass |
| Ten fresh pairs | Confirmatory novelty comparison plus secondary dynamics | No incomplete/dropped seeds or test-driven tuning |
| Independent audit | Separate usability, dynamics, novelty and mechanism conclusions | Stop and report; no automatic scaling |

## 1. Three questions, three separate answers

1. **Does Schrödinger attention (SA) learn usable policies?** Measure its own
   improvement over initialization and uniform locally legal random actions,
   separately on routine and novel-composition problems. This does not require
   beating softmax.
2. **Does it get there differently?** Compare paired learning curves, sample
   exposures, measured training time, gradients and evolution effects. A different
   trajectory is not necessarily a better one; a faster update curve can still
   be slower in seconds.
3. **Does it yield more useful novelty?** Test distinct valid novel routes at
   matched quality and sampling effort, with temperature/entropy controls. Mere
   entropy, invalid routes or attention changes do not answer this question.

Report separate SA-usability, dynamics, novelty and mechanism statuses. Failure
of a narrow novelty gate must not erase successful learning; inability to establish
equivalence must not be reported as proof of no difference. Fixed-input SA is
deterministic; Born conversion does not supply quantum randomness.

## 2. Frozen dataset and explicit proposed amendments

Use only the accepted pool512 **proposal14**, lengths14/15/16, quota6/5/5, from
`execution/next_level_v3_pool512/attempts/feasibility-001`. Manifest SHA256:
`305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395`;
Sol results review SHA256:
`81fa7253e5e69d5b478227fab5355a098c18ed9d0b4d40155445f9a69e030110`.
Train1,024 problems/64 maps; validation 384 routine+128 challenge; test 1,536
routine+512 challenge. The selected224 maps are disjoint canonical identities.
Do not combine failed proposal12 data or old256-pool training support with this.

Retain all v3/v2 scientific thresholds and main seed lists below. Propose these
explicit amendments for approval, not silent execution changes:

- **Paired entry diagnostic:** train both seed 1701 models to 1,000 updates before
  applying the baseline-first gate. Old v3 could stop before observing any SA
  learning. This bounded, exploratory change guarantees an initial SA observation
  if profiling permits; it does not waive the subsequent baseline/main gates.
- **Bounded proper-score banks:** replace the inherited all-reachable-state
  scoring bank with 32 deterministic states per map for checkpoint/test proper
  scores. Rollout problems and K32 counts remain unchanged. This estimates policy
  fit on a fixed sampled state distribution, not every reachable state. It avoids
  assuming that repeated exhaustive scoring fits the remaining budget.
- **Timing and instrumentation specification:** add exact checkpoint/time/probe
  rules below, disable costly diagnostic forwards in ordinary training, and
  prospectively redistribute unused resources within the same7,200-second cap.

No dataset resizing, larger evolution strength, new optimizer search, seed
replacement or changed novelty effect size is proposed. Inspiration is post hoc
to earlier synthetic-task diagnostics and dataset work; no route-model scores
have been observed. Main seeds remain independent of exploratory pilots.

## 3. Matched models and actual implementation gap

Existing `model.py` is a d32 binary XOR/COPY classifier, not this route policy.
Existing softmax attention lacks the eight capacity-control scalars. Existing
training/timing code and unconditional forward diagnostics must not be presented
as a ready-to-launch route experiment. New additive route model/harness needed;
reuse reviewed exact attention primitives, not old classifier or mutable globals.

Both policies: CLS+12 row tokens, shared linear36→64 projection of row wall,
current-position and goal indicators (12 each), learned row-position embeddings,
two pre-norm layers, two heads, FF128/GELU, final LayerNorm, four-action CLS head.
No dropout. Shared base tensors initialized identically per seed and hash-checked;
separate optimizer states. Both use eight active additional scalars across four
heads: softmax exp(alpha) score/exp(beta) value scales, alpha=beta=0; SA uses
reviewed raw_dt/raw_gamma. SA effective dt=.5 sigmoid(raw_dt), initially.05;
gamma=pi tanh(raw_gamma), initially.1; phase=gamma*S. H=(S+Sᵀ)/(2sqrt(13)),
U=exp(-i dt H), query-row evolution psi0@Uᵀ, probabilities=|psi1|². No new
normalization or approximation. Equal scalar counts are not equal function classes
or equal initial predictions; report both initialization difference and counts.

CPU float32/complex64, two intra-op threads, one inter-op; fixed runtime/hardware
record. Same AdamW(lr=.001, betas=.9/.999, eps=1e-8, weight_decay=.01), batch 64,
global gradient clipping 1, no schedule, no tuning. Apply identical parameter-group
weight-decay policy to all trainable tensors, including the extra scalars.

Legal-action mask covers board edges/walls only, never oracle optimality. Fixed
action/tie order N,E,S,W. At inference stop on first goal or 16 moves. Exact verifier
requires reaching the goal in the problem's shortest length; detours, loops,
early failures, duplicates and overlong attempts stay in metric denominators.

## 4. Supervision, banks and random streams

Load all saved deduplicated nonterminal training DAG states and exact completion-
count teacher q; no canonical single-path labels. q(a)=C(next)/C(current) on
distance-decreasing actions, zero otherwise. Stable CE uses log-softmax over legal
actions and only q>0 terms, avoiding0*(-inf). Brier=sum_a(p-q)² and KL(q||p)=CE-H(q).
Report raw CE and teacher entropy separately: irreducible ambiguity is not error.

Training objective: equal maps, then equal deduplicated states within each map.
Each batch independently samples64 training map IDs uniformly with replacement,
then one sorted state uniformly within each chosen map. Freeze state order
(canonical map ID, goal, current cell). Paired minibatches are precomputed from
PCG64 SeedSequence([95001,seed]) and hashed; each model consumes the identical
prefix. Exposures=64*updates. Report unique state counts and weighted sampling
definition; any64u/N "effective epochs" is a nominal exposure ratio, not full passes.

Before model scores, freeze the scoring banks as follows. For each validation/test
map, take the union of its selected problems' goal cells (deduplicate goals), then
all free current cells with finite BFS distance to each goal, excluding the goal
itself. Deduplicate by (goal,current), not by a path occurrence; each distinct goal
defines a distinct policy task. The training-bank candidates instead are that
map's saved deduplicated supervised DAG states. This deliberate difference in
state distributions must accompany train-versus-held-out score comparisons.

Serialize each candidate as UTF-8 bytes `route-score-v1` plus one zero byte, a
one-byte unsigned board size (12), the 144 canonical-map bytes (each 0 or 1), then
goal and current cell IDs as unsigned two-byte big-endian integers. Rank by
(SHA256(serialized candidate) raw digest bytes, goal, current), with the latter
two fields resolving digest collisions deterministically. Take the first 32, or
all candidates if fewer. No RNG or outcome-dependent resampling. Freeze/save the
full candidate ID list in (goal,current) order and the selected ID list in rank
order. Each list's hash is SHA256 of concatenated four-byte big-endian record
length followed by serialized record; save separate candidate, selected and exact
q-array hashes, counts, serialization version and map identity. Validate cell
indexing and canonical orientation against the saved inventory, never rotate a
state independently of its map. Build banks before inspecting model scores.

Reconstruct oracle q exactly for each selected state. Weight states by 1/N_map
using the actual selected count, then maps equally within stratum, then 0.8 routine
and 0.2 challenge. A map with fewer than 32 states keeps equal map weight, without
padding/duplication; an empty bank is a technical failure. Nominal sizes are 1,024
validation, 4,096 test and 2,048 training states. The complete training-suffix
support is not sampled or changed and still defines route novelty exactly.

Mechanism probes are fixed subsets, not selected by largest effects: first four
canonical maps per I/L training family and first eight scoring states/map (64);
validation first four routine maps per family plus all eight challenge maps and
first eight scoring states/map (128). Record actual smaller counts if unavailable.
No test probes before final test release.

Categorical rollouts use common uniforms across architectures/temperatures/dt0:
PCG64 SeedSequence([95002,seed,splitcode,map_id,start,goal,replicate,sample]) then
16 successive uniforms in step order; splitcode train 0/validation 1/test 2. K32
attempts, K8/K16 prefixes secondary. Independent pilot replicates use IDs0–3;
main replicate0. Keep all IDs/configs and stream hashes. Greedy uses fixed ties.
No model observes q, optimal masks, support membership or verifier feedback in
its inputs/actions. On-demand batched rollout inference may replace a full logit
cache, but must give identical probabilities; profile actual traversal/aggregation.

## 5. Staged execution after a future approval

**Block A — implementation/numerics/profile (cap 400 seconds).** Terra implements
only model/data adapter, reviewed safety harness and metrics; Sol exact-version
PASS before measured runs. Tests: shared tensor/minibatch identity,8 vs 8 active
scalars and finite gradients, legal masking/q normalization, route/signature
verifier fixtures, per-map weighting, checkpoint reload and deterministic resume,
dt0 equivalence to same-tensor unscaled softmax (not the separately trained scaled
baseline), Hermiticity/unitarity/row sums, real one-pair end-to-end smoke, isolated
ledger/output locks and explicit exit. Retain the accepted numerical tolerances:
representative complex64 unitary/row error <= 2e-4, Hermiticity <= 1e-6; dt0
probabilities/output allclose with atol=2e-6, rtol=2e-5. Scheduled runtime probes
abort on Hermiticity > 1e-6 or unitary/row error > 2e-3, as in the accepted old
contract (its representative tests are stricter than its runtime abort threshold).
Include length 13 representative tests and report actual error distributions.
A violation is numerical/implementation failure, not a scientific loss.

Profile fresh throwaway seed 1699 (not a pilot):5 warmup+20 measured training
updates/model and a representative fixed validation rollout/scoring/probe batch.
No test model scores. Record median/p95/update and all overhead. Forecast with 1.5×
measured cost before the first paired diagnostic; if both1,000-update models plus
required scoring/audit reserve cannot fit, report a resource stop without selecting
a faster configuration. Discard profiling weights; never reuse them as a seed.

**Block B — paired early diagnostic and validation pilots (cap 2,000 seconds).**
Pair1701 trains both policies from scratch to 1,000 updates, evaluating at 0,500,
1,000. This runs regardless of early baseline quality, subject to technical/resource
limits. Report each model's initial-to 1,000 fit/quality change and pair difference;
one pair is exploratory, not a reliable architecture effect. If interrupted, keep
both traces and report asymmetric observed exposure, not a completed paired test.

Then follow baseline-only continuation at 2,000/4,000/8,000 until its earliest
checkpoint>=1,000 meeting all inherited validation usability gates: greedy>=80%,
T1 shortest-route quality>=70%, Brier at least20% lower than own initialization,
T1 quality at least20 pp above both initial and uniform-legal random controls,
reachable90% mixture-quality decoding point within.5 pp, challenge normalized valid
K32 coverage<.90. Mixture scores use0.8/0.2; report strata separately. Relative
Brier improvement with zero initial Brier is NA and cannot pass this gate.

Freeze this exposure T for every later model/seed. Explicitly disclose the
softmax-selected stopping-budget asymmetry; never choose T using SA advantage.
Continue1701 SA from its saved optimizer/RNG checkpoint toT if needed. If baseline
never passes by 8,000 or the block cap, stop the confirmatory program: SA's observed
1,000-update result is still reported, but longer-run SA usability remains unknown.
Do not silently fund extra SA-only training or label it incapable of learning.

If baseline passes, complete paired pilot seeds 1702–1705 atT. Baseline mean must
pass and>=4/5 seeds improve quality/Brier over initialization. SA is evaluated
regardless of whether it passes; separately report its own usability. For eligible
paired policies fit validation operating points and take four independent K32
replicates/seed for the inherited power gate (section8). No pilot test predictions.
Stop main if usability, matched operating point, headroom, power or budget fails;
retain all exploratory results rather than claiming architecture equivalence.

**Block C — fresh main comparison (training cap 2,200 seconds).** Only if all gates
and the complete runtime forecast pass:10 paired seeds 2101–2110, each architecture
T updates, no selection of best checkpoints/seeds. Run one model at a time; odd
seed softmax first, even seed SA first, pilots same parity rule. Failure/timeout
does not authorize replacement or dropping the seed; incomplete confirmatory
cohort is INCONCLUSIVE. Save optimizer/RNG/data cursor and source/input hashes.

**Block D — locked evaluation/audit (cap 1,300 seconds).** Validation-only choices
frozen before any test logits/scores. Release the fixed test set only after all
required main runs/operating points have completed. No test curves across training,
model selection, temperature refitting or architecture correction using test results.
Compute final full novelty/quality endpoints and sampled-state proper scores;
Sol audits calculations, provenance and all attempted seeds. Save raw per-problem,
per-map/per-seed values, checkpoints, curves and a concise report. Stop afterward.

## 6. Learning dynamics and timing

Save initial weights, every 100-update checkpoint and the final T checkpoint;
checkpoints contain exact cumulative training timing and data-stream prefix.
Validation quality/proper scores at 0,500,1,000,2,000,4,000,8,000 restricted to<=T;
also evaluate frozen equal-time selected checkpoints after runs, on validation
only. Training CE/loss every update; gradient/parameter summaries every 100 updates.
No interpolated or extrapolated model metrics.

At every scheduled validation checkpoint, the same **T=1, K=32** rollouts also
yield U_novel/K, U_valid/K, V_novel/K, invalid rate and duplicate rate (V-U_valid)/K.
Save routine/challenge and weighted mixture values with raw counts. These show
when valid novelty emerges, without changing decoding temperature at each step.
The quality-matching search and full temperature curves occur only at the frozen
final exposure. Charge checkpoint rollout/aggregation costs in profiling forecasts.

Training-only seconds include batch materialization, forward/loss/backward,
finiteness checks, clipping and optimizer step. Exclude and separately measure
checkpoint I/O, scalar logging, evaluation and diagnostics. Disable invariant
matrix probes during normal batches; scheduled probes are detached/inference-mode
outside the timing loop. Also report complete end-to-end time, CPU configuration,
run order, cache/rollout/signature costs and resident-memory proxy. These are elapsed
CPU measurements, not FLOP, energy or pure hardware-causal claims.

For each pair, c=min(final cumulative training seconds of its two T-update runs).
At c/4,c/2,3c/4,c, choose each architecture's last saved checkpoint whose measured
training seconds<=cutoff; report actual updates/exposures, realized times and slack.
Use initialization only when no trained checkpoint qualifies and mark it clearly.
Never call a later checkpoint equal-time or pretend unequal slack is exact equality.
If slack exceeds10% of the cutoff, label that equal-time point too coarsely resolved
for efficiency interpretation; retain it descriptively. No extra training needed.

Predeclared dynamics summaries: per-seed normalized trapezoid AUC of validation
KL over the common scheduled update grid throughT (lower better); paired final
Brier/quality; checkpoint-wise raw curves and equal-time endpoints; exposures and
seconds to 80% greedy validation quality and 20% Brier improvement, separately and
jointly. First crossing lies in(previous checkpoint,current checkpoint], never
an invented exact update. Not reached byT is right-censored (>T), notT itself.
If only one model reaches, report censoring rather than a finite speedup ratio.
Efficiency/material-difference claims remain secondary exploratory summaries;
no multiple-curve winner selection or novelty rescue. Ten seed-pair CIs accompany
predeclared summaries; do not count checkpoint points as independent replicates.

Log preclip global/group gradient norms, clipping frequency, update/weight norm
ratios (NA at zero reference), and per-layer/head dt/gamma or baseline alpha/beta
every 100 updates. At scheduled score checkpoints, fixed probe banks measure:
direct A_evolved vs softmax(S) TV on the *same SA hidden states*, all rows/CLS
separately; projected attention-output absolute RMS and relative RMS; ||dt H||₂,
relative phase dispersion; full-path normal-vs-dt0 policy TV, KL/Brier/CE changes
and greedy disagreement. Report mean/p50/p95/max and per-head/per-stratum values;
absolute differences prevent signed cancellation. Separate direct local changes
from propagated later-layer changes and independent trained-model comparisons.
Same-trained-SA dt0 is a counterfactual dependence check, not an independently
trained softmax control or causal proof of beneficial interference.

## 7. Quality, diversity and control policies

**Quality always means exact-valid-shortest attempt mass:** Q=V_valid/K, where
V_valid counts every successful attempt, including repeated routes. It is not
U_valid/K (distinct valid yield), pass@K, local-action accuracy or conditional
validity after rejecting failures. Greedy uses one deterministic attempt/problem
(K=1); T1, temperature fitting, initial/uniform controls, quality matching,
noninferiority/equivalence and test quality gates all use K=32. These definitions
apply to every occurrence of quality in this plan, including stopping rules.
Average Q over the 16 problems within each map, then equally over maps within
each stratum, then apply 0.8/0.2. Per-stratum gates omit the final mixture step.
The common uniform streams in section 4 apply to all sampled quality estimates;
replicate 0 is used for checkpoint gates, temperature fitting and main outcomes.
Initial controls use each model's own saved initial weights, identical inputs,
K and uniforms; uniform-legal uses probability 1/number_of_legal_actions and the
same uniforms. Temperature searches reuse the same uniforms at every candidate.
The four pilot variance replicates keep the frozen fitted temperatures, vary only
replicate ID and remain four separate K32 estimates, not merged K128 uniqueness.
The challenge headroom quantity is mean U_valid/M at K32, not Q or U_valid/K.

Inherited final estimand: average problems within map, maps within stratum, then
0.8routine+0.2challenge. With K32 attempts/problem, primary U_novel/32 counts
distinct exact valid shortest routes whose canonical signatures are outside the
complete saved training-suffix support. Invalid and duplicate attempts count in
the denominator. Also V_novel/32 (including repeated novel attempts), U_valid/32,
pass@32, U_valid/M, U_novel/Mnovel, valid duplicate concentration sum(n_r/V)²,
and raw counts. Routine novel coverage is NA (Mnovel0), V0 conditional metrics
are NA; zero total valid mass fails usability/known-majority gates.

Fit each final policy temperature on validation only in[.25,3], <=8 bisections
for90% mixture quality with.5 pp tolerance, bracket and monotonicity checks; if
failed use nearest-quality T from fixed grid{.5,.75,1,1.25,1.5,2}, lower-T ties.
If still unmatched it is ineligible, not relaxed. Use common uniforms; finite-K
curves may be nonmonotone and this must be recorded. Show greedy/T1 and all fixed
grid quality–diversity points regardless of primary outcome. Softmax entropy-match
to SA T1 uses same bounds/search/fallback on validation proper-score bank, entropy
tolerance.01 nats; infeasible match is explicitly unavailable, not forced.

All-layer dt0 at final SA weights uses identical uniforms, fixed T1 and a separately
validation-rematched quality temperature. If primary support holds and dt0 is
quality-eligible, inherited active-evolution check is gain removal>=50% with a
reduction in>=8/10 seeds. A surviving gain may be training-mediated; no dt/gamma
sweep or retraining ablation is authorized by this plan. Proper scores describe
fit to multi-solution q, not epistemic uncertainty or confidence in route success.

## 8. Confirmatory gates, inference and feasibility

Preserve pilot power formula from v2: five seed means of four paired K32 replicate
effects; between-seed variance sbar² and mean within-seed variance vwithin.
sbar_upper²=4*sbar²/chi2(.20,4), vwithin_upper=15*vwithin/chi2(.20,15),
s_main_upper=sqrt(sbar_upper²+.75*vwithin_upper). Require sqrt(vwithin_upper)<=.002
and (t(.975,9)+z(.80))*s_main_upper/sqrt(10)<=.01. This is a noisy planning proxy,
not a guarantee of joint gate power. Pilot mean advantage never selects eligibility.

Main experimental unit is each of 10 independently trained seed pairs. Primary
paired mean gain in quality-matched U_novel/K must be>=.01, paired Student-t95% CI
strictly above 0, and>=8/10 positive seeds. Both architectures must demonstrate
test usability on each stratum: T1 quality>=70%,>=20 pp above own initial and
uniform-legal controls, Brier>=20% improvement over own initial sampled-state bank.
Both matched policies require>=88% mixture test quality and mean absolute paired
quality difference<=1 pp. Routine quality equivalence requires paired90% CI within
[-.01,.01]; mixture noninferiority one-sided95% lower bound>=-.01; challenge
noninferiority lower bound>=-.02. Each model's weighted known-valid attempt mass
divided by weighted valid attempt mass must be>=.80 (not average conditional ratios).
Use2,000 paired map-cluster bootstrap samples within seed/stratum as complementary
conditional uncertainty, never additional independent seeds. No secondary metric
can rescue failure of this composite primary novelty claim.

Budget starts at 923.003597253 of 7,200 elapsed CPU seconds:6,276.996402747 remain.
Proposed prospective allocation: A400+B2,000+C2,200+D1,300+reserve376.996402747.
All setup/oracle work, tests, profiling, failed attempts, I/O and audits count;
do not reset historical allowances or infer unused budget from model time alone.
Reconcile latest ledger before execution. Preserve at least120 seconds for final
independent audit and 30 seconds for failure finalization inside these allocations.

Forecast1.5× measured remaining training, every scheduled checkpoint, proper bank,
greedy/T1/K32/pilot replicates, temperature search/fixed curves/entropy/dt0, Python
rollout/uniqueness/signature work, bootstrap/serialization/audit and reserve before
initial diagnostic and again before main. Count both architectures and all seeds,
not just cached tensor inference. If infeasible, stop at reviewed exploratory
findings; no seed/test reduction, relaxed criteria, larger cap or paid resources.
Resource-only redistribution inside cap requires prospective Astra decision/Sol
review, never a live deadline extension or scientific change.

## 9. Artifacts, review and approval

After approval use new `execution/model_training_comparison/` only. Work contracts
remain bounded: A1 adapter/model/numerics, A2 metrics/timing/safety and tiny complete
smoke/profile, B pilots/gate report, C main runs, D summaries/independent audit.
Each complete implementation gets Sol exact-version PASS; at most two correction
cycles before bounded respecification or explicit blocker. Preserve original source.

Owned fail-if-output-exists lock, unique immutable attempt directories, one compute
process, true UTC generated by process/clock, exact source/config/data/initial-state
and output hashes, append-once UUID charges. Print full command results, retain
yielded session ID and poll to explicit exit before another launch. Failed attempts
are never overwritten or selected away. Save raw checkpoint metrics, predictions,
per-map/per-seed endpoint tables, all uniforms/stream identities, censoring, elapsed
costs and learning/quality–diversity figures. No logging every attention matrix
for every batch; bounded probe arrays suffice.

The user must approve execution of this plan, including the paired diagnostic,
bounded scoring banks and prospective resource allocation. Plan-review PASS means
the specification is reviewable, not that models learn, budget feasibility is
established or execution has started. No Terra activation in this planning turn.
