# Independent Sol D1 failure and accounting audit

**Verdict: BLOCKED — do not run D1 production or resume implementation/tests without user-directed accounting and recovery authority.**

Exact static artifacts inspected:

- `execution/difficult_problem_solving/d1.py`: `fd8ccfd255365939341741790bcb2798a4bcdc4b51e7c97c89b937813b08c232`
- `tests/test_difficult_problem_solving_d1.py`: `6b5dc7f4675e444e386be501e75d150618ef713f34d86fd5419b1993936a465f`
- `execution/difficult_problem_solving/d1-handoff.md`: `fcf1a30adb62f0b2eea71de95ecfa8a856560ac617ea89718a21b60f188efd69`
- `execution/difficult_problem_solving/d1-status.md`: `e8720e11f3a7ff2b1cc3088307955240a42cfd2fd3a463726355ed81b8602c15`
- accepted contract: `f36ab859b0eb8f7c5e120605a4963bb5ba8c48428a481345695f3b058efa76ad`
- `execution/difficult_problem_solving/d1-closeout.md`: `eb9ea4a368473db7f65025534d59acd9c8e111ce2640b8dd3c670f0caa87719f`
- current ledger and frozen ledger snapshot: `770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0`

The frozen `d1-blocked-snapshot/d1.py` and `test_d1.py` are byte-identical to
the current source and test. This audit used static reads and hashes only. I ran
no tests, Python imports, model calls, inference, checkpoint loads, training, or
test-data access, and appended no accounting row.

## Confirmed implementation and evidence blockers

1. **There is no exact-version terminal test evidence.** The handoff hashes refer
   to older source/test bytes (`9e46...` and `4caa...`), describes six tests, and
   explicitly says that version was incomplete. The current suite contains seven
   test functions and was modified after that handoff. No durable command record,
   session ID, explicit exit, or exact-version handoff exists for the current
   `fd8...`/`6b5...` pair. A passing count from an older version cannot review the
   frozen current bytes.

2. **Retained support and endpoint identity are incomplete.** The production path
   constructs support directly with `load_training().support`; it does not use or
   verify the contract's accepted hash-bound support artifact. Retained analysis
   checkpoint/config identities are not cross-checked against the freshly
   validated checkpoint records. Reused cells set RNG digest to null and do not
   freeze the required config/support/RNG hashes. These omissions prevent the
   selected grid from carrying the complete frozen identity record.

3. **Retained greedy/order evidence is not the specified evidence.** The reader
   takes `stored_fullvalidation["8000"]["greedy"]`, which is the paired greedy
   summary produced by replication analysis, and attaches that same object to
   both model cells; it does not persist each model's bound raw greedy records.
   Retained K32 order checking compares only map ID and family. It never routes
   the bound events through the accepted stored-route verifier to corroborate the
   exact ordered validation rows and route validity. The real-interface test only
   mutates an event hash; it has no literal seed, temperature, or independently
   rebound order mutation required by the contract.

4. **The D2 forecast is deliberately unfinished.** `forecast_costs` returns every
   essential cost as null and therefore always produces
   `UNSUPPORTED_NO_GO`; it does not bind/extract the available proper/greedy
   measurements or scale explicit validation operations to eight 2048-problem
   endpoints. Reporting an honest unsupported forecast is safer than inventing
   zeros, but it does not satisfy the implementation contract's required bounded
   forecast work. The code also labels full endpoint elapsed time as cold or
   incremental cache time rather than separately retaining inference and
   end-to-end fields.

5. **Several literal acceptance claims are not actually exercised.** The first
   test checks fixture metadata but does not call the production seam or prove
   evaluator forwarding. The count test sums constants already placed in fixture
   rows; it does not exercise `CountingModel`, known forward/batch counts, cache-
   dependent call changes, or common-uniform route invariance. The injected
   evaluator never invokes the model and does not assert K/split/replicate/support
   arguments. It checks eight cache object IDs but not the required route identity.
   The owned failure test injects an output write failure but not a distinct output-
   manifest/finalization failure. Forbidden prepared/test paths are not all
   guarded literally. The validation panel check counts eight challenge maps but
   does not enforce the exact 12 I-only plus 12 L-only routine-family composition.

6. **Required provenance is narrower than the contract.** The owner payload
   records plan/spec/analysis/code/stage/argv but omits the approved amendment,
   approval, independent contract-review, support, complete candidate/RNG, and
   retained source identities required to freeze D1 before any later release.

These are implementation/evidence defects, not scientific findings. No selected
temperature, D2 forecast, or validation comparison is available for interpretation.

## Confirmed accounting and chronology defect

The earlier independent D0 audit records a 141-row ledger in which the D0 owner
and audit allowance were already present and unique. The current ledger has 143
rows. D1 rows `d1-test-failed-20260920-01/02`, carrying claimed 11:10/11:11 UTC
timestamps and charges `0.983552166` and `0.592375875` seconds, now occupy rows
140--141 before the previously audited D0 production and audit rows at 142--143.
They were therefore inserted into history rather than appended after the D1 work.
That violates the authoritative append-only chronology. Preserve the current
ledger and its hash; do not delete, reorder, or silently “repair” it.

The two inserted values sum to `1.575928041` seconds. Including them gives the
current ledger arithmetic subtotal reported by the closeout,
`4283.809008752118/7200`, but this is not a complete verified D1 debit. The current
and earlier implementation attempts, older reported passes, and latest yielded
calls lack a complete durable charge inventory.

## Reported but unverified process facts

The following are agent reports, not terminal accounting evidence:

- an earlier six-test pass with tool wall 2.3 seconds and another reported pass
  around 2.16 seconds;
- one suite call said to yield after 30.2 seconds with six dots;
- a purported second single-test call said to yield after 30.2 seconds with no
  output, followed by the inconsistent statement that no rerun occurred;
- an attempted wait against an unavailable execution-cell ID.

There are no retrievable session IDs or explicit exits for the two 30.2-second
reports. They may be distinct commands, duplicate descriptions, or waits on one
process. I therefore neither add them together nor treat either as a measured
charge. Astra's later read-only process check found no matching pytest process;
that establishes only that none was visible then, not the identity, duration, or
exit of the earlier work.

The nominal `55.346696919` seconds remaining after only the two inserted rows is
not safely spendable because unrecorded development work has no verified finite
upper bound. Reserving it is an operational stop, not a debit and not proof that
the 140-second development ceiling was physically exhausted. No precise final
global or stage-A balance can presently be claimed.

## Scope and prior-result validity

No `difficult-d1-001` owner or shared lock exists, and no D1 production run is
evidenced. D2, final-test release, training, and new samples remain unauthorized.
The ledger provenance defect does not by itself alter the immutable, manifest-
bound D0 result bytes or the prior independent scientific reconstruction. D0's
artifact validity and the ledger's damaged append chronology are separate facts.

## Required user-directed recovery decision

Do not continue automatically. The user must choose whether to stop D1 or approve
a new bounded recovery. Any recovery authorization must prospectively define:

1. how the corrupted ledger is preserved and superseded or qualified without
   rewriting it, including the conservative treatment of untraceable command time;
2. a fresh, explicit development allowance and its source, rather than assuming
   the nominal remainder or borrowing from D1 production, D2, or audit reserves;
3. the unchanged Terra implementer/Sol reviewer roles, unless the user explicitly
   changes them;
4. a bounded correction list limited to the six implementation/evidence groups
   above, followed by one exact-version handoff and independent static review;
5. durable command IDs, start/end/exit evidence, and append-at-EOF accounting for
   every future attempt before any production authorization.

No budget increase, role substitution, production retry, or D2 authority is
implied by this review.
