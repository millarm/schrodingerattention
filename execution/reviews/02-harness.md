# Sol review — Block 2 data, classifiers, and harness

## Exact version inspected

No Git commit is available. Frozen implementation and primary handoff files:

| File | SHA-256 |
| --- | --- |
| `schrodinger/data.py` | `085c8480c49906e24beb74f0680b563c5d866c8f8782ae1dbca0ce4e6cf9dd9c` |
| `schrodinger/model.py` | `95a6e849e2ac7816ca92f2c6c4cf27024fa6ab35eaa14a14b5197cff3f77afad` |
| `schrodinger/experiment.py` | `0cb234170eee6bae25a6014a80dd3be99ad66bbf89539e1cf335e8edd8091059` |
| `schrodinger/__main__.py` | `f91c4ca53a88e177f0e28034eb6c73d1dfb73729b3605f9883b193e223e3732d` |
| `tests/test_data.py` | `a7ecf383afaaa935997fb1dc2dd8c4f78486d48a119f8149617943f722a0fc69` |
| `tests/test_experiment.py` | `24a85e573be35c95394abf041ce2292a15c45236a5462642b968fde3d39e967e` |
| `execution/config.json` | `9ebace507a57202f483cefd55d5f50db868ad2abd214145a86f722386b2ffd4f` |
| `execution/handoffs/02-harness.md` | `9c9d131bc1f8f75c2a4a5b18a45d5dc4356e978f85dacbfef233261e1a90afeb` |
| `execution/logs/02-harness.md` | `9ba0365c4be5faba6416fba291d3bf7e5c5687ce7ba20894070ee8322acd2d58` |
| `execution/compute_ledger.jsonl` | `9bb061ebd9dfecadfcd367be52114e73f97585f984629c059efcb6d1cdf52147` |

Governing specification: `execution/specs/02-harness.md`, SHA-256
`aa44ea9851324c1fce460f7d95fae35edb7a18c44d54f5a8810fd4994ed21266`.
Frozen contract inspected at SHA-256
`5ea6cda81fa8f95f3e2a9c39e9ca47d34ca6134697bca3305967e6f31d8507de`.

## Verdict

**CHANGES REQUIRED**

The attention integration and paired parameter copy are promising, but the
frozen implementation is not yet the measurement harness specified by Block
2. It cannot run a valid paired comparison, enforce the resource cap, or
produce several mandatory endpoints. No measured comparison should start from
this version.

## Required findings

### 1. Train/evaluate CLI workflow is incomplete and asymmetric

Location: `schrodinger/experiment.py`, `main()`.

`train` always selects `paired_models(seed)[0]`, so it can train only the
softmax model. The declared `evaluate` command always raises an exception.
There is no checkpoint-mode selection/loading interface, final fixed-condition
evaluation, literal-`dt=0` evaluation command, or equal-time checkpoint
evaluation. Block 3 therefore cannot execute six paired runs or required
interventions using the frozen CLI.

Required correction: provide explicit baseline/Schrödinger train selection,
checkpoint loading, final and intervention evaluation, and the checkpoint-at-
common-time workflow. Ensure every run records architecture, seed, effective
config and code/data hashes.

### 2. Required training lifecycle and invariant enforcement are absent

Location: `schrodinger/experiment.py`, `_train_steps()`; model integration in
`schrodinger/model.py`.

Training neither evaluates nor checkpoints step 0. It records only step 100
and final. It never obtains attention diagnostics, records maximum Hermiticity/
unitarity/Born errors, or aborts above the training tolerance. Consequently it
cannot satisfy checkpoint selection, equal-time censoring, or the mandatory
runtime numerical guard.

Required correction: add step-0 validation and checkpoint, step-100/final
records, propagate per-layer attention diagnostics through the classifier,
aggregate the required maxima, and reject nonfinite values or invariant errors
above `2e-3`. Reload tests must cover a real saved checkpoint including model,
optimizer, step, seed, mode, timings and config/code identifiers.

### 3. Timing and hard-cap accounting are invalid for measured training

Location: `schrodinger/experiment.py`, `_train_steps()`, `append_ledger()`, and
`main()`.

Batch generation occurs before the training timer despite the contract
explicitly including generation. The cap is checked only after smoke/profile
complete, never before each long command or training step. The `train` command
does not append any ledger entry at all. Evaluation, checkpoint and end-to-end
durations are not consolidated for train runs. A job can therefore exceed the
aggregate ceiling unnoticed and its measured training time is understated.

Required correction: include batch generation in per-update training time;
check the shared cumulative ledger before every run and update (with a
conservative projected-step guard); append success and failure charges; and
record training, evaluation, checkpoint and end-to-end time separately. Avoid
a hard-coded historical base that can drift from accepted ledger evidence, or
make that base an explicit immutable ledger entry.

### 4. Fixed evaluation data violate size and block-generation requirements

Location: `schrodinger/data.py`, `evaluation_sets()`.

One `count_per_operation` value is applied to every condition. At its default,
independent inspection found 256 XOR plus 256 COPY rows for *all* conditions:
validation is correct, but each final test condition is half the required 512
XOR plus 512 COPY. The function builds complete operation/label cells and then
performs one global permutation; it does not build and independently shuffle
balanced blocks of 64 as frozen in the contract. Only reduced `SMOKE` arrays
and hashes were saved, not the full pre-training evaluation artifact.

Required correction: generate validation at 256/op and every test condition at
512/op, in independently shuffled 64-row blocks with exact per-block
operation/label balance; enforce split-wide uniqueness/overlap rules; save the
full immutable arrays, metadata and hashes before any training; and make
training/evaluation consume those stored arrays rather than silently generate
different-size collections.

### 5. Training-stream generation omits blacklist rejection and misuses RNG

Location: `schrodinger/data.py`, `training_batch()` and `validate_batch()`.

Training batches are never checked against the frozen validation/final token-
sequence blacklist, permitting exact evaluation examples into training.
`training_batch()` draws distractor count from one generator and then resets a
new generator to the identical SeedSequence inside `make_batch`; this reuses
the same initial random bits instead of continuing the single frozen batch RNG
and creates an avoidable correlation with the first sampled pair. Finally,
`validate_batch()` demands all 12 keys occur in every seen batch—even tiny
test batches—whereas the contract requires individual-key coverage over the
training domain/run. This can create seed-dependent batch failures unrelated
to data validity.

Required correction: use one continuing PCG64 generator per seed/update for
the distractor draw and all row sampling; reject/retry rows in the complete
evaluation blacklist deterministically; test byte-identical paired batches;
and move individual-key coverage to a domain/run-level assertion while keeping
per-example structural checks in `validate_batch()`.

### 6. Mandatory metrics and artifacts are missing

Location: `schrodinger/experiment.py` and emitted smoke/train records.

Measured training has no final per-condition JSON, equal-time result, `dt=0`
result, invariant maxima, parameter-count record, code/runtime/data identity,
failure artifact, or complete training/evaluation/checkpoint/end-to-end timing.
There is no CLI path demonstrating that metrics are recomputed from stored
correct/count denominators after checkpoint load. These omissions prevent the
Block 3 audit and later summary from being reproducible.

Required correction: implement and test the exact per-update JSONL,
checkpoint, final-evaluation and intervention schemas required by the contract
and Block 2 spec, including operation counts, learned scalars, RSS
qualification, identities/hashes, and failure preservation.

### 7. Smoke and tests do not establish the advertised acceptance behavior

Location: `schrodinger/experiment.py`, `smoke()`; `tests/test_data.py` and
`tests/test_experiment.py`.

The “fixed-batch” smoke measures one fixed batch before and after four updates
on different streamed batches; it does not optimize the fixed batch as the
acceptance check requires. Its small loss decreases are therefore incidental
and are not an optimization test. Only four Block 2 tests exist, and they do
not exercise the CLI, step-0/final checkpoints, optimizer reload, full fixed
evaluation sizes/hashes, blacklist rejection, invariant logging/failure,
timing/ledger guard, final metrics, `dt=0` checkpoint evaluation, or count-based
metric recomputation.

Required correction: make a bounded fixed-batch optimization smoke for each
architecture and add targeted tests for every listed harness acceptance path.
Keep all smoke artifacts explicitly separate from measured outputs.

### 8. Positional frequencies are inverted relative to standard sinusoidal encoding

Location: `schrodinger/model.py`, `TinyClassifier.positional()`.

The code divides positions by `exp(index * -log(10000)/32)`, which multiplies
by increasing powers of 10000. Standard fixed sinusoidal encoding multiplies
positions by that decreasing exponential. This creates rapidly increasing,
aliased frequencies and is not the conventional fixed sinusoidal positional
representation selected to avoid the length-15 extrapolation confound.

Required correction: use `positions * exp(index * -log(10000)/d_model)` (or
equivalent division by a positive-exponent denominator) and add exact-value
tests at lengths 11 and 15.

## Independent checks performed

- Recomputed the frozen source, test, config, handoff, log and ledger hashes
  listed above; the six hashes claimed by Terra match.
- Read the data/model/experiment implementation and tests end to end and traced
  score/data axes, paired state copying, checkpoint contents, timing boundaries,
  CLI dispatch and emitted artifacts.
- Ran `.venv/bin/python -m pytest -q tests/test_data.py tests/test_experiment.py`:
  exit 0, four tests passed, pytest 0.68 seconds, full process wall 0.99 seconds.
- Independently instantiated default `evaluation_sets()`: every condition had
  512 total rows (256 per operation), confirming the final-test under-sizing.
- Recomputed a deterministic training batch and inspected positional values;
  the generator is repeatable, while the positional factors differ from the
  standard decreasing-frequency construction as described above.
- Confirmed corresponding classifier tensors are copied bitwise and the
  experimental model has exactly eight additional trainable scalars. The
  existing length-15 `dt=0` test passes, but its appended fact tokens are not a
  structurally valid long-condition example.

Sol's bounded executable review used 1.7 seconds tool wall time. Charge **1.8
seconds conservatively** to the shared compute ledger for this review before
the final review-file hash command.

## Checks not verifiable on this version

- A Schrödinger CLI training run, final checkpoint evaluation, equal-time
  selection, stored full evaluation identity, blacklist-clean training stream,
  invariant abort, aggregate cap enforcement and failure recovery do not exist
  and could not be tested.
- No measured run was started, as required.

## Non-blocking observations

- Global sequence-level deduplication across fixed conditions is stricter than
  cell-local deduplication and is scientifically acceptable once correct block
  sizes and construction are implemented.
- `resource.getrusage(...).ru_maxrss` is correctly labelled as macOS process
  RSS in source; it still needs to be emitted consistently in measured
  artifacts.

---

# Sol re-review — Block 2 revision 1

## Exact version inspected

No Git commit is available. Current frozen revision:

| File | SHA-256 |
| --- | --- |
| `execution/specs/02-harness-revision.md` | `c72ad679731f6df31135500d1355359380e469034b8044b3b7d92d8985d3b049` |
| `execution/handoffs/02-harness-revision1.md` | `d7a8ed4e76b95ca00c434bf4623334d79d693258a296f1252407b85f2db2bba7` |
| `schrodinger/data.py` | `3fab8bafdecd773df13d81c81653ece8760707b5f11f59cb2f5c56ab225278e3` |
| `schrodinger/model.py` | `b2892ee6dc8158b326b2fbb3ecc242e030edd94f36f5d407246a4666ac4dc36a` |
| `schrodinger/experiment.py` | `16a06102a3f9e563409d6cedb24e183498a3a0fd62cd1f04683bf6ce06b599a5` |
| `tests/test_data.py` | `8394b449d25c65105262324e2ff2a750123ab8b350f73375ab8787a9cb4d2c78` |
| `tests/test_experiment.py` | `43e5268f88b21dd3d89789d38f2a2188faaa8a8d5c27f332f77999893fcdb07f` |
| `execution/config.json` | `9ebace507a57202f483cefd55d5f50db868ad2abd214145a86f722386b2ffd4f` |
| `execution/compute_ledger.jsonl` | `aaf0bf80f27d545c11ac64fa31c97289c812d87107caa0d4dd6716408771dcae` |
| `execution/results/block2-final2/softmax/evaluation.npz` | `1a83c3ebcbcb45d12d490ffa2a7def5d29f86b21962930290fbf369eea9fcecc` |
| `execution/results/block2-final2/schrodinger/evaluation.npz` | `1a83c3ebcbcb45d12d490ffa2a7def5d29f86b21962930290fbf369eea9fcecc` |

Original Block 2 spec remains SHA-256
`aa44ea9851324c1fce460f7d95fae35edb7a18c44d54f5a8810fd4994ed21266`;
contract remains SHA-256
`5ea6cda81fa8f95f3e2a9c39e9ca47d34ca6134697bca3305967e6f31d8507de`.

## Verdict

**CHANGES REQUIRED**

Revision 1 resolves the data sizes/block construction, RNG continuation,
blacklist use, positional encoding, two-mode CLI, checkpoints, basic timing,
and fixed-batch smoke. Six bounded correctness/traceability issues remain
before this harness can produce reviewed measurements.

## Required findings

### R1. Final invariant evidence is taken from the intervention and is not a maximum

Location: `schrodinger/experiment.py`, `evaluate()` and the `train` final
artifact construction.

`evaluate()` overwrites each layer's `last_diagnostics` for every condition.
The final dictionary evaluates the normal model, then evaluates `dt=0`, then
calls `model.invariant_maxima()`. Thus the saved SA `invariants` describe only
the final condition of the `dt=0` intervention. The current final artifact's
unitarity error is consequently exactly zero. Neither per-condition nor
run-wide maxima are accumulated, so the mandatory maximum numerical errors
cannot be audited.

Required correction: have evaluation return normal-path diagnostics per
condition and aggregate maxima across layers, conditions and logged training
evaluations. Capture the normal result before running `dt=0`; report
intervention diagnostics separately if desired. Add a test that would fail if
the normal evidence were overwritten by intervention evaluation.

### R2. Required nonfinite enforcement is incomplete

Location: `schrodinger/experiment.py`, `_train_steps()` and `evaluate()`.

Training checks forward values, loss and gradients before the update, but never
checks parameters after `optimizer.step()`. Evaluation does not reject
nonfinite logits or cross-entropy. A corrupted update or invalid final metric
can therefore be checkpointed/reported as a run result.

Required correction: check all parameters after every update and all logits,
losses and emitted metrics during evaluation; fail with a preserved failure
artifact and whole-command ledger charge. Add focused injected-nonfinite tests
for the training and evaluation paths.

### R3. Initialization and pairing identities are not reliably persisted or enforced

Location: `model_identity()`, `_train_steps.save_point()`, and
`pair_evaluate()`.

Every checkpoint recomputes `model_identity()` from the current trained state
but labels that digest `shared_initial_tensor_digest`. Independent inspection
confirmed the step-102 checkpoint digests differ from the true initial digest
in both modes. `pair_evaluate()` verifies only evaluation-data equality; it
does not reject different seeds, same-mode inputs, differing initialization,
stream digests, config hashes or source hashes, and its output omits this
pairing evidence.

Required correction: compute the corresponding initialization digest once
before training and persist it unchanged in every checkpoint/final record.
Persist both initial identity and, if useful, separately named current-state
identity. Pair evaluation must validate and emit seed, opposite modes, initial
shared digest, aggregate stream digest, config/contract/source identities and
stored evaluation hashes before producing a comparable endpoint.

### R4. Cap protection and ledger history are not yet trustworthy

Location: `budget_guard()`, training/evaluation loops, and
`execution/compute_ledger.jsonl`.

The guard checks only already elapsed current-command time immediately before
an operation; it does not reserve a conservative projected next step or
evaluation duration as required by the revision specification. In addition,
historical ledger `cumulative_seconds` values are non-monotonic (a 21.25 entry
is followed by 18.39) because older entries were inserted/replayed. Although
summing `charged_seconds` currently works, the recorded cumulative field
cannot be used as evidence.

Required correction: reserve a fixed conservative next-operation allowance in
the guard (well within the contract's 600-second summary margin), add one
explicit conservative setup/test allowance as Astra directs, and make the
canonical ledger internally monotonic or explicitly supersede stale cumulative
fields with a reviewed recomputation. All measured commands must continue to
receive reliable finally-path whole-command charges.

### R5. Revision acceptance tests remain materially incomplete

Location: `tests/test_data.py` and `tests/test_experiment.py`.

The suite now has 33 tests overall, but only ten cover data/harness behavior.
There is no deliberate blacklist-rejection test, all-three-seed pairing test,
explicit reversed-heldout training exclusion test, two-mode train/evaluate CLI
test, initialization/stream mismatch rejection test, nonfinite failure test,
or failure-artifact/ledger-finally test. Integer metric recomputation is also
not asserted from a stored final artifact. These were explicit revision
acceptance criteria, not optional breadth.

Required correction: add bounded tests for those paths. Tests may use tiny
SMOKE datasets and injected failures; no measured comparison is needed.

### R6. The revision handoff is not a complete reproducible version manifest

Location: `execution/handoffs/02-harness-revision1.md`.

The handoff first cites stale intermediate code hashes, then current source and
test hashes, but omits hashes for config, revision spec/log, full evaluation
arrays/manifests, final/evaluator/pair artifacts and checkpoints. It claims a
“full SHA256 manifest” requirement was satisfied when no such manifest exists.
The named revision log is also not linked in the handoff.

Required correction: provide one unambiguous current-version manifest covering
all reviewed code, tests, config, spec, logs and current `block2-final*`
evidence; mark earlier hashes/artifacts superseded without presenting them as
the review target.

## Independently verified corrections and evidence

- Full evaluation arrays have the correct 512 validation rows and 1024 rows
  for each final condition. Every 64-row block has exactly 16 examples in each
  operation/label cell; all 4,608 token sequences are globally unique.
- Both modes store byte-identical evaluation NPZ files. Recomputed batch
  digests match both manifests.
- Replayed all 102 seed-11 training batches against the stored full blacklist:
  zero collisions. The aggregate digest
  `70c4e48f437f55dfac77b5e7edbcab03768880a167660dce26557832227359e9`
  matches both final artifacts.
- Step 0, 100 and 102 checkpoints and JSONL points exist for both modes.
- Stored final accuracies exactly equal integer correct/count ratios.
- The paired initial digest in both final records is identical and parameter
  counts are 18,498 baseline versus 18,506 SA.
- The corrected sinusoidal formula matches the standard decreasing-frequency
  construction.
- The equal-time artifact follows the checkpoint-discretized frozen rule and
  reports its large step-0 SA slack honestly.

## Independent commands and compute charge

- Full suite: **33 passed**, pytest 1.08 seconds, full process wall 1.46
  seconds.
- Artifact/data replay: exit 0, full process wall 0.76 seconds.
- One malformed audit command failed immediately with a Python syntax error;
  its 0.01 seconds is retained rather than hidden.
- Read/hash commands used approximately 0.7 seconds tool wall in aggregate.

Charge **3.0 seconds conservatively** to the shared compute ledger for Sol's
revision-1 review, plus 0.1 seconds for the final review hash command when
recorded.

## Checks not verifiable on this version

- Correct run-wide normal-path invariant maxima, post-step/evaluation
  nonfinite failure behavior, immutable initialization identity, robust pair
  rejection and projected cap protection require the corrections above.
- No measured comparison was started.

---

# Sol final evidence review — Block 2

## Exact version inspected

- Pair helper `schrodinger/experiment.py` SHA-256
  `cf75e1b35fe6fb1fb462d78d415ea60115dcd267957303ef56427861ae55c288`.
- Current `tests/test_experiment.py` SHA-256
  `71e54231de2e73102cab047d46af28be305cd5ddbe7f5be78298c77c7e44a0f8`.
- Final handoff `execution/handoffs/02-pair-validation.md` SHA-256
  `6bd09ad0ed03beb1abaf9e57932aeef560f24d379d644a70220623e9758056a5`.
- Complete inventory `execution/manifests/02-current.sha256` SHA-256
  `c7073a2a769e9dea8a8024bc0acc4c1044395e6558c93ad9f811cfa0945dcb27`.
- Compute ledger SHA-256
  `1e9d59fd457c60b75e9e94a1056e2f480d771cb2e23b9d67cbccf62fe6bc3370`.

## Verdict

**PASS**

All Block 2 required corrections and acceptance evidence are now satisfied.
The reviewed harness is ready for the frozen measured comparison; no measured
comparison was run during review.

## Final evidence checks

- Each parameterized identity-mismatch test first constructs and successfully
  evaluates a valid nonempty completed pair, then changes exactly one field and
  asserts the specific seed/config/source/initial-identity/mode error. These
  tests now reach the intended branches.
- The unequal-final-step regression uses internally consistent raw and
  checkpoint stream digests at steps 1 and 2, then asserts the exact
  `paired completed final steps differ` rejection.
- The separate stream-mismatch regression uses equal final steps and valid
  per-run raw/checkpoint digests, then verifies cross-pair digest rejection.
- Focused independent rerun of these cases: **7 passed**, 13 deselected; pytest
  0.66 seconds and full process wall 0.90 seconds.
- Recomputed every entry in `execution/manifests/02-current.sha256`; all 31
  current source, test, config/runtime, checkpoint, evaluation, JSONL,
  smoke/profile and pair-result hashes passed.
- Independently summed all ledger `charged_seconds`: `211.14571995799997`,
  matching the handoff's canonical `211.145719958` seconds. Historical
  nonmonotonic display cumulatives remain explicitly noncanonical.
- Existing 102-step pair-validation output records equal final steps, the
  verified nonempty aggregate stream digest, shared initial identity,
  config/source/evaluation identities, selected checkpoints, common time and
  slack.

## Required findings

None.

## Checks deferred to Block 3 review

- The actual three-seed measured run order, common update count, byte-identical
  completed streams, checkpoint selection, cap charges and final endpoint
  completeness.

## Non-blocking observation

- The opening paragraph of the final handoff retains the immediately prior
  pair-test hash, while the linked complete inventory contains the current
  evidence-only test hash shown above. The inventory is unambiguous and fully
  verified; future handoffs should avoid retaining an unlabeled stale hash in
  prose.

Charge **1.3 seconds conservatively** for this final evidence review, including
the final review-file hash command.

---

# Sol re-review — completed-run pair validation

## Exact version inspected

- `schrodinger/experiment.py` SHA-256
  `cf75e1b35fe6fb1fb462d78d415ea60115dcd267957303ef56427861ae55c288`.
- `tests/test_experiment.py` SHA-256
  `e701e44dbdc3e3e3417b2b26fb5207c2b6f250abdbe68a7e4a430eadd2c5a216`.
- `execution/handoffs/02-pair-validation.md` SHA-256
  `c07ea0094cc818ce45f028489cb59a6e7f6a208c69a6eb6e31809d80e29e32e2`.
- `execution/compute_ledger.jsonl` SHA-256
  `053c3bdbcec220e18c9e3e5f4245bd2a9b4c5ff09758d642ed9efe8b9158ba5f`.
- Existing 102-step pair-validation artifact SHA-256
  `0a372b495a064accb850dbe73ff3a13663c5851804f865349f61640c791776af`.

## Verdict

**CHANGES REQUIRED**

The executable helper correction is scientifically correct and resolves the
last implementation blocker. Two required acceptance/traceability corrections
remain; neither requires training or model/data code changes.

## Required corrections

1. The parameterized seed/config/source/initial-identity/mode mismatch tests
   still construct only step-0 checkpoints with no valid completed stream.
   `completed()` rejects them before any identity branch, so these tests pass
   without testing their named behavior. Rebuild those fixtures as valid
   completed nonempty equal-stream pairs, mutate exactly one identity field,
   and assert the specific mismatch message.
2. Add an explicit unequal-final-step regression. The new combined test name
   claims final-step and stream coverage but exercises only unequal stream
   digests at equal step 1. Use valid raw/checkpoint digests with different
   completed final steps and assert `paired completed final steps differ`.
3. Complete the promised handoff manifest. The current handoff lists only the
   helper, pair-test and pair-result hashes; it omits the current full source,
   data/model/config/runtime, evaluation arrays/manifests, completed JSONLs and
   checkpoints, revision evidence/logs and ledger reconciliation. Record exact
   commands and current paths in one unambiguous manifest; earlier evidence may
   remain explicitly superseded.

## Independently verified implementation behavior

- A completed run is the highest existing checkpoint and raw JSONL may not
  extend past it.
- The helper recomputes SHA-256 over raw per-step batch digests and requires it
  to match each completed checkpoint's nonempty digest.
- It requires equal completed final steps and equal completed stream digests
  before evaluating endpoints.
- It retains the prior data, seed, opposite-mode, config, source and initial
  shared-identity checks.
- The emitted real pair result contains completed steps `[102, 102]`, stream
  digest `70c4e48f437f55dfac77b5e7edbcab03768880a167660dce26557832227359e9`,
  initial identity, config/source identities, evaluation hashes, selected
  checkpoints, common time and slack.
- Recomputed hashes for the two raw JSONLs and final checkpoints are recorded
  in the independent command output; the real helper command is charged in the
  ledger at 1.14572 seconds after the 180-second conservative preparation
  allowance.

Independent full-suite rerun: **47 passed**, pytest 1.28 seconds, full process
wall 1.66 seconds. Source/artifact inspection used approximately 0.2 seconds.
Charge **2.0 seconds conservatively** for this review, plus the final review
hash command when recorded.

## Checks not yet verifiable

- The two currently unreachable identity-test branches and unequal-final-step
  regression require corrected fixtures.
- No measured comparison was started.

## Non-blocking observations

- The final2 smoke metrics are implementation evidence only and are correctly
  superseded for scientific comparison purposes.
- Selecting step 0 for the slower model can be the honest result of the frozen
  100-step checkpoint cadence; the recorded slack is essential and present.

---

# Sol re-review — Block 2 revision 2

## Exact version inspected

Current frozen revision:

| File | SHA-256 |
| --- | --- |
| `execution/specs/02-harness-revision2.md` | `e67e46d91b21abf87de1592b507c9e537a4d6e0119d659d5b18a08f2a2a1cfc6` |
| `execution/handoffs/02-harness-revision2.md` | `dd454addfe39fcf693205a9aba3e1cea14bec19b36c02d588c9feb3042634fdb` |
| `schrodinger/experiment.py` | `613f8c90f127ebd5fe835d977038cca842ad1642bd7af78b57ef6e2868a5c4c0` |
| `tests/test_data.py` | `688b6b5200d447efc8bc27d4823944575a046de641b923ceb5047eb1e9b5bab5` |
| `tests/test_experiment.py` | `8dc0ba4b8008b0fc9a7d8ab0e235cecc7ef8592029caff1f8afeee59d1f4a684` |
| `execution/compute_ledger.jsonl` | `0ae235c7a2ee4c28259f2cd1eb19f3acb2fe372db475545b22d242fdbf3b6dd8` |
| current full evaluation NPZ | `1a83c3ebcbcb45d12d490ffa2a7def5d29f86b21962930290fbf369eea9fcecc` |
| current evaluation manifest | `ae9be5a446d46904825f394f03f36ec7186573be6933d08b033f09c681204b96` |
Current final artifact hashes are softmax
`da0515c3377c538a902adb9c118a0fca7db501743de12a134d036b74cf303062`,
SA `7b26dd862fefe704aee998ccf81fe2f34ffad9870908e8a2b365275f409a887a`,
and pair result
`bfae7c4f51c399e7ac1fd2a9aa917fe0b00583c65357de51c27c0edf1fbd4eb8`.

## Verdict

**CHANGES REQUIRED**

Five of the six revision-1 findings are substantively resolved. One pairing
integrity blocker remains in the executable helper; the handoff manifest also
needs a documentation-only completion.

## Required finding

### R2-1. Pair evaluation does not enforce equal completed data streams or updates

Location: `schrodinger/experiment.py`, `pair_evaluate()`.

The helper now correctly enforces equal evaluation arrays, seed, config,
source hashes and initial shared identity, plus opposite modes. It never loads
or compares the completed-run aggregate `stream_digest`, and it does not require
the same final update count. Checkpoint 0 contains only the empty stream digest,
so the current checks would accept models trained on different batch streams or
different equal-update budgets as a valid pair. The pair artifact also omits
the asserted identities, preventing downstream audit from the result alone.

Required correction: load the two final checkpoints or final records; require
equal final step and equal nonempty aggregate stream digest; cross-check those
against the JSONL-derived digest; and emit the verified seed, final step,
stream digest, initialization digest, config/source identifiers and evaluation
hashes in the pair result. Add one mismatch-rejection test for stream/final
step. This is a single-helper correction and does not require new training.

## Documentation correction required before acceptance

The revision-2 handoff lists important hashes but is not the promised full
manifest: it omits current checkpoint, JSONL, smoke/profile, pair integration
and reconciliation hashes, and lists command categories rather than exact
commands/output paths. Complete the handoff or attach a machine-readable
manifest. This does not invalidate the implementation evidence and needs no
source change.

## Resolved findings and independent evidence

- Normal invariants are now stored per condition before `dt=0`; final SA normal
  maxima are Hermiticity `0`, row error `4.768e-07`, and unitarity
  `5.960e-07`. Validation snapshots remain in checkpoint JSONL, so Block 4 can
  aggregate run-wide normal maxima without overwriting evidence.
- Evaluation rejects nonfinite logits/loss; training rejects nonfinite loss,
  logits, gradients and post-optimizer parameters. Focused injected-failure
  tests cover both paths.
- The true initial shared digest is captured once and remains separate from
  current-state identity in checkpoints.
- The 60-second projected-operation reserve is active. The ledger now includes
  a clearly labelled conservative allowance bringing canonical preparation
  charge to 180 seconds; `execution/ledger-reconciliation.md` (SHA-256
  `f1283677ceca4578248cd589f9c6932e5ac0e4f42d2c7f1a2b7657a22d0e21d8`)
  explains why historical display cumulatives are not canonical.
- The suite now covers blacklist replacement, all protocol seeds, heldout
  exclusion, invariant separation, nonfinite failures, stable initialization,
  mismatch rejection, reserve behavior and correct/count recomputation.
- Real two-mode 102-step SMOKE runs preserve equal initial digest and equal
  stream digest `70c4e48f437f55dfac77b5e7edbcab03768880a167660dce26557832227359e9`;
  final condition counts, hashes and normal/intervention evidence are present.

Independent full-suite rerun: **46 passed**, pytest 1.29 seconds, full process
wall 1.65 seconds. Hash/source/artifact inspection used approximately 0.2
seconds. Charge **2.0 seconds conservatively** for this review, plus the final
review hash command when recorded.

## Checks not yet verifiable

- Automatic rejection and emitted proof of a completed-stream/final-step
  mismatch require R2-1.
- No measured comparison was started.

---

## Final Block 2 status

**PASS** — This is the latest verdict and supersedes every earlier
`CHANGES REQUIRED` verdict in this cumulative review file. The evidence and
exact hashes supporting PASS are recorded above under “Sol final evidence
review — Block 2.”
