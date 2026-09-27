# Sol review — Block 3 measured comparison

## Exact version inspected

- Specification SHA-256:
  `2049777cdb78a18555eddfa0dbe76caa424578b4ec8a12378edead28793c88ee`.
- Handoff SHA-256:
  `0ac2b05287dad05e5482683c2dcd1fe12c13ffdc4539215c5738789017d33421`.
- Frozen config SHA-256:
  `9ebace507a57202f483cefd55d5f50db868ad2abd214145a86f722386b2ffd4f`.
- Frozen runtime SHA-256:
  `805b8c51fd21468ccb2f5c70bc122b52bf13f601331937e9979efcc5c5184995`.
- Frozen experiment source recorded by every current run:
  `cf75e1b35fe6fb1fb462d78d415ea60115dcd267957303ef56427861ae55c288`.
- Current ledger SHA-256:
  `8908d745860006917eabbdc559ee2d06e89512a75bc4bd83de20edfd20ddca31`.

Current final JSON, training JSONL, and equal-time artifact hashes were
independently recomputed; the exact values are retained in Sol's review command
output. The six final JSON hashes begin `089650e9`, `c3d1e346`, `665f989a`,
`b6c1c95d`, `39cda67d`, and `6e7f65a7` in seed/mode order.

## Verdict

**CHANGES REQUIRED**

The current equal-update modelling artifacts are internally coherent and can
be summarized as descriptive screening evidence. The wall-clock/equal-time
comparison is not a controlled measurement because execution provenance was
not preserved. The handoff must be corrected to state this explicitly before
Block 3 can be accepted as an `INCONCLUSIVE` completed screen. No rerun is
authorized or required.

## Required finding — undisclosed retries invalidate timing provenance

Location: `execution/handoffs/03-comparison.md`, measured result directories,
and `execution/compute_ledger.jsonl`.

The handoff states that six training commands and all pair commands exited
successfully. The ledger instead proves eight training launches and one failed
pair command:

- Seed 22 softmax ran twice. The first apparently successful train was followed
  by a failed pair evaluation (`raw JSONL extends beyond completed checkpoint`),
  then the same directory was retrained and overwritten.
- Seed 33 Schrödinger ran twice even though the first equal-time command had
  already succeeded; the same training and equal-time paths were overwritten.
- `execution/results/measured/seed-22/failure.json` preserves the pair failure,
  but the handoff does not disclose it or identify superseded results.

Follow-up commands were launched based on artifact existence without preserved
proof that the prior process had exited. Non-overlap, the first runs' internal
training timings, and a predeclared choice between first and retry timings are
therefore unrecoverable. The current equal-time JSON files are mechanically
consistent with the current overwritten runs, but they must not be reported as
a controlled wall-clock comparison, nor may the apparent roughly 3x overhead
be used for the frozen severe/tolerable-overhead decision.

Required correction: revise the handoff and downstream summary to enumerate
all eight launches, the failed pair command, overwritten artifacts and unknown
overlap; mark training throughput, per-run training time, time ratio, selected
equal-time checkpoints and equal-time accuracies **invalid/unavailable for
scientific comparison**. Preserve their raw values only as operational logs.
Do not rerun training to repair provenance.

## Independently verified valid evidence

- Every current run contains 2,001 continuous JSONL rows from step 0 through
  2,000 and checkpoints at step 0/every 100/final.
- Within every seed, both modes have identical nonempty aggregate stream
  digest, initial shared-tensor digest and fixed-evaluation hashes. Raw JSONL
  recomputation matches each final checkpoint and final JSON.
- All runs record the same config, runtime versions and source hashes. Final
  counts are 256 XOR/256 COPY for validation and 512/512 for each final
  condition.
- Every normal and `dt=0` accuracy exactly equals integer correct/count.
  Required final `dt=0` metrics exist for all SA conditions.
- Run-wide logged SA maxima are Hermiticity `0`, unitarity at most
  `1.073e-06`, and Born row error at most `1.073e-06`, below the frozen
  tolerances. Values, gradients and checkpoints remained finite.
- Final learned `dt`/`gamma`, process RSS proxy, validation curves and normal
  final metrics are present for every run.
- The current equal-time files apply the declared checkpoint rule correctly to
  the current logs (softmax step 2000 versus SA step 600 with disclosed slack),
  but their scientific timing status is invalid for the provenance reason
  above.
- Canonical ledger charge recomputes to `380.9506345819944` seconds, well below
  both resource ceilings and inclusive of retries/failure.

## Frozen endpoint audit

- Neither model reaches 90% or 95% validation XOR in all three seeds. Only
  seed 33 reaches either target, so both sample-efficiency targets are
  right-censored and no first-target `dt=0` checkpoint intervention is
  required or admissible for the gate.
- Mean equal-update primary heldout/d4 XOR difference is
  `+0.0201822917` (SA minus baseline), below `+0.03`.
- Mean equal-update secondary seen/d8 XOR difference is
  `+0.0162760417`, below `+0.03` and not positive in seed 22.
- Setting `dt=0` does not remove the observed mean advantages: primary mean
  advantage becomes `+0.0208333333`; secondary becomes `+0.015625`.
- Mean final validation XOR is `0.71875` baseline and `0.7369791667` SA.
  Neither reaches the frozen `0.80` learning-adequacy threshold. The research
  result is therefore **INCONCLUSIVE**, not a negative mechanism conclusion,
  independently of the provenance defect.

## Independent checks and compute charge

Performed read-only hashing; checkpoint metadata inspection; raw-stream digest
recomputation; continuous-step/checkpoint-cadence checks; count-denominator
metric recomputation; target-censoring reconstruction; invariant/RSS/scalar
aggregation; paired endpoint calculations; equal-time selection checks; file
timestamp inspection; and ledger summation. No training or model forward pass
was run.

Observed executable review time was approximately 1.1 seconds. Charge **1.3
seconds conservatively**, including the final review hash command.

## Checks not verifiable

- Actual non-overlap and first-attempt timings for the overwritten seed-22
  softmax and seed-33 SA runs.
- Whether seed 33 was retried for any reason other than orchestration; no
  preserved failure or pre-results decision explains it.
- A valid wall-clock/equal-time architectural comparison.

---

## Final Block 3 status after provenance correction

**PASS**

This PASS accepts Block 3 as a fully audited **INCONCLUSIVE** execution record;
it does not validate the timing/equal-time measurements. It supersedes the
earlier `CHANGES REQUIRED` verdict after the documentation correction only.

Corrected handoff:
`execution/handoffs/03-comparison.md`, SHA-256
`f9ef6328a2763cca75176067b589e22e3260071a58d98a5791f8c302229115f4`.
Corrected provenance log:
`execution/logs/03-run-provenance.md`, SHA-256
`09bea318455089c945924451956408023b5412c450f1ff33c52ec2897829a604`.

The corrected record explicitly reports eight successful training launches and
five pair-evaluation attempts (four successful, one failed), identifies the
seed-22 softmax and seed-33 SA duplicate-path follow-ups, discloses overwritten
artifacts and unprovable process non-overlap, and marks all timing/equal-time
comparisons invalid. Equal-update surviving artifacts remain internally valid
descriptive evidence. No additional training is authorized.

Total conservative Sol Block 3 audit charge: **2.0 seconds**, including final
hashing and provenance verification.
