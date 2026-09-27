# Independent implementation review — paired-behavior analysis

## Verdict: CHANGES REQUIRED

Exact reviewed files:

- `analysis.py`: `99061c822f751c99d1fa1a1a94f92dfe17b6f97195b04145ed247e488d35fa44`
- `job.py`: `accc922108d979d99c2e311df7a3b3670a62065c664d63069bb468b56b52cfed`
- tests: `8579366d71d3a98ae8db723c7ea0465d9d05946b7a1ad5a0cec2c504f92f3552`
- governing plan: `be5e5fea4fd5f2ee0e4cb3013637127b9437409bef6d6fa993f06777e65b39be`

Do not launch `paired-behavior-analysis-001` from this version. The pure helpers contain useful alignment and set logic, but the composed job has one immediate runtime failure and several required outputs/bindings are absent.

## Required corrections

1. **Actual retained-event serialization is incompatible with both adapters.** `_storedproper` assumes `raw["canonical"]` is a `{bytes_hex: ...}` object and `_storedroutes` assumes a route is such an object or a directly bytes-convertible sequence. In the accepted immutable result files, both are hexadecimal strings. The first stored proper row therefore fails at `raw["canonical"]["bytes_hex"]`; a route string reaches `bytes(route)` and fails without an encoding. The synthetic adapter test encodes the wrong wrapper format and cannot detect this. Correct both decoders and exercise the literal retained event representation.

2. **Route records are still paired by an inadequately checked positional zip.** `_storedroutes` validates only `map_id` and `family`; many consecutive validation problems share both. It then injects canonical/start/goal from the expected dataset row, so `paired_greedy` sees apparently matching keys even if saved problem groups within a map are reordered. This violates the frozen requirement to verify route order against the bound dataset rather than blindly zip. The bounded correction must bind the immutable event/result and dataset identities and validate all available per-problem evidence against the expected problem before injecting its identity; add a negative same-map reorder fixture.

3. **The required T=1 behavior outputs are incomplete.** `valid_route_sets` returns unique valid-route and signature counts but not the retained raw valid sets, attempt-level quality, pass@32, `U_valid/K32`, `U_novel/K32`, or `V_novel/K32`. The job drops the stored T=1 problem records after forming count rows. Consequently it cannot provide the planned paired sampled-success/pass@32 comparison or independently audit route-set membership and novelty. Retain raw sets/counts and report the required normalized quality/diversity metrics with equal-map summaries. Both-empty Jaccard NA is already correct.

4. **State uncertainty scoring is only partially implemented.** Raw aligned p/q and entropy differences are retained, but the paired state/per-map output omits CE, KL, Brier and nonoptimal mass for each architecture, despite these being the predeclared ambiguity-aware measurements. `proper_sm`/`proper_sa` retain only the event's global weighted summaries, not paired state/per-map values. Compute these directly from the already aligned p/q rows and include them in the raw/equal-map summaries; this requires no inference.

5. **Block 3 does not bind or include the existing softmax A/B/C scores.** The job hash-reads only `matched_support.json`, computes only the Schrödinger cohorts, and never reads the immutable three-way softmax result. Thus the promised paired architecture differences cannot be produced and the softmax comparator is not provenance-bound. Bind the accepted support hash **and** three-way result hash, validate that its embedded support/checkpoint identities match, and retain the corresponding softmax scores alongside the new Schrödinger scores. Merely recording whatever support hash is currently present is not an immutable expected-hash check.

These are direct plan requirements, not optional framework expansion. The quality-control grid itself is correctly limited to two new SA rollout calls plus retained T=1, with the frozen validation-only tolerances and tie rule. The owner deadline, checkpoint guards, batch-digest check and no-test boundary are otherwise appropriately scoped.

Per the parent-approved recovery boundary, one bounded correction may address this consolidated list. If any substantive item remains afterward, the analysis job must stop; the accepted training result and a smaller read-only report remain available without waiving this production gate.

Static review only; no tests, inference, or ledger charge.
