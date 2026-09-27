# Productive-diversity v3 Block 1 core review

## Verdict: CHANGES REQUIRED

The direct placement implementation, explicit-dimension oracle calls, shortlist construction, and rational ranking formulas are consistent with the contract. However, the deterministic global-inventory boundary that assigns the map IDs used by shortlist RNG is absent, and several required tests assert only replay rather than the frozen streams and ranking precedence. These are bounded Block 1 corrections; no support, novelty, runner, production pool, or model work is requested.

## Exact versions reviewed

- Current accepted plan (status-only change after review 00): `productive_diversity_v3_plan.md`, SHA-256 `982674c12fba12bfa4338ae49f76234777af0a287c76de2e062bb4125385d601`
- Current accepted contract (status-only change after review 00): `execution/next_level_v3/specs/00-dataset-contract.md`, SHA-256 `4d41b6574b557ffb175e55cee04e6a7c4f67b78d660ac2b19de5ab6bf259e039`
- Block 1 specification: `execution/next_level_v3/specs/01-core-inventory-ranking.md`, SHA-256 `db0ad84f2f516009b3b2d148f7ee032013533df52d3714b4501ad2f6b50a20a3`
- Handoff: `execution/next_level_v3/handoffs/01-core.md`, SHA-256 `e73b91873585e8de45351934d5e8fa949fb29e53f33356a49be961ca4300e00b`
- Pure module: `schrodinger/productive_diversity_v3_data.py`, SHA-256 `eb1a9cf21cd06e27295209b3652c991dc7e3b1130ab42a43e70d13774aa5ac78`
- Focused tests: `tests/test_productive_diversity_v3_data.py`, SHA-256 `4ee760e5dd1d04d5fc3d4f365f0c52cc1274ff4d5bd497c037acf4bfcf230988`
- Ledger inspected: `execution/next_level_v3/ledger.jsonl`, SHA-256 `4533bb85174d9c041f83a0740268f1f89c67513a8583943c9de4eb7acd98122f`

The accepted scientific hashes remain recorded in `execution/next_level_v3/decisions.md`; the current plan/contract changes are acceptance-status text only.

## Required bounded corrections

1. **Implement and test the global inventory identity boundary.** Block 1 currently exposes per-family pools, a per-wall candidate function, and a per-map shortlist function, but no pure composition that combines all three family pools, rejects a canonical identity appearing under multiple families as a technical error, globally sorts canonical bytes, assigns stable increasing map IDs, reconstructs/validates walls and family, computes explicit-n candidates, and derives shortlists from those global IDs. This boundary is scientifically material because `SeedSequence([93001,map_id,length])` depends on the globally assigned ID. Add an injected small-pool interface/test; production defaults remain unchanged and must not be run.

2. **Exercise every pool rejection branch and frozen stream identity.** The current injected pool test proves overlap-first behavior and self-replay only. The touching and D4-duplicate counters/priority are not reached; the n=6 smoke conditionally validates a map only if the random pool happens to be nonempty. Add deterministic injected draw/placement fixtures that separately produce overlap, orthogonal touching without overlap, a retained map, and then a D4 duplicate. Assert exact counters/trial stopping and an independently constructed expected PCG64 draw prefix for `SeedSequence([93000,family_code])` rather than only comparing the function to itself.

3. **Strengthen inventory/shortlist oracle evidence.** The n=12 inventory test currently invokes `inventory_candidates` twice and checks q normalization, but does not independently verify candidate ordering, distance/M bounds, or BFS multiplicity on a retained pair involving cells above 63. The shortlist test checks replay/cap but not its frozen seed identity. Add one bounded oracle fixture that recomputes a candidate's distance/count independently and asserts sorted uniqueness/bounds, then constructs the exact expected permutation from `PCG64(SeedSequence([93001,map_id,length]))` and matches retained IDs/order. This need not generate any pool.

4. **Prove the full proposal-ranking precedence.** Existing feasible proposals all have identical scores and costs, so tests cover quota/window lexical fallback but not the declared primary ordering. Add a fixture where: a higher exact minimum normalized family-supply score beats a lower score regardless of cost; equal scores choose lower exact rational mean M; an exact score-and-cost tie chooses lower window start; and an intra-window tie chooses earlier canonical quota. Assert one winner per window and final top-three distinct-window order. Retain the route-enumeration prohibition.

## Static checks accepted and retained

- `direct_shape_placements` produces immutable cached tuples and correctly implements 240 I and 484 L placements at n=12. Small-n exhaustive equivalence is genuinely tested for n=3,4,5.
- Pool streams use `PCG64(SeedSequence([93000,family_code]))`, draw one component per literal family letter with replacement, and the source order is overlap, touching, then duplicate. Canonical retained maps are sorted and geometry validation is explicit in n.
- `inventory_candidates` passes n explicitly to BFS and applies the frozen 12–20 and `16 <= M <= 256` filters with deterministic tuple sorting.
- Per-map/length shortlists use independent `SeedSequence([93001,map_id,length])`, permute the complete sorted list once, and retain the first 64 without route enumeration.
- `rank_proposals` evaluates all 12 window/quota combinations, uses exact `Fraction` supply scores and mean-M costs, filters necessary 92/92/40 shortages, selects one quota per window, and retains at most three distinct windows. Its source ordering matches score descending, cost ascending, lower window start, and canonical quota order.
- No support, route-signature novelty, held-out selection, runner, CLI, production generation, or model code was added.

## Independent checks and charge

I recomputed all listed hashes and completed a static source/test trace against the accepted contract and Block 1 specification. The missing interface and assertions are directly visible, so I did not rerun pytest or any inventory command. Independent charged compute: **0 seconds**. Terra's reported `7 passed in 0.77s`, full-wall charge `0.901775708s`, and carry-forward ledger entry were inspected but not independently rerun.

Production inventory, proposal supply, support, novelty, dataset feasibility, runtime, and all model outcomes remain **NOT_EVALUATED**.
