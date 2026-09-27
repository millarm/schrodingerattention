# Block 2 — deterministic data, classifiers, measurement harness

Prerequisites: frozen contract and Block1 Astra acceptance. Read those records.
Objective: implement all data/model/run measurement contract requirements.

Allowed implementation paths: `schrodinger/data.py`, `schrodinger/model.py`,
`schrodinger/experiment.py`, `tests/test_data.py`, `tests/test_experiment.py`,
`README.md`, `execution/config.json`, `execution/compute_ledger.jsonl`,
`execution/logs/02-*`, `execution/results/smoke/`,
`execution/handoffs/02-harness.md`. Block1 code changes require explicit finding
and re-review; originals cannot change. No measured paired comparison yet.

Use frozen contract exactly. PRNG is numpy.random.Generator(PCG64), with
installed NumPy version recorded. Training batch RNG uses SeedSequence
([100000+seed, update_index]); all sampling uses that local generator. Build
deterministic eval data once, store token
and label arrays with op metadata and condition names plus hashes. Generation
must independently validate pair exclusion, labels, unique facts, label/op
balance, fact count/length, individual key coverage, no split duplicates or
overlap, and both reversed pair orders excluded. Training stream derives from
seed/update, not global model RNG, paired batches verified byte-identical.

Model initialization creates a baseline once per seed and copies all matching
named tensors into SA. Test corresponding parameters byte-identical, logits
equal with dt=0 (atol2e-6 rtol2e-5), positional handling length15, and document
SA-only parameter count. Classifier is exactly specified in contract.

Provide CLI subcommands for smoke, profile, train, evaluate. Config loading
must preserve all frozen settings and record effective configuration/version.
Profile performs only declared steps and throughput calculations, no comparative
quality-driven choices. Train saves step0/every100/final checkpoint including
model state, optimizer state, seed, step, timings/config hashes. Evaluation
supports literal dt=0. Raw per-update JSONL contains step/examples, train loss,
training seconds/cumulative seconds; validation points add loss and per-op
accuracy, dt/gamma, invariant max errors and RSS. Use atomic checkpoint writing
if feasible. Final evaluations separate from validation. Tests never inspect
full-run comparative outcomes.

Track peak process RSS with macOS ru_maxrss bytes, explicitly not tensor-only
or isolated model peak. Record training/eval/checkpoint/end-to-end times;
training timing excludes eval and checkpoint I/O. Compute ledger append entries
for numerical tests, profile, smoke, training/evaluation including failures,
and cumulative seconds; guard cap before each long command/step. Check remaining
budget across processes, not an independently reset per-run timer. Account for
Block0 probe and Block1 tests. Hard stop at13800 charged seconds.

Acceptance checks: pytest invariants above; deterministic repeated generator;
paired stream byte identity; classifier dt=0 identity; short fixed-batch smoke
loss decreases for both architectures; short normal training stream run exercises
validation, checkpoint save/load, final per-condition metrics and dt=0. Reload
logits atol1e-6; metrics recomputed from stored counts, all finite. Smoke uses
small eval count override explicitly marked SMOKE, never a measured artifact;
full config remains untouched. Unit tests may use small data counts.

Permitted compute: <=300 seconds smoke/tests, plus <=180 seconds profiling,
CPU threads2/inter-op1 one training process. Logs and failures preserved. Handoff
SHA256 hashes all code/tests/config, commands exit codes and evidence. Freeze
on handoff; Sol must PASS current version and Astra accept smoke evidence.
