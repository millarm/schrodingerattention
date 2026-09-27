# Narrow runner respecification after two correction cycles

Sol14 verifies the other safeguards but three direct requirements remain. The
cause is incomplete assertion-to-behavior matching: a truthy future list was
treated as truthful status, and a fixed provenance list/test existence checks
were treated as complete binding. No new science, core-data edit, pool generation
or resource increase. Terra changes runner/tests only; one complete handoff then
Sol definitive review. Do not reopen already verified runner behavior.

## 1. Truthful exact statuses

Replace the hardcoded all-stage future list. Track callback proposal/name/outcome,
artifact/hash and actual write failures. Each attempted proposal has the frozen
five-stage status map. Successful callbacks mean COMPLETE only for actual OK
results; scientific-failure callbacks retain their failure outcome and explicit
future NOT_EVALUATED callbacks remain unvisited, not completed computations.
On full PASS all five selected-proposal stages are COMPLETE and future list is
empty. A stage artifact write fault marks that stage FAILED and later stages
NOT_EVALUATED. A deadline between completed callbacks leaves the first missing
stage NOT_COMPLETED/UNKNOWN (do not invent whether it started); later stages
NOT_EVALUATED, with the actual pipeline error/phase retained. Completed-only
callbacks cannot establish a more precise start time. Unattempted ranked
proposals may be listed separately, never as scientific failures.

Assert exact success status values and exact post-real-training-callback failure
values, not mere list truthiness. No stage may simultaneously be COMPLETE and
NOT_EVALUATED. Retain existing completed artifact hashes/profile/q evidence.

## 2. Complete runtime provenance inventory

Hash mandatory runner/data/route helper, both v3 test files, v3 plan and agent
protocol, plus a deterministic sorted inventory of every v3 specs/*.md and
reviews/*.md present at invocation. Fixed required files missing must raise,
not silently disappear. Runtime discovery includes the eventual accepted review
without another source edit. Preserve fixture input hashes in test manifests.
The real success integration asserts the exact expected path set and recomputes
each byte hash, not only currently returned dictionary entries. Existing output
hash/manifest/attempt bindings remain required and unchanged.

## 3. Two primary write-fault cases

One parameterized integration injects an exclusive-write failure at a real
proposal-stage artifact and at result.json. Exercise the real eight-map pipeline
with fault injection only at writing. Both raise, produce FAILED attempt and one
ledger charge, release only the owned lock, preserve the original write error,
and retain truthful partial manifest/summary. Assert the failed artifact absent,
all completed output hashes exact, stage statuses truthful, and future statuses
as in item1. A result write failure follows completed scientific stages: preserve
them COMPLETE, but mark pipeline persistence FAILED—never label the invocation
successful. Do not alter already verified manifest/summary chained-error tests.

Run the focused runner suite once after all three closures (<=60s), capture full
result, append actual charge once at true EOF. Handoff03a gives literal assertion
locations, source/test hashes and actual limitations. If any exact closure remains
unimplemented, report that concrete blocker; no new open-ended microcycle.
