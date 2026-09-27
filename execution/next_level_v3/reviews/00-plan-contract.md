# Productive-diversity v3 plan and dataset-contract review

## Verdict: PASS

The v3 plan and frozen Stage 0 contract define one bounded, deterministic 12×12 dataset construction and preserve the accepted v2 learning/comparison criteria. The redesign directly addresses v2's observed length-flow failure by ranking only three-length, same-quota-per-map proposals before support construction, without using model outcomes or weakening novelty. It is suitable for the stated three-block implementation sequence. No production generation or model work is authorized until all implementation blocks independently pass.

## Exact documents reviewed

- V3 scientific plan: `productive_diversity_v3_plan.md`, SHA-256 `7d7681941ab2c9aa607bb93c1c323ac3e26c3dac78ff036f710b9a226384b543`
- V3 dataset contract: `execution/next_level_v3/specs/00-dataset-contract.md`, SHA-256 `70d8a36982816287a3827060cb5861678e7cb5557daf6706bf3a4ad76d3c5fc4`
- Inherited v2 criteria: `productive_diversity_v2_plan.md`, SHA-256 `c603fec5d64314514bb971afa41b84344e8e3ff81f4fcf0c3d7e1ade14ceefc9`
- Reviewed v2 stopping result used as motivation: `execution/next_level_v2/final_report.md`, SHA-256 `a73fe1ff40f7050c9e2106d4a31b7fbff06bdd8555c3fbd9727f96c84013deca`

## Scientific and determinism checks

- **One task and representation:** n=12, exactly eight separated triominoes, homogeneous I⁸/L⁸ training and routine maps, I⁴L⁴ challenge maps, and CLS+12 row tokens are explicit. The 36 wall/current/goal features remain compositional and shared across architectures. Architecture capacity controls, optimizer, decoding, quality, power, uncertainty, dt0, and interpretation rules are inherited without introducing a favorable extra arm.
- **Direct geometry:** exact I and L placement counts, sorting, family strings/codes, draw streams, rejection order, D4 identity, pool limits, and technical geometry checks are frozen. All geometry/oracle calls must receive n=12; no fixed-N=8 v2 data helper is admissible.
- **Shortlists:** complete sorted ordered-pair inventories use distances 12–20 and `16 <= M <= 256`. Per-map/length PCG64 streams, the 64-pair cap, retained ordering, pair identities, and raw counts are fixed before any support or novelty computation.
- **Proposal sufficiency:** the raw totals 92 I⁸, 92 L⁸, and 40 I⁴L⁴ exactly equal the disjoint map needs across train/validation/test. All 12 window/quota proposals are scored. Exact rational minimum normalized supply, pair-weighted rational mean-M cost, lower-window and quota-order ties make ranking deterministic. One quota is retained per window and at most three distinct windows proceed.
- **No support leakage in ranking:** raw ranking uses only fixed BFS length/M capacity. It does not inspect training signatures, held-out novelty, model outputs, or learned scores. Proposal identity is stable by window start rather than outcome-dependent rank.
- **Support dependence handled correctly:** each proposal first freezes 32 training maps per homogeneous family and exact quota-selected pairs, then independently builds deduplicated DAG/q supervision and complete nonempty shortest-suffix support. Support is rebuilt and hash-keyed per proposal; it cannot leak across proposals.
- **Held-out selection:** frozen family/split streams, ascending lengths, shortlist order, full per-map quotas, commit-after-complete-pass, and prior-identity exclusion are exact. Routine requires zero novel routes; challenge requires at least four and ratio `[.25,.75]`. Validation precedes test. Unscanned maps are correctly `NOT_EVALUATED`, not negative evidence.
- **Length fairness:** every selected map in every stratum uses the same chosen three lengths and one 6/5/5 permutation, totaling 16. Thus split length proportions are identical by construction and every training length has far more than the minimum 16 examples. Narrowing length support is explicitly part of the post-v2 design and is not hidden as greater length diversity.
- **Proposal advancement:** only raw/held-out finite supply or training-orientation shortage may advance to the next pre-ranked proposal. Technical, oracle, count, hash, deadline, or budget errors stop. Using oracle construction feasibility—including the targeted final-test stratum—to choose among pre-ranked proposals is model-blind dataset construction, not model-selection leakage; the plan correctly limits resulting prevalence claims.

## Inherited endpoint and fairness checks

- The primary endpoint remains K32 distinct valid novel routes divided by all attempts, averaged problem→map→stratum and weighted 0.8 routine/0.2 challenge. The 1 pp gain, CI-above-zero, and 8/10-seed gates are unchanged.
- Known-valid mass uses weighted attempt totals, not averaged conditional ratios. Routine equivalence, overall 1 pp noninferiority, challenge 2 pp noninferiority, >=88% test quality, and <=1 pp paired quality difference remain conjunctive; routine mass cannot hide challenge damage.
- Validation-only quality matching, fixed temperature curves, entropy control, common indexed uniforms, zero-denominator behavior, support coverage, duplicate concentration, proper scoring, bootstrap, and fresh paired seeds remain inherited.
- The corrected four-replicate pilot variance addback and single-K32 MC-SD gate remain unchanged. Test outputs cannot select exposure, temperature, power eligibility, proposal, or architecture settings.
- The dt0 intervention remains secondary and training-mediated persistence is not mislabeled as absence of usable learning.

## Feasibility, budget, and process checks

- The finite pool, 64-pair shortlists, three proposals, bounded support-keyed caches, lazy per-length scans, route counters, and 1,600-second dataset ceiling make resource failure observable rather than silently changing the sample.
- The v2 conservative debit `443.384519002s` is carried exactly once. The remaining allocation sums to `6,756.615480998s`, preserving the 7,200-second global ceiling; v3 uses a separate ledger but must include that opening debit in every global guard.
- Development checks are limited to 180 cumulative seconds and 60 seconds per command. Tests may use internal small fixtures but cannot expose relaxed production CLI options or count as pool outcomes.
- The three implementation blocks are properly separated: pure geometry/pools/ranking; support/lazy held-out construction; then the safety/evidence runner. Each must provide executable assertions and independent review before the single production command. Terra resumes implementation ownership; Astra remains supervisor/specifier.

## Unknowns preserved by this PASS

Pool supply, proposal raw capacity, orientation coverage, exact support size, routine/challenge quota supply, runtime, 13-token learnability, pilot power, quality matching, productive-diversity gain, and dt0 removal remain unknown. Any frozen dataset, learning, power, quality, or runtime gate may stop the experiment. Such a stop is evidence about this bounded construction only and is not permission to add windows, resample maps, change quotas, weaken novelty, or claim domain-wide impossibility.

No code, pool, proposal score, dataset, model, pilot, or training command was executed during this review. Independent charged compute: **0 seconds**.
