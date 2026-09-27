# Independent plan review — difficult unfamiliar problems

**Plan SHA-256:** `738d95bd2e2e1329a484581175c02387432262b949df9bf71b0488515b0f4a1b`

**Verdict: CHANGES REQUIRED**

The plan is scientifically focused and appropriately staged. It has one primary D2 endpoint, keeps D0 explicitly post-hoc, defines difficulty without model outcomes, tunes both architectures on the same fixed validation grid and budget, treats the four old training seeds as conditional checkpoint evidence rather than new seed replication, separates seed and map uncertainty, and preserves the global/stage caps. The revised text also correctly discloses that the reserved mixed population was selected for structural novelty (`Mnovel≥4`, fraction `.25–.75`) and that this is a new endpoint/authorization amendment—not evidence that the old strict-novelty main gate passed or a representative sample of difficult planning generally.

Three bounded clarifications are required before implementation:

1. **Freeze the routine control population.** D1 and D2 require routine-Q guardrails but do not define which routine validation/test maps and problems enter them. State whether all frozen routine maps are used (the natural choice: all available frozen routine validation maps for tuning and all 96 frozen routine test maps for D2), or freeze another model-independent subset now. Specify equal-problem-within-map/equal-map weighting, exact identity hashes, and that routine inclusion is not filtered by mixed-map `d≥2` eligibility or either model's output. The selected architecture/seed temperature must then be evaluated on that same frozen routine control population at D2.

2. **Make test-time pairing explicit.** D1 specifies common uniforms, but D2 does not explicitly require them after the two architectures may select different temperatures. Freeze the test rollout RNG mapping so the same seed/map/problem/attempt uniforms are used for SM and SA at their respective validation-selected temperatures, with identical K, batching and verifier order. Bind the RNG/version and all included problem IDs before predictions. This preserves the paired seed/map endpoint and prevents avoidable Monte Carlo imbalance.

3. **Remove ambiguity from the D0 map-sensitivity gate.** “No single-map deletion reverses the sign” currently allows a leave-one-map-out contrast of exactly zero. Define the intended rule mechanically—for example, every leave-one-map-out four-seed mean challenge pass@32 contrast must remain strictly positive (or explicitly allow zero and explain why). Also state that each deletion removes the same challenge map across both architectures and all four seeds and recomputes the original equal-map statistic. This must be frozen before the decomposition is inspected.

The retained-bag hypergeometric pass@K and expected-distinct-route estimators are preferable to treating the saved attempt order as primary; prefix curves are appropriately relegated to sensitivity analysis. The hard population `d≥2`, support floors, symmetric grid, test-map bootstrap, correctness conjunction and productive-variation claim rule are otherwise sufficiently specified.

The proposed resource totals fit only narrowly but arithmetically: A adds at most 100 seconds to `466.802 < 700`; D adds at most 820 seconds to approximately `479.898 < 1300`; the 7200-second cap remains respected. Each block specification must use exact current ledger totals and include startup/finalization in its maximum. The 60-second D reserve may absorb accounting variance but is not permission to add endpoints or exceed a live owner deadline.

No implementation, tests, inference, training, final-test access, or model calls were performed for this review.
