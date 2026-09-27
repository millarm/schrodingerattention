# Sol review — Block 1 exact attention

## Exact version inspected

No Git commit is available. Frozen implementation and evidence inspected:

| File | SHA-256 |
| --- | --- |
| `requirements.txt` | `75cc9611447448ebc842ed38040468de5cdb1a67435b89b14de73efdba806403` |
| `schrodinger/__init__.py` | `f063f8b1d73e3953b498b23daab877d2c43ccd28a9790d54d669ee2dde7ef5db` |
| `schrodinger/attention.py` | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| `tests/test_attention.py` | `85d2808de8c07a6e1020fc0f4a998cb75367038d3d67aae9e66fa262477f7856` |
| `execution/logs/01-numerics.json` | `afe1d67c15fcbe61a4beefd1cb249c824cfb76e8d4d1ae14e4132d6c9d68b795` |
| `execution/logs/01-attention.md` | `e2f4501b6c71b015771d06f7fdd2c686176158d373b76e403cd2aa80eb6b6b49` |
| `execution/handoffs/01-attention.md` | `a1eba1242d9a5b6aaa683916ddb7e0fbab01010fa0a1e63a50d5f2d456fdf87e` |

Governing specification:
`execution/specs/01-attention.md`, SHA-256
`a8cccf18cc6174b2814847a0d89a78c4ae859640542b31cc0c2ca51d44ab04af`.

## Verdict

**PASS**

The implementation follows the frozen exact-attention formula, respects the
required tensor axes and row-state orientation, preserves norm numerically,
retains differentiability, and recovers the matched softmax computation at
literal `dt=0`. The tests and independent rerun satisfy the Block 1 acceptance
criteria.

## Required findings

None.

## Code and mathematical inspection

- Scores are `[batch, heads, query, key]`; Q/K scaling uses
  `sqrt(head_dim)`, while the symmetric Hamiltonian independently uses the
  required additional `sqrt(length)` divisor.
- `H = (S + S.T)/2/sqrt(length)` is real symmetric and therefore Hermitian
  after conversion to the selected complex dtype.
- Evolution uses exact `torch.matrix_exp(-i dt H)` and
  `psi0 @ U.transpose(-2,-1)`. The transpose, not adjoint, is correct when a
  conventional column-state equation is represented as a row state. No query
  rows are mixed.
- Initial amplitude is `sqrt(softmax(S)) * exp(i gamma S)`. Born probabilities
  are measured before multiplication by values, with no defensive
  renormalization.
- Float32 maps to complex64 and float64 maps to complex128. Diagnostics detach
  scalar evidence and do not retain the training graph.
- Effective `dt` and `gamma` use the frozen bounded transforms and inverse
  initializers. A literal override of zero still executes the complete exact
  path; it is not a baseline shortcut.
- The multihead reshape/transposes preserve the head, query, key, and value
  axes, and all corresponding Q/K/V/output interfaces match baseline mode.

## Independent checks performed

Recomputed every SHA-256 above and reran:

`MPLCONFIGDIR=/private/tmp/schrodinger-sol-mpl .venv/bin/python -m pytest -q -s tests/test_attention.py`

Result: exit 0, **23 passed**. Pytest reported 0.85 seconds; full process wall
time including startup was 1.22 seconds. The encompassing hash-and-test command
used 1.3 seconds tool wall time. Charge **1.4 seconds conservatively** to the
global ledger for Sol's Block 1 executable inspection, including the earlier
source/hash command.

Independent observed maxima/results:

- Hermiticity error: `0`.
- Unitarity error: `6.557e-07`.
- Born row-sum error: `5.960e-07`.
- `dt=0` probability error: `1.192e-07`.
- `dt=0` output error: `2.384e-07`.
- Wrong-orientation separation: `1.951e-02`.
- Effective initial values: `dt=0.05000000074505806`,
  `gamma=0.10000000149011612`.
- Fixed optimization MSE: `1.066010` to `0.336738` in 30 steps.
- Double/complex128 gradcheck passed; finite score, value, phase, time, Q/K/V,
  output-projection, gamma, and dt gradient paths were exercised.

## Checks not independently verified

- No performance or scaling claim was assessed; this is intentionally an
  exact CPU reference module.
- The later classifier's cross-model state-copy logic and full checkpoint
  integration are Block 2 checks.
- Invariant logging during training is not present in this block and remains a
  harness requirement.

## Non-blocking observations

- Terra's handoff charges the two pytest-reported durations (2.01 seconds),
  which omit some process startup/teardown. The global ledger should add a
  conservative startup allowance when those historical commands are folded
  into it. This tiny accounting correction does not affect the implementation
  verdict or feasibility.
- Gradient tests require finite, present gradients as specified; they do not
  impose a nonzero-gradient threshold. The double-precision gradcheck provides
  the stronger local derivative validation for the score-level primitive.
