# Four fresh paired-seed replications

Status: **COMPLETE — independent Sol final-results audit PASS.** All eight
training runs and four analyses completed. No additional training, inference,
seeds or final-test access.

## Answer to the broader hypothesis

Schrödinger attention learns and produces different correct routes, but the
discovery seed's overall quality and unseen-map advantage did **not** reliably
replicate. Useful variation and transfer gains depend on the seed and evaluation
setting. There is a small descriptive challenge-coverage signal, not evidence
of a general same-quality diversity advantage or proven creativity.

The user's broader emphasis on productive variation/transfer was recorded
mid-study in the independently reviewed interpretation addendum. The frozen
primary endpoint and all four T1 comparisons remain unchanged; strict novelty
is supplementary, not silently replaced in the preregistration.

## Final quality and productive diversity

Fresh seeds 1702–1705 only, equal 8000 updates (512,000 sampled exposures),
T1/K32. Values are percentages; differences are percentage points. Seed is the
replication unit, not the thousands of states or sampled routes.

|Endpoint|Softmax mean|Schrödinger mean|SA−SM|Positive pairs|
|---|---:|---:|---:|---:|
|Overall valid-route Q, frozen primary|38.198|37.749|−0.449|1/4|
|Routine Q|43.815|43.231|−0.584|1/4|
|Mixed-composition challenge Q|15.729|15.820|+0.092|2/4|
|Frozen unseen-routine-map C Q|45.416|45.025|−0.391|2/4|
|Overall greedy Q|58.242|56.693|−1.549|0/4|
|C greedy Q|68.229|66.840|−1.389|2/4|
|Overall distinct valid routes/K32|28.604|28.415|−0.189|1/4|
|Challenge distinct valid routes/K32|11.176|11.304|+0.128|2/4|
|Challenge pass@32 (≥1 valid route)|51.367|54.102|+2.734|3/4|
|Overall exact valid-solution fraction covered|13.148|13.116|−0.032|2/4|
|Challenge exact valid-solution fraction covered|4.239|4.630|+0.391|2/4|

|Fresh seed|Primary ΔQ|Challenge ΔQ|C ΔQ|Overall ΔU_valid/K|Challenge Δpass@32|
|---|---:|---:|---:|---:|---:|
|1702|−2.521|−1.343|−1.389|−1.353|−0.781|
|1703|−0.059|+2.637|+0.174|−0.184|+3.906|
|1704|−1.068|+2.051|−4.145|−0.628|+3.906|
|1705|+1.852|−2.979|+3.798|+1.408|+3.906|

Primary paired mean −0.44881185 pp, sample SD 1.83708492 pp, range
−2.52115885 to +1.85221354 pp. Descriptive 95% paired-t interval (df3,
t=3.182446): **[−3.3720, +2.4744] pp**. With only four pairs, its normality
assumption is weak; this establishes neither superiority nor equivalence.
No p-values or map/sample pseudoreplication. Discovery 1701 (+2.941 pp overall,
+5.382 pp C) is separate, not counted as a fresh replication.

Challenge pass@32 is task success coverage at a finite sampling budget, not
coverage of the exact solution set. The retained `valid_headroom` is the distinct
valid routes divided by exact total shortest solutions M for each problem,
then aggregated: it is the exact valid-solution fraction covered. The separate
`coverage: null` field concerns novel-solution coverage (unique novel/Mnovel),
whose denominator was not supplied here; it is not all-solution coverage.
Pass@32 uses the same 32 draws per problem for each
architecture, but training compute is not equal. It counts at least one valid
solution among draws, not necessarily increased multiplicity of correct solutions.
The same frozen challenge opportunities are used within every pair.
Challenge and C measure different
generalization settings. C's frozen matching controls selected distance/branching
bins, not every geometry, path multiplicity or goal-distribution factor.

## Learning path and quality controls

[All paired trajectories](/Users/gmh-company/codex/schrodinger/execution/seed_replication/trajectories.md)
retain quality AND productive diversity at 1k/2k/4k/8k. At 1k all four Q deltas
favor SA; mean Q is 28.096% vs 27.383%, and mean U_valid/K is 23.026% vs 22.634%.
The mean Q advantage fades by 4k and reverses at 8k. This is a descriptive
training-stage pattern, not a selected-checkpoint significance claim or an
equal-time benefit. Both architectures improve route success substantially.

Frozen SA temperatures .75/1/1.25 were all retained for each pair; nearest
quality point is T1 in every seed. Only 1703 and 1704 meet the prespecified
approximate quality tolerances (2 pp mixture, 3 pp each stratum). Both have
lower overall U_valid/K than softmax, although challenge U_valid/K improves
by +0.806 and +1.416 pp respectively. This suggests a setting-specific shift,
not a general diversity gain. Seed 1702 fails the mixture bound; 1705 fails a
stratum bound. No grid extension, interpolation, matched-subset primary estimate
or same-quality claim for unmatched pairs. Raw grids remain in each analysis.

## Different behavior is real; useful uncertainty is not established

Mean state-policy TV is 0.1051 and argmax disagreement 11.46%; mean finite-K
valid-route-set Jaccard is 0.2725 on its defined nonempty-union domain. These
between-model differences are not within-model diversity or an effect isolated
to evolution at inference. Raw greedy outcome counts across the same 512 problems:

|Seed|Both solve|SM only|SA only|Neither|
|---|---:|---:|---:|---:|
|1702|214|74|67|157|
|1703|232|49|46|185|
|1704|212|68|51|181|
|1705|245|55|50|162|

These raw counts are descriptive and are not the 80/20 weighted endpoint.
There are complementary SA successes despite no overall robust advantage.
Teacher-relative mean KL is SM 0.36667 vs SA 0.35912, but Brier is SM 0.15064
vs SA 0.15395. Mean policy entropy is 0.42025 vs 0.42350 nats, teacher entropy
0.37229. Directions vary; entropy alone is not calibrated error uncertainty.
Mean duplicate fraction is 9.594% vs 9.334%, and duplicate concentration
0.22466 vs 0.22237: small descriptive changes can accompany different validity.

Strict novelty means an exact shortest legal route whose canonical action
signature is absent from complete training-route and suffix support, after
rotation/reflection/reversal equivalences. U_novel counts distinct valid raw
routes satisfying that test per K, not human-original strategies. Mean overall
U_novel/K is 0.9009% vs 0.9082%; challenge-only 4.5044% vs 4.5410%. Routine
has none by construction. This near-zero difference is supplementary.

## Execution, cost, and limits

All eight fresh owners validate identical within-pair shared initialization and
all 8000 minibatch digests. Seeds vary initialization, training stream and decoding
uniforms jointly; fixed model order is block-balanced. Same model/data/optimizer,
no test release or new cohort selection. Historical full-validation route rows
lack independent start/goal IDs: immutable producer/dataset order and verifier
checks bind them, but all-invalid within-map permutations cannot independently
prove order. New ABC outputs retain explicit identities.

Mean core training time SM **39.867 s**, SA **128.316 s** (ratio **3.22×**).
Eight training owners charged 1805.992922501 s total; four analysis owners charged
196.144278208 s. These include endpoint/setup/owner costs beyond core training.
Global operational debit **4156.469097296/7200 s**, remaining **3043.530902704 s**;
this cycle adds 2091.137200709 s to the inherited 2065.331896587 s. Includes
all failed tests, a disclosed extra 13.6 s conservative accounting allowance,
and 20 s read-only reporting/audit allowance; these are not extra model runs.
All stage ceilings remain respected. No further compute is planned.

Recommendation: do not claim a replicated creativity or transfer advantage.
The most defensible follow-up proposal is a separately frozen, adequately
replicated test of early-stage learning and challenge pass@K/valid diversity at
comparable quality and measured compute, not selecting the favorable seeds or
checkpoints here. This report does not authorize that follow-up.

Evidence: [frozen plan](/Users/gmh-company/codex/schrodinger/execution/seed_replication/plan.md),
[session record](/Users/gmh-company/codex/schrodinger/execution/seed_replication/run-record.md),
[implementation PASS](/Users/gmh-company/codex/schrodinger/execution/seed_replication/reviews/analysis-review-01.md).
[Final independent audit PASS](/Users/gmh-company/codex/schrodinger/execution/seed_replication/reviews/final-results-review.md)
reproduced the summaries, identities, coverage definitions and final budget.
Raw outputs are the four `replication-SEED-analysis/analysis.json` owners under
`execution/model_training_comparison`; each includes exact source/input/checkpoint
hashes, all retained event bindings, per-map/state/routes and all temperature points.
