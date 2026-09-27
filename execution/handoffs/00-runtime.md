# Block 0 runtime handoff

## Summary

Created the isolated `.venv` runtime from the bundled Python 3.12.14 and
installed the required local packages. Exact CPU `torch.complex64`
`matrix_exp` completed a finite forward and backward probe with the required
Torch worker settings: two CPU threads and one interop thread. The usable
runtime is CPU-only: PyTorch was built with MPS support but reported MPS
unavailable, and CUDA was unavailable.

## Changed files and reviewed version

This workspace is not a Git work tree, so no commit identifier is available.
The exact files for review and their SHA-256 hashes are:

| File | SHA-256 |
| --- | --- |
| `requirements.txt` | `7f3afea068a167c68c7dc0c7f5bd634d99fdb46a8e4d4119c753ca2974462f25` |
| `execution/runtime.json` | `805b8c51fd21468ccb2f5c70bc122b52bf13f601331937e9979efcc5c5184995` |
| `execution/logs/00-runtime.md` | `012a8d0fc939da342cde35b96ff98c5a1fa78309fc136a99f667d5042ab31fc9` |

`.venv/` is a generated local environment (827 MB) and is not presented as a
reviewed source file.

## Commands and evidence

The complete command summary and outputs are in
[`../logs/00-runtime.md`](../logs/00-runtime.md). All listed commands exited
0. The relevant results are also machine-readable in
[`../runtime.json`](../runtime.json):

- `torch 2.14.0`, `numpy 2.5.3`, `matplotlib 3.11.2`, and `pytest 9.1.1`;
- Apple M4 Mac mini, 10 CPU cores, 24 GB memory (from `system_profiler`);
- tiny CPU complex64 probe elapsed `0.005954541000392055` compute seconds;
- finite forward values and gradients; maximum probability-normalization and
  unitarity errors of approximately `1.19e-7`;
- `pip check` reported no broken requirements.

## Deviations, limitations, and questions

No model or experiment code was created, and no training was run. The only
environment caveat is that PyTorch's MPS backend is built but unavailable to
this process; planned work must therefore remain on CPU unless this changes.
Direct `sysctl` measurements were sandbox-denied, but `system_profiler`
provided the hardware model, core count, and memory. Pip emitted a harmless
warning that its global cache was not writable; installation and validation
succeeded. The runtime preparation meets the block specification's acceptance
criteria and is ready for Sol's inspection and Astra's next decision.
