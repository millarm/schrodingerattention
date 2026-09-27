# D1 closeout — BLOCKED before production

2026-09-20. User authorized D1 and the resource-only amendment. Scientific
contract passed Sol review, but implementation has **not** passed independent
review. No D1 production model evaluations, tuned results, training, or final-test
access are evidenced or claimed. D0 remains the previously audited result.
All implementation and compute are stopped pending independent failure audit
and user direction; no automatic retry or role change is authorized.

## Frozen current artifacts

Byte-identical additive preservation is in `d1-blocked-snapshot/`:

|Artifact|SHA-256|
|---|---|
|d1.py|fd8ccfd255365939341741790bcb2798a4bcdc4b51e7c97c89b937813b08c232|
|tests/test_difficult_problem_solving_d1.py|6b5dc7f4675e444e386be501e75d150618ef713f34d86fd5419b1993936a465f|
|authoritative ledger snapshot|770d3490766d0ec2e40a796ee8f896b4f1fbc3e7647c00d145cf4010dfc7d7c0|

`d1-handoff.md` is an earlier incomplete handoff, not exact-version acceptance.
Current source includes an owned production branch and an added synthetic
production-path test, but that test has no retained explicit successful exit.
Forecast extraction deliberately labels available timings raw D1 evidence and
unavailable D2 cost bounds unsupported; no D2 runtime estimate or permission
follows. Remaining compliance is for static Sol audit, not assumed from earlier
six-test partial runs. Accepted scientific modules and old results are unchanged.

## Test/process evidence and limitations

The fresh Terra reported earlier failed interpreter/fixture attempts, a six-test
pass with tool wall 2.3 s, and another six-test pass reported as 2.16 s. Their full
command responses and complete individual charges were not supplied to Astra or
durably appended to the authoritative ledger. Those reports are not substitutes
for verified terminal records.

For the added production-path regression, Terra reported a focused suite yielding
after 30.2 s with stdout `......`, then a **second single-test exec** yielding after
30.2 s with empty stdout, without retrievable session IDs. It also subsequently
stated “No rerun was performed.” This inconsistency is unresolved. We cannot
establish whether these were distinct commands or misunderstood waits, cannot
infer exit codes, and do not sum the two values as measured unique compute.
The reported wait on an internal ID failed with `exec cell ... not found`.

Astra's targeted process inspection was first sandbox-denied; a permitted
escalated read-only `ps -axo pid,ppid,etime,command` filtered for this test/pytest
then exited 0 and showed only its own shell/rg, **no pytest process**. This proves
no matching process was visible at that inspection, not that either test passed
or that earlier processes did not overlap. No kill or relaunch was performed.

## Accounting defect — preserve, do not repair history

The accepted pre-D1 global debit was 4282.233080711118 s, development
83.077375040/140 s. Two old-Terra reported failures, 0.983552166 and 0.592375875 s,
now appear as `d1-test-failed-20260920-01/02` **inserted before** the accepted D0
production/audit rows, with 11:10/11:11 timestamps preceding D0 production. They
were absent in earlier read-only snapshots during this D1 turn. This violates
append-only true chronology. Their sum is 1.575928041 s; the present ledger's
arithmetic global subtotal is 4283.809008752118 s, but it is **not** a verified
complete D1 total. No earlier rows were repaired or deleted during closeout.

Fresh-Terra tests are missing from that ledger. The 55.346696919 s nominal
development remainder after the two inserted entries is therefore not available
to spend: conservatively reserve it all pending reconciliation. This operational
reservation is not a measured charge or proof of physical cap exhaustion. If
the two reported 30.2 s calls were distinct, they alone would exceed that
remainder; without full terminal evidence that cannot be asserted as measured.
There is no verified finite upper bound for missing command durations. Do not
claim a precise final global balance or silently fund recovery from D1/D2/audit
reserves. Further compute requires user direction after the accounting audit.

## Next authority boundary

Root has requested static independent Sol failure/accounting review in
`d1-failure-review.md`, with no tests/imports/inference. It should distinguish
implementation completeness, test/process traceability, and budget/chronology
defects from scientific results. No temperature-control finding exists yet.
Any renewed implementation/compute must have an explicit bounded recovery and
resource decision; D2 and final-test release remain unauthorized regardless.
