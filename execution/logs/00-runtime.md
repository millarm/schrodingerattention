# Block 0 runtime log

All commands ran in `/Users/gmh-company/codex/schrodinger` on 2026-09-15.
No model implementation or training was run.

| Command | Outcome |
| --- | --- |
| `/Users/gmh-company/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 --version` | Python 3.12.14. |
| `/Users/gmh-company/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m venv .venv` | Exit 0; isolated project environment created. |
| `.venv/bin/python -m pip install -r requirements.txt` | Exit 0; installed torch 2.14.0, numpy 2.5.3, matplotlib 3.11.2, and pytest 9.1.1. |
| `system_profiler SPHardwareDataType` | Apple M4 Mac mini, 10 cores, 24 GB memory. |
| `.venv/bin/python -c '<complex64 matrix_exp probe>'` | Exit 0; CPU forward and backward finite. Elapsed compute: 0.005954541 s. |
| `.venv/bin/python -m pip check` | Exit 0; no broken requirements. |

The probe set `torch.set_num_threads(2)` and
`torch.set_num_interop_threads(1)`. It constructed a symmetric real score
matrix, computed `torch.matrix_exp(-1j * 0.1 * H)` in `torch.complex64`,
evolved row states with `psi0 @ U.transpose(-2, -1)`, and backpropagated a
finite scalar loss. Maximum probability-normalization error was
`1.1920928955078125e-07`; maximum unitarity error was
`1.1921255804736575e-07`.

Accelerator checks: `torch.backends.mps.is_built()` was true but
`torch.backends.mps.is_available()` was false; CUDA was unavailable. Direct
`sysctl` hardware queries were denied by the sandbox, so hardware facts above
come from `system_profiler`.
