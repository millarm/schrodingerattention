# Checkpoint diagnostic implementation handoff

Status: ready for Sol implementation review. No retained-checkpoint diagnostic
analysis command has been run, and no original source, checkpoint, evaluation
array, or prior report was modified.

## Current implementation manifest

| SHA-256 | Path |
|---|---|
| `851f8cfa177016c2a02eba5177991f33afde59b533e76199a7395c465dfd4160` | `schrodinger/checkpoint_diagnostic.py` |
| `2c9e36f7a2f65337a1d5d6f4c9de9905026d8cd026d28141412d214d6873c45c` | `tests/test_checkpoint_diagnostic.py` |
| `b160517e6a6c8d707fe50d392b3953dac447b99d74eeda2893a53c15dfd66b16` | `checkpoint_diagnostic_plan.md` |
| `c79527ee2ae8173a867e5d79fb27af44faee55d7cad5d2eb7e7da615a3a4b415` | `execution/diagnostics/status.md` |
| `9ebace507a57202f483cefd55d5f50db868ad2abd214145a86f722386b2ffd4f` | `execution/config.json` |
| `805b8c51fd21468ccb2f5c70bc122b52bf13f601331937e9979efcc5c5184995` | `execution/runtime.json` |
| `5ea6cda81fa8f95f3e2a9c39e9ca47d34ca6134697bca3305967e6f31d8507de` | `execution/experiment_contract.md` |
| `c3f08f029284da84c6bbdfc1f2324707479db4f649f3c71ef1311391944fa346` | `execution/diagnostics/ledger.jsonl` |

## Checklist coverage

- `trace_model` reconstructs normal and all-layer `dt=0` paths using actual
  normalized states, Q/K/V, gamma, and dt. It records fixed-normal-input local
  evolved-vs-softmax attention/value/projection measurements separately from
  propagated full-path attention, hidden, and layer-2 normalized-input changes.
- `trace_batch` writes row-level seed/condition/op/label/layer/head/query data,
  including TV/key maximum, Y and projected RMS/reference/relative values,
  propagated metrics, `dt*H` operator norm, eigenphase RMS, circular phase
  dispersion, learned effective dt/gamma; it writes per-example normal/dt0
  logits/probabilities/CE/predictions/correctness/disagreement/loss benefit.
- The all-seed CLI loads only retained step-2000 checkpoints and each stored
  `evaluation.npz`; verifies all 512/1024 stored counts plus normal and dt0
  retained CE/correct/counts; emits compressed row/example NPZs, stratified JSON
  and CSV summaries, numerical checks, runtime/input manifests, and a faceted
  seed-condition XOR/COPY figure.
- The attempt context rejects existing outputs, uses atomic `O_EXCL` locking,
  cleans up acquired locks even after mkdir or attempt-log failure, writes
  success/failure attempt records and ledger entries, has prior-ledger-aware
  900-second/30-second reserve guards before every batch, and never represents a
  manifest-only path as success.

## Executed bounded verification

1. `.venv/bin/python -m pytest tests/test_checkpoint_diagnostic.py -q`
   — exit 0, **10 passed in 0.76s** (latest targeted run before final suite).
2. `.venv/bin/python -m pytest -q` — exit 0, **58 passed in 1.57s**.
3. `.venv/bin/python -m compileall -q schrodinger/checkpoint_diagnostic.py`
   — exit 0.
4. `.venv/bin/python -m schrodinger.checkpoint_diagnostic --help` — exit 0.

Targeted tests cover hand-calculated TV/quantiles/RMS, exact direct-dt0
softmax equality, changed-time detection, manual normal/dt0 API reproduction,
fixed-input versus propagated layer-2 distinction, row/data/count behavior,
selected retained checkpoint API reproduction, lock contention with a different
output directory, no-overwrite, mkdir/log failure cleanup, failed-attempt
persistence, and prior-charge reserve enforcement. Tests use temporary ledgers
and outputs; retained artifacts are read only.

## Diagnostic compute ledger

`execution/diagnostics/ledger.jsonl` records Sol plan review 0.2s and a
conservative Terra bounded-test allowance of 10.0s: **10.2s charged**. No
full diagnostic attempt or training was launched.
