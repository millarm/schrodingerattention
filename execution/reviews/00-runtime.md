# Sol review — Block 0 runtime preparation

## Version inspected

No Git commit is available. Frozen files inspected:

| File | SHA-256 |
| --- | --- |
| `requirements.txt` | `7f3afea068a167c68c7dc0c7f5bd634d99fdb46a8e4d4119c753ca2974462f25` |
| `execution/runtime.json` | `805b8c51fd21468ccb2f5c70bc122b52bf13f601331937e9979efcc5c5184995` |
| `execution/logs/00-runtime.md` | `012a8d0fc939da342cde35b96ff98c5a1fa78309fc136a99f667d5042ab31fc9` |
| `execution/handoffs/00-runtime.md` | `e419718c52d20862af1e58593f807cf42f78bfbb5ff5af58a0c75cb44ebcaf28` |

The governing specification was `execution/specs/00-runtime.md`, SHA-256
`e3e9fbb7e47c10568598ade94c10a2ed6fb1b77414c6626dd12235d991ddea45`.

## Verdict

**PASS**

The runtime meets the Block 0 acceptance criteria. It provides a reproducible
project environment, records actual CPU-only hardware availability and package
versions, and demonstrates exact complex64 matrix-exponential forward and
backward operation with the required worker settings. No implementation or
training was performed.

## Required findings

None.

## Independent checks performed

- Recomputed every SHA-256 above; all handoff hashes match the frozen files.
- Inspected the runtime log and machine-readable record for internal
  consistency: Python 3.12.14, PyTorch 2.14.0, two intra-op threads, one
  inter-op thread, CPU device, MPS unavailable, and CUDA unavailable.
- Imported the frozen environment and independently reran a seeded
  `torch.complex64` exact `matrix_exp` calculation on symmetric Hamiltonians,
  followed by row-state evolution and backward propagation.
- Independent maximum unitarity error was `3.576285507733701e-07`; maximum
  Born row-sum error was `2.384185791015625e-07`; loss and input gradients were
  finite. These are comfortably inside the later contract's representative
  complex64 tolerances.
- Confirmed the independent runtime reported Python 3.12.14 and PyTorch 2.14.0
  and honored the declared 2/1 thread settings.

## Checks not verified

- The `system_profiler` hardware command was not rerun independently; its
  captured Apple M4, 10-core, 24 GB result is consistent between the log and
  `runtime.json`.
- Package installation was not repeated. The handoff records its exit status,
  and the installed environment successfully imports and executes PyTorch.

## Non-blocking observations

- `requirements.txt` is intentionally unpinned, while the realized versions
  are captured exactly in `runtime.json`. Recreating the environment in the
  future may resolve newer packages; preservation of the current environment
  plus runtime metadata is adequate for this bounded local execution.
- CPU-only execution is a feasibility constraint, not an implementation
  defect. The profile-derived update count and four-hour ledger remain the
  appropriate controls.
