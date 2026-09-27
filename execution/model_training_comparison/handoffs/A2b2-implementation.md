# A2b2b implementation handoff — pending Sol review

This additive handoff covers `schrodinger/route_policy_experiment.py` and its
focused tests only. No production prepare, smoke, profile, pilot, main run, or
test-model inference was invoked by this implementation work.

## Command and ownership surface

`python -m schrodinger.route_policy_experiment` exposes `prepare`, `smoke`,
`profile`, `train`, and `evaluate`.  Every command is wrapped by `OwnedAttempt`,
uses an immutable named output and shared lock, writes an attempt record/ledger
charge on either outcome, and prints strict JSON only after success. Prepare
constructs all three frozen banks without model inference. Every later command
requires a decision that binds the frozen config hash, manifest and prepared
artifact hash; the saved provenance covers the exact source/test/spec/review/
approval files, plan hash, runtime, Python/Torch/Numpy and thread settings.

Train is runtime-configured to two intra-op and one inter-op thread, creates the
paired seeded initial tensors and records their shared digest, uses the accepted
scheduler, fixed validation probes, durable `curves.jsonl` and `events.jsonl`,
and accepts a resume only when the decision binds its full identity/checkpoint
hash and the original initial checkpoint.  Scheduled controls are greedy K=1,
T=1 K=32, own-initial and uniform-legal. Evaluation supports validation
checkpoints; test evaluation additionally refuses unless the release decision
binds twenty distinct completed seed/mode/checkpoint identities and all gates.

## Profile and forecast

The throwaway profile is seed 1699, softmax then SA, five warmups plus twenty
measured updates per model. It selects the first two canonical maps in each
I/L/mixed family (six maps/96 problems), measures actual greedy K1, T1 K32,
proper, fixed probes and checkpoint I/O. The all-work forecast applies 1.5x to
both 1000-update models, eleven writes, evaluations at 0/500/1000, controls,
probes, setup/audit/serialization and full 512 validation extrapolation. A
missing stratum uses the largest observed per-problem rate; temperature endpoint,
midpoint/grid fallback, fixed curves, entropy matching and dt0/rematching work
are explicit.

## Verification

Focused command-harness suite: `10 passed in 14.43s` via
`.venv/bin/python -m pytest -q tests/test_route_policy_experiment.py`.
The tests cover immutable prepare/bank identities, strict release refusal,
actual tiny route smoke, resume binding/replay, durable safety lifecycle,
separate timings and conservative all-work forecast arithmetic. This is not a
Sol acceptance and does not authorize a production command.

Frozen review identities at handoff creation: `route_policy_experiment.py`
SHA256 `8dfcd291b38001db21b140a7b74e7040360e920a1784e47712b626253979f833`;
focused test SHA256
`8e54b229ec4a1881beca7316bd590743820f6d5034d0a3f1d9d430e21a10a744`.
The retained direct-exit command record is: focused `9 passed in 13.87s`
(tool wall `14.6636945s`), compile/help (wall `0.47977775s`), focused `10
passed in 14.42s` (wall `14.666336417s`), focused `10 passed in 14.43s`
(wall `14.676564375s`), and one full suite `217 passed in 28.31s` (wall
`28.583526083s`). These five charges were appended as new EOF ledger UUIDs;
no duration is rounded or inferred.

Known review item: the current forecast implementation should be audited for
physical 384/128 validation work across both models and all three endpoints;
this handoff does not claim that its current aggregate arithmetic establishes
the final resource gate.

## A2b2b-00 consolidated correction (pending Sol review)

The corrected source is SHA256
`d7999a69fb52414cebca2501bb78daae884f9448ac600d045d8955cf6ddc20ea`
and focused tests are SHA256
`1061726393affdb9bfde4b35cab35137e95841033fe9a1cfd170c17257bea627`.
The new `F1B03693-AD5B-410C-A23F-F3EE32ADEA3C` EOF ledger row retains the
direct focused result: 11 passed in 14.55s, tool wall 14.816794041s.

The correction maps Sol's six findings as follows: (1) forecast is now physical
384 routine + 128 challenge per model and endpoint, multiplied by two models,
three endpoints and 1.5, with separate 11×2 writes/probes/fixed measured units;
(2) CLI prints COMPLETE only after owned finalization and artifact verification;
(3) training decisions bind command/seed/mode/update/fresh-or-resume and permit
only 1701 pilot plus explicitly bound 2000/4000/8000 resumed continuations;
(4) resume validates the hash/full identity/state hash of the original initial
checkpoint before restore; (5) both train/validation probes and support-aware
evaluation are wired; and (6) provenance has path hashes, argv and RSS.

Focused literals include strict release/prepare, resume and substituted identity
coverage, conservative physical forecast cells, durable traces, and CLI success
versus forced finalization failure with no COMPLETE output. Future temperature
and main/test analysis remain `NOT_IMPLEMENTED_GATED`; test inference is hard
gated and no future main framework is claimed. Production profile/pair work was
not invoked.

## A2b2b-01 final correction (pending Sol review)

Harness SHA256: `e9ea4858176a19c4ef267ea70592f69eb9795c3fc41eea787a40c74921d3bb7d`.
Focused tests SHA256: `7d44a67a5a62cb19df50d8bc8a85d3518b672eb92c232f1a5d397277ea92d728`.
Selectors are exactly 64 train probes (first four I/four L maps) and 128
validation probes (first four I/four L/all eight mixed), eight states per map.
Profile retains greedy/T1/proper/own-initial/uniform timings; future
temperature/dt0/rematching is costed from the conservative measured cell and
explicit candidate counts while analysis remains gated. Prepared artifacts embed
frozen source provenance. Focused result: 12 passed in 18.38s, wall
18.655783375s; EOF ledger UUID DEADF981-22E2-4454-8DED-C9465F999CEF.
