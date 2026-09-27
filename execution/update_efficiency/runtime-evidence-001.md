# First bounded runtime evidence

Exact full-static review SHA `34ed2d8aa335605ac0246489c4491573e82a190542a13da14956308f254fb9c0`.
Frozen study `a62a3724…`, tests `7dbb7c31…`, driver `3adda02c…`.

- Smoke decision `smoke-decision-001.json`, command through `command.py` with
  seconds10/seed2201/mode softmax. Tool session83809 was polled to explicit
  exit0. Owner `attempts/driver-6c0e7f36-7b02-4eab-a873-d09895436be0`.
  Pytest1 passed in3.12s; child exit0, cleanup verified, no timeout. One ledger
  charge4.4263019589707255s. Terminal later sampled4.427897374844179s; ledger
  value remains authoritative and includes the one-second finalization allowance.
- Suite decision `suite-decision-001.json`, seconds30, same seed/mode. Session12031
  polled to explicit exit1. Owner `attempts/driver-22a50df3-932d-4e3a-a238-60fe2a6203da`.
  Pytest24 passed/3 failed in1.87s; child exit1, cleanup verified, no timeout.
  One ledger charge3.347905582981184s. The source/real owner integration tests
  passed; the three named fixture failures are retained in raw stdout.

No duplicate launch, retry-on-yield, production model run or test-data access.
Both full tool results and explicit terminal results were retained in task history.
No ledger rewrite; two EOF charges, new A total7.77420754195191/100s.
The three-fixture correction requires exact static review and a new unique
decision before a repeated suite. No production acceptance is implied.
