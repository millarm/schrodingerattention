# Stage 0 substep B pipeline handoff

Implementation is frozen for Sol’s complete Stage-0 review; no full inventory
CLI execution was launched.

| SHA-256 | Path |
|---|---|
| `60684723ab541dba1e147c8f0286ed78978d7c04173214a1b98251815d39b9cd` | `schrodinger/route_feasibility.py` |
| `60915a1c8f7c5fce2776017a078f1d63db67ceb146c2562c9fc5f78a7657bc1c` | `tests/test_route_feasibility.py` |
| `ca8e8caccee56fa726d947c40ea83fa874e4bb78aa89ed09f050f50ef55be9a9` | `execution/next_level/specs/02-pipeline-completion.md` |
| `54ccaedc9b6bba021f88a8d53dba9901ce8df4bd8d19d33e8bc32674c5bebf50` | `execution/next_level/ledger.jsonl` |

The CLI code path now creates the complete canonical inventory, frozen disjoint
split selection, training/evaluation problem selections, bin quotas/residual
flow, supervised suffix support binary, per-IL route signatures/M_novel records,
and strict novelty-gate summary. Selection failures raise frozen evidence rather
than resampling. Feasibility novelty failure remains an execution-complete
scientific outcome. The isolated next-level Attempt owns its O_EXCL lock/output,
uses a real stage timer, separate rejection records and its own advisory-locked
ledger; it never imports or writes the prior diagnostic ledger.

Selection refinements from the B preflight are included: typed numeric flow-node
ordering and one continuous per-family problem RNG that independently permutes
each cell list while maps/cells are traversed in frozen lexical order.

Verification: focused route fixtures **6 passed in 0.46s**; full suite
**73 passed in 1.59s**. Stage-0 ledger total is **10.0s**. No full inventory,
training, model, or later-harness work was run.
