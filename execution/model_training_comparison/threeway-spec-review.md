# Independent review — three-way checkpoint diagnosis specification

## Verdict: PASS

Reviewed specification SHA-256: `577a8ada24fa6708281d730bb291a78a89967f87aefc484e1c90449ac8325b5c`.

The frozen construction is sufficiently precise to test the intended retrospective distinction:

- A measures original training pairs on seen training maps.
- B changes the goal on those same maps and proves that the goal was absent from the complete saved per-map training-state goal set.
- C uses held-out routine maps, separately within the I and L families.

The design prevents the important exposure leak: every A DAG state must exist in the complete saved training-state set, while every B `(canonical,current,goal)` DAG state must have zero overlap with it. A coordinate seen on another map does not make the B goal seen on the current map. The result must therefore be described as map-specific goal exposure, not unseen spatial tokens.

The matching algorithm is actionable and outcome-blind. Route and state selection use identical joint-bin quotas across all three cohorts within each fixed triplet; the per-bin cap, deterministic ranking and collision tie-break are frozen; no secondary selector may disturb the state quotas. Requiring at least three route rows, eight state rows per triplet, and eight retained triplets in each family supplies an honest pre-inference feasibility gate with no replacement or reselection fallback. The byte prefix is interpreted literally as `b"goaldiag-route-v1\\0"`—a backslash byte followed by ASCII zero—as specified; this convention has no scientific effect provided it is tested and used consistently.

Equal within-map and then equal-map aggregation is appropriate because matched row counts are equal inside each retained triplet. Reports must still retain route/state bin denominators, exclusions, per-family values and the A/B/C pairing so the joint quotas are independently reconstructible. C is family/rank paired, not geometry matched.

The checkpoint-only measurements preserve the accepted source, data, initialization and evaluator boundaries. B's route multiplicity `M` must come from the accepted exact BFS path count and its novelty denominator should remain unavailable/unused; no novelty inference is supported. Split codes, seed and replicate are frozen, and all route success must be measured by the exact verifier rather than inferred from state averages.

The scientific limits are explicit: this is a retrospective matched population from one trained seed, first-action branching is not full difficulty matching, and differences cannot uniquely identify memorization, map transfer, spatial bias, or optimization cause. Mixed composition remains outside the three-way comparison.

The 120-second allocation is internally consistent with the inherited debit. This PASS authorizes implementation and focused literal tests only; it does not authorize inference until an exact-version implementation PASS, and it authorizes no training, test-set access, rematching, fallback cohort, or automatic follow-on experiment.

Static review only; no compute or ledger charge.
