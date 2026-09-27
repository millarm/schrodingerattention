# Next research steps for exact Schrödinger attention

## Decision context

The completed evidence does not support scaling the mechanism. Exact amplitude
evolution is stable and behaviorally active, but the seed-1701 discovery result
did not replicate on the frozen four-seed primary endpoint. D1's restricted
temperature-controlled challenge comparison is +0.781 pp pass@32 with a
four-seed interval crossing zero, not a reliable difficult-solving benefit.
Exact SA also cost about 3.22x softmax in measured training-core time on this
reference. No model has been evaluated on the reserved route-policy final-test
split.

This document recommends decision gates, not new authorization. Each item says
what it can establish and what it cannot. The default scientifically sound
option is to stop; every other option requires a new written plan, frozen
settings, explicit budget authority, and independent review before execution.

## Option 0 — stop and archive (recommended default)

**Question.** Is current evidence sufficient to justify more experimental
expense or claims of an advantage?

**Action and endpoint.** No additional model execution. Archive the evidence
map in [the research paper](schrodinger_attention_research_paper.md), the
[fresh replication report](../execution/seed_replication/final_report.md), and
[D1 audit](../execution/difficult_problem_solving/d1-result-audit.md). The
endpoint is a complete, immutable negative/inconclusive record rather than a
new model metric. The unit is the research record.

**Cost authority and go/no-go.** Zero additional model budget. This is the
appropriate no-go if no sponsor is willing to fund a confirmation that is
powered for a practically meaningful effect *and* can tolerate the exact
method's substantial compute overhead.

**Cannot prove.** Stopping does not prove the mechanism cannot work elsewhere,
with another implementation, at another scale, or on another task. It simply
declines to infer a benefit from uncertain, small-scale evidence.

## 1. D2 runtime forecast before any new model run

**Question.** Can a fully specified confirmation be executed within a credible,
bounded envelope, and what is its smallest useful design?

**Minimal test.** Perform a read-only engineering forecast using the existing
D1 owners, measured core timings, artifact-write timing, memory/profile data,
and every required category for a non-overlapping 2,048-problem evaluation.
Do not extrapolate a single aggregate D1 duration into a forecast: enumerate
model forward/sampling, route verification, cache behavior, output persistence,
startup/finalization, audit, and contingency separately. Freeze the exact
software revision, CPU/GPU target, model checkpoint set, K, temperatures,
panel size, model order, and wall/core-time accounting definitions. Report a
range and assumptions rather than a point estimate.

**Primary endpoint and unit.** The endpoint is a pre-authorized runtime and
resource envelope with all cost categories covered; the unit is one complete
evaluation owner. A forecast is acceptable only if it identifies what is
measured versus assumed and preserves enough budget for independent audit.

**Cost-authority gate.** D1 explicitly left D2 forecast deferred/no-go because
essential scaling categories were missing. This forecast itself should be
read-only and must receive a small, separate accounting authorization if it
requires profiling. It must not silently run new inference, use final-test
models, or change the 7,200-second accounting interpretation. The current
qualified operational debit (4764.416447001050/7200 seconds) includes a
300-second administrative uncertainty allowance; it is not a physical-runtime
total and should not be combined with historical cumulative totals.

**Go/no-go.** Go only if a reviewed forecast demonstrates a bounded execution
with an explicit scientific effect threshold worth the expected cost. No-go if
the forecast remains materially incomplete, exceeds authorized resources, or
shows that the design cannot distinguish a benefit commensurate with roughly
3.22x core training cost.

**Cannot prove.** A forecast cannot show modelling benefit, efficiency on a
different accelerator, or a scalable approximation. It only makes a proposed
test auditable before resources are spent.

## 2. Untouched-map confirmation, conditional on a forecast and authority

**Question.** With all choices frozen before inspection, does SA improve a
preselected practical endpoint on genuinely untouched maps?

**Minimal test.** Reuse the existing four trained seed pairs and their fixed
8,000-update checkpoints; do not train new models in this smallest confirmation.
Evaluate a confirmation panel from maps never used for temperature selection,
D0/D1 analysis, or checkpoint/model decisions. Preserve the 12x12 route lengths,
exact oracle, legal-mask policy, common-uniform rollouts, K=32, map balancing,
and paired evaluation protocol unless a separately reviewed change is necessary.
Before opening the panel, freeze:

- Primary endpoint: challenge pass@32 at the D1-selected/frozen temperature
  policy, with a paired-seed estimator.
- Secondary endpoints: Q, U_valid/K, valid_headroom, duplicate and invalid
  rates, routine Q, and proper scores; label these secondary.
- A minimum practically meaningful effect, decision interval rule, exact seed
  count, map count, stopping rule, and a single multiplicity policy.
- Temperatures and selection rule. Prefer carrying the D1 rule forward without
  retuning; if any calibration is necessary, do it only on a distinct tuning
  panel and never reuse confirmation maps.

The primary unit remains an independent paired seed. Maps support the endpoint
but do not multiply the number of training replications. Use a predeclared
hierarchical/map-aware uncertainty analysis as a secondary sensitivity check,
not pseudoreplication.

**Cost-authority gate.** First complete Step 1. Then obtain explicit authority
for evaluation, verification, and independent audit of these existing
checkpoints. The panel must be technically inaccessible to the analysis workflow
until the freeze record is accepted. This is a conditional recommendation, not
permission to release the existing reserved route-policy final test or generate
a substitute favorable panel; that release requires separate explicit authority.

**Go/no-go.** A positive result requires the primary paired estimate and its
predeclared uncertainty/decision rule to clear the practical threshold, while
routine quality and cost criteria are not materially worse. If it misses, stop
the advantage claim and publish the negative confirmation. If it is ambiguous,
do not recursively retune or enlarge the panel without a new plan.

**Cannot prove.** One confirmation cannot establish language-model scaling,
general creativity, mechanism causality, or hardware efficiency. It tests one
frozen route-policy claim.

## 3. Fresh-seed, equal-compute comparison only if powered

**Question.** Is any quality or challenge-coverage difference worth the compute
premium when both architectures receive comparable measured compute rather than
equal updates?

**Minimal test.** Do not run another four-seed equal-update study. First design
for the smallest effect that would justify the exact method's overhead. If the
confirmation endpoint warrants it, train fresh independent pairs with both an
equal-update and an equal-measured-core-compute arm, randomizing or
block-balancing model order. Predeclare whether the primary endpoint is
compute-to-quality, quality at equal core time, or quality at a fixed update
count; it cannot be all three without multiplicity control. Include the full
wall/core timing protocol and preserve non-overlapping attempt ownership.

**Primary endpoint and unit.** The primary unit is a fresh paired seed, with
core training seconds (not aggregate ledger debit) as the compute denominator.
If route quality at equal compute is primary, report Q and pass@32 at frozen
temperature along with Brier/KL and error bars. The observed ratio to beat is
about 3.22x core time, not an immutable law of all implementations.

**Cost-authority gate.** Require a prospective power calculation tied to the
minimum practical effect, anticipated paired variance, attrition plan, and
budget. Four fresh pairs produced a primary SD of 1.837 pp and a wide interval;
no credible result follows from treating 512 route problems as replacement
seeds. If the forecasted seed count or budget cannot be funded, choose Option 0.

**Go/no-go.** Go only when the study is powered for a decision-relevant effect
and the exact compute envelope is approved. Claim a practical advantage only if
the frozen primary test clears its effect/cost threshold. Otherwise stop; do not
select early checkpoints, discovery seed 1701, temperature cells, or challenge
subgroups after results.

**Cannot prove.** Even a powered route-policy result does not establish that
phase/evolution is the causal reason or that performance transfers to causal
language modeling.

## 4. Mechanism causal ablations — only after a benefit survives

**Question.** If a reproducible benefit exists, which element causes it:
complex phase, unitary evolution, Hamiltonian symmetrization, optimization path,
or extra learned controls?

**Minimal test.** Do not perform broad ablation fishing now. The existing
same-weights dt0 diagnostic already proves that evolution can be active and
heterogeneous, while showing no consistent benefit. After a benefit passes an
untouched confirmation, compare independently trained, compute-accounted
variants with matched capacity and initialization: (a) parameter-matched
softmax, (b) nonzero evolution with learned versus zero/fixed/random phase, (c)
a separately trained dt=0 control, and, if warranted, a real norm-preserving
control. A “phase-only, no-evolution” variant is **not** distinct here: at
dt=0, `|sqrt(softmax(S))*exp(i phase)|²` is exactly softmax(S), regardless of
phase. Predefine a small set of contrasts and use the same primary task endpoint
as the successful confirmation.

**Primary endpoint and unit.** A causal contrast is the difference between
independently trained variants across fresh paired seeds. Attention TV,
eigenphase, and dt magnitude are mechanism measurements, not efficacy endpoints.
The primary endpoint is the previously validated benefit metric; secondary
mediation-style analyses must be described as associative.

**Cost-authority gate.** No ablations unless the benefit is both replicated and
worth explaining. Require a separate budget because matrix-exponential variants
and controls can have different speed profiles.

**Go/no-go.** Continue only if a predeclared ablation changes the replicated
benefit in the predicted direction without an explanatory compute/capacity
confound. Otherwise report that behavior differs but mechanism attribution is
unresolved.

**Cannot prove.** Ablations cannot make an internal amplitude analogy into a
physical quantum claim, and no dt0 counterfactual alone proves training causality.

## 5. Separate baseline-representation branch

**Question.** Are the route benchmark's baseline limits dominated by spatial
representation/generalization rather than attention type?

**Minimal test.** Treat this as a separate baseline research question, not an
SA rescue. Use softmax-only models with one prespecified spatial representation
alternative (for example, coordinate/graph-aware features) against the current
row-token encoder, keeping the oracle, maps, data exposure, optimizer family,
and held-out cohorts fixed. Analyze seen pairs, new goals on seen maps, and
unseen routine maps without treating their descriptive difference as a causal
decomposition. Freeze whether the endpoint is held-out Q, proper score, or a
generalization gap before running.

**Primary endpoint and unit.** Independent softmax seed is the unit. Report
training-DAG and aligned held-out DAG proper scores alongside route Q; do not
use training loss alone as evidence that the representation solved
generalization. The known 8k baseline pattern—training KL improves while mixed
held-out KL worsens—motivates this branch but does not identify a cause.

**Cost-authority gate.** This branch requires its own plan and should not open
the final test. It does not authorize new SA training or a post-hoc encoder
change within an SA comparison.

**Go/no-go.** Advance only if the new baseline reliably improves held-out route
quality/proper scores at an acceptable cost. If it does, restart any SA
comparison from an explicitly new, matched protocol rather than mixing old and
new baselines.

**Cannot prove.** A better representation would not prove softmax is globally
superior, nor would it erase the current exact-SA result. It improves the
benchmark's diagnostic value.

## 6. Language-model scaling is last

**Question.** Does an advantage that survives the preceding gates extend to
causal language modeling and longer contexts?

**Minimal test.** Only after a route-policy confirmation and causal-ablation
case, design a new causal formulation rather than reuse the bidirectional
symmetric Hamiltonian unchanged. Begin with a numerically verified short-context
reference, then compare parameter-, token-, and measured-compute-matched small
decoder models across multiple seeds. Predeclare loss/perplexity as primary;
include throughput, memory, latency, and causal-mask validation. Exact matrix
exponentiation may be a reference only; any approximation requires a separate
numerical and fairness validation.

**Primary endpoint and unit.** Seed-level validation loss/compute-to-target is
primary, with task-specific behavior secondary. Use held-out text and avoid
interpreting a synthetic route effect as a scaling law.

**Cost-authority gate.** This is a new project with a new budget, data/license
review, hardware plan, and causal-attention design review. It is not covered by
the remaining route-study operational envelope.

**Go/no-go.** Go only after the low-cost evidence shows a practical, replicated,
compute-aware benefit. Stop if causal correctness, numerical stability, or
compute economics fail before a fair model comparison.

**Cannot prove.** A small language-model test would still not prove broad
scaling behavior; scaling laws require multiple sizes and materially larger
budgets.

## Recommended sequence

1. Choose Option 0 unless a decision-relevant benefit is worth funding.
2. If funded, perform the read-only D2 forecast and freeze a complete protocol.
3. Run one untouched-map confirmation with settings fixed before access.
4. Only on a positive, practical confirmation, run a powered fresh-seed,
   equal-compute comparison.
5. Only after benefit survives, investigate causal mechanism; independently
   improve the baseline representation if needed.
6. Treat causal language scaling as a last, separate programme.

This sequence prevents the common failure mode in exploratory architecture work:
turning an interesting seed, subgroup, or internal diagnostic into a reason to
retune indefinitely. It protects both possible outcomes—an eventual real effect
and a clean, useful negative result.
