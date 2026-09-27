# Checkpoint diagnostic results audit

## Verdict: PASS WITH EXECUTION LIMITATIONS

The single immutable diagnostic result is internally complete and reproducible from its raw arrays. It answers the frozen question with a **mixed, substantially changed-attention regime**, not a uniformly near-softmax regime: only 70/240 direct cells meet the frozen local-small band. Downstream effects are smaller in many cells but not uniformly small (17/30 overall; 13/24 test cells), include rare very large probability changes, and show no consistent useful benefit under the frozen rule. All eight test condition/operation benefit flags are false. Therefore the defensible conclusion is “attention often changes substantially, downstream response is mixed and sometimes cancellation/insensitivity occurs, but no consistent downstream benefit is observed,” not blanket downstream insensitivity.

## Exact immutable result reviewed

Directory: `execution/diagnostics/attempts/checkpoint-001`

- `attempt.json`: `79dbf48fd17f65bd78ecb04b528bc33d449dfb0a555961e46194b8a4b9a54482`
- `input_manifest.json`: `ed678bb78eff3ed8d0fb2ec423ed1b1c0b57ac08e6bef7ecb5c9020eb10d8b20`
- `runtime.json`: `8b9ba74643de22c383f7c3e6f0af6a9995254a23f229c5e41302177806e833ea`
- `rows.npz`: `7e5dc48f2663e08110517e82dc14887079b47bbe30bf189556bcf146eac1c9c9`
- `examples.npz`: `4c76334579532bbfbb5629d1cb3282870b09eda5419b78eb05d752fcb602ea5e`
- `summary.json`: `2e81d2037604287dfe3a041f42ba2aa31e9ca410ec91d23c1b36a8fe10ebd9b5`
- `summary.csv`: `3568b1315531634cca1e6a2a2b0fea65c8eadb788b92190c6fbfc1947224b632`
- `local_vs_downstream.png`: `e857568b047fd5005fa344fd7d9d87da62189918e64d8bf35abb521be838abd7`
- Run handoff: `execution/diagnostics/handoffs/05-run.md`, SHA-256 `0fcc01d8487aaab8a8f90f79afb7472459b873478dcf57131929c92370dac386` (its immutable-output hashes match the files above)
- Astra final report: `execution/diagnostics/final_report.md`, SHA-256 `00c3d01ac48a99f9a6c8f40f49f6cc5502d1739f25b2653ba16068a763886b25`
- Diagnostic ledger at audit start: SHA-256 `e6eaa6efb0b9379758ef32d51f0364a56fda97c853d5d0e5e03642b3c69fe1c0`
- Diagnostic ledger after the preserved chronology clarification and conservative Terra/Astra allowances: SHA-256 `4cd5d103d19ff77fcf0b6817ddc5697533978ba36181b1d4476a8304eace212f`

## Independent reconstruction

- Loaded all 1,059,840 raw row records and 13,824 raw per-example records. All numeric fields are finite. Raw direct TV lies in `[0, 0.2860615849]`; propagated TV lies in `[0, 0.4583503902]`.
- Confirmed complete coverage of seeds 11/22/33, five conditions, XOR/COPY, two layers, two attention heads plus projection rows, and the expected 240 direct, 120 post-projection, and 30 downstream cells.
- Recomputed every direct cell, post-projection cell, downstream cell, and frozen flag using the accepted summary functions. All four reconstructed structures compare exactly equal to `summary.json`.
- Rehashed all 33 input-manifest paths against the current frozen files: zero mismatches.
- Confirmed all 15 numerical records pass; reported maximum attention-row and unitarity errors are each `1.1920928955078125e-6`.
- Inspected the PNG. Its 3x5 seed/condition facets, XOR/COPY colors, and axes match the raw provenance. It is readable and honest, though rare probability-change tails near one compress most points near zero; quantitative tails must accompany it.
- Audited Astra's final report against the reconstructed summaries and targeted raw examples. Its tables, percentages, tails, operator/phase values, cancellation counts, limitations, and mixed-effect/no-consistent-benefit conclusion are factual. It appropriately retains the original `INCONCLUSIVE` scaling result and makes no timing-efficiency claim.

## Headline result checks

- Direct local effect is clearly nonuniform: 70/240 cells are locally small and 170/240 are not. By seed, locally-small counts are seed 11: 5/80; seed 22: 25/80; seed 33: 40/80. The largest cell mean is `0.1555063` (seed 22, heldout d4 XOR, layer 1/head 1 in one-based language, CLS), with p95 `0.1851525`.
- Test downstream-small counts are seed 11: 3/8, seed 22: 2/8, seed 33: 8/8. Across seed/condition pools, mean absolute probability change reaches `0.0210300` for seed 22 seen d8; per operation it reaches `0.0256697`. Rare COPY changes are much larger, including `0.9942727` for seed 11 heldout d8 and `0.9911900` for seed 22 heldout d8.
- The primary heldout-d4 XOR cancellation check is exact. Seed 11 has 30/512 disagreements but unchanged accuracy: 15 normal-correct/dt0-wrong and 15 in the opposite direction. Seed 22 has seven disagreements, three gains and four losses, for a normal-minus-dt0 accuracy delta of `-1/512`. Seed 33 has no disagreements. Thus an accuracy-null alone would conceal material behavior changes in seed 11.
- No test condition/operation crosses the frozen benefit rule. The largest equal-seed mean benefit is `0.0075481` nats (seen d8 COPY), below `0.01`; heldout d4 COPY is `0.0055018`. Signs vary across seeds.

## Execution and provenance limitations

- The original launch tool's return metadata was discarded at its 30-second yield, so its tool-level `exit_code` was **not observed**. This audit does not claim exit zero. Completion rests on immutable `attempt.json` (`status: success`, `error: null`, PID 59118), absent diagnostic lock, and the later `ps` result showing that PID absent. No relaunch is permitted or needed.
- The persistent ledger's physical order places the post-run OS-audit entry before the run-attempt entry. Terra confirmed this was an `apply_patch` insertion-context mistake made after the run, not execution order or a missing entry. The entries' numeric sum remains valid, but physical file order is not chronological provenance and must not be presented as such. This does not alter raw scientific outputs or hashes.
- Original Block 3 timing/equal-time evidence remains invalid as previously recorded; this checkpoint-only diagnostic supports no efficiency claim.

## Budget and actions

- The ledger summed to `63.02535483300308` seconds at audit start: 23.7 seconds pre-run, 38.325354833003075 seconds for the run including startup allowance, and 1.0 second charged OS audit.
- The subsequently finalized ledger adds a zero-charge chronology clarification, a conservative 10-second Terra OS/provenance allowance, and a 2-second Astra report/figure allowance, for `75.02535483300308` seconds before this final Sol audit charge.
- Conservatively charge **6.2 seconds** for this independent raw reconstruction, hashing, report check, and visual audit, yielding final diagnostic usage of **`81.22535483300308` seconds**. This remains well below 900 seconds.
- No model execution, training, sweep, output edit, or diagnostic relaunch was performed.
