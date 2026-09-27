# Checkpoint diagnostic final safety handoff

Status: frozen for Sol review. This revision changes only the additive
diagnostic module/tests/ledger/handoff. No full diagnostic, training, or prior
artifact modification was performed.

## Current identities

| SHA-256 | Path |
|---|---|
| `6e3ab0681ef9a0d522f3346f8a48c73f51a60eeb59963acfd30b0d539fc15317` | `schrodinger/checkpoint_diagnostic.py` |
| `3e49f48833b41a0a2e18ba103e4b9a7bf120ee97a8120486bffff7a83b4d7786` | `tests/test_checkpoint_diagnostic.py` |
| `b160517e6a6c8d707fe50d392b3953dac447b99d74eeda2893a53c15dfd66b16` | `checkpoint_diagnostic_plan.md` |
| `34f53ab294135e169046aba77b2de8f394a853f8499f3c070eb9bfd8c2ae16c6` | `execution/diagnostics/specs/02-final-safety-corrections.md` |
| `5304d564012468f766939b841426041c704f719e1640fa18766659c70fca3346` | `execution/diagnostics/reviews/02-revision1.md` |
| `2801d23227019bc4d29b6709ae19d438f482b36804ff7f93c8ec68bb829fe981` | `execution/diagnostics/ledger.jsonl` |

## Required correction mapping

1. **Real deadline:** `Attempt` installs `SIGALRM`/`ITIMER_REAL` for remaining
   cumulative budget after prior charges, a 2-second startup allowance, and the
   30-second reserve. Its dedicated `DiagnosticTimeout` reaches normal attempt
   cleanup, failure persistence, and lock release. It disarms/restores the
   prior timer/handler in finally. `test_real_sigalrm_interrupts_post_processing_and_restores_handler`
   sleeps through a 20ms deadline and verifies failed attempt record + handler
   restoration.
2. **Exact provenance/races:** CLI takes `sys.orig_argv`, retains
   `sys.executable`, charges 2s startup plus measured elapsed to success,
   failed, and rejected attempts, and includes these in cap accounting. Atomic
   O_EXCL/mkdir races generate unique O_EXCL rejection JSON under
   `execution/diagnostics/rejections/`, with advisory-locked ledger appends;
   another owner’s lock/output is never removed. Tests verify exact argv,
   nonzero rejection charge, active-owner preservation, and failed required-log
   accounting.
3. **Traceability:** every direct summary cell contains `locally_small` under
   the frozen mean/p95 thresholds. The manifest includes implementation/test,
   frozen plan, both correction specs, plan/implementation reviews, and prior
   handoffs. Explicit regression verifies every requested stable membership and
   every direct cell flag.

## Executed verification

- `.venv/bin/python -m pytest tests/test_checkpoint_diagnostic.py -q` — exit
  0, **17 passed in 0.82s**.
- `.venv/bin/python -m pytest -q` — exit 0, **65 passed in 1.61s**.
- `.venv/bin/python -m compileall -q schrodinger/checkpoint_diagnostic.py` —
  exit 0.

No command yielded; no active session exists. The permitted tests use temporary
outputs/ledgers, except read-only selected retained checkpoint validation. No
all-seed analysis is authorized or launched.

## Ledger

Actual current diagnostic ledger total is **20.0s**, including the 1.3s Sol
revision-1 review and a conservative 2.0s Terra final-safety test allowance.
It remains separate from the original experiment ledger and below the 900s cap.
