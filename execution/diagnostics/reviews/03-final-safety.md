# Checkpoint diagnostic final-safety review

## Verdict: CHANGES REQUIRED

The real elapsed watchdog, original-argv/startup charging, advisory-locked ledger, per-cell `locally_small` flag, and expanded manifest are implemented and covered by focused regressions. One critical output-race defect remains in the exact no-overwrite mechanism; it must be corrected before the full diagnostic.

## Exact revision reviewed

- Final-safety specification: `execution/diagnostics/specs/02-final-safety-corrections.md`, SHA-256 `34f53ab294135e169046aba77b2de8f394a853f8499f3c070eb9bfd8c2ae16c6`
- Handoff: `execution/diagnostics/handoffs/03-final-safety.md`, SHA-256 `04e8e79c7c05cbd42d1ee6013d304e8e4e6a8936af38e174175acebaf76fd067`
- Implementation: `schrodinger/checkpoint_diagnostic.py`, SHA-256 `6e3ab0681ef9a0d522f3346f8a48c73f51a60eeb59963acfd30b0d539fc15317`
- Tests: `tests/test_checkpoint_diagnostic.py`, SHA-256 `3e49f48833b41a0a2e18ba103e4b9a7bf120ee97a8120486bffff7a83b4d7786`
- Diagnostic ledger: `execution/diagnostics/ledger.jsonl`, SHA-256 `2801d23227019bc4d29b6709ae19d438f482b36804ff7f93c8ec68bb829fe981`
- Prior review: `execution/diagnostics/reviews/02-revision1.md`, SHA-256 `5304d564012468f766939b841426041c704f719e1640fa18766659c70fca3346`

## Required correction

1. **Track output ownership across the atomic output-creation race.** `Attempt.__enter__` acquires the diagnostic lock and then calls `self.output.mkdir(..., exist_ok=False)`. If another actor creates that output between preflight and this call, the exception handler sees `self.fd is not None and self.output.exists()` and writes `attempt.json` into the other actor's directory. That directly violates the frozen requirement never to overwrite any unowned output. If this write itself raises, execution leaves the exception handler before reaching the subsequent file-descriptor close, lock unlink, and timer disarm, so the attempt can also leak its owned lock/deadline state. Track an explicit `output_created_by_this_attempt` boolean; write an in-output attempt record only when it is true; log an output-mkdir race only to a unique external rejection record; and place descriptor close, owned-lock removal, and timer restoration in an unconditional outer `finally`. Add a regression that injects the output-mkdir race, plants sentinel content in the competing directory, proves it is unchanged, proves the acquired lock is released, and verifies the charged external rejection record. Also inject failure of any attempted failure-record write and prove cleanup still runs.

## Accepted closure from this revision

- `SIGALRM`/`ITIMER_REAL` interrupts a single long stage and normal `Attempt` cleanup records failure, releases the lock, and restores the handler.
- The CLI uses `sys.orig_argv`, records `sys.executable`, adds the declared two-second startup allowance, and charges nonzero rejection attempts. Ledger writes use an advisory lock and flush/fsync.
- Every direct summary cell contains the exact frozen local-small decision; the manifest includes the requested test, plan, correction-specification, review, and prior-handoff identities.
- The prior mathematical, metric, numerical, retained-input, and trace-invariant acceptances remain unchanged.

## Independent checks

- Read the complete final-safety implementation, handoff, specification, and targeted race/deadline/manifest tests, and followed the exception paths through acquisition and cleanup.
- Ran `/usr/bin/time -p .venv/bin/python -m pytest -q tests/test_checkpoint_diagnostic.py`: **17 passed in 0.77 s**, explicit exit; whole-command elapsed **1.06 s**. The passing suite does not exercise the output-mkdir race described above.
- Conservatively charge **1.3 s** for this independent test and hash/static check. Starting from the handoff total of 20.0 s, the diagnostic ledger should advance to **21.3 s** before further work.

## Not performed

- No full checkpoint diagnostic, training, sweep, or artifact regeneration was run.
- The handoff's 65-test repository-wide result was not independently rerun; it cannot resolve this uncovered exception path.

