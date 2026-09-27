# Block 2 revision 1 — complete executable contract

Do not begin until Astra forwards Sol's consolidated Block2 review. This
specification supplements original02-harness.md without changing the contract.
Objective: replace incomplete scaffolding with a complete tested execution path
for Block3, which permits no implementation edits.

Allowed files are original Block2 paths plus `schrodinger/__main__.py` for CLI
entry, smoke/profile artifacts under uniquely versioned directories, and
revision handoff/logs. Preserve failed/superseded evidence and mark its status.
Do not change accepted attention math or frozen experiment data/parameters.

Required implementation behavior:

1. Full `train --mode softmax|schrodinger --seed ... --steps ... --output ...`
   and `evaluate --checkpoint ... --dt-zero ...` work; no placeholder branch.
   A paired-evaluation command/helper chooses common-time checkpoints from logs
   and evaluates them. All configuration values used by execution must match
   effective config. Defaults/seeds/dimensions/optimizer remain frozen.
2. Evaluation creation uses exact512 validation total and1024 per final test
   condition, balanced block64 algorithm and independent seed mapping. Deduplicate
   globally across eval splits, with rejections in same op/label cell. Store full
   data arrays and hashes BEFORE any training. Training's generator consumes
   the same local batch RNG after drawing d, and rejects all eval token sequences
   while preserving cell balance. Prove reversed heldout-pair exclusion and
   every key's eligible training-query coverage globally, not as an accidental
   mandatory property of each randomly sampled small batch.
3. Save/evaluate step0 and every100/final, no best selection. Checkpoint includes
   model mode, architecture/config/code hashes, corresponding-init hash and
   optimizer/step/timing. Write raw JSONL incrementally so failed runs retain
   progress. Record per-batch stream digest and final aggregate digest for pairing.
4. Training clock starts before data generation/tensor conversion and ends after
   optimizer; evaluation/checkpoint times separate. End-to-end timer includes
   initialization/data preparation/evaluation/I/O. Global ledger includes full
   command durations (conservative startup allowance acceptable), not only
   successful inner loops. Before each step/evaluation check prior charged total
   plus elapsed current command, abort at13800 and record failure/elapsed in
   finally. Log nonfinite loss/output/gradients/parameters failures; numerical
   diagnostics at validation check H<=1e-6, U/row<=2e-3 with unrenormalized values.
5. Final artifacts include final all-condition metrics from integer counts,
   SA dt0, val CE, dt/gamma, parameter counts, process peak RSS byte caveat,
   throughput/clock boundaries, config/runtime/code/eval hashes, checkpoint refs.
   Final tests only after run finishes and never influence training. Equal-time
   evaluation uses latest checkpoint at/below pair T and reports slack and steps.
   First-target checkpoint intervention can be invoked if sample gate qualifies.
6. Smoke uses the SAME end-to-end train/eval/checkpoint paths for each mode with
   explicitly tiny SMOKE settings in a separate directory. Fixed-batch loss
   reduction smoke actually optimizes a fixed batch or is labelled accurately;
   also execute a short normal stream train. Assert reload equality and dt0 path.
7. Add meaningful acceptance tests for full counts/block64 balance, blacklist
   rejection deliberately exercised, all seed pairing and heldout reversal,
   step0/final artifacts, each CLI mode, evaluator/intervention, finite/budget
   failure recording and integer metric correctness. The previous27 tests alone
   do not establish harness correctness.
8. Correct sinusoidal positions to positions*exp(-index*log(10000)/32), not
   division by that decreasing factor; test reference values at lengths11/15.
   Address all eight required groups in execution/reviews/02-harness.md.

Run throughput-only profile again after generation/timing corrections; old
profile cannot choose N because its timing excluded generation. No comparative
quality tuning. At most600 additional elapsed seconds for revision tests/smoke/
profile and retain full compute ledger, initial14.506s prior history, plus
SolBlock2 review1.9s and conservative startup allowance for prior smoke/profile.
Represent the14.506s initial charge explicitly once rather than hidden base.
Handoff
full SHA256 manifest for code/config/tests/data and commands/results; enumerate
each resolved Sol finding and any deviation. Freeze after handoff for re-review.
