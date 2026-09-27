# Sol review — Block 4 summary

## Exact version inspected

| File | SHA-256 |
| --- | --- |
| `execution/specs/04-summary.md` | `f5d6f8693c28271b45f95c8a5a81ffe6d0cb397459d943c0d07db63987014f17` |
| `execution/handoffs/04-summary.md` | `eb4330721f4b9b6cd713d15d84d51654a6dd9421c6368ee9e4f8603f6112396b` |
| `schrodinger/summarize.py` | `86e402eba56634f4a4814e305f8de7b565a8548570e5e4f4928a6dd3311158c1` |
| `execution/results/summary.json` | `8a14fd884a66925aaa920860dfc1a94859e7598818c59b22bb4af87636f11e64` |
| `execution/results/summary.csv` | `c90afc35c3e1b190c5a5124da7575887444beb94623f5193296cfe4904983ad8` |
| `execution/results/summary.md` | `5d5d841a03276d30475e3c0dacfea45622e5330d928d3e016c8b021928435c62` |
| `execution/results/learning_curves.png` | `ddc223def4a935bcc566fca4837a152eac2fe9693e55c755252b1e203882feb2` |
| `execution/final_report.md` | `5ce1b8928e0213abd739f66d5dd9128c7a15205f8c8074fdb1461da85b07e7a0` |

## Verdict

**CHANGES REQUIRED**

The calculations and final interpretation are factually correct. Two
machine-readable traceability fields required by the summary specification are
missing and need a bounded aggregation-only correction. No raw artifact,
training output, gate, or final interpretation should change.

## Required findings

### 1. Run-wide normal numerical maxima are not aggregated

Location: `schrodinger/summarize.py`, construction of
`scalars_invariants_rss`.

The summary copies only `final["invariants"]` for each run. It does not combine
normal validation checkpoint diagnostics from `training.jsonl` with normal
final-condition diagnostics. The final report's stated overall maximum is
correct, but it cannot be reproduced from the machine-readable aggregate.

Required correction: compute per-run normal maxima across all preserved
validation records and all final normal conditions, then emit per-run and
overall maxima. Keep `dt=0` diagnostics separate. The independently recomputed
overall values that the regenerated summary must reproduce are Hermiticity
`0`, unitarity `1.1920928955078125e-06`, and Born row error
`1.1920928955078125e-06`.

### 2. Embedded equal-time/provenance inputs are not hashed

Location: `schrodinger/summarize.py`, `input_hashes` and `invalid_equal_time`.

The summary embeds all three raw equal-time artifacts and hard-codes attempt
provenance, but hashes only final JSON and training JSONL inputs. A later change
to the embedded equal-time/provenance sources would not be detectable from the
recorded input identity.

Required correction: add hashes for all three equal-time JSON files and the
Block 3 provenance/audit inputs used to assign invalidity and attempt counts.
Also record the summarizer/config/contract identity in the output or linked
manifest. Regenerate all outputs and update the handoff hashes.

## Independent checks performed

- Recomputed selected raw means, ddof-1 sample SDs and paired differences for
  validation XOR, primary/secondary XOR, and the two COPY veto endpoints; all
  match `summary.json` and `final_report.md`.
- Recomputed the equally weighted five-condition combined CE mean and seed SD
  for each architecture; both aggregates match exactly.
- Recomputed all input hashes currently present; all match their raw files.
- Recomputed target censoring: only seed 33 reaches 90%/95%, at the examples
  stated in the report, so neither sample gate is eligible.
- Recomputed primary and secondary `dt=0` drops and confirmed neither is
  meaningful under the frozen rule.
- Recomputed the run-wide normal invariant maxima quoted above.
- Independently summed the current ledger to `392.9506345819944` seconds,
  comfortably inside the cap.
- Visually inspected `learning_curves.png`: it uses only the valid examples
  axis, shows all six unsmoothed seed curves, labels XOR accuracy and validation
  CE clearly, and makes no timing claim.
- Checked the final report's parameter counts, effective-dt range, RSS caveat,
  provenance counts, invalid timing status, endpoint values and
  `INCONCLUSIVE`/do-not-scale conclusion against raw evidence; no factual
  correction is required.

## Checks not yet verifiable

- Regenerated hashes and explicit run-wide maxima require the two corrections
  above.

Charge **0.6 seconds conservatively** for this review, including the final
review hash command.

---

# Sol final re-review — Block 4 traceability correction

## Exact version inspected

| File | SHA-256 |
| --- | --- |
| `schrodinger/summarize.py` | `95e60ac112f56b8cff1cc066849d0adcd31d1fcc556b9eecfc8396df35a7c47c` |
| `execution/results/summary.json` | `ba29759235f74162fdea1294ac39eb1bc5bb739418d6261683bf83aff359f52c` |
| `execution/results/summary.csv` | `c90afc35c3e1b190c5a5124da7575887444beb94623f5193296cfe4904983ad8` |
| `execution/results/summary.md` | `5d5d841a03276d30475e3c0dacfea45622e5330d928d3e016c8b021928435c62` |
| `execution/results/learning_curves.png` | `ddc223def4a935bcc566fca4837a152eac2fe9693e55c755252b1e203882feb2` |
| `execution/handoffs/04-summary.md` | `4780027016af9b92e0100ebcd9e3b234a671f8a500aadb84f5b0600bed6900b9` |
| `execution/final_report.md` | `5ce1b8928e0213abd739f66d5dd9128c7a15205f8c8074fdb1461da85b07e7a0` |

## Verdict

**PASS**

This verdict supersedes the prior traceability-only `CHANGES REQUIRED` verdict.
Both required fields are present and correct. All previously verified
statistics, figure provenance, invalid-timing status, and final-report
conclusions remain unchanged.

## Resolution and independent checks

- The summary now emits per-run normal invariant maxima using preserved
  validation checkpoints plus normal final-condition maxima. Independent
  recomputation matches every run. Exact-attention overall maxima are
  Hermiticity `0`, unitarity `1.1920928955078125e-06`, and Born row error
  `1.1920928955078125e-06`.
- `input_hashes` now contains 20 verified inputs: six final JSONs, six training
  JSONLs, all three equal-time JSONs, Block 3 provenance and review, config,
  frozen contract, and the summarizer itself. Independently recomputed SHA-256
  values match all 20 entries.
- Output hashes match the regenerated handoff. CSV, short Markdown summary,
  and PNG are byte-identical because the traceability correction changes only
  machine-readable aggregation fields.
- The final report remains factually consistent and requires no edit.

## Required findings

None.

## Non-blocking observation

- The handoff preserves the superseded hashes in one prose line followed by a
  clearly labelled current replacement line. The current target is
  unambiguous, though future handoffs would be cleaner with a single versioned
  hash table.

Charge **0.4 seconds conservatively** for the final re-review, including final
review hashing.
