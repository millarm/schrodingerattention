# Block 1: inference-only scoring of existing early checkpoints

2026-09-27. Astra specification, methodology review required before code work.
The binding plan is plan.md. The 200k branch is HOLD and must not be resumed.

## Scope and reuse

Luna may create execution/early_learning/{study.py,command.py,inventory.json},
tests/test_early_learning.py and handoff/runtime outputs. Astra owns plans and
acceptance; Sol owns reviews. Keep existing sources, checkpoints, ledgers,
hashed reports, and partial 200k implementation untouched. Do not base this
block on unreviewed 200k code. Reuse the accepted update_efficiency watchdog and
its accepted lifecycle/accounting logic with narrow new identity/budget bindings.
Avoid a new background coordinator: operate the four owners sequentially after
explicit terminals. All computation is inference-only.

## Input and evaluation contract

Create a mechanically derived immutable inventory of the four original owner
attempt/result/index/manifest hashes, original source/config/input/bank identities,
all 31 target checkpoint hashes and the four reusable score hashes per owner.
Derive tensor identities from existing score JSON where available; verify actual
checkpoint payload identity and original parent chain inside bounded ownership.
Review hashes bind the inventory. Do not trust freshly substituted parent files.
No prepared payload or final-test data access; use accepted manifest-bound IDs
and validation reconstruction to match the original 1,024-state bank exactly.

Load RoutePolicy state_dict at each target checkpoint and model.eval(); wrap
all model/probe computation in torch.inference_mode(). Call accepted evaluators
unchanged. Never instantiate an optimizer or sampler for training, call backward,
train_step, scheduled_training, or modify parameters/checkpoints. Capture before/
after model state hashes for mechanism probes and reject mutation.

At the 16 reused proper/Q cells verify old score checkpoint hash and metric
schema, copy/reference raw old evidence with explicit lineage, and evaluate only
the new greedy/probe components. At new cells save complete proper arrays,
rollout evidence, compact metrics and timing with fresh identities. Entropy uses
proper.weighted entropy_p/entropy_q, not greedy-route entropy. Greedy Q means
the accepted deterministic greedy valid-route fraction. Freeze aggregation as
in plan; retain routine/challenge metrics separately. Clear per-checkpoint caches
to bound memory. Reuse same-checkpoint caches only with distinct valid identity
keys and unchanged model semantics.

Use accepted validation_probe_candidates to select 128 deterministic validation
states. Record candidate IDs/hash/order; call accepted mechanism_probe for SA
at the seven fixed points. Preserve raw record counts/fields for verification;
report per-head summaries as summaries of that diagnostic panel, not an unbiased
population estimator. Effective dt/gamma extraction uses actual model raw values.
Keep numerical thresholds and reconstruction/state-mutation checks unchanged.

## Summaries

Pure functions require the exact 31-point ordered grid and finite metrics.
Window means/slopes use all intended inclusive grid points with no imputation.
Slope x=update/1000; least-squares slope=sum((x−xbar)(y−ybar))/sum((x−xbar)^2).
Paired summaries require same seeds/grid/checkpoint lineage/input/bank identities
and the original full 16,000 paired batch-digest agreement. Missing owners remain
visible and preclude a complete two-pair aggregate. Preserve raw curves and
sampled tied minima, without selecting a favorable checkpoint as the headline.

## Ownership and acceptance tests

Fresh zero-carry ledger under this study: A 120, B 1,440, C 0, D 240 seconds;
global cap 1,800 seconds.
External driver holds an exclusive reservation, source/review/decision bindings,
fixed 300/360-second owner envelope, explicit cleanup/terminal proofs and exactly-once
charges including failures. Bind decisions to current ledger EOF, inventory,
seed/mode/grid and full frozen source set including accepted evaluator/model/
data/metrics/probe/runtime dependencies. Neural imports occur only in bounded
owned processes. No ambiguous accounting releases the reservation. Preserve
old ledger SHA before/after and require 2 GiB free. No unreviewed runtime.

After static PASS run one 10-second smoke and one 60-second targeted suite.
Use only tiny private panels for runtime tests, including mechanism probes;
the suite must not evaluate the full production panel. Tests must exercise
actual composed driver→study decision/ownership path with a tiny private fixture
panel/grid and real inference, not just isolated helpers. Include rejected
tampered inventory/checkpoint/source/ledger, score-reuse binding, metric/entropy/
greedy extraction, analytic mean/slope/tie and gap-SD cases, exact missing-cell
rejection, and no training/model mutation. Exercise timeout descendant cleanup
and charged terminal/reservation safety using accepted fixtures as appropriate.
Compare any repeat reused-score fixture metrics within 1e−8 for identical arrays;
model/probe reconstruction tolerances remain accepted 2e−6 absolute / 2e−5 relative. Do not expand
to a broad full repository suite. Record exact hashes/tests/commands in handoff.

Final audit binds all 4 × 31 checkpoints, 108 new + 16 reused Q/proper cells,
124 greedy evaluations and 14 SA probes, source/inventory/ledger identities,
cleanup, and raw-to-summary arithmetic. Astra accepts only after exact Sol PASS.
Report partial results explicitly if any resource or integrity gate prevents
completion. Inference outputs never authorize new training or final-test use.
