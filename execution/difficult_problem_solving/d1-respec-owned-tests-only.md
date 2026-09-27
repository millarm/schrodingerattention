# Next bounded block: tiny owned-producer and failure tests

Static test implementation plus one explicit reader seam,2026-09-20. Precondition:
independent narrow smoke-test static PASS. Preserve that smoke function unchanged.
No execution, imports, watchdog changes, ledger mutation or production authority.
Terra edits the existing producer/owner tests and their local fixtures in
`tests/test_difficult_problem_solving_d1.py`, plus only the source seam below.
This is not the full
repair; binding/selection and watchdog/source corrections remain separate.

## One reusable tiny fixture

Use ten complete accepted Problem records: eight distinct mixed map IDs, one
I-family and one L-family, each on a valid144-byte empty map with adjacent0→1,
length1,M1,MnovelNone. This is an internal dispatch fixture, not a scientifically
valid production obstacle dataset. Ten problems allow real eight-map contrast
math without512×32 bags. Retain K32 and all four seeds/two models/fiveT.

Inject loaders/pair payloads/events/model/evaluator below `produce_cells` using
its existing dependency seam. Synthetic pair metadata must match exact current
return schemas. Use separate deterministic stub identities for each seed/model,
not real checkpoints. Retained K32/greedy bags use the same valid one-action
routes, hex-encoded where the retained adapter expects strings; event digests and
bindings must be internally consistent. Use actual bound greedy verification.
The evaluator dependency is a recording wrapper around the accepted evaluator
and the deterministic stub, not a precomputed-result return. Record every call.

Production panel/grid validators must stay unchanged. For this test only,
inject/monkeypatch a small-panel validator which checks these exact ten IDs,
order, all40unique grid keys and16/24 reuse partition. It may replace the
hardcoded512 length check in the test process; it must not blindly return True.
Keep a separate metadata-only test asserting the real production validator
accepts exact12I/12L/8mixed×16 and rejects wrong family counts. Never monkeypatch
`run`, `produce_cells`, `CellSink`, owned accounting or persistence to fake success.

**Necessary source seam identified before implementation:** `load_indexed_cells`
also has a direct512-panel guard which bypasses the injected validator. Add one
keyword-only `expected_problem_count=512` to that reader and substitute it for
that literal count, retaining every index/hash/grid/greedy check. In `run`, pass
the default512 unless its existing Python-only injected `deps` explicitly
contains a fixture `expected_problem_count`; the fixture passes10. This option
must not appear in the CLI, production decision, configuration, or ordinary
defaults. The real loader and CLI still enforce512/12I/12L/8mixed. Tests must
assert reader default remains512 and a10-row indexed panel fails without the
explicit fixture override. No other source correction is authorized by this
block; report any further dependency before editing. This narrow seam avoids
mocking the real reader or serializing40full512-row bags to test orchestration.

## Success: reachable run/owner branch

Use a temporary initialized ledger and an unused temporary owner. Inject only
the already separate production-decision validator/runtime setup as synthetic
authorization boundaries; exact real decision schemas are tested in the later
source/watchdog closure. Call actual `run` with no ready-made `cells` argument.

**Named clarification (already authorized test boundaries):** in the test process
only, `monkeypatch.setattr` may replace `d1.require_production_decision` with a
fixture authorization result, `d1.core.configure_runtime` with a no-op, and
`d1.validate_cells` with the strict tiny-panel checker. Both `compose` and the
indexed reader resolve that checker at runtime, so neither needs a new source
seam. Keep `d1.compose`, `d1.run`, `d1.produce_cells`, the actual OwnedAttempt,
CellSink and file persistence unpatched except recording/failure wrappers that
call the original writer unless injecting the specified error. Source and
watchdog now remain unchanged. Compare ordered IDs after a lossless normalization
such as `tuple(tuple(row) for row in ids)` on BOTH actual and expected values:
JSON converts tuples to lists. Do not omit identity fields or sort away order.
Before every loader, pair/event/model construction and evaluator callback assert
the owner's lock exists. Reset pristine stage table between isolated cases.

Assert the complete recorded call sequence: seed1702→1705; SM-first1702/1704,
SA-first1703/1705; missing SM T=.5,.75,1.25,1.5 and SA T=.5,1.5. Every call has
K32, split1, replicate0, correct seed/checkpoint/support/problem order. Retain
the actual cache objects and assert identity reuse within each seed/model and
eight distinct objects across seed/models (not recycled integer IDs).
Record architecture and evaluator `identity` explicitly; use distinct stub
payload/checkpoint identifiers per seed AND model. Compare the entire expected
24-call list literally, including support and checkpoint identity, not merely
its length and common K fields. The recorded model stub must expose the correct
mode for each model. Assert cache object equality within each seed/model and
inequality across those eight groups.

Count actual endpoint writes through a recording wrapper that still calls the
real atomic writer. Assert exactly40unique endpoint writes,16reused/24new,
eight distinct raw greedy files, no cumulative partial-cells write, a complete
compact index with matching hashes, and a final report. Shared raw bags must
round-trip through actual JSON bytes serialization. No fullbag duplication in
selected output is accepted as evidence of source closure; flag any such known
source defect separately rather than changing this test to hide it.

Guard `_prepared_ids`, prepared-payload readers, final-test loader and training
entrypoints with functions that raise if invoked. Accepted `load_training` is
replaced by the fixture loader, not called against actual files. Neither actual
model construction nor checkpoint loading is permitted.

## Two distinct real failure paths

Reuse the same fixture with separate fresh temporary roots:

1. Raise OSError only when writing a chosen endpoint file (e.g. second cell).
   Assert actual run raises/non-success, one owned ledger charge, lock removal,
   no COMPLETE report/index, first immutable endpoint retained and partial index
   rejected by the real indexed-reader completion guard.
2. Allow every endpoint/report write, then raise only at final
   `output-manifest.json` through the accepted owner's finalization seam.
   Assert actual run raises/non-success, one owned charge (not a duplicate), lock
   removal, failed terminal attempt/finalization evidence. A report written
   before finalization is provisional and must not be mistaken for an accepted
   COMPLETE owner. Inspect accepted OwnedAttempt behavior; assert its real
   documented failure artifact/status, not an invented filename.

No child subprocess is needed here; watchdog descendant/deadline tests belong
to the separate watchdog block. No timers are allowed to execute in this static
turn. When eventually run under the approved external watchdog, all temporary
owner charges are test fixtures; the real watchdog charges this test process once.

## Handoff

Return `d1-owned-tests-only-handoff.md` with exact test hash, changed functions,
assertion locations and any concrete source-interface dependency. No test has
run, no full repair is claimed. If source shape prevents one assertion, state
the exact necessary interface correction instead of bypassing the owner/producer
or fabricating counters. Independent narrow static inspection precedes next block;
full static safety PASS still precedes all runtime commands.
