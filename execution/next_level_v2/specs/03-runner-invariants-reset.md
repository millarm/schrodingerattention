# Corrective reset after two failed runner reviews

The prior bounded correction did not achieve its acceptance checklist. Root
cause: passing tests exercised mocks without enforcing returned scientific
invariants, and handoff prose asserted changes absent from implementation.
Do not waive Sol findings or launch production. No scientific plan changes.

Parent bounds recovery to ONE final complete Terra correction covering C1+C2,
then one final Sol re-review. Work sequentially internally, but return only the
whole completed correction with exact added assertions. If recurring findings
remain, stop with implementation blocker and request parent direction on roles;
no model substitution and no unaccepted production launch. No optional features,
source reformat or model work.

## C1: returned-stage invariants and truthful summaries only

Preserve an injected counts argument: use defaults only if counts is None, never
overwrite it. After each returned stratum, runner independently requires exact
total=sum(required_family_maps)*problems_per_map, exact map/family counts,
per-map problem cardinality, no duplicate(start,goal), no cross-split canonical
map, supplied length quotas, M=number of routes, and valid novelty predicate:
routine M_novel==0; challenge M_novel>=4 and .25<=M_novel/M<=.75. Violations
are technical errors (not scientific dataset failure, not permission for B).
Test injected tiny counts actually control observed required counts. Most
importantly test a callback returning M_novel=0 for challenge is REJECTED and
never DATASET_PASS. A success fixture may inject selection, but not fabricate
challenge-valid oracle metrics. Separate real oracle challenge predicate tests
are fine; do not label a routine-only composed fixture complete dataset PASS.

run_rung must persist its own immutable summary for COMPLETE/scientific/technical/
deadline exits with stage completion/reached-failure/NOT_EVALUATED distinctions;
preserve completed artifact paths and original exception. Parent summary must
have execution_status, outcome, selected_rung, every attempted rung, observed
and required gate counts. Test actual run_rung technical/deadline failure after
inventory so its rung summary survives; replacing run_rung cannot prove this.

Finish C1 exact negative and count/status assertions before proceeding to C2;
final handoff gives function/test names and exact hashes for both.

## C2: narrow safety/provenance/cache closure in same final correction

Inject rejection directory (no global test pollution), propagate attempt-log
write failure after exactly-once charge/cleanup (main must not exit0), full
effective N/seed/familycode/splitcount config and spec02/03 hashes, independent
manifest source/output hash assertions, and actual shared-cache identity/reuse
regression. Sol05 details remain binding. Existing deadlines, test allowance and
append-only ledger rules unchanged. No production before final whole-block PASS.
