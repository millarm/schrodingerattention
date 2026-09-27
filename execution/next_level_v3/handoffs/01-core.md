# V3 Block 1 — pure n=12 core handoff

Status: ready for independent Sol review.  This handoff covers only the frozen
geometry/pool/inventory/shortlist/raw-capacity-ranking block.  No production
pool or inventory was generated.

## Changed files

- `schrodinger/productive_diversity_v3_data.py`
  `eb1a9cf21cd06e27295209b3652c991dc7e3b1130ab42a43e70d13774aa5ac78`
- `tests/test_productive_diversity_v3_data.py`
  `4ee760e5dd1d04d5fc3d4f365f0c52cc1274ff4d5bd497c037acf4bfcf230988`

Frozen inputs read for this block:

- `productive_diversity_v3_plan.md`
  `982674c12fba12bfa4338ae49f76234777af0a287c76de2e062bb4125385d601`
- `execution/next_level_v3/specs/00-dataset-contract.md`
  `4d41b6574b557ffb175e55cee04e6a7c4f67b78d660ac2b19de5ab6bf259e039`
- `execution/next_level_v3/specs/01-core-inventory-ranking.md`
  `db0ad84f2f516009b3b2d148f7ee032013533df52d3714b4501ad2f6b50a20a3`

## Evidence

Command (one focused development computation):

```
.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_data.py
```

Exit status: 0.  Full tool wall elapsed: 0.901775708 s.  Pytest reported
`7 passed in 0.77s`.  The v3 ledger has exactly one new test charge,
`8e63d280-3c2a-403f-952d-f06b87583737`; its current SHA-256 is
`4533bb85174d9c041f83a0740268f1f89c67513a8583943c9de4eb7acd98122f`.
The carry-forward debit 443.384519002 s remains explicitly non-compute.

## Acceptance mapping

| Frozen requirement | Function / assertion |
| --- | --- |
| Direct immutable I/L placements; small exhaustive equivalence; 12x12 counts | `direct_shape_placements`; `test_direct_placements_match_small_exhaustive_and_n12_counts` checks n=3/4/5 exact old-oracle sets, 240 I, 484 L, and a cell above 63. |
| Frozen seeded bounded family drawing and rejection priority | `pool_family`, `validate_family_components`; `test_pool_has_seed_replay_and_rejection_priority` injects overlap and asserts replay and overlap-before-touch/duplicate. |
| Canonical identities / separated components | `validate_family_components`; `test_pool_canonical_dedup_and_component_validation` checks sorted unique canonical result and validates a compact n=6 smoke map. |
| Explicit n=12 BFS/q semantics | `inventory_candidates`; `test_explicit_n12_bfs_and_q_oracle_uses_cells_above_63` uses n=12 target 143 and checks q normalization. |
| Per-map/length PCG64 shortlists | `shortlist_by_length`; its test verifies replay, complete permutation length, cap 64, and retained permutation order. |
| All 12 raw proposals, exact ratios/costs, capacity failure | `rank_proposals`; `test_ranking_raw_capacity_failure_exact_ratio_and_no_route_enumeration` checks 91/92 exact Fraction JSON and `RAW_JOINT_CAPACITY_FAILED`. |
| Quota tie order, one winner/window, distinct-window top-3 | `rank_proposals`; `test_ranking_quota_order_mean_m_tie_and_three_distinct_windows` checks 12 proposals, four winners, canonical first quota, exact mean M, and starts 12/14/16. |
| Ranking must not enumerate routes | The failure test monkeypatches a raising `enumerate_routes`; ranking succeeds without invoking it. |

## Scope limits

This is intentionally not a production inventory, proposal-support/novelty
implementation, held-out selection, runner, CLI, model, or training result.
The compact pool test uses n=6 and injected placement fixtures only.  Production
defaults remain encoded in the pure functions but were not executed here.
