# V3 Block 1 correction handoff — global inventory and deterministic evidence

Status: ready for Sol re-review. This remains the frozen pure Block 1 only:
no production generation, routes, novelty/support, held-out selection, runner,
or model work was performed.

## Versions

- `schrodinger/productive_diversity_v3_data.py` — `047c45b104c2ca92c2451e518102211760374c397f7efe950e9e107a4cd8882f`
- `tests/test_productive_diversity_v3_data.py` — `39d4d0347dd1dbab7887a25f5436c5316c02e2d9528271fac4e9a3b17540be3e`
- Sol review `execution/next_level_v3/reviews/01-core.md` — `eac7486ce1d5be1e99a8636d03c98a8157c39cc4f5b99a20db8eedd6d101b49c`

## Corrected review mapping

1. **Global identity boundary:** `assemble_global_inventory` consumes all three pools, rejects any repeated canonical bytes as `GeometryError`, sorts bytes globally before assigning zero-based IDs, reconstructs/validates walls and family, calls the candidate oracle with explicit `n`, and derives shortlists with that global map ID. `test_global_assembler_sorts_ids_rejects_cross_family_and_passes_n` uses three real valid eight-component n=12 maps, asserts global byte order, IDs 0/1/2, explicit n=12 calls, and a cross-family collision error.
2. **Pool branches and frozen stream:** `PoolResult.draw_prefix` audits each trial and `pool_family(..., injected_draw_rows=...)` is an internal fixture seam only. `test_pool_branch_order_and_independent_pcg64_draw_prefix` independently instantiates `PCG64(SeedSequence([93000,0]))`, asserts the actual eight-index prefix, then separately drives overlap, no-overlap orthogonal-touching, retained, and D4-duplicate paths with exact four-trial counters. The component validator is deliberately bypassed only for the indexed branch fixture; the assembler test exercises real n=12 validation.
3. **Inventory and shortlist oracle evidence:** `test_explicit_n12_bfs_candidate_bounds_order_and_q_oracle` independently checks the empty-board retained pair `(98,143,12,C(12,3)=220)` above cell 63, sorting/uniqueness and frozen bounds. The shortlist test independently builds `PCG64(SeedSequence([93001,17,12]))`, asserts its full permutation and exact first-64 retained order.
4. **Ranking precedence:** `test_ranking_precedence_score_cost_window_quota_and_top_three` builds all four windows with raw eligible counts: score 2 beats score 1 even at higher cost; score ties use exact mean M; score/cost ties use lower window start; each window uses canonical quota index 0; final retained starts are 12,16,18. The retained no-route-enumeration monkeypatch remains in the raw capacity failure test.

## Commands and charges

All commands used the focused fixture-only test target:

```
.venv/bin/python -m pytest -q tests/test_productive_diversity_v3_data.py
```

| Result | Full tool wall | Pytest result | Ledger UUID |
| --- | ---: | --- | --- |
| Failed correction iteration | 0.961363583 s | 4 failed, 3 passed | `0be701d0-db39-43d3-8709-c81f379de4e7` |
| Failed correction iteration | 0.607238042 s | 2 failed, 5 passed | `3d655f09-4b30-441b-907a-0446fdff6bb7` |
| Final verification | 0.603277917 s | 7 passed | `619b2272-6c96-4912-bfad-33af2fdb7ad5` |

Including the original 0.901775708 s Block-1 verification, recorded v3 development test charge is **3.073655250 s**, well below the 180 s ceiling. The carry-forward debit remains a separate 443.384519002 s non-compute entry. The two failed attempts are preserved, not rewritten; their recorded times are late but ordered, as disclosed in their ledger notes.
