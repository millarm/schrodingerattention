# Revised Block A contract: fractions of8000 training updates

Read `plan-v2.md`, protocol and pending Sol review. This supersedes
`spec-01-wrapper.md` scientifically; the earlier spec and partial code remain
historical. No Terra edits/imports/tests until Astra dispatches Sol protocol PASS.

Allowed files stay `study.py`, `command.py`, `tests/test_update_efficiency.py` and
study-local handoffs. No accepted scientific module changes. Preserve all old
artifacts and original central ledger. Existing literal input-ID/q-bank lineage
in `decisions.md` remains valid, including its Sol clarification review.

## Required scientific changes

- Seeds2201–2204/order unchanged; horizon8000; grid0/1200/2400/3600/4800/6000/8000.
- Seven full-panel T1/K32 evaluations and exact1024-state q bank. Unchanged
  `scheduled_training(validation=None)` saves every100, no scheduling monkeypatch.
- Primary C and secondary stage contrast exactly as plan-v2; per-seed raw
  endpoints/contrasts plus four-seed summaries, no nonlinear shape search.
- Common Q milestones.30/.38198 with lower1pp tolerance; two consecutive passes,
  initial anomaly, interval/censoring, exact-threshold sensitivity, separate
  KL>.40/challengeQ<.08 flags. Remove old single30%-guard-composite estimator.
- Literal tests cover affine Δ trajectories giving C0, known curvature magnitude,
  sign reversal, unequal/corrupt grids, four-seed SD/t interval, missing seed
  refusal; common thresholds/intervals/censoring/anomaly and guardrail separation.
- Full pairing validates shared initial tensors/digest, all8000 batch digests,
  exact checkpoint/source/config/input IDs, q/order/RNG identities. Keep target
  crossing independent of timing and never infer outcomes from historical seeds.

## Mandatory source/driver safety (not optional scope)

Retain original spec's literal actual run/owner/evaluator/checkpoint composition
and failure tests, not a manually rebuilt approximate path. Tiny test-only
loader/schedule injection must not be reachable in production CLI. Actual owner
endpoint-write and final-manifest failures prove one charge and durable failure;
forbidden test/prepared loaders must be spied/rejected. No placeholder fixtures.
Source bank canonical identity uses actual canonical bytes, not serialized full
candidate identifiers. Verify the accepted API/schema before handoff.

The six driver-closure items in `spec-01a-driver-closure.md` remain mandatory,
with these EXPLICIT replacements: production is8000; per-owner capSM200/SA250;
new-study B1800; stage capsA1000/B4100/C0/D800. A100 andD100 remain. Study owner
and command identifiers must say8000, never old4000. Exact authority hashes now
bind plan-v2/spec-02 and their designated Sol reviews, not the superseded plan.
Driver/scientific source use the same identity dictionary contract. No broad
mutable stage policy: scope/restore original constants. Reuse reviewed pure
watchdog supervision/records rather than another process-control framework.

All initialization, loaders, training, scoring and writes inside owned deadline;
external driver captures all startup/cleanup/failure accounting. One command
reservation, central+local locks, exact147-line prefix and unique carry, new-study
caps as well as global/stage caps. Production reconciliation by actual owner UUID
on ALL exit paths, permanent uncertain fallback never promoted; complete bound
manifest/result/index/endpoint hashes before success. EOF-only charges once.

## Bounded development and acceptance

Terra first completes driver-only sub-block with literal static assertions, then
study estimator/actual composition sub-block; return complete small handoffs, not
repeated partial whole-harness claims. No runtime before all source/test/driver
frozen exact static PASS. Then10s smoke/30s suite with full external records within
A100, inspected correction only within remaining allowance. Two correction
cycles require concrete respecification/blocker, never waived acceptance.

Sol implementation PASS/Astra acceptance precede production. First2201 pair then
objective resource forecast gate exactly per plan. No production delegated by
this spec. No fresh-seed outcome can change grid, targets, contrast or order.
