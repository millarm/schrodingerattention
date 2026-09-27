# Block 1 attention handoff

## Summary

Implemented the reusable score-level attention function and matched multihead
self-attention module in conventional softmax and exact Schrödinger modes.
Exact mode uses the frozen formula: symmetric Hamiltonian divided by
`sqrt(length)`, `torch.matrix_exp`, complex64/complex128 selected from the
real input type, Born measurement, and row-state evolution
`psi0 @ U.transpose(-2, -1)`. It has no probability renormalization or
dt=0 baseline shortcut. The multihead module exposes bounded per-head
evolution time and phase parameters only in Schrödinger mode.

Added numerical tests and concrete measured evidence for all frozen lengths,
score scales, invariants, gradient paths, gradcheck, dt=0 equivalence,
orientation, and the fixed optimization/checkpoint-reload smoke test.

## Exact implementation version

This workspace is not a Git repository, so the reviewed version is identified
by the following SHA-256 hashes:

| File | SHA-256 |
| --- | --- |
| `requirements.txt` | `75cc9611447448ebc842ed38040468de5cdb1a67435b89b14de73efdba806403` |
| `schrodinger/__init__.py` | `f063f8b1d73e3953b498b23daab877d2c43ccd28a9790d54d669ee2dde7ef5db` |
| `schrodinger/attention.py` | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| `tests/test_attention.py` | `85d2808de8c07a6e1020fc0f4a998cb75367038d3d67aae9e66fa262477f7856` |
| `execution/logs/01-numerics.json` | `afe1d67c15fcbe61a4beefd1cb249c824cfb76e8d4d1ae14e4132d6c9d68b795` |
| `execution/logs/01-attention.md` | `e2f4501b6c71b015771d06f7fdd2c686176158d373b76e403cd2aa80eb6b6b49` |

## Commands, results, and compute ledger

| Command | Exit | Result |
| --- | ---: | --- |
| `.venv/bin/python -m pytest -q -s tests/test_attention.py` | 0 | Initial 15-test run passed in 1.15 test-process seconds. |
| `.venv/bin/python -m pytest -q -s tests/test_attention.py` | 0 | Final 23-test run passed in 0.86 test-process seconds. |
| `.venv/bin/python -m py_compile schrodinger/__init__.py schrodinger/attention.py tests/test_attention.py` | 0 | Syntax validation passed. |
| `.venv/bin/python -m json.tool execution/logs/01-numerics.json` | 0 | Numeric evidence JSON validated. |
| `.venv/bin/python -m pip check` | 0 | No broken requirements. |

Numerical compute charged to Block 1 is 2.01 CPU seconds (the two pytest
processes). Full numeric maxima and coverage are in
[`../logs/01-numerics.json`](../logs/01-numerics.json), and the command log is
in [`../logs/01-attention.md`](../logs/01-attention.md). Final observed maxima:
Hermiticity `0`, unitarity `6.557e-07`, Born row sum `5.960e-07`; dt=0
probability `1.192e-07` and output `2.384e-07`. The 30-step smoke MSE fell
from `1.066010` to `0.336738`, with finite values throughout.

## Limitations and review request

The module is an exact CPU reference implementation; its batched matrix
exponential is intentionally not optimized. It accepts only float32 and
float64 real score inputs, which is the specified experimental scope. No
dataset, classifier, harness, or comparison code was created. Code and tests
are now frozen pending Sol's review and Astra's acceptance.
