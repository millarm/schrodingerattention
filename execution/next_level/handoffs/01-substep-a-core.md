# Stage 0 substep A — partial core/selection handoff

This is deliberately **not** a Stage 0 completion or implementation-PASS claim.
It covers only `execution/next_level/specs/01-core-completion.md`; CLI dataset
integration, full inventory, support persistence, novelty gate, and final safety
remain for the separately authorized substep B.

| SHA-256 | Path |
|---|---|
| `6bbb25018bb65441c4638231e206aa194f7de73588855b75edc05e0147d35f99` | `schrodinger/route_feasibility.py` |
| `7f1d0a8b2ae561a69803508391d9024de4eff317d61866e02928722d26efadec` | `tests/test_route_feasibility.py` |
| `4da537e20c0648a6e1754d949dc57c5c55836fb376e20ce3e3561be1c07ccc1d` | `execution/next_level/specs/01-core-completion.md` |
| `4f0b008a58d109b3cdad3723a12900586134ae934cfabfd57e63e49b3fbcb6f5` | `execution/next_level/ledger.jsonl` |

Completed pure-core fixes:

- Residual-graph lexicographic Edmonds--Karp allocator, including reverse map/
  cell residual edges and a fixture that requires reassignment for max flow.
- Separate distance and multiplicity inputs for frozen median bins.
- Continuous PCG64 split/family problem RNG consumption across maps/cells;
  no per-map reinitialization.
- Four-action q target with illegal-action zeros; branching complete-route
  products equal `1/M`; independent BFS/enumeration, suffix support, and
  verifier collision/too-long/early-goal fixtures.

Executed: `.venv/bin/python -m pytest tests/test_route_feasibility.py -q` —
exit 0, **6 passed in 0.46s**. No CLI inventory/full feasibility run or training
occurred. Stage-0 ledger is now **7.0s** (prior 5.0s plus 2.0s allowance).
