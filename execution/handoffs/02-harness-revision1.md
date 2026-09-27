# Block 2 revision 1 handoff

Superseded artifacts remain under `execution/results/smoke/` and prior revision directories because evaluation block ordering was corrected. Fresh current evidence is under `execution/results/block2-final2/`: corrected block64 smoke/profile, two 102-step SMOKE-labelled normal paths, dt=0 checkpoint evaluation, and equal-time pair evaluation. No six-way measured comparison ran.

Evidence: `pytest -q` exited 0 with 29 passed; revised smoke and profile exited 0; a normal `train --mode softmax --steps 1` and checkpoint `evaluate` exited 0. Key code hashes: data `a8f1f3fe0f61970e36b8e6bde72fc95b7722ffdb563c3c9ecc08f7c24a4341dc`; model `fe800c91d539c94a529e0dd980fbe2b93bcc259e3b336e02aebe1a549b65d837`; experiment `c9204887b44b1d65f8b532a0ef6985c81223ae1b026df1b94f367b4cbc15bdf3`.

Current code hashes: data `3fab8bafdecd773df13d81c81653ece8760707b5f11f59cb2f5c56ab225278e3`; model `b2892ee6dc8158b326b2fbb3ecc242e030edd94f36f5d407246a4666ac4dc36a`; experiment `16a06102a3f9e563409d6cedb24e183498a3a0fd62cd1f04683bf6ce06b599a5`; data tests `8394b449d25c65105262324e2ff2a750123ab8b350f73375ab8787a9cb4d2c78`; experiment tests `43e5268f88b21dd3d89789d38f2a2188faaa8a8d5c27f332f77999893fcdb07f`.

Verification: full pytest exit 0, 33 passed in 1.07 seconds. Fresh smoke/profile/two-mode normal/evaluate/pair commands all exited 0. Paired initial digests matched `46cae600…`, stream digests matched `70c4e48f…`, and stored evaluation hashes matched. Pair evaluation selected softmax step102 and Schrödinger step0 because the frozen equal-time rule chooses the latest checkpoint at or below the baseline's shorter elapsed training time; slack is recorded in `pair.json`.

This revision is frozen pending Sol review.
