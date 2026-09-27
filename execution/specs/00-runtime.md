# Block 0 runtime preparation

Objective: establish the local runtime and measure hardware availability before
freezing the comparison. Read the three original markdown files in full.

Terra may create `.venv/`, `requirements.txt`, `execution/runtime.json`, and
`execution/handoffs/00-runtime.md`, and runtime logs under `execution/logs/`.
No model or experiment implementation yet. No edits to existing source documents.
Use bundled Python 3.12 at
`/Users/gmh-company/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`
or Homebrew Python 3.12 to establish a project venv. Install torch, numpy,
matplotlib, pytest through pip as necessary. Network/sandbox escalation for
routine local dependencies is in scope; no paid resources.

Inspect Python/package versions, actual machine model if permitted, CPU count,
memory if observable, MPS availability, and a tiny complex64 CPU matrix_exp
forward/backward. No full training. Use one CPU worker configuration with
torch threads=2 and interop threads=1. Log commands and outcomes, elapsed
compute seconds for the tiny probe, and unavailable hardware measurements
explicitly. Acceptance: exact complex64 matrix_exp and finite backward work,
versions captured, reproducible environment available. Stop after 5 minutes
compute or a genuine dependency blocker. File edits use apply_patch.
