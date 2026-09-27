# Stage 0 CLI fixture regression

This is a test-only, frozen handoff supplement. No full feasibility inventory,
model, or training work was launched.

The new `test_main_subprocess_tiny_injected_inventory_full_artifacts` starts a
fresh Python subprocess, imports `schrodinger.route_feasibility`, injects a
one-record in-memory `_inventory_records` fixture, assigns `sys.argv` exactly
as the public `--output` CLI invocation, and calls `main()`. Its test-local
`Attempt` factory supplies test-local lock and ledger paths while retaining the
real `Attempt` implementation and all of `main()`/writer behavior.

The subprocess is asserted to exit `0`; its output has `summary.json` with
`execution_status == "COMPLETE"` and
`outcome == "FROZEN_SELECTION_FAILED"`, the complete JSON artifact set
(`inventory`, `selection`, `splits`, `training_states`, `novelty`, `summary`,
`manifest`, `attempt`), and exactly one local ledger entry. This is an explicit
scientific failure outcome, not a successful feasibility result.

Focused evidence: `.venv/bin/python -m pytest tests/test_route_feasibility.py -q`
returned exit code **0**, **11 passed in 1.24s** (external wall 1.374s).

| SHA-256 | Path |
|---|---|
| `6f3850051b178680346ebc0aa73aaeb183b6d963fdec49c0293c276bb91d338f` | `schrodinger/route_feasibility.py` |
| `a8623ebac320fee64a57ec43b58de28f4e084736bb73425b2728657dfdce3393` | `tests/test_route_feasibility.py` |
| `f72520845539e1d9a0812323160c09519619088973ab693aa99fe5928f610398` | `execution/next_level/ledger.jsonl` |
| `3774ce90681ae194bc367dc9ebe344c5ee0eaa86284e6fe472a5b114484315be` | `execution/next_level/specs/04-safety-correction.md` |
| `78508de8d4cf78b0d833f3f31517ef933ecb3265091cfe3584a7cbcef5895f40` | `execution/next_level/reviews/03-feasibility-implementation.md` |

The append-only next-level ledger currently totals **21.00637700000516s**. Its
latest 2.006377s CLI record came from the earlier failed assertion run before
the test-local `Attempt` factory was added; it was still a one-record injected
fixture subprocess, not an inventory run. The corrected passing test creates
only its test-local ledger and does not alter the shared ledger.
