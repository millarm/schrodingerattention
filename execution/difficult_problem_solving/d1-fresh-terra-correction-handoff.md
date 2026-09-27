# Terra correction handoff after fresh static review — 2026-09-20

## Exact review target

| Artifact | SHA-256 |
| --- | --- |
| `execution/difficult_problem_solving/d1.py` | `b881a7068ab9f82b92220bc87b3d166a78d8c482fd5044e1c61bde322792d5b0` |
| `execution/difficult_problem_solving/d1_watchdog.py` | `96aa33a1fc6268276d6d0879545b9d974b14fd73d2452d5b1e22e519e5815bf2` |
| `tests/test_difficult_problem_solving_d1.py` | `b31c79111eebfcebdb2e1e4f604ed77836b43804662676a15fb2d32432f787b3` |

No tests, Python imports, checkpoint loads, inference, production commands, or
ledger mutations were run. This is not a PASS and grants no smoke authority.

## Implemented static corrections

- Retained analysis pairs are kept and compared field-for-field with one current
  `validate_pair` read (checkpoint hashes/identities, initial hashes, owner
  authority, shared initialization, and batch prefix); model construction then
  uses that validated pair rather than reloading checkpoints.
- Training support is canonical length-prefixed bytes and must equal the accepted
  loader `support_hash`. Cells bind this hash and the manifest-bound common input
  IDs. Historical counters are null with an explicit unavailable reason.
- Per-cell JSON uses the accepted serializable adapter, allowing reversible bytes
  route encoding. The ordered panel is written once and hash-referenced by cells;
  greedy files are separately hashed and all eight plus all forty cells are
  required before indexed selection. New endpoints distinguish endpoint elapsed
  from evaluator cache timing fields.
- Production now requires a hash-bound exact release decision (source/test/
  watchdog/plan/approval/review/ledger/owner/argv) rather than a boolean.
- The watchdog now validates the frozen 143-line prefix and approved addendum,
  holds an exclusive accounting lock, uses exact decision-bound argv/version
  records, writes terminal evidence before charging, charges actual elapsed time,
  and reconciles a unique OwnedAttempt output or emits one uncertain fallback.

## Literal-test mapping and remaining review issue

The revised test fixture now carries accepted training support hashes, retained
pair fields, and per-problem map/family fields. It still does **not** close all
of Sol's required literal test additions: the 144-byte evaluator fixture with
known count assertions, injected tiny-panel call/caches/lock negative coverage,
real owner write/finalization failure tests, and watchdog child-process tests are
not complete in these bytes. Therefore this handoff is intentionally incomplete
and should receive `CHANGES REQUIRED`, not be used for a smoke command.

The source also needs Sol's static scrutiny for the exact decision-record schema
and the analysis-bound retained QC K32 route-verification path before it can be
considered safe.

## Commands run

Only static reads, searches, `apply_patch`, and SHA-256 calculation. No dynamic
command was substituted for the prohibited test procedure.
