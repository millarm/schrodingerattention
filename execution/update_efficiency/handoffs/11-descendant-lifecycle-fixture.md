# Descendant lifecycle fixture respecification

This is the sole proof-preserving fixture change authorized by
`spec-07-descendant-lifecycle.md` after the retained EPERM outcome.  Only
`test_driver_watchdog_descendant_fixture` changed.

## Exact source inventory

- tests `tests/test_update_efficiency.py`:
  `5fb793d5794836462d0b145cc0d613ef4c0c3b3f29ac28ec1c30cdd75e2378c6`
- frozen driver `execution/update_efficiency/command.py`:
  `3adda02c82b2eb6a059d890b967950c6718e7406e64dd99fdcfe2dab47f38b4f`
- frozen study `execution/update_efficiency/study.py`:
  `a62a37248421660f94edce139a7e9ca471890bab8c0ba4463edd8ffb6c396204`
- frozen accepted watchdog `execution/difficult_problem_solving/d1_watchdog.py`:
  `2b3fed56e07da5a33c122afa10e9cc5b77df0df77ec492db0bfaf4887708a8c8`
- respecification `spec-07-descendant-lifecycle.md`:
  `e9443c18b26c96ed8e3a5c466b0257cf1128fcfc31e3112a55bd499d0b162f1c`

## Literal proof map

- A real parent is launched through unchanged `command.supervise`; its real
  child inherits the launched process group.
- Both processes write private fsynced proof files.  The parent installs its
  SIGTERM handler before child readiness, records actual parent/child PID and
  PGID, waits for child readiness, then marks parent readiness.
- The child has a finite four-second defensive lifetime.  The parent has its
  own finite four-second defensive lifetime; after group SIGTERM its handler
  path waits/reaps the actual child and records its PID, `-15` return code and
  handler reason before exiting zero.
- The unchanged watchdog receives a two-second total deadline and its existing
  group probe is used directly after return.  Assertions require durable
  readiness/start/reaping evidence, distinct PID identities, parent-as-PGID,
  child membership in that PGID, real reaping, parent zero exit,
  `timed_out`, `cleanup_verified`, and accepted `group_gone` truth.

There is no mocked cleanup result, EPERM waiver, skip, changed watchdog logic,
or post-return polling.  No tests, imports, subprocesses, model/data work,
ledger writes, or production actions were performed while editing.  Sol static
PASS is required before the one permitted new 30-second suite attempt.
