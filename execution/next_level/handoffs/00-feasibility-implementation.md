# Stage 0 feasibility implementation handoff

Status: implementation frozen for Sol review; no full 6x6 inventory or
feasibility CLI invocation has occurred.

| SHA-256 | Path |
|---|---|
| `6221633d28f77fac4f3ad9f33f6c212370d228a92669087976997c7bc1f5082a` | `schrodinger/route_feasibility.py` |
| `54160b95d6904247a8b504299b91154376c6119f6df7698529fa12ea9152ff9f` | `tests/test_route_feasibility.py` |
| `7ebe049dcdbeeffea8933242fe90fcd794698741869c6e7102726d4496279464` | `next_level_learning_plan.md` |
| `3b573fd5e67de97fd3ce9d0a4a4bfcf7b858ddcb65841638c6059f075ddcc0a3` | `execution/next_level/specs/00-feasibility-contract.md` |
| `5ac506babca0de4f5a2a2a03a919ef9ad479ab1209b6b93c918994615c431858` | `execution/next_level/ledger.jsonl` |

Implemented only the additive Stage-0 module and tests: D4 canonical map and
route/reversal signatures; triomino/component enumeration; BFS distance and
dynamic shortest-suffix counts; exact q target, route enumerator/verifier and
suffix support; frozen PCG64 map/problem ordering helpers; equal-frequency bin,
Hamilton quota and lexicographic Edmonds--Karp allocation; plus isolated
fresh-output/lock/ledger CLI ownership primitives. No model, optimizer,
training, decoding, or full inventory work was added.

Fixture evidence:

- `.venv/bin/python -m pytest tests/test_route_feasibility.py -q` — exit 0,
  **5 passed in 0.47s**.
- `.venv/bin/python -m pytest -q` — exit 0, **72 passed in 1.91s**.

Tests cover map D4 identity, D4/reversal route signatures, BFS/enumerated
counts, q normalization, shortest-route verifier failures, suffix support and
novelty examples, seeded map replay, median/Hamilton ties, deterministic flow
feasible/infeasible allocation and per-map cap, and temporary-ledger
fresh-output/lock safety. No failure artifact was created and no run session
exists. Stage-0 ledger charge is a conservative **5.0s**.
