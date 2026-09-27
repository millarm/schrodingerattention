# Diagnostic implementation correction — bounded revision 1

Astra decision: Sol's six findings in `../reviews/01-implementation.md` are
required, not waived. Core mathematical trace is accepted provisionally; no
full diagnostic run is authorized. Same frozen question, inputs and thresholds.

Terra may change only the new diagnostic module/tests and diagnostic handoff/
ledger records. Do not change original sources, data, checkpoints, reports, or
the scientific plan. Complete all six groups in one handoff with a regression
mapping. Internally implement trace validation, aggregation, and execution
safety sequentially; this is not permission for partial final handoffs.

1. Add explicit disagreement and absolute-loss-change raw fields; maximum
   probability change, margin p95/max, absolute-loss mean/p95/max and signed
   benefit quantiles. Emit local-small and per-condition/op equal-seed benefit
   flags exactly as frozen. Keep test and validation benefit results distinct.
2. Reject all nonfinite numeric metrics; zeros are schema placeholders only,
   with documented head=-1 versus per-head field applicability. Enforce finite
   probabilities/attention, sums and TV bounds at runtime, tolerance 2e-4.
   Assert layer-1 normalized inputs match, and retain API trace-error evidence.
3. Validate retained checkpoint seed/mode/step, state/config/source identities
   against their existing declarations and final artifact. Validate evaluation
   hashes/digests, keys, shapes, domains, labels, operation/label balance and
   counts. Prior overwritten-run provenance is not recoverable: do not invent
   it or silently reinterpret hashes. If an existing declaration is genuinely
   inconsistent, stop and report the exact mismatch to Astra before analysis.
   Include new implementation, tests, specification and review identities.
4. Convert raw lists to arrays once and reuse them across summary masks;
   detach/cache dt/gamma rather than create autograd scalars in row loops.
   Guard the cumulative budget through post-processing, compression and plot.
   A hard elapsed deadline/watchdog or equivalent bounded interruption should
   cover a single expensive stage; reserve alone must not authorize overshoot.
   Partial data/status must be explicit. Add post-processing cap regression.
5. Record exact executable/argv, start/end timestamps, PID, actual runtime
   versions/hardware and lock path. Time starts at entry to the command, with
   conservative startup allowance if interpreter imports cannot be measured.
   Rejected lock/output attempts must not overwrite existing outputs or touch
   an owned lock; log them into separate fresh failure records/atomic ledger
   entries. Preserve failed status if required record writing fails. No stale
   lock clearing without supervisor permission and confirmed process exit.
6. Add focused negative tests for checkpoint/evaluation identity and malformed
   arrays, NaN/TV/sum bounds, failure persistence, exact provenance, cumulative
   and post-processing cap handling, plus existing complete trace fixtures.

Budget: current charge 11.7s (10.2 plus Sol1.5), separate 900s cap. Up to 60s
additional synthetic/read-only selected-batch regression checks permitted.
No full analysis or training. Poll every yielded session until explicit exit.
Handoff includes all six mapped fixes, hashes, actual commands/exits, charge,
and limitations. Freeze code for Sol re-review; Astra authorizes the one full
run only after PASS. Do not add optional sweeps or unrelated refactoring.
