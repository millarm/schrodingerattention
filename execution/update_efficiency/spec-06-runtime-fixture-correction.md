# Three observed test-fixture corrections only

First full suite terminated explicitly with exit 1: 24 passed, three fixture
failures, no timeout. Immutable evidence is under
`attempts/driver-22a50df3-932d-4e3a-a238-60fe2a6203da/`.
Stage A charge 3.347905582981184 seconds; preserve all evidence and ledger rows.

Terra may edit only these three tests in `tests/test_update_efficiency.py`:

1. `test_driver_watchdog_descendant_fixture`: create its own log directory before
   invoking the accepted watchdog, whose interface requires an existing directory.
   Retain the genuine child/descendant timeout and cleanup assertions.
2. `test_driver_append_uses_actual_single_descriptor_snapshot`: pass the temporary
   ledger explicitly to `ledger_rows(ledger)`. The default argument is bound at
   definition time; changing module LEDGER does not change it. Keep actual locked
   append and duplicate checks, never touch production ledger from this fixture.
3. `test_driver_final_terminal_failure_retains_a_and_b_reservations`: isolate each
   parametrized case's monkeypatch context or capture the true original durable
   function outside the loop. The second case currently captures its preceding
   wrapper and recursively calls itself. Both A/B terminal-failure assertions,
   one charge, and retained reservation remain mandatory.

No study/driver/watchdog/science/config changes. No tests during editing. Return
exact test hash and handoff; Sol static review of this narrow diff is required
before a new single 30-second suite decision bound to current ledger/source.
All prior attempts remain immutable. New-study A100 cumulative cap unchanged.
