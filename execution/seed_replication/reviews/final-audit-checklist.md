# Frozen final audit checklist

This checklist was fixed while the eighth training owner was still active. It does not contain or select on later results.

## 1. Completion and provenance

- Exactly eight distinct training owners exist in the frozen command order: seeds 1702–1705, both modes, update 8000; exactly four analysis owners exist.
- Every owner is terminal `COMPLETE`, lock-free, uniquely charged once, manifest-valid, and associated with the retained command/session and explicit exit 0. No replacement seed, relaunch, resume, overlap, or extra inference owner exists.
- Every training result binds the accepted prepared/source/config/manifest and selection hashes, reviewed wrapper/plan/resource table, exact seed/mode decision and argv.
- Every analysis result binds the reviewed analysis/helper hashes and both consumed training owners. Output-manifest hashes match all consumed result, checkpoint, curve, event and analysis artifacts.

## 2. Within-pair fairness

For each fresh seed independently verify:

- matching non-null shared-initial digest and equality of every common initial tensor;
- exact 1…8000 checkpoint/sampler lineage and all 8000 minibatch digests identical across modes;
- correct seed/mode/update/source/config/input identities and distinct immutable owner/checkpoint hashes;
- identical frozen full-validation problem/event order, q rows and rollout stream identifiers where required;
- both fresh models, not discovery substitutes, score all A/B/C rows with the prescribed seed, split and replicate.

## 3. Primary fresh-four estimate

- Extract each seed's stored 8k full-validation T=1/K32 equal-map 80/20 mixture quality and compute `d_i = Q_SA − Q_SM`.
- Report all four `d_i`, arithmetic mean, sample SD with denominator `n−1`, min/max range, and positive/negative/zero direction count.
- Report the descriptive df=3 interval `mean ± 3.182446 × SD / sqrt(4)` without a p-value or a claim of definitive proof; explicitly retain the weak-normality and n=4 limitations.
- Present seed 1701 separately as discovery. Any pooled-five value is exploratory and cannot replace the fresh-four estimate.

## 4. Frozen secondary evidence

- At 1k/2k/4k/8k, report full-validation T1 quality and productive valid-route metrics from retained events for both modes; include routine, challenge and fixed 80/20 mixture, with equal-map weighting.
- At 8k report proper KL/Brier and q-relative entropy, greedy complementary outcomes, policy disagreement, valid-route overlap, raw and normalized `U_valid/K`, strict `U_novel/K` and `V_novel/K`, plus duplication/concentration only where actually retained.
- Report A/B/C for both fresh models in every seed. Treat C as unseen routine-map transfer and full-validation challenge as mixed-composition transfer; do not merge or call either final-test performance.
- Preserve exact route validity, fixed K=32 denominators, support/signature definition and the disclosed historical all-invalid permutation/order limitation.

## 5. Quality-control interpretation

- For every seed verify the grid is exactly SA T=.75, 1, 1.25 against paired SM T=1, with only two new calls, current seed, split 1 and replicate 0.
- Recompute nearest mixture-quality selection with lower-temperature tie break, then independently apply the ≤.02 mixture and ≤.03 both-strata tolerances.
- Report all grid points. If unmatched, make no same-quality novelty/diversity claim and do not pool a selected temperature as though preregistered. No cross-seed temperature selection or expanded search.

## 6. Retrospective productive-diversity synthesis

- Label the useful-valid-variation emphasis explicitly retrospective and supplementary to the primary quality estimate.
- Invalid or repeated routes do not add productive diversity; finite-K diversity remains quality-dependent.
- Separate within-model diversity from between-model disagreement/overlap and entropy.
- State whether the fresh evidence supports useful varied solutions and transfer in this toy setting only; do not generalize to human creativity, architectural superiority or causal mechanism.

## 7. Budget and execution closeout

- Reconcile unique ledger UUIDs, stages and charged seconds against the reviewed A/B/D ceilings and 7200-second global cap. Preserve the disclosed conservative duplicate D allowance and A correction; do not rewrite history.
- Account for all failed development tests, training/analysis owner allowances, independent audits and finalization allowance.
- Confirm all sessions exited, no job/lock remains, and no final-test artifact was opened or scored.
- Bind final raw summary/report/figure inputs and outputs by SHA-256. Report measured versus conservative allowances distinctly.
