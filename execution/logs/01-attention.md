# Block 1 numerical execution log

No dataset generation, model training harness, or comparative training was
performed. Torch tests configured two CPU threads and one interop thread.

| Command | Exit | Measured test-process elapsed time |
| --- | ---: | ---: |
| `.venv/bin/python -m pytest -q -s tests/test_attention.py` (initial 15-test run) | 0 | 1.15 s |
| `.venv/bin/python -m pytest -q -s tests/test_attention.py` (final 23-test run) | 0 | 0.86 s |
| `.venv/bin/python -m pip check` | 0 | not a numerical compute measurement |

The numerical ledger charge for this block is **2.01 CPU seconds** from the
two executed pytest processes. The final run passed 23 tests. Its observed
maximum errors are recorded in
[`01-numerics.json`](01-numerics.json): Hermiticity `0`, unitarity
`6.557e-07`, Born row-sum `5.960e-07`, dt=0 probability `1.192e-07`, and
dt=0 output `2.384e-07`. These are below the frozen contract tolerances.

The final run also passed double-precision gradcheck, finite gradient checks
through score/value/phase/time and all multihead parameters, the explicit
row-state orientation reference, and the fixed 30-step optimization/checkpoint
reload smoke test. `pip check` reported no broken requirements; it emitted
only the pre-existing non-writable global pip-cache warning.
