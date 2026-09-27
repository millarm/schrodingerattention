# Checkpoint diagnostic implementation review

## Verdict: CHANGES REQUIRED

The implementation has the correct central experimental separation: direct local attention is recomputed from each normal-path layer's fixed normalized hidden state, `S`, and `V`, while the propagated comparison independently runs the normal and `dt=0` full paths. The attention scaling, output projection, full-path logits, losses, and retained normal/`dt=0` endpoint reproduction are implemented coherently. It is not yet safe or complete enough for the authorized checkpoint analysis.

## Frozen artifacts reviewed

- Plan: `checkpoint_diagnostic_plan.md`, SHA-256 `b160517e6a6c8d707fe50d392b3953dac447b99d74eeda2893a53c15dfd66b16`
- Handoff: `execution/diagnostics/handoffs/01-implementation.md`, SHA-256 `099ae4edf51950ebc69db558467f847666f8813eba2c4b31f2f5186f8fbdee80`
- Implementation: `schrodinger/checkpoint_diagnostic.py`, SHA-256 `851f8cfa177016c2a02eba5177991f33afde59b533e76199a7395c465dfd4160`
- Tests: `tests/test_checkpoint_diagnostic.py`, SHA-256 `2c9e36f7a2f65337a1d5d6f4c9de9905026d8cd026d28141412d214d6873c45c`
- Diagnostic ledger: `execution/diagnostics/ledger.jsonl`, SHA-256 `c3f08f029284da84c6bbdfc1f2324707479db4f649f3c71ef1311391944fa346`
- Experiment runtime: `execution/runtime.json`, SHA-256 `805b8c51fd21468ccb2f5c70bc122b52bf13f601331937e9979efcc5c5184995`
- Experiment contract: `execution/experiment_contract.md`, SHA-256 `5ea6cda81fa8f95f3e2a9c39e9ca47d34ca6134697bca3305967e6f31d8507de`

## Required corrections

1. **Complete the frozen downstream measurements and classifications.** Per-example output lacks explicit disagreement and absolute loss change. Aggregates omit maximum probability change; p95/maximum absolute margin change; and mean/p95/maximum absolute loss change. The signed loss output is only a mean and sample SD, not the requested distribution. Emit the frozen local-small decisions and the seed/test-condition/operation benefit aggregation (`mean >= 0.01` and positive in at least two of three seeds), so the final answer does not require undocumented reconstruction. Preserve raw values from which every result is reproducible.

2. **Make numerical rejection strict at runtime.** The current finite check evaluates `a[~np.isnan(a)]`, so it deliberately removes NaNs before checking and therefore accepts them. Reject every non-finite metric value. Enforce, in the full run rather than only fixtures, TV in `[0, 1]` within the frozen tolerance, probability and attention row sums, and other declared numerical bounds. Add negative tests that inject NaN and out-of-range TV/row sums and prove a failed attempt is persisted.

3. **Verify immutable inputs, not merely hash them.** `_manifest()` records current hashes but the run does not establish that checkpoint metadata matches mode/seed/step 2000, frozen source/config hashes, and its retained final artifact; nor that loaded evaluation arrays reproduce the frozen evaluation-manifest/final digests, shapes, domains, operation balance, and labels. Perform these identity and content checks before analysis and fail loudly on any mismatch. Include all diagnostic implementation/test/specification artifacts needed to identify the reviewed implementation in the recorded manifest.

4. **Cover the whole command with the 900-second cap.** Guards currently occur before trace batches only. After the last guard, the program constructs and repeatedly reconverts very large Python lists during cell summaries, compresses outputs, summarizes, and plots. This can consume substantial CPU without a remaining-budget check. Precompute reusable arrays/masks, add reserve-aware guards before and within expensive aggregation/serialization/plotting, and persist a clear failed/partial attempt if the cap would be crossed. Test a cap failure in post-processing, not only during tracing.

5. **Correct attempt and runtime provenance.** The recorded command is reconstructed and omits the actual executable and a non-default `--lock`; the diagnostic `runtime.json` labels `experiment.config()` as runtime rather than preserving the actual runtime/version/hardware identity. Timing begins only after preflight/lock acquisition, while output-exists and lock-acquisition failures occur before the attempt record and are not logged. Record exact argv, lock path, runtime identity and relevant hashes; charge the entire attempt; and safely persist every success/failure without overwriting an existing output or racing the shared ledger. A failure to write the required attempt record must not leave the ledger claiming an unqualified success.

6. **Promote trace/data assumptions to runtime invariants.** Validate every evaluation array and metadata length/shape/count, operation and label domains, and per-condition balance. Assert normal and `dt=0` layer-1 normalized inputs agree and that traced API/manual-path identities meet tolerance on the actual analysis, with explicit diagnostics on failure. Add tests for mismatched checkpoint/evaluation identities and malformed inputs.

## Independent checks

- Read the full plan, handoff, implementation, and diagnostic tests and inspected the attention trace, projection, retained-metric, manifest, attempt, summary, plotting, and cap paths.
- Recomputed the intended direct-versus-propagated data flow from the source. Direct layer 2 correctly fixes the normal evolved layer-1 hidden state rather than the `dt=0` state; the propagated path correctly allows hidden states to diverge.
- Ran `.venv/bin/python -m pytest -q tests/test_checkpoint_diagnostic.py`: **10 passed in 0.77 s**, explicit process exit; observed whole-command wall time **1.12 s**.
- Conservatively charge **1.5 s** to this independent diagnostic-review activity, separate from the original experiment ledger. This covers command startup/exit and review hash checks.

## Not performed

- No checkpoint analysis, training, sweep, or output regeneration was run.
- The reported repository-wide 58-test result was not independently rerun; it does not exercise the missing runtime and provenance failure cases above.
- Performance under the full approximately million-row result volume was not benchmarked because the implementation gate fails before full-run authorization.

