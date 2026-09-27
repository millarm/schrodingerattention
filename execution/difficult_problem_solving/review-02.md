# Definitive D0 final-correction review

**Implementation SHA-256:** `63ecc9c8106c4b313053e0d79fce141fba6629224bd72e0c88f616c6cd761fe7`  
**Tests SHA-256:** `299b3b2770f0c9b1c7beab2a63c0f6c48a143d8d504e9c256556ce78e5120e05`  
**Handoff SHA-256:** `04972ee9fd657968e35831a5b1ab47cd62f9fc4b257a247e32456be91e68b6aa`  
**Correction record SHA-256:** `81844c361ae5b03f60a263fa504795eb7c95bcd0f45d00bf6afbc8f3e7f55a9e`

**Verdict: BLOCKED — do not launch production**

The core production assembly is now substantially complete: it separates geometry by stratum/seed/mode, includes routine and challenge paired map cells, aggregates prefixes, emits fixed bin keys, enforces the exact family/map composition, retains identities, and leaves the scientific gate unchanged. The declared final correction nevertheless does not literally close all seven acceptance items, and the handoff overstates and misreports its evidence.

## Concrete unresolved items

1. **Owned success/write/finalization evidence is absent.** `test_owned_d0_seam_fixed_stage_alarm_and_failure_never_succeeds` raises from `_prepared_ids` immediately after entering a fake attempt. It confirms the stage/name/alarm and that this early exception leaves the context as failed, but it never executes assembly, `_write_json`, successful finalization, `d0.json`, `attempt.json`, or the output manifest. It also does not inject a write or finalization failure. Therefore correction item 7's required successful owned-result evidence and “failed write/finalization cannot return success” evidence remain untested.

2. **The retained-route mutation negative does not isolate route order/identity verification.** The reversed event keeps the old event digest, so `_storedroutes` can reject it at event-digest verification before checking problem order/identity. Add a mutation with a recomputed valid event binding but wrong route-problem order/identity, alongside the existing digest-mutation case.

3. **The composed fixture does not demonstrate the promised differing comparisons.** All four seeds have the same outcomes; every challenge problem is SA-only and every routine problem is neither. It does not exercise differing seed effects, both/SM-only outcomes, or an explicitly empty fixed bin with null metrics. It also lacks a literal unknown-family rejection despite that being correction item 5's acceptance evidence. The production code appears capable, but the final-cycle claim requires the actual assertions.

4. **Solved-only/count and paired-delta output remains narrower than the correction record.** `valid_count_distribution` is all-problem only; `solved_only` carries support and U summaries but no solved-only `c/u` distribution or explicit zero accounting. `sa_minus_sm` contains only bag-pass differences, not the other paired aggregate fields (empirical Q, U metrics, duplicate concentration, or prefix sensitivity) implied by the required paired comparison record. These values are reconstructible from mode summaries, but the frozen correction explicitly required them to be emitted.

5. **The handoff is not a truthful final evidence inventory.** It still describes only the earlier two successful rows and reports stale totals (`A 476.5018…`, global `4166.1690…`), omitting the later charged `6.2s` failed, `5.8s` failed and `5.9s` passing runs. It does not enumerate test names/assertions against all seven correction items and still describes only challenge paired-map values even though the code now emits all 32 maps. An exact-version handoff cannot be accepted with stale accounting and coverage claims.

## Scope of blocker

This is an implementation/evidence blocker, not a scientific failure and not evidence about D0's outcome. No model inference, training, new data, threshold change, or framework redesign is needed. If the parent authorizes a bounded respecification, it should cover only: truthful handoff/accounting; the successful-owner and write/finalization-failure seams; a recomputed-digest route-order negative; literal varied/empty-bin/family fixture assertions; and the two missing explicit summary fields. Otherwise stop and report D0 as not executed because implementation acceptance was incomplete.

The `7 passed` result and all preceding failed/passing commands remain charged, but passing test count cannot substitute for the specified assertions. No independent tests or compute were run for this review.
