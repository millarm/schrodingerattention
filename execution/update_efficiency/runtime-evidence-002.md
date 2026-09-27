# Repeated suite and process-group capability evidence

The corrected tests are `a1d879c7…`; study and driver are unchanged.

- `suite-decision-002.json`: tool session3238 polled to explicit exit1.
  Owner `attempts/driver-b775f472-8548-4e22-835b-09fc169e6cab` reports
  26 passed, one failed in1.69s. Sole failure: real descendant watchdog receives
  EPERM from `os.killpg(pgid,0)` and defensive SIGKILL. Outer pytest cleanup
  verified, not timed out. One stage-A charge3.0941978748887777s.
- Sol `reviews/07a-sandbox-permission.md` concurred with one unchanged
  permission-escalated 30-second retry, not a waived cleanup assertion.
- `suite-decision-003.json`: launched using `require_escalated`; session40757
  polled to explicit exit1. Owner `attempts/driver-edcc623d-cb6e-406a-87cb-912a80dd1d96`
  reports26 passed, one failed in1.45s, the same EPERM boundary. Outer pytest
  cleanup verified, not timed out. One stage-A charge2.8018142499495298s.

Escalation did not resolve the failure. Therefore a sandbox-only explanation is
not established; the host process-group/descendant lifecycle boundary remains
unverified. No further retry or production launch is authorized by this record.
Independent static diagnosis is pending; no weakening of cleanup requirements.

New-study cumulative stage-A debit13.670219666790218/100s; qualified global
4778.086666667840/7200s. Current ledger SHA
`a1b6c3678335557debfba48b419ac582039e631c0ee1e1b20498120f98bfbb51`.
All four test-attempt charges remain appended exactly once in chronology.
