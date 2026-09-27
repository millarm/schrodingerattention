# A2b2a evaluator handoff

Status: A2b2a evaluator subset complete for Sol exact-version review. No CLI,
immutable output/ledger ownership, production bank build, profile, pilot or test
release logic has been added; those remain A2b2b.

Implemented additive files:

- `schrodinger/route_policy_evaluation.py`: batched active-rollout missing-state
  cache scoped by `(checkpoint identity, dt0, map, goal, current)`, common stream
  sampling/greedy ties, raw routes and A2a per-problem metrics; batched supplied
  `ScoreBank` proper scores; timing fields; and read-only full-path dt0 policy-TV
  summary with frozen numerical threshold fields.
- `tests/test_route_policy_evaluation.py`: uses a small real `load_validation()`
  subset and `heldout_bank`; asserts cache reuse, batched forwards, identity
  separation, common stream repeatability, proper cache reuse, parameter
  immutability, timing/metric keys and dt0 same-score behavior for softmax.
- `local_mechanism_probe` now completes the read-only SA local reconstruction:
  for each of two layers/two heads it rebuilds q/k/v, S, H, dt, gamma, psi/U
  through the accepted primitive on the normal-SA hidden input. It returns raw
  all-row and CLS A-TV, AV/projected absolute and relative RMS, dtH spectral
  norm and wrapped-phase RMS, each with mean/p50/p95/max summaries. It separately
  returns normal-vs-all-layer-dt0 final-policy TV, signed CE/KL/Brier deltas and
  greedy disagreement on the supplied bank q/legal masks. The probe rejects
  numerical threshold violations, verifies dt0 local fidelity and asserts no
  parameter mutation; it installs no hooks. The real-fixture test asserts the
  layer/head/CLS array shapes and numerical bounds.

The final rollout closure supplies a caller-visible `replicate`, precomputes one
16-draw stream per problem/sample before stepping, supports actual uniform-legal
actions, and aggregates every endpoint problem→equal-map→stratum→0.8/0.2 mixture.
It reports Q/U/V/pass/coverage/headroom/invalid/duplicate/concentration plus the
ratio of weighted known-valid mass to weighted valid mass (not a mean of
conditionals), retaining `None` for unavailable denominators. The test uses an
unequal problem-count map fixture, frozen replicate streams, temperature cache
reuse and uniform-legal control.

Focused commands were direct, no sessions:

- `e2555a6e-4bb1-4f2b-8d40-bd2344be6de0`: exit 1, `2 failed, 1 passed in
  2.67s`, charge `3.0` seconds from retained rounded outer tool wall.
- `85ed402d-7cc1-42ea-ae92-6af3d6c5e734`: exit 0, `3 passed in 2.70s`, same
  conservative rounded outer-tool-wall charge.
- `3e84a730-3cd5-4e6d-bebd-728a2a49897a`: exit 2, collection syntax error,
  retained displayed tool wall `0.8s` (not precision claimed).
- `bf3be8c6-4b42-4e53-8675-ef0bf498dc1e`: exit 1, `1 failed, 2 passed in
  2.60s`, retained displayed tool wall `2.9s`.
- `7a1d5445-f4d7-417b-a254-9a310bd12c6d`: exit 0, `3 passed in 2.65s`,
  retained displayed tool wall `2.9s`.
- `b00e36c6-c0b3-4aec-b2b1-913cbd1f09a1`: exit 0, `4 passed in 2.64s`,
  retained displayed tool wall `2.9s`.

## Sol A2b2a-00 correction evidence

- Mixture known-valid ratio is now the ratio of separately weighted routine and
  challenge known/valid masses, with zero denominator `None`.
- SA probe records retain candidate/map/family/stratum/layer/head/row/CLS IDs;
  head contributions use their own output-weight blocks. Relative RMS reports
  `None` at a zero reference and summaries exclude NA with a count.
- Softmax reports `applicable: false` and no fabricated SA local/numerical fields.
  SA manual normal reconstruction is allclose to ordinary forward; local dt0
  fidelity and full-path dt0 values remain distinct arrays.
- Final focused result: `4 passed in 2.73s` (direct exit, retained displayed
  tool-wall charge `3.0s`, not precision claimed).

Final A2b2a bindings: `route_policy_evaluation.py`
`fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec`; focused
tests `79221f21d9692c3e05d9dfc00e63ba93723136800b67fce0116db305218780ca`.

Final A2b2a-01 literal correction run: `6 passed in 3.72s`; full-path records
carry canonical/map/family/stratum/goal/current and every propagated metric with
per-stratum summaries. `aggregate_rollout_metrics`, used by evaluator rollouts,
is tested with map A's three Q=.2 problems and map B's one Q=.8 problem producing
routine Q=.5 (not .35), plus challenge weighted-mass mixture ratio evidence.

These are append-only Stage A charges. No production model predictions occurred.
