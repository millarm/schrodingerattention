# A1 adapter/model handoff

Implemented only the additive route adapter and matched policy modules; no
optimizer step, measured training, profiling, scoring bank, or final-test model
prediction occurred.

Frozen source hashes:

- `schrodinger/route_policy.py` — `c0b735b096ebda8c4fbbccd2274ef3486ea8e0cb1921c848c31d97f2946a27c0`
- `schrodinger/route_policy_data.py` — `f2bd33eceddbdaddc040222f584ca94d6d2b245765743c6ff2919a37cd02ae8e`
- `tests/test_route_policy.py` — `63d23b30e1098fde08aac85686a54c6dbe8b1002be3036dcdf8ef51637240b4a`
- `tests/test_route_policy_data.py` — `2654f47a2afd585970f0eeb1e9f89cd3b96b4f82a1374d6c13d0d45f0fb95401`

`route_policy_data` verifies the frozen proposal14 manifest and artifact hashes
before decode, uses `(canonical, current, goal)` state keys and action key/value
q mappings, verifies selected map identity against immutable inventory, rejects
blocked endpoints/non-finite or illegal q mass, retains canonical orientation, and
offers separate training, validation, and final-test loaders.  The sampler uses
`SeedSequence([95001, seed])`, a single map-index draw, sorted per-map states,
resumable RNG state, and a batch hash.

`route_policy` is CLS plus 12 row tokens, d64, two pre-norm attention/FF128 GELU
layers, two heads, final LayerNorm, and four raw logits. Softmax and SA each have
eight active extra scalars; SA uses the unchanged exact attention primitive and
supports a same-tensor `dt_override=0`; ordinary diagnostics are off.

Focused evidence:

` .venv/bin/python -m pytest -q tests/test_route_policy.py tests/test_route_policy_data.py`

returned `4 passed in 0.58s`, tool wall `0.711590583s`. Tests cover feature and
wall legality/q rejection; current/goal decode ordering; sampler restore/hash;
13-token/4-logit shape; matched eight-scalar counts; shared initialization copy;
strict finite non-None gradients for all softmax parameters; masked CE; exact
state-dict reload; and dt0 output consistency plus explicit diagnostics.

Charge was appended once to the new ledger at true UTC `2026-09-19T12:06:03Z`:
UUID `9fd18d64-01d2-4c22-88dd-930218e6a1eb`, stage A,
`0.711590583s`. Old ledgers and existing source/test/plan files were not edited.

## Test-command reconciliation

Every A1 compute/test command was the same focused pytest command.  All returned
directly (no yielded session): failed `2 failed, 2 passed`, exit 1, wall
`3.668493042s`; failed `2 failed, 2 passed`, exit 1, wall `0.644829584s`; passed
`4 passed in 0.70s`, exit 0, wall `0.842685292s`; and the final charged pass,
exit 0, wall `0.711590583s`.  The first three had initially been omitted from
the ledger. They are reconciled exactly once in ledger UUID
`706e7f52-28da-4b33-b647-06712d91b2b9`, true process UTC
`2026-09-19T12:08:02Z`, aggregate `5.156007918s`; individual exits and walls are
preserved in its `attempts` field. No other A1 test or compute command ran.

## Review-00 correction

The corrected adapter now returns immutable typed training and held-out bundles,
preserves selected problems/full support/support hash, validates all held-out rows
against inventory, and includes one count-only frozen training/validation/test
adapter smoke. The corrected model rejects invalid modes/masks, uses q-positive
CE with finite Brier/KL helpers, exercises both architectures' complete gradient
sets, and tests length-13 primitive numerical thresholds at score magnitudes
0.1/1/3 plus same-tensor dt0 equivalence. Focused final result: `5 passed in
3.71s`, tool wall `3.811011875s`; preceding correction pass was `4 passed in
0.73s`, wall `0.915378875s`. Both direct-exit charges are ledger UUIDs
`b1ac2cb1-0d94-454e-bbb6-a0facab61e18` and
`4a5e60a9-f04d-4c4c-a9dd-3e77b68a1c72`.

Corrected hashes: route model `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4`;
adapter `234943a02b068e1d0d7bb3d25402b2647ed4cf2515cf00ce6d539763dcadd381`;
model tests `0cdf0f84812aa1e7cd987d6f72beb88f76ceb252d3f44b3ccd5d2054bff56581`;
adapter tests `078f0e7f7ab23825101546dc1d8b1abe643d85cb9610837f1f18cf79eceaaf47`.
