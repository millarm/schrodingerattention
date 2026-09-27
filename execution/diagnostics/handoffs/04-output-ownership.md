# Checkpoint diagnostic output-ownership repair handoff

Status: frozen for Sol’s scoped ownership review. This is the explicitly
authorized post-cycle repair only; no trace, metrics, input validation, full
diagnostic, training, or original artifact changed.

## Current identities

| SHA-256 | Path |
|---|---|
| `0468355260054a29243a2348b76db664b2d07d9f0a368058e3631c8334c79374` | `schrodinger/checkpoint_diagnostic.py` |
| `40be7c2e56fc21cef19ab896c7a5d0640e0dce8ae569ef09249c1f5da42ecb8f` | `tests/test_checkpoint_diagnostic.py` |
| `815247ae8d75e5a68d45f868ab7a2fe06701e7efa6714593ffcc7f28e1804d3c` | `execution/diagnostics/specs/03-output-ownership-fix.md` |
| `0294636261e6dbfcc477fd12c11300ce540c0998a06c70e9d3442361780378ed` | `execution/diagnostics/reviews/03-final-safety.md` |
| `a773d0a74863b679ffd79ce4b2033e288ca9778c68f1d730209f33be1aa95845` | `execution/diagnostics/ledger.jsonl` |

## Scoped repair and regressions

- `Attempt.output_owned` begins false and changes only after this attempt’s
  `mkdir(..., exist_ok=False)` succeeds. Enter-path attempt logs are written
  only when it is true.
- An output mkdir race therefore follows the unique external charged rejection
  path; it cannot write `output/attempt.json`, remove another owner’s lock, or
  mutate the contender output.
- `_cleanup()` unconditionally closes this instance’s descriptor, unlinks only
  its owned lock, and restores the deadline handler/timer. It is reached even
  when enter-path failure logging itself raises.
- `test_output_mkdir_race_preserves_other_owners_sentinel_bytes` creates a
  sentinel `attempt.json` between lock acquisition and mkdir failure, verifies
  byte identity, owner-lock cleanup, and unique charged rejection.
- `test_enter_record_write_failure_still_cleans_owned_resources` injects
  attempt-record writing failure after successful output ownership and deadline
  failure, verifies lock cleanup and failed ledger status.

## Commands

- `.venv/bin/python -m pytest tests/test_checkpoint_diagnostic.py -q` — exit
  0, **19 passed in 0.79s**.
- `.venv/bin/python -m pytest -q` — exit 0, **67 passed in 1.64s**.
- `.venv/bin/python -m compileall -q schrodinger/checkpoint_diagnostic.py` —
  exit 0.

No yielded process/session and no full diagnostic analysis occurred.

## Ledger

Diagnostic ledger total: **22.3s**, including Sol final-safety review 1.3s and
the conservative Terra ownership-test allowance 1.0s. It is separate from the
original experiment ledger and remains below the 900s diagnostic ceiling.
