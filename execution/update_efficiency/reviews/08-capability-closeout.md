# Sol runtime capability closeout

**Verdict: BLOCKED at the runtime safety gate. No implementation PASS and no
production authorization.**

Static closeout audit only. I did not import project code, execute tests or
subprocesses, load model/data artifacts, modify source, or write the ledger.

## Exact evidence

- capability report `6434afed05caca0cd1f95996fc2d8f0a4e4cc6c9afbde4001749ee36453b186c`
- read-only lifecycle transcription
  `dcb2a5c50a51ae40542c786ce6962d133cab88b6224cdab91ac7f26740439061`
- study `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- driver `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- tests `5fb793d5794836462d0b145cc0d613ef4c0c3b3f29ac28ec1c30cdd75e2378c6`
- current ledger `ffb377e0aaf76ce0c46f7d015f6d7f54976d9f9bcb84258fd6942e3116c3aaf5`
- immutable owner `attempts/driver-d54acc18-5583-4058-84f2-8b77aa44ff28`

The final authorized suite reached explicit exit 1: 26 tests passed and only the
real descendant-watchdog test failed. The outer pytest child was not timed out,
exited 1, and was cleanup-verified by the driver.

Durable fixture evidence records parent PID/PGID 14118 and child PID 14119 in
that same group, with both readiness records and exact parent-child identity.
The parent then recorded that it reaped child 14119 with return code -15 on its
SIGTERM-handler path and exited zero. This establishes the intended child's
termination and reaping. It does not establish absence of every process in the
group: the unchanged required `killpg(pgid, 0)` probe returned EPERM, and the
defensive group kill also returned EPERM. The accepted cleanup proof therefore
remains unavailable on this host/tool path.

## Scope and scientific qualification

This is a platform/runtime safety capability blocker, not a scientific result.
All other 26 tests—including the scientific estimators, both actual two-update
owner paths, provenance, checkpoint/evaluator composition, and failure/accounting
checks—passed. No fresh production seed trained, no endpoint was observed, and
no final-test payload was released. Those passes do not waive the failed group
cleanup proof.

The exact source authority is unchanged. There is no evidence of a new source
defect, but the evidence also does not justify treating EPERM as group absence.
Review 07b's platform-cause qualification remains controlling.

## Accounting audit

The ledger contains five unique update-efficiency stage-A attempts with charges
4.4263019589707255, 3.347905582981184, 3.0941978748887777,
2.8018142499495298, and 4.395713374949992 seconds, totaling
18.065933041740210/100 seconds. The final owner terminal was written slightly
later and reports 4.396791958017275; the append-only ledger row is the controlling
charged amount and appears once. The qualified global debit is
4782.482380042790/7200 seconds, including the retained historical administrative
uncertainty. Budget remains available but cannot substitute for missing safety
evidence.

## Closeout

The bounded retry path is exhausted. Do not run more tests, do not retry, do not
weaken the assertion, and do not write `08-implementation.md` as PASS. Further
work requires explicit user/root direction for either an execution environment
that permits independently verified process-group cleanup or separate authority
for a reviewed platform-specific safety implementation providing equivalent
cleanup evidence.
