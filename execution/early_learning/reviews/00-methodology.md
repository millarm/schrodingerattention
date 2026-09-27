# Block 1 independent methodology review

2026-09-27. Reviewer: GPT-6 Sol. **Verdict: PASS** for the exact plan and specification below. This is a methodology review only. It permits Luna to implement the bounded inference harness; it is not a static implementation PASS or authority to score models yet. The 200,000-update extension remains on hold.

## Exact documents inspected

| Document | SHA-256 |
| --- | --- |
| `execution/early_learning/plan.md` | `fcfc12a9a250a85391259cbff3bd2bd62a8a429e8b0a1615944ad40682f9be5f` |
| `execution/early_learning/spec-01-dense-scoring.md` | `b0bf16e0caaf1407fd72c148622b73826f998885fb124be77da24cdd88be90cc` |
| `research/early_learning_refocus_2026-09-27.md` | `05b11395c7c0fd518cd80672ed1835aed1555102c090a74cfe4ff43023ff41b0` |
| `README.md` | `da0a349576c7e5e282f6cfd4bc7963294852ef25fc94941a09fc6579adc55f91` |
| `execution/long_horizon_200k/hold-decision.md` | `da67b9bb31bff7053dbc2be123082859b3b42ae76e22e91a92ac1f6dd780b0c7` |
| `agent_execution_protocol.md` | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |

Hashes were computed by a read-only SHA-256 command. I also inspected the accepted evaluator/probe interfaces, without importing or invoking them. No tests, inference or training were run.

## Methodology assessment

The exact 0–3,000 grid has 31 checkpoints per owner, four reused Q/proper cells and 27 new Q/proper cells per owner: 16 reused plus 108 new across four owners. Greedy evaluation at each checkpoint gives 124 cells. Seven fixed SA probe checkpoints for each of two SA owners give 14 probes. The 16 reused cells are required to retain old score and checkpoint hashes and explicit lineage; the remaining cells use the same validation bank, aggregation, T1/K32 sampling and common uniforms. This preserves comparability without new training or final-test access.

The primary 800–2,000 inclusive window contains 13 equally spaced points. Arithmetic means and ordinary least-squares slopes in update/1,000 units are defined before dense scoring. Secondary windows, overlapping boundaries, sampled tied minima and no interpolation are explicit. The plan requires seed-level paired differences before its two-seed mean/range, while raw checkpoint-gap and detrended-residual SD describe within-run variation. It forbids checkpoint/map/rollout pseudo-replication, p-values and population inference. It correctly labels the windows exploratory because prior scores and the critique informed them.

The interpretation distinguishes sampled valid-route Q from oracle-distribution agreement and treats falling policy entropy plus worsening KL/Brier as compatible with sharpening, not proof that all route gains are confidence artifacts. Greedy Q and local SA probes are descriptive companions. The probe remains a fixed-weight evolution intervention on a deterministic 128-state subset; head/row/state summaries carry denominators but no independence claim. The 1,200-update prior KL minimum is identified as the first previously scored nonzero checkpoint and only a sampled minimum.

The fresh A120/B1440/D240 allocation totals 1,800 seconds with zero carry. Four external envelopes sum to 1,320 seconds. At the prior maximum 7.405 seconds per proper+Q cell, 108 new cells would take about 800 seconds, leaving roughly 520 seconds within those envelopes for 124 greedy cells, 14 probes, startup, serialization and cleanup. The forecast is provisional, as the plan states; strict deadlines and fail-stop partial reporting are appropriate. The 10-second smoke and 60-second suite use tiny private panels, including for mechanism probes, and must exercise the composed driver-to-study path before production. The old ledger hash and 2 GiB disk gate are explicit.

## Root document observations

The addendum accurately qualifies the earlier 1,200 minimum and the old Q plateau claim. README now says the dense panel will find the *sampled* minimum and bracket worsening, which matches the 100-update resolution. Minor wording only: “compare learning rates” in README could be read as comparing optimizer LR values; “compare changes in measured scores” would be clearer. This does not affect the frozen scientific contract or block implementation.

## Conditions for the next gate

The implementation review must verify immutable original-checkpoint inventory and parent chain; exact reused-score evidence; no training or final-test access; actual composed decision/ownership path; bounded neural imports; source/review/ledger binding; numerical and state-mutation checks; exact 31-point summaries; all failure charges and cleanup proof. No authority to run full inference follows from this methodology PASS alone.

METHODOLOGY_REVIEW_VERDICT: PASS
