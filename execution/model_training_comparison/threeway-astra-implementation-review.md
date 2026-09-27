# Independent review — Astra three-way implementation closure

## Verdict: PASS

Exact reviewed artifacts:

- corrected source: `7b2a53d37bcae421fbd82ba3c174c0f9f812a051f583faceb8fc6ef7095620ef`
- corrected tests: `a1cad097c2fbe3029a5eab7e3a81f267b884827b458a2cbb5c8e341f8d1275f8`
- authorization: `dac982fc81b3f17c4551224917ccb40c4c0964ee4234bc83ea4a369a90394818`
- handoff: `17cf84027d92a7b99c5f388273cd981c75b4c1f0adc83b1ba9792d3ddda690ee`
- governing specification: `577a8ada24fa6708281d730bb291a78a89967f87aefc484e1c90449ac8325b5c`

The narrow authorized correction closes all three blockers from `threeway-implementation-review.md` without changing cohort construction or scientific gates:

1. `matched_support.json` now derives `MATCHED_SUPPORT_SUFFICIENT` or `MATCHED_SUPPORT_INSUFFICIENT` from the same retained-family threshold used to decide whether inference may proceed. The pre-inference artifact is truthful on both paths.
2. Joint-bin metadata now distinguishes unconstrained per-bin `capacities` from final selected `quotas`. The latter increments only when a row is actually retained before the global 6/32 cap, so its sum and bin counts exactly match persisted identities for all three cohorts.
3. Literal tests now verify the exact open-grid completion-weighted start q, true 14/15/16 path lengths and multiplicities, an eight-bin capacity truncated to six actual quotas, both support statuses, a genuine successful three-cohort route-to-DAG composition, direct `selected == candidates == states` banks, q normalization, and identical actual state-bin counts across cohorts.

The previously accepted source boundaries remain intact: map-specific complete saved-goal exclusion, A/B exposure checks, fixed triplets and ≥8/family gate, outcome-blind support persistence, all-selected banks without secondary sampling, updates 1,000/4,000/8,000 only, exact checkpoint/prepared/source identities, accepted evaluators/support, 70-second owned deadline, finite JSON and owner manifest semantics.

This PASS authorizes exactly one uniquely owned `threeway-diagnosis-001` inference-only attempt. A genuine `MATCHED_SUPPORT_INSUFFICIENT` result must stop without fallback or rematching. No training, model/data modification, test-set access, rerun, or automatic follow-on experiment is authorized.

Static review only; no independent test execution or ledger charge.
