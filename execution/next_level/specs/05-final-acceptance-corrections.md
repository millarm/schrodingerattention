# Re-scoped final Stage0 correction after two implementation review cycles

Astra records the residual cause: the primary scientific pipeline now matches
the contract, but failure-path record states and several promised acceptance
tests were omitted. Generic happy-path tests were repeatedly mistaken for
coverage of explicit criteria. This narrower specification is required by the
protocol's revision limit; it does not waive review or change the experiment.

No full inventory or model work. Preserve current scientific implementation.
Terra must complete exactly these three groups and then freeze for Sol:

1. **Two record-state bugs.** Any __enter__ failure after output ownership,
   including an exhausted timer, writes attempt.json and exactly one charged
   ledger record with status failed and execution_status FAILED, then always
   cleans owned lock/FD/timer. If required attempt.json writing fails, the
   fallback ledger is also failed/FAILED, never COMPLETE. No writes to unowned
   output and no duplicate charge on rejection paths. Add injected entry-timer
   failure and log-write failure tests asserting actual record fields/charge
   plus lock/FD/handler cleanup; do not merely assert an exception occurs.
2. **Traceability.** Manifest hashes all new Stage0 specs and review records,
   plus source/tests/plan. At finalization the attempt records the exact
   manifest hash and output-hash table (excluding self to avoid circularity).
   Early entry failures explicitly have NOT_EVALUATED manifests. Test membership
   and binding using actual generated files, not a handoff assertion.
3. **Missing literal acceptance fixtures.** Add nonuniform training fractions
   with exact expected Hamilton quotas; a cross-family split flow that succeeds
   but separate per-family quotas cannot; exact novelty-gate cases255/256 and
   15/16 qualifying maps; actual BIN_MATCH_INFEASIBLE schema with retained
   selection/evidence and later NOT_EVALUATED; O_EXCL lock-race owner preservation;
   charged output-mkdir rejection; cumulative exhausted budget before body.
   All fixtures are tiny/injected, not full6x6 inventory. These assertions must
   execute real helpers/pipeline/Attempt paths, not fabricated dictionaries.

Permitted <=20s additional tests; retain every attempt charge and add2s allowance
for the prior corrected CLI fixture command (~1.374s) if not already accounted.
No old artifact modifications. Full tool result retained, subprocess/session
explicit exit before dependent work. Handoff maps each bullet to test names,
current hashes and whole-command exits. All three groups must be complete;
then Sol reviews only residual closure and regression impact.
