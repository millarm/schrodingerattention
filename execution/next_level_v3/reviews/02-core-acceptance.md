# Productive-diversity v3 Block 1 correction review

## Verdict: CHANGES REQUIRED

The four findings from review 01 are correctly closed. One bounded resource/provenance defect introduced by the correction remains: `PoolResult.draw_prefix` retains every component-index draw, potentially through the 200,000-trial production ceiling. Fix only this issue, preserving all RNG consumption and scientific outcomes.

## Exact versions reviewed

- Correction handoff: `execution/next_level_v3/handoffs/01-core-corrections.md`, SHA-256 `0d7a0cf19e654b33878d432c1f899a10998d0bf0286ca9850ce006b09cae4b86`
- Pure module: `schrodinger/productive_diversity_v3_data.py`, SHA-256 `047c45b104c2ca92c2451e518102211760374c397f7efe950e9e107a4cd8882f`
- Focused tests: `tests/test_productive_diversity_v3_data.py`, SHA-256 `39d4d0347dd1dbab7887a25f5436c5316c02e2d9528271fac4e9a3b17540be3e`
- Prior review: `execution/next_level_v3/reviews/01-core.md`, SHA-256 `eac7486ce1d5be1e99a8636d03c98a8157c39cc4f5b99a20db8eedd6d101b49c`
- Ledger inspected: `execution/next_level_v3/ledger.jsonl`, SHA-256 `59bcc20d032ff1655eb84adfc4418c3ebc21aeca3ef7076932aa419baee4c19c`

## Required correction

`pool_family` appends every eight-index trial tuple to `draws` and returns the complete tuple as `draw_prefix`. At the frozen maximum this retains 1.6 million Python integer entries per family and may later inflate immutable artifacts, even though the contract requires exact seed, trial count, rejection counts, and maps—not a full random-draw transcript. Bound `draw_prefix` to the first **16** trials (at most 128 indices/family). Continue consuming the same RNG stream and processing every trial exactly as before; the cap must not change maps, counters, stopping, or replay. Add a fixture with more than 16 injected trials that asserts the prefix length/content is capped while total trials and rejection counters still cover every supplied/processed trial.

## Prior findings now accepted

1. **Global identity boundary — PASS.** `assemble_global_inventory` requires all three pools, detects cross-family canonical collisions technically, globally sorts canonical bytes, assigns zero-based IDs, reconstructs and validates n=12 walls/families, invokes the candidate oracle with explicit n, and binds shortlists to global map IDs. The real valid-map fixture verifies order, IDs, dimension propagation, and collision rejection.
2. **Pool branch and stream evidence — PASS apart from prefix retention.** Independent `PCG64(SeedSequence([93000,0]))` output matches the implementation. Deterministic injected rows exercise overlap, orthogonal touching without overlap, retained identity, and D4 duplicate with exact counters and order. Geometry validation remains covered by the real assembler fixture.
3. **Inventory/shortlist evidence — PASS.** The n=12 empty-board fixture independently identifies `(98,143,12,C(12,3)=220)`, verifies bounds/sorting/uniqueness above cell 63, and the shortlist fixture exactly matches `PCG64(SeedSequence([93001,17,12]))` permutation and retained order.
4. **Ranking precedence — PASS.** The fixture proves higher exact normalized supply outranks lower cost, equal supply selects lower exact rational mean M, equal score/cost selects lower window start, intra-window ties select canonical quota order, and only three distinct windows remain. Ranking still performs no route enumeration.

## Independent checks and charge

I recomputed all hashes and performed a complete static trace of the corrected source/tests. I did not rerun tests because the remaining unbounded append is directly visible. Independent charged compute: **0 seconds**. Terra's preserved two failed iterations, final `7 passed`, and cumulative v3 development-test charge `3.073655250s` were inspected.

No production pool, support, novelty, dataset, runner, model, pilot, or training command was run. All remain **NOT_EVALUATED**.
