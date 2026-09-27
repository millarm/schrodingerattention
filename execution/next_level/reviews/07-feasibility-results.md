# Stage 0 feasibility-results audit

## Verdict: PASS — FEASIBILITY_FAILED_NOVELTY

The single authorized Stage 0 invocation completed successfully as a process and produced a valid scientific stop. The frozen benchmark has only 6/512 IL problems with at least four structurally novel shortest routes, spread across 3/32 IL maps, versus required minima of 256 problems and 16 maps. The plan therefore stops before model construction or training.

This result establishes that the **frozen selected construction under the predeclared strict novelty definition** lacks sufficient primary-stratum support. It is not evidence for or against Schrödinger attention, usable learning, productive diversity in another domain, or creativity.

## Exact immutable evidence reviewed

Directory: `execution/next_level/attempts/feasibility-001`

- `attempt.json`: `a221add32428be9f74921b2f5f432c64fcbff08d2b1060339ce2fa4a7d7171a3`
- `inventory.json`: `df7ff28b308c3bbba16f57d59e53a4e729d9d1e8be9adf5ae2a4d6773f9e0ab4`
- `manifest.json`: `fb30ad5570ce595cd536e9a750a03f436ab2a1a8d06804e49da95b41d910597e`
- `novelty.json`: `e907bafab1fdf0f0f52d8dc36fd4d8317649e292331526da8f651cb7e7257678`
- `selection.json`: `e8cad99f923a935f41df222872ad99e9907c8dd8b8db3fdac4e56822fcb81d8f`
- `splits.json`: `5eed3f6addb193d3ca934e9e0c2f0ad656c13523f9bfd3c38ab9b359ae9774cb`
- `summary.json`: `beef914fe8512dc939850ff62d1b87e973035dd247144664cfe6c5f9caa67f08`
- `support.bin`: `8e800a7f457e6e2ff6ea3bb9e67a03b504c56f17e2d7a2163421cab441aaa9ee`
- `training_states.json`: `451f76bb3b1cf42dc84db622e25787324303c7abc77ede673a2169195158355`
- Run handoff: `execution/next_level/handoffs/09-feasibility-001.md`, SHA-256 `71c9e826be6ac5d2363867ba646019b8d07234fc2baf56c1d2b395a09ed633cb`
- Astra draft final report: `execution/next_level/final_report.md`, SHA-256 `4944aa1a43836bff1840d5b885fd1e7fed32c797572802dda2e41171b070a9b1`
- Ledger at audit start: `execution/next_level/ledger.jsonl`, SHA-256 `ff35171c4239b0eb48cd6f068e50e280a388b2532d3011b314e64f742744081e`

The attempt's manifest digest and noncircular output-hash table match the files exactly. All manifest input hashes also match the accepted source, tests, plan, specifications, and reviews.

## Independent reconstruction

- Inventory: 794 canonical eligible maps — 86 II, 378 LL, and 330 IL. Every map has at least 16 candidate start/goal pairs.
- Replayed the frozen PCG64 map permutations from the stored inventory and prior-split exclusions. Selected IDs match exactly: training 32 II + 32 LL, validation 4 + 4, ID 8 + 8, and IL 32. All 120 selected canonical maps are disjoint.
- Recomputed candidates for selected maps only and replayed the continuously consumed family problem RNGs. The complete 1,024-problem training selected set and the ordered validation/ID/IL selections match the persisted records.
- Training bin boundaries are distance `6.0` and `log2(M)=2.584962500721156`. The four training counts are 393, 184, 160, and 287. Hamilton targets and persisted flow totals agree exactly: validation 49/23/20/36, ID 98/46/40/72, and IL 197/92/80/143. Every selected evaluation map contributes exactly 16 problems.
- All 10,314 training `(map,current,goal)` records are unique. Recomputed BFS counts and every four-action `q`; all entries are finite, sum to one, and match exactly.
- Decoded `support.bin` into 598 unique length-prefixed signatures occupying 5,730 bytes. Its digest matches the summary. Regenerating the full suffix support from the 1,024 persisted training problems produced the same 598-signature binary set; an additional direct suffix-membership check found no missing signature.
- Verified every stored route, signature, `M`, and `M_novel` across 128 validation, 256 ID, and 512 IL problems. All routes are legal, goal-reaching, and exact shortest length; signature arrays equal fresh D4/reversal canonicalization; no count mismatch was found.

## Gate arithmetic and descriptive evidence

IL `M_novel` distribution:

| `M_novel` | Problems |
| ---: | ---: |
| 0 | 502 |
| 1 | 3 |
| 2 | 1 |
| 4 | 1 |
| 5 | 1 |
| 6 | 1 |
| 7 | 1 |
| 8 | 2 |

Thus 10/512 IL problems have any novel route, but only 6/512 have `M_novel >= 4`; those six occupy 3 maps. Across all 512 IL problems, 43 of 5,062 exact shortest routes have signatures absent from the complete training suffix support. The persisted `qualifying_il=6`, `qualifying_maps=3`, and `FEASIBILITY_FAILED_NOVELTY` are exact.

The ID split is similarly dominated by zero novelty (248/256), but it is descriptive only and does not alter the IL gate.

## Execution, ledger, and report audit

- The one command returned an explicit tool exit code 0 without yielding and was not relaunched. Attempt status is COMPLETE with `error: null`; elapsed time is `10.785864792000211` seconds and charged time is `12.785864792000211` seconds including startup.
- The shared ledger contains 15 entries totaling `47.89224179200537` seconds at audit start. Its two UUID-bearing attempt records have unique IDs and chronological start timestamps; the final cumulative value matches the arithmetic.
- Astra's draft report is factual: inventory/support/state counts, novelty distribution, route totals, stop decision, execution history, and limitations agree with the immutable evidence. It clearly states that no architecture or learning claim is supported and that changing the task or novelty definition would require a new plan.

## Audit charge and limitations

- Conservatively charge **5.0 seconds** for this model-free audit, including full hash validation, selected-map candidate/RNG replay, complete training-support regeneration, all-state `q` validation, and all evaluation-route/signature checks. The ledger should advance from `47.89224179200537` to **`52.89224179200537` seconds** before Astra's separately charged report closeout.
- The audit did not regenerate the complete 794-map inventory from geometry; it verified every persisted canonical identity/hash, replayed the inventory-based frozen selection, and independently recomputed candidates for all selected maps. This is sufficient to audit the gate without launching a second full inventory.
- No data selection was changed, no alternate map was tried, and no model, pilot, optimizer, training, temperature evaluation, or dt0 intervention was run.

