# Exact Schrödinger Attention on an Oracle Route-Policy Benchmark

## A bounded empirical record through D1

### Abstract

This paper reports the completed empirical record for an exact, classical
implementation of Schrödinger attention (SA): complex attention amplitudes are
initialized from softmax probabilities, evolved by a unitary matrix exponential,
and measured with squared magnitudes. The scientific question was deliberately
modest: under a matched small-model route-policy task, does this primitive learn
meaningfully different and better policies than softmax attention? The answer is
mixed. Exact amplitude evolution is numerically viable, is not merely inert, and
can produce substantially different attention distributions and policies. Both
SA and softmax learn the oracle route task. A discovery pair (seed 1701) favored
SA at 8,000 equal updates (+2.94 percentage points [pp] valid-route quality;
+5.38 pp on an unseen-routine-map cohort), but SA's measured training-core cost
was about 3.27 times softmax's. In four fresh paired replications, the frozen
primary outcome instead favored softmax by 0.449 pp on average (SA minus softmax
95% descriptive paired-t interval [-3.372, +2.474] pp; one positive pair of
four). A small challenge pass@32 difference at the untuned temperature
(+2.734 pp) shrank to +0.781 pp after a symmetric, predeclared temperature
selection with quality floors; its seed interval was [-5.050, +6.612] pp and
only two pairs favored SA. Thus the evidence supports *different learned
policies*, not a robust quality, diversity, transfer, or “creativity” advantage.
No model-bearing evaluation exists on the reserved route-policy final-test split.
This is a reproducible research
record and a basis for deciding whether a narrowly powered confirmation is worth
authorizing, not evidence for language-model scaling or quantum computation.

## 1. Question and scope

Softmax attention turns query--key scores into a non-negative distribution. The
proposal behind this work was that a latent complex amplitude state could give a
network an additional route to reinforcement and cancellation before it is
reduced to an ordinary probability distribution. This is a mathematical,
classical hypothesis: it does **not** posit quantum hardware, quantum randomness,
or a physical quantum state in the model.

The original research proposal set a broad programme spanning synthetic tasks,
language modelling, scaling, and causal attention concerns
([proposal](../schrodinger_attention_research_proposal.md)). The completed work
is far narrower. It establishes and evaluates a short-sequence, bidirectional
route-policy reference model with an exact shortest-path oracle. It does not
evaluate a causal language model, long contexts, approximate or fused kernels,
energy use, or scaling laws. Those distinctions matter: an exact short-sequence
reference can validate a mechanism and expose failure modes, but cannot answer
whether the mechanism is economically useful in a transformer deployed at scale.

The central comparison was frozen in internal execution plans: matched softmax
versus exact SA on the same 12x12 grid-policy data, architecture, optimizer,
updates, within-pair initialization, batch stream, and evaluation draws. The
main unit of architecture replication is a paired training seed, not individual
states, problems, maps, rollouts, heads, or checkpoints. This paper retains
unsuccessful dataset stages and provenance limitations rather than
retrospectively presenting only the successful benchmark construction or the
favorable discovery seed.

### Related work and terminology

The conventional baseline follows the attention framing of Vaswani et al.,
[*Attention Is All You Need*](https://arxiv.org/abs/1706.03762). Recent adjacent
preprints include Nahid et al.'s phase-aware score-factorization method,
[*Q-Interference*](https://arxiv.org/abs/2608.17288), and Reinhardt and Hauser's
Born-rule analog for simplex softmax, [*A Quantum Roadmap for Softmax
Attention*](https://arxiv.org/abs/2608.11173). They are cited as related
preprints, not as an exhaustive review or a priority claim. In particular,
Born-rule terminology by itself does not establish additional expressivity or a
performance benefit. The implementation here is distinct from phase-aware
factorization: it explicitly forms a real symmetric Hamiltonian, differentiates
through one exact matrix exponential per head/batch score matrix, and applies
that evolution to each attention row.

We use “Schrödinger” as a description of the update equation, not as evidence
that the computation is quantum. “Novel route” is also deliberately technical:
it means a legal shortest route whose canonical action signature is absent from
complete training-route and suffix support, after specified spatial and reversal
equivalences. It is not a claim about human originality, broad creativity, or
unbounded planning.

## 2. Implemented method

For a head with score matrix \(S\in\mathbb{R}^{L\times L}\), the actual
reference implementation uses

\[
H = \frac{S+S^T}{2\sqrt{L}},\qquad U=\exp(-i\,\Delta t\,H).
\]

It initializes each row-state as

\[
\psi_0=\sqrt{\operatorname{softmax}(S)}\odot\exp(i\gamma S),
\qquad \psi_1=\psi_0 U^T,
\qquad A=|\psi_1|^2.
\]

The attended output is \(AV\). The transpose in the row-state update is
intentional: each query row is represented as an amplitude state over keys.
The Hamiltonian is real symmetric, hence Hermitian after complex conversion, and
the matrix exponential is unitary up to numerical precision. Squared complex
magnitudes are non-negative and sum to one per row; no post-measurement
renormalization is performed. The exact source is
[`attention.py`](../schrodinger/attention.py) (SHA-256
`e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a`).

Both modes use the same route-policy backbone: 13 tokens (a CLS token plus 12
grid rows), two transformer blocks, two heads, model width 64, feed-forward
width 128, and 70,540 parameters. For SA, each head learns bounded \(\Delta t\)
and phase scale \(\gamma\); for softmax, two learned scales control score and
value matching. This equivalence of total parameter count is useful but not a
guarantee of equivalent inductive bias or computational cost. The implementation
is in [`route_policy.py`](../schrodinger/route_policy.py) (SHA-256
`95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4`).

This model is not causal language-model attention. It receives a fully available
13-token grid representation. Legal-action masking is applied only at the final
four-action policy distribution: walls and grid edges are masked; the attention
mechanism itself is not a causal mask. Accordingly, results cannot be transferred
to decoder-only settings, where a symmetric sequence Hamiltonian would create a
substantive causal-design problem.

Numerical tests checked Hermiticity, unitarity, Born-row normalization, finite
and double-precision gradients, and the dt=0 reduction. Across retained runs,
maximum unitarity/Born-row error was about 1.2e-6, below the 2e-3 guard. The
dt=0 condition uses the same learned phase and weights but switches evolution
time off. It reduces to softmax weighting because the amplitude magnitude is the
square root of softmax probabilities; it is not an independently trained
softmax model. These implementation and interpretation boundaries are important
for every mechanism claim below.

## 3. Benchmark, oracle, and evaluation protocol

The final accepted benchmark comprises 12x12 obstacle grids with route lengths
14--16 and 16 start/goal problems per map. Training contains 64 homogeneous
maps (1,024 problems). Validation contains 24 routine and 8 mixed-composition
challenge maps (512 problems total); the reserved, untouched test contains 96
routine and 32 challenge maps (2,048 problems). The exact construction
expanded each family candidate pool to 512 maps while retaining the frozen
geometry, selection, and novelty rules. Its independent review is recorded in
[the pool-512 report](../execution/next_level_v3_pool512/final_report.md)
(report SHA-256 `1f5e1f99bd847c2f4dc64d31935dcbb88abcc7794f26e468277765e341211d85`).

The oracle performs breadth-first search from the goal. At each state the
teacher distribution \(q\) assigns probability proportional to the number of
shortest completions available through each legal optimal action. This avoids
pretending that a multi-solution shortest-path problem has one privileged
action. The action legality mask excludes wall and off-grid moves only. The
metric/oracle code is [`route_policy_metrics.py`](../schrodinger/route_policy_metrics.py)
(SHA-256 `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34`).

For the 8,000-update route comparisons, the saved configuration uses AdamW
(learning rate 0.001, betas 0.9/0.999, epsilon 1e-8, weight decay 0.01),
gradient clipping at 1.0, and batches of 64; 8,000 updates therefore equal
512,000 sampled exposures. The route runs use CPU execution with two Torch
intra-op and one inter-op thread. The repository pins its relevant packages in
[`requirements.txt`](../requirements.txt): Torch 2.14.0, NumPy 2.5.3, and pytest
9.1.1. This is a protocol description, not an assertion that every historical
run used identical physical hardware.

Reported policy metrics include proper-score Brier and KL(q||p), greedy exact
shortest-route quality, and sampled route metrics using K=32 rollouts. Let Q be
the fraction of valid exact-shortest routes among K draws; pass@K is whether at
least one valid route occurs. \(U_{valid}/K\) is the number of *distinct* valid
routes divided by K. `valid_headroom` is distinct valid routes divided by the
exact count \(M\) of valid shortest solutions, whereas `coverage` refers to
novel-route coverage and uses \(M_{novel}\). These are different denominators.
Entropy is reported descriptively but is not calibration and cannot substitute
for a proper score or quality control.

Routine and challenge summaries are map-balanced and then combined at fixed
80/20 weights unless labeled otherwise. Common random uniforms align sampled
rollouts within a pair. Equal update count gives equal sampled exposures, not
equal wall time or compute: exact matrix exponentiation is intrinsically more
expensive in this reference. A seed-level mean is therefore the relevant
replication statistic. Confidence intervals below are descriptive small-sample
paired-t intervals; four seeds are too few to establish normality, superiority,
or equivalence, and 512 problems must not be treated as 512 independent training
replications.

## 4. Chronological empirical record

### 4.1 Initial classifier screen: suggestive but inadequate

The first XOR/COPY screen retained three paired seeds at 2,000 updates. On its
held-out-pair XOR primary endpoint, softmax scored 70.90% and exact SA 72.92%, a
mean paired difference of +2.02 pp. The frozen success threshold was +3 pp;
neither architecture met the 80% mean validation-XOR adequacy requirement.
COPY showed no material regression. Only one seed learned XOR robustly enough
to reach the high targets, and disabling evolution changed the primary endpoint
by about -0.065 pp on average. These data did not attribute the small difference
to evolution or qualify sample efficiency.

The numerical reference passed, but execution provenance invalidated controlled
timing and equal-time claims: output-directory reuse and unconfirmed process
completion made attempt-specific timing/non-overlap unrecoverable. These results
remain descriptive, with their limitation plainly recorded in the
[initial final report](../execution/final_report.md). They were an appropriate
reason not to scale a language model, not a negative verdict on the mechanism.

### 4.2 Same-weights mechanism diagnostic: evolution is heterogeneous

A checkpoint-only normal-versus-dt0 diagnostic then asked a narrower question:
with all learned weights fixed, does evolution alter attention and downstream
predictions? It does. Across 240 direct attention cells, mean total-variation
(TV) redistribution ranged from 0.00553 to 0.15551; only 70 cells satisfied
the predeclared small-effect band. In the original primary XOR condition, one
seed/layer/head had 15.551% mean CLS-row TV and 18.515% p95. Full-path changes
also altered predictions: for one seed, 30 of 512 labels changed with exactly
offsetting 15 gains and 15 losses.

Yet there was no consistent useful result. No condition met the frozen
noticeable-benefit criterion (mean loss benefit at least 0.01 nats and positive
in at least two seeds); gains and harms offset. Direct attention changes,
projection changes, and downstream changes differ by head and seed. The correct
conclusion is neither “attention is unchanged” nor “interference helped”: it is
heterogeneous active evolution without a consistent task benefit in those
retained checkpoints ([diagnostic report](../execution/diagnostics/final_report.md)).

### 4.3 Constructing a benchmark capable of testing route diversity

Several frozen feasibility stages stopped before any learning. An early
construction had only 6 of 512 unseen-composition problems with four or more
novel shortest routes. Two 8x8 dataset rungs then failed predeclared allocation
gates. A first 12x12 pool created useful partial oracle evidence but missed the
challenge-test target by seven maps. These are benchmark-construction failures,
not model failures; no thresholds were relaxed or favorable map selection made.

The 512-pool 12x12 expansion finally passed all construction gates. Challenge
problems each have at least four qualifying structurally novel shortest routes
and a specified novel-solution fraction; routine problems have none under the
same support definition. Importantly, these are *oracle opportunities*, not
model-generated novelty. This succession of stops is evidence that a named
“new map” is not enough to support a novelty claim, and it constrains how later
route results may be described.

### 4.4 Initial route training: learning, but softmax was the practical baseline

At 1,000 equal updates on discovery seed 1701, both matched 70,540-parameter
models learned relative to initialization. SA's Brier fell from 0.45874 to
0.17502 and KL from 0.83877 to 0.34705; T=1 valid-route Q rose to 20.78%.
Softmax was slightly better at that point (Brier 0.172393, Q 21.17%). SA's
core training took 15.792 s versus 4.750 s for softmax (3.32x). At matched core
time, softmax at update 1,000 was much stronger than SA at update 300: Q 21.17%
versus 9.89%.

The planned softmax-only continuation showed a baseline usability limitation:
by 8,000 updates, greedy Q was 53.85% and T1 Q 34.23%, below 80%/70% gates.
Diagnostic analyses found training-DAG KL improving from 0.204 to 0.101 while
aligned routine DAG KL was approximately flat (0.196 to 0.194) and mixed KL
worsened (0.568 to 0.667). This is a baseline generalization diagnosis, not an
identified architectural cause. A three-cohort view (seen pairs/new goals on
seen maps/unseen routine maps) was 54.99/48.33/39.15% T1 success, likewise
descriptive and one-seed only. See the [training comparison](../execution/model_training_comparison/final_report.md).

### 4.5 Discovery pair: a reason to replicate, not a conclusion

Training both models to 8,000 equal updates on seed 1701 changed the picture.
SA T1 Q was 37.17% versus softmax 34.23% (+2.94 pp); greedy quality was 56.72%
versus 53.85%. On frozen transfer cohorts, SA-minus-softmax Q was +0.48 pp for
seen pairs/maps, +2.69 pp for new goals on seen maps, and +5.38 pp for unseen
routine maps. Their policies were meaningfully different: action-probability
TV was 0.0969, argmax disagreement 11.33%, and many differing actions were both
oracle-optimal.

This is intriguing, but not a favorable narrative to generalize. At T=1, SA did
not improve distinct valid novel routes per K (0.8789% vs 0.8984%); an SA T=.75
novelty increase was confounded by much higher Q and failed the predeclared
quality match. A same-trained SA dt0 probe slightly improved mean CE, so it did
not establish evolution as the training-causal source of SA's outcome. Core
training cost was 126.85 s for SA versus 38.82 s (3.27x) for softmax. Timing was
sequential and descriptive, not a randomized hardware benchmark. The right
action was fresh replication, which was performed ([paired-behavior report](../execution/paired_behavior/final_report.md)).

### 4.6 Fresh four-pair replication: primary result does not replicate

Fresh seeds 1702--1705 used the same architecture, data, optimizer, 8,000
updates, 512,000 exposures, T=1/K32 endpoint, and within-pair initialization
and streams. The frozen primary overall valid-route Q was 38.198% for softmax
and 37.749% for SA: SA-minus-softmax = -0.449 pp, positive in one of four
pairs. The sample SD was 1.837 pp and the descriptive 95% paired interval was
[-3.372, +2.474] pp. Routine Q was -0.584 pp and frozen unseen-routine-map C Q
was -0.391 pp. Overall greedy Q was -1.549 pp. Thus no replicated overall
quality or transfer advantage was demonstrated.

There is a small setting-specific signal worth reporting but not promoting.
Challenge pass@32 was 51.367% (softmax) versus 54.102% (SA), +2.734 pp, with
three positive pairs. Challenge distinct valid routes/K was 11.176% versus
11.304% (+0.128 pp); exact valid-solution fraction covered was 4.239% versus
4.630% (+0.391 pp). These measures differ: pass@32 is whether a finite bag
contains one valid route, whereas valid headroom is route-set coverage. Overall
valid-route diversity was slightly lower (-0.189 pp), and strict-novel metrics
were near equal. Policy difference persisted (mean state-policy TV 0.1051 and
argmax disagreement 11.46%), but different policies are not necessarily better
or more diverse within a policy.

Each pair's three SA temperatures (.75/1/1.25) were retained. T=1 was nearest
the softmax quality point; only seeds 1703 and 1704 met the approximate mixture
and stratum quality tolerances, and both had lower overall distinct-valid/K than
softmax. No grid was extended or interpolated. Mean core times were 39.867 s
softmax and 128.316 s SA, 3.22x. The complete fresh-seed record and definitions
are in [the replication report](../execution/seed_replication/final_report.md)
(SHA-256 `c5ca3ecf6474eaa09f489225c094400438e58ec9a209a802cdda29ecffc854ed`).

### 4.7 D0/D1 difficult-problem analysis: a reduced, uncertain signal

D0 reused the same four seeds and eight challenge validation maps; it performed
no new training or inference. The T1 challenge pass@K curve rose from a +0.092
pp difference at K=1 to +2.734 pp at K=32. Leave-one-map-out differences all
remained positive, but map 344 contributed 7 of 14 net problem-seed successes.
SA solved more problems at least once (277 vs 263) without a clear increase in
route multiplicity on shared solved problems. This is a robustness description
of a selected validation panel, not an independent replication or a broad
difficult-planning result ([D0 report](../execution/difficult_problem_solving/d0_report.md)).

D1 then performed a frozen symmetric five-temperature search for each mode,
retaining all 40 cells. Candidate temperatures had to meet both routine and
challenge single-draw Q floors: at least paired softmax T=1 minus 2 pp. These
are eligibility floors, not exact quality matching. SA seed 1702 at T=1 missed
the routine floor and SA seed 1705 at T=1 missed the challenge floor; their
eligible SA selections were T=.75. The selected result was challenge pass@32
51.367% softmax versus 52.148% SA (+0.781 pp), positive two of four pairs.
Its paired seed interval was [-5.050, +6.612] pp; the conditional reused-panel
map-bootstrap interval was [-1.758, +3.711] pp. Both cross zero. Challenge
distinct-valid/K was 11.176% versus 11.249%
(+0.073 pp), and valid-solution coverage 4.239% versus 4.623%.

This D1 result is quality-controlled only in the limited floor sense, reuses the
same validation maps for selection and scoring, and does not equalize training
compute. It weakens rather than confirms the raw T1 signal. SA's route variation
was mixed: slightly higher coverage and U_valid, but higher duplicate rate and
nonuniform per-seed directions. The audited report correctly records D2
forecast as deferred/no-go, not as a model-runtime failure.
[D1 report](../execution/difficult_problem_solving/d1-report.md), SHA-256
`7c56622bd375e0dc8f66cce09ae126e428728ad703b04010ce94737af3874d84`; the
independent audit is [here](../execution/difficult_problem_solving/d1-result-audit.md),
SHA-256 `ada20693ec3edb8381fc02948b645227263aa539f25a8a650fbbc81c6997cfec`.

### 4.8 Consolidated numerical results

These rows are not a pooled meta-analysis. The discovery pair selected the
subsequent investigation; the fresh four-pair result is the frozen primary
replication estimate; D0 reuses the fresh validation result; and D1 reuses the
same validation panel after frozen floor-based temperature selection. Q is
single-draw valid-shortest-route quality; pass@32 is the fraction of problems
with at least one valid shortest route among 32 draws.

| Status and endpoint | Softmax | Exact SA | SA − softmax | Unit / interpretation |
|---|---:|---:|---:|---|
| Discovery 1701, 8k overall T1 Q | 34.23% | 37.17% | +2.94 pp | One seed; exploratory discovery |
| **Fresh 1702–1705, 8k overall T1 Q (primary)** | **38.198%** | **37.749%** | **−0.449 pp** | Four paired seeds; descriptive 95% interval [-3.372, +2.474] pp |
| Fresh 1702–1705, challenge T1 pass@32 | 51.367% | 54.102% | +2.734 pp | Four paired seeds; secondary; reused by D0 |
| D1 floor-selected challenge pass@32 | 51.367% | 52.148% | +0.781 pp | Same validation panel; exploratory; four-seed interval [-5.050, +6.612] pp |

## 5. Discussion

The most durable positive finding is methodological: exact amplitude evolution
can be trained stably in a small conventional model and can change attention,
actions, route solutions, and learning trajectories. This defeats the narrow
explanation that the implementation simply reproduces softmax or that evolution
is numerically negligible. It does not identify which aspects of phase,
Hamiltonian coupling, additional learned controls, optimization, or finite-task
geometry create those differences.

The quality result is not favorable. The discovery pair justified replication;
the fresh primary result did not reproduce it. The challenge coverage signal is
smaller after symmetric temperature selection, has wide seed uncertainty, and
comes from a repeatedly analyzed eight-map validation panel. It is compatible
with a small useful effect, no effect, or a harmful effect of practical size.
The same data cannot establish equivalence because the interval is wide. A
claim that SA increases “creativity,” useful uncertainty, general transfer, or
difficult-problem solving would exceed the evidence.

Cost changes the decision threshold. Even if a small advantage existed, a
roughly 3.22x core-training cost in this exact CPU reference means it would need
substantially stronger quality, sample-efficiency, or deployment value to be
competitive. These measurements are not estimates for GPU kernels, approximate
evolution, or long sequences, but they rule out a claim that the implemented
exact reference is already cost-neutral. Historical classifier timing is
invalid and must not be combined with later timing. The current qualified
operational debit is 4764.416447001050 of 7200 seconds; it includes a 300-second
administrative uncertainty allowance and is not a measured physical-total
runtime. Cumulative budgets from different reports must not be summed.

Important limitations remain. The benchmark is small and selected; the initial
route data has an all-invalid within-map ordering limitation, though source/order
bindings and legal-route checks support retained alignment. The teacher is an
oracle for shortest paths, not a natural-language target. Temperature selection
and difficult-problem scoring reuse validation data. The baseline itself has
meaningful held-out generalization limits. Mechanism tests are same-weights
interventions, not independently trained causal ablations. Finally, no
model-bearing evaluation has used the reserved route-policy final-test split.
These constraints are reasons to preserve
the result as inconclusive, not excuses to select a positive metric.

## 6. Conclusion

Exact Schrödinger attention is a numerically sound, deterministic classical
attention primitive that changes learned behavior. In this bounded benchmark,
it did not demonstrate a robust replicated benefit over matched softmax. The
favorable 1701 outcome failed to replicate on the frozen primary endpoint, and
the residual difficult-panel coverage difference is small and uncertain after
limited quality control. The implemented reference is materially more expensive
in core training. The justified conclusion is therefore: **do not scale or make
broad capability claims on the present evidence**. A future study should either
stop here or first meet a strict authorization, runtime-forecast, untouched-map,
and replication standard described in [next research steps](next_research_steps.md).

## Appendix A. Reproducibility map

This paper describes repository artifacts; an external reader needs a snapshot
of this repository to resolve the relative links and reproduce local hashes.

| Evidence | Immutable/reviewable location | Hash or verification boundary |
|---|---|---|
| Original hypothesis and planned controls | [proposal](../schrodinger_attention_research_proposal.md) | Historical proposal, not a claim that all stages ran |
| Exact attention source | [`schrodinger/attention.py`](../schrodinger/attention.py) | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| Matched policy source | [`schrodinger/route_policy.py`](../schrodinger/route_policy.py) | `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` |
| Oracle and metrics | [`schrodinger/route_policy_metrics.py`](../schrodinger/route_policy_metrics.py) | `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34` |
| Initial screen and timing limitation | [execution final report](../execution/final_report.md) | Retained descriptive endpoints; equal-time invalid |
| Same-weights diagnostic | [diagnostic final report](../execution/diagnostics/final_report.md) | 19 diagnostic / 67 total tests reported |
| Complete 12x12 dataset | [pool-512 report](../execution/next_level_v3_pool512/final_report.md) | `1f5e1f99bd847c2f4dc64d31935dcbb88abcc7794f26e468277765e341211d85` |
| First route pair and baseline stop | [model comparison](../execution/model_training_comparison/final_report.md) | Independent final audit linked in report |
| Discovery-pair behavior | [paired behavior](../execution/paired_behavior/final_report.md) | Independent auxiliary audit linked in report |
| Fresh four-seed primary result | [seed replication](../execution/seed_replication/final_report.md) | `c5ca3ecf6474eaa09f489225c094400438e58ec9a209a802cdda29ecffc854ed` |
| D0 reused-panel screen | [D0 report](../execution/difficult_problem_solving/d0_report.md) | No new training/inference |
| D1 selected-temperature result | [D1 report](../execution/difficult_problem_solving/d1-report.md) | `7c56622bd375e0dc8f66cce09ae126e428728ad703b04010ce94737af3874d84` |
| D1 independent result/accounting review | [D1 audit](../execution/difficult_problem_solving/d1-result-audit.md) | `ada20693ec3edb8381fc02948b645227263aa539f25a8a650fbbc81c6997cfec` |

The output manifests, attempts, ledgers, plans, and independent reviews linked
from these reports provide artifact-level hashes and command/provenance records.
They do not turn a small, reused validation analysis into a final-test result.

## Appendix B. Interpretation rules used in this paper

This appendix makes explicit several distinctions that are easy to lose when a
compact result table is read in isolation.

**Equal updates, equal data exposure, and equal compute are different.** Within
each paired run the two models share initialization, minibatch digests, update
count, optimizer settings, and decoding uniforms. That is a strong control for
one kind of comparison: whether the architectures take different learning paths
under equal update exposure. It is not a control for computation. Exact SA
constructs a complex matrix exponential per head/batch score matrix and was slower in the
measured CPU reference. The reported 3.22x mean core-time ratio from fresh
replications is therefore a relevant practical finding, even though it is not a
universal estimate for optimized GPU kernels. Conversely, a comparison that
gives SA fewer updates to match core seconds is a compute-efficiency comparison,
not an equal-exposure comparison. Neither should be relabeled as the other.

**Route quality and route variety are different.** Q counts valid shortest
routes in finite samples. Pass@32 asks whether a problem receives at least one
such route. A model can increase pass@32 by spreading rare success across more
problems without generating many different solutions on problems it already
solves. That is the likely interpretation of the D0 pattern: SA had more
problem-seed successes but no convincing increase in distinct route count among
the shared solved subset. `U_valid/K` corrects for repeated valid outputs but
still has K in its denominator; valid headroom instead normalizes by the exact
number of shortest routes available for that problem. Neither establishes an
ability to discover new strategies. Strict novelty further requires absence from
the complete canonical training support, and it was supplementary in the route
study.

**Temperature floors are not matching.** D1 selected the temperature that
maximized challenge pass@32 among candidates meeting routine and challenge Q
floors. Its design protects against accepting an endpoint that visibly loses
single-draw route quality, but a candidate can be materially better or worse in
either stratum while remaining eligible. Its result should therefore be called
“floor-controlled” or “limited quality-controlled,” never exactly
quality-matched. Moreover the same validation panel chose and evaluated the
temperatures, so the D1 point estimate is exploratory even though every cell and
selection rule was frozen before the new endpoints were computed.

**A dt=0 intervention is not an independently trained baseline.** Given the
implementation, \(\Delta t=0\) yields
\(|\sqrt{\operatorname{softmax}(S)}e^{i\gamma S}|^2=
\operatorname{softmax}(S)\) exactly. The learned phase is invisible at
measurement without evolution. Thus a same-checkpoint dt0 run asks what happens
when evolution is removed from an already trained SA model; it cannot determine
whether independently training without evolution would reach the same weights,
optimization basin, or route policy. It also means a proposed “phase-only,
no-evolution” model would be degenerate with softmax in this exact formulation.
Meaningful causal ablations must be independently trained and account for
capacity and compute.

**The statistical unit is a seed.** A single seed emits many route rows, but
those rows share weights and correlated map geometry. The four fresh pairs give
four architecture replications. The paired intervals are intentionally shown to
communicate imprecision, not to create a pass/fail ritual. The D1 map bootstrap
answers a different conditional question—variation over the eight
already selected maps at fixed seed/temperature selection—and does not repair
the lack of fresh training seeds or panel reuse. Similarly, leave-one-map-out
positivity tells us an average is not caused by one indispensable map, not that
the result generalizes to new maps.

**“Classical” is a substantive boundary.** All operations here are conventional
PyTorch-like complex tensor arithmetic. Unit norm is a numerical invariant and
the Born rule is a deterministic map from complex amplitudes to real weights.
Sampling occurs later from an ordinary policy distribution. No claim in this
paper rests on quantum hardware, measurement randomness, or a physical
interpretation of the learned amplitudes.

## Appendix C. Stage-by-stage decision ledger

| Stage | Decision made by the evidence | What it did not decide |
|---|---|---|
| Initial XOR/COPY screen | Exact module was viable; small retained difference did not meet gate; timing comparison invalid | General SA efficacy or efficiency |
| Same-weights diagnostic | Evolution can substantially redistribute attention and alter predictions | That evolution causes a training benefit |
| Early feasibility ladders | Several frozen constructions lacked adequate novel-route support or quotas | That models fail at novelty/diversity |
| 512-pool benchmark | A complete oracle-controlled route dataset exists | That either architecture learns it well |
| 1k paired training | Both learn; softmax is more cost-effective at measured equal time | Long-run SA quality or transfer |
| 1701 discovery pair | A replicate-worthy SA advantage is possible in one seed | Replicated advantage or creativity |
| Fresh 1702--1705 pairs | Primary overall advantage did not replicate | Equivalence or impossibility of a small effect |
| D0 | Raw challenge coverage is not solely a single-map artifact | Independent difficult-task evidence |
| D1 | Temperature floors reduce the raw signal to a small, uncertain contrast | Exact quality matching, final confirmation, or D2 authorization |

The operational resource ledger has a different role from this scientific
ledger. It preserves attempted work, administrative allowances, and provenance
without rewriting history. Qualified totals are useful for authorization and
audit; they are not a substitute for the measured core timing fields used for a
compute comparison. In particular, the final D1 global debit includes an
explicit historical uncertainty allowance. It would be misleading to describe
it as all physical experiment runtime or to add it to intermediate cumulative
totals that already include inherited debits.

## Appendix D. Minimum reporting requirements for any successor study

A successor study can be smaller than a language-model project while still being
more decisive than the current record. At minimum it should publish: the exact
source revision and hashes; a frozen model/configuration table; train/tune/
confirmation-map identities and disjointness checks; seed and model-order rules;
all failed and completed attempt owners; measured core, inference, and overhead
timings separately; one primary endpoint and its practical threshold; temperature
selection separated from confirmation scoring; seed-level raw paired outcomes;
map-aware sensitivity summaries; all eligible temperatures rather than only the
winner; and a clear statement of whether final test access occurred.

The comparison should also reserve the right to be negative. A sensible
precommitment is that a failed confirmation will be written up as a bounded
negative result, rather than triggering a hidden sequence of map changes,
temperature grids, checkpoint choices, or longer training. This is especially
important because the current study already contains a plausible discovery seed
and a plausible challenge subgroup. Those are precisely the situations in which
selection can manufacture a narrative without producing a dependable effect.

## Appendix E. Why the exact reference is useful despite its cost

The exact matrix exponential is not proposed as a production attention kernel.
Its value in this programme is epistemic. It gives a well-defined target
calculation: for a symmetric real score-derived Hamiltonian, the unitary is
computed directly rather than replaced by a truncation whose stability or error
might itself explain a performance difference. It also makes several numerical
claims testable. Hermiticity, unitarity, normalization, and the dt=0 reduction
have crisp expected values. A later efficient approximation would need to show
not only an end-task result, but also how closely it preserves the reference
operation and whether any change in quality is due to approximation rather than
the amplitude mechanism.

There is a complementary limitation. The reference's costs grow unfavorably as
the attention-state length increases, and complex matrix operations have
different implementation characteristics from softmax. A result on 13 tokens
cannot establish latency, memory, prefill throughput, decode throughput,
KV-cache behavior, accelerator utilization, or energy for language models. The
3.22x training-core figure should therefore be read narrowly: it is an observed
economic disadvantage of the exact CPU implementation on this task. It neither
licenses a claim that all unitary/phase methods are 3.22x slower nor permits an
efficient variant to inherit a benefit that the exact reference has not shown.

The same reasoning applies to causality. For every query in this benchmark, the
full grid is a legitimate input. A decoder sequence instead exposes only a
prefix. Simply masking a score matrix while symmetrizing it can break either
normal causal semantics or the Hermitian structure on which unitary evolution
relies. A causal formulation may need a query-specific key-subspace evolution or
a different factorization. That is an architectural research problem, not a
minor engineering port. It should be solved and numerically audited before any
claim that the present exact method improves autoregressive attention.

## Appendix F. Reading the discovery and replication together

The 1701 result should not be discarded: it revealed that an equal-update SA
learning path can be better than softmax on some instances and supplied a
concrete candidate outcome for replication. But it cannot be pooled with seeds
1702--1705 as though all five were a prospectively homogeneous sample. The
discovery seed informed the decision to examine transfer cohorts, temperatures,
and difficult-panel coverage; including it in the primary fresh-replication
mean would understate the selection process. Reporting it separately is the
more informative choice: it tells future investigators what signal motivated
the work while preserving the conclusion that the signal was not reliably
reproduced.

The fresh seed trajectories add nuance without changing that conclusion. SA
held a mean early Q advantage at 1,000 updates (28.096% versus 27.383%) that
faded by 4,000 and reversed at 8,000. This pattern is hypothesis-generating,
not evidence that a favorable early checkpoint should replace the frozen 8,000
endpoint. It could reflect different optimization dynamics, overfitting,
sampling noise, or details of the route representation. It becomes scientifically
useful only if a future study predeclares an early-stage endpoint and demonstrates
it under equal compute and fresh seeds.

Finally, the small D1 difference is not inconsistent with a negative overall-Q
mean: the endpoints ask different questions and weight different subsets. A
model can have a modestly higher chance of one success in a difficult finite
sampling bag while being no better, or worse, in single-draw quality and overall
route validity. That possibility is why the paper reports both measures and
refuses to choose the favorable one as a universal score. The open question is
not whether a positive number can be found in the record; it is whether a
precommitted, practical advantage remains when new seeds, new maps, matched
quality, and cost are all brought to bear.
