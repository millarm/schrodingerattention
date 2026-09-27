# A2b2 — complete bounded evaluation and profile harness

After accepted A2b1, Terra completes route_policy_experiment.py and its tests
under the full A2b-harness-profile.md specification. This subdivision does not
reduce any acceptance requirement or authorize production before Sol PASS.

Complete prepare/smoke/profile/train/evaluate entry points, explicit decision
authorization and final-test release guards; serialize frozen banks, source/
input/runtime provenance and immutable attempt artifacts. Reuse the accepted
safety/training core rather than a second runner. Production-style tests use
temporary ledger/output roots only; actual saved adapter data stays immutable.

Implement batched missing-state inference across active rollouts, cache identity,
raw per-attempt/per-problem metrics, fixed proper banks, own-initial/uniform legal
controls and all scheduled model probes. Probes may use external hooks/read-only
tensor reconstruction without changing accepted model equations. Separate direct
local same-state attention differences from full-path dt0 changes. All required
per-head/CLS/stratum distributions and numerical abort checks remain as frozen.
No test predictions in prepare/smoke/profile/pilot.

Implement the exact seed1699 five-warmup/twenty-measured profile and fixed six-map
validation subset, actual stage timing and the conservative 1.5x forecast from
A2b. Include Python rollout/uniqueness/serialization, every scheduled evaluation,
controls, probes and checkpoint I/O, not just neural step time. Forecast failure
is an honest resource stop, never a smaller batch/model/K/configuration.

Tests exercise cached/uncached batched equality, real tiny route evaluation and
proper/probe output, same-tensor dt0 fidelity, test-release refusal, CLI immutable
attempt safety, separate timing fields and conservative missing-cell extrapolation.
The small A2b1 training fixture can be reused without redundant long runs. Target
<=20 seconds focused tests within existing A400. All attempts charged once.

Handoff A2b2-implementation.md must bind the final exact source/test hashes and
full A2b checklist to actual assertions, documenting any unavailable field. Sol
reviews the final combined harness before one unique smoke/profile invocation.
Astra authorizes that invocation only after PASS. Sol then reviews actual runtime
forecast before any seed1701 training. No main-framework/plotting additions yet.
