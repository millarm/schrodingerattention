# Minimal configuration extension contract

Read productive_diversity_v3_pool512_plan.md and accepted original runner/data.
Terra owns only new implementation/tests under pool512 names. No edits to old
source/tests/plan/protocol/ledger/artifacts. Sol reviews this contract before code.

Implement a small additive module schrodinger/productive_diversity_v3_pool512.py:
reuse original Attempt, ProposalStatuses, strictJSON/hash/write/PASS-validator and
data functions unchanged by import. Because original execute_pipeline hardcodes
the256 manifest, a narrow copy of that orchestration function is allowed with
literal512 default pool generation and truthful manifest/source provenance. Do
not clone/rewrite safety or scientific algorithms. No monkeypatching module
globals or rewriting a manifest after the old pipeline wrote it.

Default pool callable invokes accepted data.pool_family(family,n=12,limit=512,
max_trials=200000). Preserve dependency-injection seams for tiny fixture tests;
production CLI only --output PATH. Every production effective_config.pool.limit
must be512. New _source_hashes extends old immutable provenance with newmodule,
newtest,amendment,allnew specs/reviews,prior original manifest and ledger hashes.
Eventual accepted review is discovered at invocation without source changes.

Use old Attempt with explicit new ledger/lock/rejections paths. Require valid
single carry via old _prior(require_carry=True) on new production ledger. Seed
newledger with exactly one global443.384519002 carry plus301.747054625 inherited
stage budget allowance, totaling745.131573627. Label inherited stage debit as
carry, not newly measured time; do not also carry745 globally. Bind source old
ledger SHA c2812c96c8a3e457cdc68403c3e498bd296b199a7ceefc9149273b44e6133563.
The inherited allowance representation deliberately reuses old safe budget parser;
new actual charges append only to new ledger. Runtime original constants remain
1600/7200/120audit/30finalization/2startup.

Focused finishable acceptance checklist:

1. Small deterministic pool-prefix test, e.g.limit2 then4 per family, checks
   same draw prefix where available and canonical subset. Also stub default
   generator call to assert exact512/n12/200000 arguments. Do not regenerate
   full production pools in tests.
2. Genuine existing eight-map fixture through new pipeline internal count/rank
   seam reaches PASS, preserves artifacts/status semantics; manifest says512
   and exact expanded provenance pathset/hash, while old input bytes unchanged.
3. Newledger parsing yields priorstage301.747054625/global745.131573627 and exact
   predevelopment deadline1146.252945375s. Missing/duplicate carry rejected.
   Paths are new and no old ledger writes. Normal/scientificstop and injected
   interruption preserve the already-reviewed helper behavior.
4. Compact CLI and original lock/exclusive safety are reused, not reimplemented.
   Full focused test command/result, actual wall time and hashes in one handoff.

Target<=30s new development commands, each<=60s; preserve all attempts, never
repeat on yielded session. Two review corrections maximum then concrete blocker
or bounded respec, no broad framework. After exact PASS Astra launches once;
Sol audits results before final dataset-only report.
