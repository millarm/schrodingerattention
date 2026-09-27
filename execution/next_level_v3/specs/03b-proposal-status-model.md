# Authorized bounded status-model redesign

Parent explicitly authorizes this single bounded redesign under the user's
resumed same-role dataset request. Astra specifies, Terra implements only runner/
helper tests, Sol independently reviews. Accepted data logic stays unchanged.
Original Sol15/blocker history remains. Existing resource limits apply. No
production before PASS. If this redesign fails substantive review, report the
blocker rather than continuing local patches.

## Replace, do not patch, global status mutation

Create one small proposal-keyed transition/derivation helper consuming actual
accepted Block2 callback payloads, artifact filenames and exact hashes. Keep the
ordered retained proposal IDs as context. A proposal owns its own five-stage map;
later proposals cannot overwrite earlier records. Stage order is training,
validation_routine, validation_mixed, test_routine, test_mixed.

Decode exactly these payload forms:

- training: payload.result.outcome;
- held-out: payload.results entries each have family and result.outcome;
- explicit future callback: payload.outcome == NOT_EVALUATED.

Only actual OK outcomes become COMPLETE. Preserve exact declared scientific
failure strings, plus the family-level results. Explicit NOT_EVALUATED remains
NOT_EVALUATED even though its evidence file was successfully written. Unknown
payload/outcome is technical, not COMPLETE. Link each persisted stage artifact
and hash to that proposal/stage. Track an actual failed stage write separately
as FAILED without pretending its artifact exists.

Never blanket-overwrite states because execute_pipeline returns. Overall normal
scientific construction failure is a completed invocation, not five completed
scientific stages. Full PASS has five COMPLETE stages for the selected proposal;
failed prior proposals retain their failure/future records.

On a selection interruption, preserve completed callbacks exactly. For the
active incomplete proposal, first missing callback is NOT_COMPLETED_UNKNOWN;
later missing stages are NOT_EVALUATED. This explicitly avoids claiming whether
the first missing stage started. If the last observed proposal is fully resolved
as a scientific failure and a later retained proposal is next, that next proposal
may be the unknown interrupted proposal; do not corrupt the finished earlier map.
If scientific stages completed and result persistence fails, keep those stages
COMPLETE and mark invocation/persistence FAILED, as already verified.

## Tests first: three literal integrations

Write these assertions before replacing the status model; they must fail on
the currently reviewed model, then pass after implementation. No whole-result
mocking and no changes to accepted data functions.

1. Real one-proposal scientific held-out failure: use genuine eight-record
   fixture, train1/family, val_routine3/family (only two remain), other tiny
   counts1. Require exact training COMPLETE, validation_routine
   SCIENTIFIC_HELDOUT_SUPPLY_FAILED with I evidence and L NOT_EVALUATED, later
   three stages NOT_EVALUATED. Invocation completes scientific construction
   failure; no fabricated full PASS.
2. Real first-proposal failure then second PASS: internal retained ranking first
   window(14,15,16), then(12,13,14), quota1 and tiny counts1. Fixture has no15/16
   pairs, so first training supply fails; second genuinely succeeds. Preserve
   two distinct proposal maps, exact first scientific failure/futures, second
   all COMPLETE and no future stages. This intentionally injected ranking is
   software evidence, not a claim of real production raw rank feasibility.
3. Real training callback then between-callback interruption: wrap only the
   callback of actual run_ranked_proposals, persist the real training callback,
   then raise Deadline immediately before any next callback. Require training
   COMPLETE, validation_routine NOT_COMPLETED_UNKNOWN and only later stages
   NOT_EVALUATED. Verify training artifact/hash/profile, FAILED attempt, one
   charge and lock cleanup. Do not substitute a write fault during the next
   stage; that is a different already verified case.

## Provenance evidence closure

In real success integration assert the exact expected mandatory input path set:
runner/data/helper, both tests, v3 plan/protocol, every sorted current v3 spec and
review (including eventual accepted review via runtime discovery), and three
fixture JSON inputs. Recompute each exact byte hash; missing mandatory fixed
input fails. Preserve existing manifest/output/attempt hash assertions. No
optional extra provenance framework or scientific input changes.

## Complete handoff and definitive gate

Keep existing28 runner tests and accepted data tests. One tests-first failing
run and one corrected focused run are expected; each<=60s, all actual attempts
charged once at true ledger EOF within180s development allowance. Handoff03b
must map the three real cases and exact provenance assertions to actual test
locations, identify helper semantics/source/test hashes and all failures/charges.
No partial handoff or claims based only on test count. Sol reviews this complete
bounded redesign; no unreviewed production run and no automatic patch loop if
substantively blocked again. Dataset/result audit remains the sole final scope.
