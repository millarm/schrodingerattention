# A2b1 — bounded safety and training-core implementation

This is the first sequential part of accepted A2b-harness-profile.md, not a
change to model, science or budgets. A2a acceptance precedes implementation.
Terra creates schrodinger/route_policy_experiment.py and focused tests. Existing
accepted modules remain unchanged. No production command/profile/pilot is
authorized merely by this subset's acceptance.

Implement only these concrete capabilities completely:

1. New-run ledger parsing, exactly one 923.003597253 carry, unique IDs, finite
   nonnegative charges, A/B/C/D/global arithmetic and fixed audit/finalization
   reserves exactly as A2b. Owned lock, fail-if-output-exists attempt directory,
   UTC/UUID provenance, deadline/finalization, append-once elapsed charge and
   explicit failure artifact/cleanup. Use temporary fixtures for tests; never
   touch old ledgers or reuse old mutable Attempt globals. Actual tests still
   append their real charges to this experiment ledger once.
2. Frozen-config paired initialization, shared tensor/count hashes, optimizer,
   map-balanced sampler, real training step with finite checks/clip, phase/core
   timing and bounded every-100-step gradient/update/parameter summaries. No
   costly invariant probes on regular forward. A callable scheduled-evaluation
   seam may be injected here; A2b2 supplies the real evaluator before production.
3. Complete checkpoints at initial/every-100/final with seed/mode/source/config/
   initial-state/input identities, optimizer, sampler RNG, torch RNG, update and
   timing/parent-chain metadata. Reject mismatched resume identities. Restored
   next minibatch and parameters must equal uninterrupted run exactly under
   fixed CPU settings. No silent fresh restart or checkpoint fallback.

Tests must actually exercise invalid/missing/duplicate carry and IDs, nonfinite
charge, stage/global exhaustion, lock contention, existing output, exception and
timer cleanup/charge, output-record failure handling; assert explicit outcomes.
Use a tiny complete accepted-adapter batch (not a new dataset) for both model
optimizer finite-gradient checks and deterministic interrupted/resumed matching.
Assert phase timing separates scalar/gradient summaries and I/O from core while
end-to-end charge includes all. No long training: at most five steps/model in
focused tests, with a shorter continuation split for the replay fixture.

Target <=20 seconds focused tests inside remaining A400, not additional budget.
All failed tests count. Full command result/session/explicit exit required.
Handoff A2b1-implementation.md binds exact sources/tests, literal test evidence,
commands/charges and names the unimplemented A2b2 CLI/evaluation/probe/profile
surface explicitly. Sol exact-version subset PASS then Astra acceptance is
required before A2b2 begins. No assertion of full harness completion here.

## Final bounded correction details (Sol A2b1-01)

Training core equals materialization plus neural step exactly; checkpoint training
time is cumulative over all completed updates. Preserve every layer/head control
value, never means: effective SA dt/gamma and baseline alpha/beta. The disjoint
preclip gradient groups are embedding (row projection, pos, CLS), attention
(q/k/v/o excluding controls), feed-forward, normalization plus action head, and
extra controls. Assert group membership/norm formula and distinct per-head values.
These measurement names are frozen before training and do not change the model.

Prove tensor-exact SA replay, not loss equality alone. Restore previous timer and
handler for intermediate setup exceptions as well as normal/failure finalization.
Ledger rows account cost, not successful run completion: use a neutral charged
status, never premature COMPLETE. A success attempt artifact may be emitted only
after durable ledger append succeeds. On post-write fsync failure retain the one
charged UUID and canonical failed/uncertain attempt state, no duplicate retry or
false success record. Consumers require the successful attempt artifact as well
as accounting, never interpret a neutral charge row as a completed run.
