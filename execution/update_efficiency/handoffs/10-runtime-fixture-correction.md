# Runtime fixture correction after the first bounded suite

This is the narrow three-test-only correction authorized by
`spec-06-runtime-fixture-correction.md`, following the retained suite evidence
in `attempts/driver-22a50df3-932d-4e3a-a238-60fe2a6203da/`.

## Exact source inventory

- corrected `tests/test_update_efficiency.py`:
  `a1d879c7cb73d4f9e3e9270476a920bcdafded59bfa402ee4a826ad83eaa9558`
- frozen `execution/update_efficiency/command.py`:
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- frozen `execution/update_efficiency/study.py`:
  `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- correction authority `spec-06-runtime-fixture-correction.md`:
  `99141859b6395c4ee78fe114121674873b53d18da5e54f7cc0cb8a5b857e7409`

## Literal repairs

1. `test_driver_watchdog_descendant_fixture` creates its private watchdog log
   directory before calling the reviewed real child/descendant timeout helper;
   its actual timeout and cleanup assertions remain intact.
2. `test_driver_append_uses_actual_single_descriptor_snapshot` now calls
   `ledger_rows(ledger)` explicitly, so it verifies the private one-line ledger
   rather than the definition-bound production default.
3. `test_driver_final_terminal_failure_retains_a_and_b_reservations` captures
   the module's unwrapped `durable` function once before its smoke/production
   loop and binds that function as the wrapper default, preventing the second
   case from recursing into the first wrapper.  Both terminal-failure, charge,
   and retained-reservation assertions are unchanged.

No test was rerun during this edit.  No driver/study/watchdog/science/config
file, ledger row, prior attempt, or runtime authority was changed.  Sol static
diff review is required before one newly bound 30-second suite decision.
