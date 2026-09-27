# Productive-diversity v2 scientific-plan review

## Verdict: CHANGES REQUIRED

The v2 redesign is a proportionate response to the failed 6x6 benchmark: it tests one exact-oracle route task, increases combinatorial support through an 8x8 dataset-only ladder, keeps the model compact, targets a modest deployment-weighted yield effect, and adds ten fresh paired main seeds. No model should be built until the selected rung passes strict dataset feasibility. Five bounded clarifications are required before generation so power, quality, aggregation, and budget conclusions cannot shift after pilot results.

## Exact documents reviewed

- Proposed v2 plan: `productive_diversity_v2_plan.md`, SHA-256 `9abbffab6c041dfdd3555eefdf28325ba0286953124b3cdc68678f03a181d519`
- Accepted prior feasibility report: `execution/next_level/final_report.md`, SHA-256 `99384ef4110e1eef8000cb1b8fedbe95524b5662ac4efc917ff5d464ca5b4bc6`

No map pool, dataset, model, pilot, training, or evaluation was generated or run during this review.

## Required clarifications

1. **Correct the pilot-to-main Monte Carlo variance mismatch.** Each pilot seed effect is the mean of four independent K32 replicate effects, while the main effect is one K32 replicate. The current five-seed SD therefore estimates variance with one quarter of the main Monte Carlo component and can understate required main uncertainty. Preserve a single K32 main endpoint, but freeze the following add-back or an equally conservative exact equivalent:
   - Let `d_ir` be the four paired K32 effects, `dbar_i` their mean, `sbar²` the sample variance of the five `dbar_i`, and `vwithin` the mean of the five within-seed sample variances across the four replicates.
   - Form separate predeclared 80% upper variance bounds: `sbar_upper² = 4*sbar²/chi2_quantile(.20,4)` and `vwithin_upper = 15*vwithin/chi2_quantile(.20,15)`.
   - Use `s_main_upper = sqrt(sbar_upper² + .75*vwithin_upper)` in the ten-seed power inequality. The `.75` restores the additional Monte Carlo variance of one K32 result relative to a four-replicate mean.
   - Require the conservative single-K32 paired Monte Carlo SD `sqrt(vwithin_upper) <= .002`; do not label the smaller SE of the four-replicate pilot mean as the main endpoint's MC error. Report all replicate values and the decomposition. This remains a planning proxy, not guaranteed power.

2. **Protect challenge quality directly.** Routine equivalence and 80/20 overall noninferiority can still permit a roughly five-point challenge loss to be hidden by routine mass. Add a challenge-stratum one-sided 95% paired noninferiority bound, with a predeclared margin no wider than 2 pp, to the architecture-support gate. Retain conditional challenge quality reporting, >=88% overall matched quality, routine +/-1 pp equivalence, and overall 1 pp noninferiority. A novelty gain accompanied by a challenge-quality failure must not support productive diversity.

3. **Define weighted mass and yield aggregation exactly.** Freeze per-attempt counts before ratios. For each seed/model, sum valid, known-valid, novel-valid, and distinct-route quantities within maps, average maps within each stratum, then apply 0.8/0.2 stratum weights. Define the known-valid fraction as `weighted known-valid attempt mass / weighted valid attempt mass`, with an explicit failure/NA rule if weighted valid mass is zero—not as an average of per-problem fractions. State that `V_novel` counts every valid novel attempt including repeats, while `U_novel` counts distinct exact valid novel routes within a problem. Give zero-denominator rules for exact-support coverage and duplicate concentration, and apply the primary paired effect to the resulting seed-level weighted `U_novel/32` values.

4. **Freeze rung-specific family allocation and length-flow semantics.** Before generation, specify exact per-family map counts for every split. For rung A, use equal allocations within routine III/LLL and challenge IIL/ILL strata unless a different fixed allocation is scientifically justified; rung B has one family per stratum. Define “match the exact histogram” as Hamilton-scaled training length proportions for each validation/test stratum, followed by one deterministic map-to-length residual flow with exactly 16 problems per map. Freeze placement seeds, attempt order, D4 identity, rejection reasons, start/goal selection, and rung stopping before seeing pool outcomes. Explicitly require `n=8` in every reused geometry/oracle/signature helper and regression-test against accidental 6x6 defaults.

5. **Make the runtime forecast cover the actual Python work.** The 1.5x pre-main projection must include all remaining 20 trainings and checkpoint validation, state-logit cache construction, four pilot K32 replicates, the single main K32 arrays at every fixed/matched/entropy/dt0 operating point, Python rollout traversal, uniqueness/signature aggregation, proper-score banks, bootstrap work, serialization, independent audit, and reserve. Cache inference time alone is not an evaluation forecast. Charge all dataset rung attempts, tests, failures, and audits to the same 7,200-second ledger; stop before main seeds if the conservative projected total does not fit.

## Accepted design elements to preserve

- The ladder changes dataset complexity only: rung A is attempted first, rung B only after a preserved dataset-feasibility failure, and neither uses model outcomes. Two failed rungs stop the plan.
- Eight-row plus CLS encoding with fixed column feature slots avoids a 65-token matrix exponential while retaining complete wall/current/goal visibility. The baseline pilot appropriately treats learnability as unknown.
- Full training-DAG suffix support, D4/translation/reversal signatures, disjoint canonical maps, targeted routine `M_novel=0` and challenge `M_novel` strata, and matched length support directly address the prior benchmark's failure without weakening novelty.
- The 80/20 deployment estimand, raw stratum reporting, primary `U_novel/K` yield, invalid/duplicate attempt charging, and 1 pp screening effect make the claim modest and interpretable. The physical 3:1 sample ratio is correctly separated from the 4:1 estimand.
- Active eight-scalar softmax control, paired initialization/batches, fresh ten-seed main comparison, validation-only checkpoint and temperature decisions, common uniforms, fixed K32, full quality-diversity curves, entropy control, and dt0 rematching address the major capacity, optimization, decoding, and mechanism confounds.
- Usability, headroom, dataset, power, runtime, matched-quality, equivalence, noninferiority, known-mass, and primary-effect requirements are conjunctive. Failures remain planned stops rather than evidence of equivalence or broad falsification.
- The first execution block should remain dataset-only and reuse the already verified pure oracle/canonicalization/flow/safety concepts additively under new v2 paths, with explicit 8x8 parameters. Rebuilding the model framework before dataset PASS would be out of scope.

## Review boundary

The finite pool supply, length-flow feasibility, strict novelty strata, row-token learnability, pilot variance, runtime, and 1 pp effect are all unknown. They become evidence only through separately reviewed contracts and immutable gated execution. This review does not authorize skipping the dataset-only first gate or changing thresholds after an unfavorable outcome.

