# D0: broader problem coverage, not a demonstrated increase in route variety

Status: **D0 COMPLETE — frozen screening gate PASS and independent Sol results
audit PASS.** Single retained-data job completed with explicit exit0. D1/D2 have
not run and remain unauthorized.

The small challenge-coverage advantage survives removing any one map. It is
consistent with success spread across more problems, rather than substantially
more distinct solutions on problems both models already solve. This is a
post-hoc diagnosis of the same four seeds/eight validation maps—not new evidence
of architecture superiority, general planning ability or creativity.

## Sampling-budget curve

At 8k updates, mean challenge success across seeds1702–1705. K<32 uses the frozen
hypergeometric estimate over each saved32-draw bag, not new inference. K32 is
observed success; K1 is the empirical valid-draw fraction. Values are percentages.

|K|Softmax|Schrödinger|SA−SM, pp|
|---|---:|---:|---:|
|1|15.729|15.820|+0.092|
|2|23.825|24.173|+0.348|
|4|32.201|33.134|+0.934|
|8|39.494|41.288|+1.793|
|16|45.669|48.158|+2.489|
|32|51.367|54.102|+2.734|

Prefix sensitivity gives SA−SM −1.563,+0.391,+1.563,+2.148,+2.344,+2.734 pp
at those K values. The low-K sign can depend on draw order. These are correlated
views of the same bags, not six independent experiments or an extrapolation.

## Robustness to individual maps

All eight frozen same-map deletions remain positive; the smallest is +1.5625 pp
when map344 is removed. Three of four seed differences are positive, so the
prespecified D0 screening gate passes. Zero would have failed. This rules out
dependence on one indispensable map for this observed mean, not map-sampling
uncertainty or a multi-map concentration effect.

Counts below sum four paired seeds on each map (64 problem-seed opportunities);
they are not independent new maps. Gain/loss means SA-only/SM-only success atK32.

|Omitted map|LOMO mean Δ, pp|SA-only gains on map|SM-only losses on map|
|---|---:|---:|---:|
|220|+3.5714|6|8|
|344|+1.5625|12|5|
|386|+2.4554|7|4|
|786|+2.9018|3|2|
|951|+2.4554|8|5|
|1077|+3.1250|8|8|
|1242|+2.6786|7|5|
|1288|+3.1250|4|4|

Across maps, five mean effects are positive, one negative and two zero. Map344
accounts for7 of the net14 problem-seed successes, so concentration still matters.

|Seed|Both solve|SA only|SM only|Neither|Positive/negative maps|
|---|---:|---:|---:|---:|---:|
|1702|62|10|11|45|3 / 3|
|1703|52|16|11|49|4 / 2|
|1704|50|15|10|53|4 / 4|
|1705|58|14|9|47|4 / 3|

## Coverage versus variety

Across the512 problem-seed opportunities, SA solves277 at least once versus263
for softmax:55 SA-only and41 SM-only. Total valid draws differ little,2592 versus
2577, among16384 draws per architecture. Distinct valid routes summed within
problem-seed bags are1852 versus1831 (not globally unique routes).

Equal-map, then equal-seed summaries:

|Measure atK32|Softmax|Schrödinger|
|---|---:|---:|
|Distinct valid routes/K, all problems|11.176%|11.304%|
|Distinct valid routes/exact solution count M, all problems|4.239%|4.630%|
|Distinct valid routes/K, own solved subset|22.577%|20.718%|
|Distinct valid routes/M, own solved subset|9.827%|9.207%|
|Valid-route duplicate concentration, own solved subset|0.36525|0.36130|

Own solved subsets differ between models; these conditional decreases are not a
causal loss of variety. On the **same problems both models solve**, mean distinct
valid routes per problem is7.878 softmax versus7.810 SA (map-balanced, then
seed-balanced;62/52/50/58 shared problems, all8 maps represented per seed).
The small unconditional variety gain therefore does not demonstrate a strong
increase in solution multiplicity on already shared successes. Coverage and
conditional variety are different quantities; raw zero/support counts are retained.

## Difficulty and training stage

Predeclared challenge bins, equal-map within each bin and then equal seeds.
Different support across bins prevents interpreting their differences causally.

|Bin|Maps / problems|SM pass@32|SA pass@32|Δ, pp|
|---|---:|---:|---:|---:|
|Detour0|6 / 12|95.833%|100.000%|+4.167|
|Detour≥2|8 / 116|47.261%|49.797%|+2.537|
|Length14|8 / 48|36.979%|38.021%|+1.042|
|Length15|8 / 40|56.875%|64.375%|+7.500|
|Length16|8 / 40|63.125%|63.125%|0.000|
|M1–8|0 / 0|NA|NA|NA|
|M9–64|8 / 55|38.008%|43.601%|+5.593|
|M≥65|8 / 73|62.125%|63.008%|+0.883|

The mandatory-detour subset retains a positive descriptive effect. Length15 and
M9–64 look stronger, but these are correlated, reused-data subgroups—not candidates
to select for confirmation. Sparse detour0 and empty low-M support are explicit.

|Training updates|SM / SA challenge pass@32|SM / SA distinct-valid/K|
|---|---:|---:|
|1000|50.586% /51.953%|8.337% /8.490%|
|2000|55.273% /55.273%|8.881% /9.082%|
|4000|53.711% /53.906%|10.144% /9.985%|
|8000|51.367% /54.102%|11.176% /11.304%|

More training raises valid-route variety here but does not monotonically raise
challenge problem coverage. These descriptive trajectories do not select a new
checkpoint or alter the frozen8k gate. Equal draws/updates are not equal compute:
the preceding study measured SA core training at about3.22× softmax.

## Decision and evidence

**Recommend requesting approval for D1**, symmetric validation temperature controls
and feasibility profiling, because the frozen D0 robustness screen passed. D0
cannot rule out a temperature-tuned softmax explanation. No D1, D2, final-test
release, additional training or new samples occurred or are automatically authorized.
The selected mixed-composition panel carries the original novelty-selection bias;
there are still only four seeds and eight repeatedly analyzed maps. Historical
route rows retain their producer/order binding and all-invalid permutation caveat.

Single production owner: `execution/model_training_comparison/difficult-d0-001`,
session60836, explicit exit0, COMPLETE; elapsed18.686608375s plus4s allowances,
charged22.686608375s within60s. Development83.077375040/100s. With the separately
reserved20s conservative read-only reporting/audit allowance, global operational
debit4282.233080711/7200s; remaining2917.766919289s. This allowance is not model
compute and final audit must fit it or be separately accounted.

Raw metrics/gate/provenance: [d0.json](/Users/gmh-company/codex/schrodinger/execution/model_training_comparison/difficult-d0-001/d0.json).
Implementation [independent PASS](/Users/gmh-company/codex/schrodinger/execution/difficult_problem_solving/recovery-review.md).
[Independent results audit PASS](/Users/gmh-company/codex/schrodinger/execution/difficult_problem_solving/results-review.md)
verified all reported values, gate, identities and accounting; its12.0s read-only
checks fit the existing20s allowance without a duplicate charge. Original plan
and historical records preserved.
