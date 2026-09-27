# Stage 0 novelty-cardinality regression handoff

This is a narrow implementation-regression correction only. No full 6x6
inventory, feasibility outcome, model, or training run was performed.

`_novel_records` now appends each record inside its input-row loop. The existing
tiny injected end-to-end pipeline fixture was strengthened to prove the frozen
cardinalities and identities rather than mere non-emptiness:

- validation persists exactly 32 novelty records, ID test exactly 32, and IL
  exactly 16;
- each list's ordered `(map_id, start, goal)` sequence exactly equals the
  selected evaluation-problem sequence reconstructed from the recorded split
  flow, family seed stream, and per-map allocation; no duplicates occur;
- every persisted record has `M == len(routes) == len(signatures)`;
- the primary pipeline's `qualifying_il` and `qualifying_maps` equal
  `novelty_gate()` computed over the complete persisted 16-record IL list.

Focused command: `.venv/bin/python -m pytest tests/test_route_feasibility.py -q`
returned exit code **0**, **18 passed in 1.26s** (external wall 1.373s).

| SHA-256 | Path |
|---|---|
| `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` | `schrodinger/route_feasibility.py` |
| `0e5565a39d93b34269633522256b4eef38d741879e2292af989d075500626786` | `tests/test_route_feasibility.py` |
| `1e19aac5a4f372bc9ea092b39e97a08aff23dfc140707edbac7ec89dbf320625` | `execution/next_level/ledger.jsonl` |
| `bb6f3581cc39976092f700a7a8188c37a06cc196d4c0748c7300f392b39ea18d` | `execution/next_level/specs/06-novelty-cardinality-regression.md` |
| `536a5b3ced4981e5623fcaa5b096a624eb571f7f60f9a9f877bbe1b42938f15e` | `execution/next_level/reviews/05-final-acceptance.md` |

The append-only next-level ledger totals **33.40637700000516s**, including the
Sol review charge (1.7s) and the conservative focused-regression allowance
(2.0s). Historical entries were not modified.
