# Smallest D1 repair block

**PLAN ONLY, 2026-09-20.** No code, tests, inference or ledger changes are
authorized by this document. Astra specifies; Terra implements after approval;
Sol independently reviews. Preserve the failed source/tests/ledger snapshots and
`d1-failure-review.md`. This is a repair of implementation and evidence, not a
negative scientific result or a new experiment.

## Deliverable and unchanged science

Obtain one audited D1 comparison: tuned challenge pass@32 and per-seed SA−SM
differences, challenge/routine Q, U_valid/K and valid-solution coverage, alongside
the reused T1 comparison. Retain every candidate, raw valid/invalid attempt and
actual timing. Four seeds1702–1705, final8k checkpoints, all512 validation
problems, both architectures, T={.5,.75,1,1.25,1.5}, K32, common uniforms,
16 exact reuses plus24 missing endpoints remain fixed. Keep both SM-T1-relative
−.02 Q floors, then max challenge pass@32, higher challenge Q, lower T with
1e−12 ties. No new model, training, seed, data, verifier, test release or D2 run.

## Three small changes, not a replacement framework

1. **Finish the actual input/selection contract.** Read metadata-only IDs from
   manifest-bound COMPLETE owners; never parse prepared.json or call
   `_prepared_ids`/test loaders. Cross-check retained analysis pair/config/final
   checkpoint identities against accepted checkpoint validators. `load_training`
   already hash-checks its payload: retain its identity and a canonical digest
   of its complete signature support, not unrelated ABC matching support.
   Retain one ordered validation panel, exactly12 I-only,12 L-only and8 mixed
   maps×16 problems; freeze RNG construction/digests for reused and new cells.
   Get separate raw SM/SA greedy records from bound final events, not the paired
   summary. Use the accepted pure stored-route verification seam, without its
   prepared-reading event loader, to corroborate raw route validity/order.
   Preserve the historical all-invalid permutation limitation. Bind plan,
   approval/amendment/reviews, source/input/config/support/checkpoint hashes.
2. **Remove output amplification.** Keep all loading/evaluation under the owned
   lock/deadline. Persist each endpoint once to its own immutable file; update
   only a small index of IDs/hashes/status. Store shared provenance, panel and
   greedy records once. Final selections reference cell IDs instead of copying
   entire raw bags. Never serialize the growing collection after every cell.
   This is a plausible cause of the synthetic test delay, not a demonstrated
   diagnosis:40 cumulative writes imply820 cell-equivalent serializations
   rather than40, inferred from source, not measured. Verify through the bounded
   tests below. Keep inference-component
   timings separate from cold/warm whole-endpoint elapsed time.
3. **Replace weak tests with small literal tests.** Use the actual production
   orchestration with injected loaders/evaluator, not injected completed cells.
   Keep the pure production panel validator separate from the orchestration seam
   so a tiny internal fixture can exercise all40 calls/cells without pretending
   to be the production512 panel. A separate metadata-only fixture enforces the
   exact production counts, correcting the current24-I/0-L fixture to12-I/12-L;
   do not weaken the CLI validator. No neural model or
   checkpoint inference is needed in tests.

## Literal acceptance evidence

|Test|Small fixture and required assertions|
|---|---|
|Actual evaluator smoke|Use the accepted evaluator on a few real synthetic grid problems and a deterministic callable returning logits. Its counting wrapper really runs. Verify known forward invocations/batch sizes, sum of actual route lengths, common-uniform digest/routes, and a repeated warm-cache call with fewer forwards but identical results. No mocked counter constants.|
|Owned orchestration|All4 seeds×2 modes×5T with tiny per-cell bags. Inject dependencies below the producer; assert16reuses,24new calls,40retained cells, exact K/split/replicate/support/T/order, separate checkpoint caches, lock active before loading/evaluation, eight separate greedy records, and only one write per endpoint. Guard all prepared/test/training-entrypoint paths.|
|Binding/selection|One bounded real retained-artifact interface read plus small realistic adapter fixtures. Reject hash/seed/checkpoint/config/T mutations and an independently rebound within-map order change whose real valid route fails on the substituted pair. Do not claim all-invalid order detectability. Test both Q floors, no eligible SA, all tie levels, and missing/duplicate cells.|
|Owner failures/math|Distinct injected endpoint-write and final-manifest failures: non-success, explicit error/exit, lock cleanup and one charge. Check exact seedSD/t widths/shared-map bootstrap and accounting stage-table/production cap. Historical unavailable forward counts remain null.|

No large route arrays in the orchestration fixture. Do not copy a512-problem
fixture into every cell merely to test dispatch. Tests must exercise the CLI/run
branch, serializer and actual counter wrapper, not bypass them. Handoff maps
every requirement to literal assertions and exact source/test hashes.

## Small, externally bounded test procedure

After static implementation inspection, run one externally supervised smoke
command (maximum10 charged seconds), then, only if it passes, one focused full
suite (maximum30 charged seconds). The external supervisor must not share the
child's replaceable SIGALRM timer: the current owned runner may reset that timer.
Use a narrow subprocess launcher, not another experiment framework. Before
launch, persist unique command ID, argv/cwd, exact source/test hashes, UTC start
and budget. Capture stdout/stderr, monotonic elapsed, exit/timeout, and UTC end;
terminate and reap the exact child process group on deadline. Parent launch tool
must print the **full** result and retain/poll its session ID to explicit exit.
A yielded call is running, never permission to relaunch. If completion evidence
is unavailable, stop immediately without another command.

One correction batch and one repeat focused suite are allowed within the fresh
allowance below, after inspecting the explicit failure. A prospective per-command
increase from30 to60 s is allowed only after a successful smoke plus measured
progress showing valid bounded work, and Sol's explicit concurrence; no automatic
timeout extension or retry. The user's conditional “up to10×” does not imply a
300-second command,1400-second development cap, or any global expansion. A failed
or unexplained hang is not confidence. At most120 charged development seconds
including all setup/failed commands; stop rather than borrow from production.

## Accounting proposal requiring explicit approval

Do not rewrite the damaged ledger or invent recovered command times. Freeze its
existing hash `770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0`
and acknowledge the two inserted rows and missing terminal evidence. Propose a
dated accounting addendum that qualifies this frozen prefix and appends future
entries strictly at EOF with unique IDs/current timestamps; do not backdate or
add another inherited carry. Validate the prefix hash before the first append.

For operational continuation only, request a **300 s administrative uncertainty
debit** for untraceable earlier D1 work. It is neither measured consumption nor
a proven upper bound and does not restore historical accounting confidence.
Do not also charge the unverified30.2-second reports individually. If later
evidence exceeds this allowance, stop and disclose it; never silently erase it.
The user must explicitly accept this qualified operational basis, or no compute
can resume under the old cap. Prior immutable scientific results remain separate.
Approval authorizes future spending despite unknowable historical usage; the
reserve cannot recover that history or prove the original physical total stayed
below7200 s. It is not a factual accounting reset.

|Prospective item|Stage/source|Maximum/debit seconds|
|---|---|---:|
|Untraceable old D1 administrative allowance|A; disclosed, not measured|300|
|Fresh repair/testing, replaces unusable nominal remainder|A|120|
|One D1 production attempt, unchanged|D|300|
|Independent result/accounting review|Existing D audit envelope|30|

Move unused C300 to A: proposed caps **A1000/B3500/C0/D1400**, global7200
unchanged. Current ledger arithmetic A551.455120997971 plus300+120 gives
A971.455120997971, below1000. Qualified global subtotal would start at
4583.809008752118 (4283.809008752118+300) and be at most5033.809008752118
after the other maxima. These are operational accounting numbers, not verified
historical CPU usage. D2's420 and remaining audit/reserve are not borrowed.
This plan writes no accounting entry and spends none of these allowances.

## Explicit forecast simplification proposed for approval

**Mandatory:** retain available validation rollout/greedy/proper timing cells,
source identities/cardinalities, loading/output elapsed and non-overlapping
component definitions. Extract available evidence rather than return blank
cost dictionaries. Report descriptive selected seed/map intervals with the
already frozen rules. No additional model calls beyond24 to fill missing costs.

**Defer:** building a complete D2 runtime bound if essential cold-cache/bank/
setup/scaling evidence is unavailable. List which cells were extracted, which
are absent, and which extraction/scaling work is deliberately deferred. Report
`D2_FORECAST_DEFERRED/NO_GO`, not a false measured runtime failure. This is an
explicit proposed narrowing of the prior implementation work, requiring approval;
the comparative D1 result remains deliverable. If existing evidence supports a
complete bound cheaply, retain non-overlapping8×2048 scaling and1.5× margin, but
do not make extra forecast engineering a prerequisite for D1. D2 remains sealed
and would need a separate completed forecast plus release authorization.

## Exactly one D1 launch and stop

After approved recovery/resources, completed literal tests, and exact-version
Sol PASS, Astra verifies unused owner/lock, qualified accounting headroom and all
hashes. Launch the frozen CLI once in a new unique owned output directory, with
an external300-second charged envelope and existing inner allowance-aware limit
(at most296 s). Preserve full session/terminal evidence; no automatic retry.
Run the unchanged24missing endpoints; retain partial cells if interrupted and
report partial/inconclusive, never select from an incomplete grid. Independent
Sol audits result identities, all40cells, selection and accounting. Final report
answers the symmetric tuned comparison and stops; D2 requires fresh permission.
