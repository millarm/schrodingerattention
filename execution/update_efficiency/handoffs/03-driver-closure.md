# Terra driver-only static handoff — v3 saturation

No import, test, model/data execution, subprocess launch, or ledger write was
performed. `study.py` was not edited in this driver-only sub-block.

Reviewed version hashes:

- command: `24daec613cd43ed8e49c5c358b05c94ea0bc520c2547c650bfd8379ea0d199f4`
- tests: `9bf681ea7901fb92ed75a92f350d7cbe802ecaf4f4c54877be12e7f8af85a0ad`
- v3 plan/spec/decisions: `d4ce6e3c6e4c0a7eac46aa96b2a01f442abeed573c3b78e95a2edb874caca6ae`,
  `dcca6fa6c3ba0d322a8278d6003c77249c692a1224f37a3a2bad547530285a67`,
  `77affe9064fd016e2391c0b1f6ac67a8aac9d69b4f6d7af06c36f90ee3e798c4`
- reused watchdog: `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`.

Assertion map:

1. `KINDS` binds named smoke10/suite30 and v3 production SM350/SA550 argv.
2. `reserve` holds one study lock, rejects both experiment locks, validates the
   147-line ledger prefix, carry, finite UUID rows, new-study A/B envelope and
   global/stage headroom after acquiring the lock.
3. `supervise` delegates descendant cleanup to the reviewed watchdog; terminal
   records are durable on child and driver failures.
4. A-stage branches append exactly one tagged EOF record before releasing a
   certain reservation.
5. B-stage branches reconcile a unique local-owner charge or append a tagged
   permanent uncertain fallback; COMPLETE requires attempt/result/index hashes.
6. Driver tests assert v3 named surfaces/authority inventory and an
   over-allocation reservation failure, in addition to the existing timeout
   child coverage.

This is a complete driver-only static seam for review. It does not authorize
tests or production; scientific runner/composition remains a separate dispatch.
