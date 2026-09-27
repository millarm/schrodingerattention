# D1 owned-producer tests handoff — static only

| Artifact | SHA-256 |
| --- | --- |
| `execution/difficult_problem_solving/d1.py` | `463f31c7268e410d9eb9adc4a9242213df226aa1330a9b46d92276afe15edf27` |
| `tests/test_difficult_problem_solving_d1.py` | `a0add86d5a7be0f740c7f45d24e5ffc2ece5111b0d92a5888407adc7376777fd` |
| unchanged `execution/difficult_problem_solving/d1_watchdog.py` | `96aa33a1fc6268276d6d0879545b9d974b14fd73d2452d5b1e22e519e5815bf2` |

Changed source function: `load_indexed_cells` now has the permitted keyword-only
`expected_problem_count=512`; `run` forwards the value only from Python-only
`deps`. CLI/default production remains 512.

Changed test function: `test_real_producer_dispatches_40_cells_once_under_sink`.
It uses ten complete 144-byte adjacent `Problem` records (eight mixed, I, L),
the actual producer, actual accepted evaluator behind a recording wrapper,
actual `CellSink`, real stored-route greedy verification, and a strict internal
small-panel validator. It asserts 24 evaluator calls with K32/split1/replicate0
and exact panel order, eight cache objects, 16 reuse/24 new/40 endpoint and eight
greedy writes, default 512-reader rejection, explicit 10-reader override success,
and duplicate write rejection.

No tests, imports, inference, checkpoint loads, production, timers, or ledger
writes were run.

Concrete remaining interface boundary: current `run` calls the non-injectable
`require_production_decision` before the owned producer and later calls global
`compose`/`validate_cells`. Implementing the specified actual `run` owner/failure
tests needs an explicitly approved injectable test-only decision boundary (and
small-panel compose validator), or permission to monkeypatch those named
authorization/validation boundaries in the test process. I did not bypass them
or add a new source seam beyond the one expressly authorized. Thus endpoint-write
and final-manifest owned failure tests are not claimed complete.
