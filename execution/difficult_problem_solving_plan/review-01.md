# Independent final plan review — difficult unfamiliar problems

**Plan SHA-256:** `c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`

**Verdict: PASS**

The consolidated revision closes all findings from `review-00.md` and corrects the primary estimand without introducing outcome-dependent selection.

- Routine controls are now exactly all 24 original validation and all 96 reserved test homogeneous maps, 16 problems per map, with equal problem weight within map and equal map weight, fixed identities/hashes, and no filtering by mixed difficulty or model outputs.
- D2 pairs softmax and SA with the same per-seed/problem/draw/step uniforms despite potentially different validation-selected temperatures. It freezes seed, splitcode 2, replicate 0, K32, RNG construction/digests, problem identities, and the block-balanced evaluation order before predictions.
- The D0 leave-one-map-out rule is mechanical and strict: delete the same challenge map for both modes and all four seeds, recompute each seven-map equal-map contrast, average seeds, and require every result to remain strictly positive; zero fails.

The primary D2 endpoint now remains aligned with the motivating signal: all 32 reserved mixed-composition test maps, rather than a sparse post-hoc difficulty subset. Detour, length, and multiplicity bins are model-independent, predeclared secondary descriptions only. The plan discloses that this mixed population was itself selected for structural-novelty opportunity and therefore does not represent difficult planning problems generally or resurrect the old strict-novelty main-study approval.

The rest of the design is coherent and bounded:

- D0 is a retained-data, explicitly post-hoc screen using order-invariant hypergeometric bag estimates as primary and saved prefixes only as sensitivity analysis.
- D1 tunes both architectures symmetrically on the same fixed five-temperature grid, common uniforms and validation panels, under common correctness floors; all candidates are retained and test rules are frozen before release.
- D2 has one primary held-out-map pass@32 contrast, seed-level and map-level uncertainty with distinct interpretations, demanding predeclared conjunction gates, and no inference from route draws as independent training replications.
- Productive-route-variation claims additionally require a positive seed-interval lower bound for `U_valid/K`; entropy, disagreement and strict signature novelty cannot substitute.
- Only measured K32 endpoint latency is reported. Prefix/bag curves cannot be converted into inferred time curves, and neither equal-inference-time nor equal-training-time superiority is claimed.
- D2 call cardinality, routine/mixed problem counts, proper-score work, hard 1.5× forecast gate, panel-consumption caveat and future-authority boundary are explicit.

The prospective maxima remain within the current caps: stage A adds at most 100 seconds; stage D operational work plus reserve adds at most 820 seconds to approximately 479.898/1300; the unchanged global 7200-second cap retains substantial headroom. Exact ledger values and complete startup/finalization charges must be used in later block contracts. The 60-second reserve cannot add endpoints or enlarge a running deadline.

This PASS approves the scientific plan only. It does not authorize D0 implementation or execution, D1 validation inference, oracle-only test eligibility access, D2 final-test predictions, or D3 training. Each requires the explicit future authority and exact-version gates stated in the plan.

No implementation, tests, inference, training, test-data access, or model calls were performed.
