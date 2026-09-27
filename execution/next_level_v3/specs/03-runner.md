# Block3 — one bounded immutable v3 dataset invocation

Only after accepted Blocks1+2. Terra owns new v3 runner/test files; older code
and behavior untouched. Reuse reviewed v2 safety behavior without mutating its
global constants/default dimensions/ledger. No new scientific selection logic.

CLI only --output PATH. Fixed default pipeline: all3 family pools/global inventory
→ all12 raw proposals ranked/saved → at most3 retained distinct-window proposal
attempts in order → first complete PASS or prescribed construction stop. Support,
selected data and failed prefixes remain proposal-specific; no new pools or
rankings on failure. Model/pilot/training code is out of scope.

Read the new ledger's single carried_budget_debit_seconds443.384519002 plus
subsequent actual charges/explicit allowances for global budget. Stage1600s
counts only new v3 dataset/test/audit charges, not historical carry-forward.
Global7200s cap remains. Derive interrupting deadline as minimum remaining stage
and global amount minus startup2s/finalization reserve30s; test override can only
tighten. Prospective budget amendments require recorded Sol-reviewed decision,
not CLI switches or live timer extension.

One owned O_EXCL lock, fail-if-output-exists, immutable exclusive artifact writes.
Rejections use explicit local rejection path, never old global paths. All exits,
including post-lock output race, deadline and mandatory-log/write failures,
charge once with UUID and real UTC chronology, release only owned lock, restore
signal/timer, propagate technical failures/nonzero. No successful CLI exit with
missing required attempt log. Print/store full execution result and poll yielded
session until explicit exit; no concurrent compute or relaunch.

Persist pool/inventory and ranked proposal artifacts before support evaluation.
Use completed-stage callbacks from Block2 for proposal training support/q and
each held-out stratum. On failure save truthful completed/failed/NOT_EVALUATED
stages, examined-prefix evidence and original error; do not write a generic
empty report that loses successful earlier work. Save selected16/map rows,
profile calls/routes/cache hits and elapsed time, strict JSON (nonstring dict
keys explicitly represented), sorted length-prefixed support and its hash.

Manifest binds full effective config including n12/families/shape counts/seeds/
pool/shortlist/ranking/windows/quotas/splitcounts/support semantics/budgets, Python/
numpy/runtime/thread/argv/executable, all imported source/helpers/tests, frozen
plans/contracts/reviews and output hashes. Attempt binds manifest; avoid circular
hashing and never overwrite previous attempt/proposal artifacts. Budget carry
is explicitly not newly measured time and includes historical150s allowance.

Acceptance tests: real small internal composed pipeline including genuine oracle
routine/challenge output (reuse Block2 fixture, not mocked whole PASS); first
passing proposal stops; no raw proposal and allscientificfail preserve distinct
outcomes; technical/deadline never advance; actual partial artifact+stage summary
survives interrupt; count/quota/family/identity/M/novelty defects cannot fabricate
PASS; exact hash/config assertions; cache reuse/profile; output/lock race and
rejection isolation; mandatory attempt-log failure raises/nonzero and charges
once; oldsource/ledgers unchanged; carried and stage budget arithmetic verified.

Focused tests within remaining180s development allowance, <=60s/command, no
production generation. Handoff03-runner.md exact hashes, assertion map, commands/
full results and charges. Sol current-version PASS then Astra acceptance required
before one production run. Outcome audit precedes any later model implementation.

## Concrete integration notes after Block2 recovery

Use accepted v3 data functions, not the old v2 scientific pipeline. Preserve v2
files verbatim. Reuse/copy its reviewed exclusive-write, JSON encoding, attempt
lock/log/finalization patterns with explicit v3 defaults; never monkeypatch old
module globals. Global prior includes the single carried-budget field plus new
charges; stage prior excludes that carried field. Historical misplaced ledger
rows remain valid unique charges; do not assume physical chronological sorting
for summation. Reject duplicate entry IDs rather than silently double-charge.

Write each completed family pool immediately, then full assembled inventory,
then full proposal ranking. Call accepted run_ranked_proposals with production
training count32 and its default held-out counts. Its callbacks identify proposal
IDs and completed/unvisited stages. Save one exclusive artifact per proposal and
stage, including all selected rows, failed prefixes, q/support and profiles.
Training results contain an internal `cache` object: deliberately omit that
object only, retain its profile and every scientific field. Nonstring q keys
must use explicit key/value JSON records. Do not stringify arbitrary objects.
Optional support.bin stores the exact sorted length-prefixed bytes and hash.

Keep final summary compact (outcome, selected proposal, stages/counts, file
references); raw stage files retain complete evidence. On exceptions, discover
completed stage files and persist truthful partial summary/manifest before
propagating nonzero. Summary must distinguish completed scientific construction
stop from technical/deadline failure. No models are in this request even on PASS.

The genuine eight-record test loader may be reused for an internal injected
inventory/ranking/count seam; production CLI remains --output only. Runner
success tests must pass that real fixture through its actual callback writing,
summary, manifest and attempt recording, not mock the whole dataset result.

Clarification after Sol12: “full execution result” means the external command
tool result including session ID/exit status must be retained in full. Do not
dump potentially huge q/support data to terminal. CLI normal completion prints
a compact strict-JSON outcome/output-path/manifest-hash summary, while complete
scientific results remain immutable on disk. Failure remains nonzero with the
original error and partial evidence retained.

Before production, earmark120s of the existing1600s dataset-stage allocation
for independent results audit, separate from30s failure finalization. Production
interrupt deadline is min(stage remaining, global remaining) minus startup2s,
finalization30s and audit120s. Preserve the actual prior stage/global debits;
no resource increase or live deadline extension. Include these named reserves
in effective config and exact deadline tests. Sol runner review verifies this
prospective resource-only allocation. Timeout means unreached scientific gates
remain NOT_EVALUATED, never a construction-infeasibility claim.
