# Block 1 — exact attention

Prerequisite: Astra accepts frozen experiment contract and runtime. Read contract
and original plan. Objective: reusable conventional/exact attention and all
numerical evidence, before dataset/model harness work.

Terra may create `schrodinger/__init__.py`, `schrodinger/attention.py`,
`tests/test_attention.py`, `execution/logs/01-*`,
`execution/handoffs/01-attention.md`. May update requirements only to pin installed
dependencies. No dataset, classifier, training harness, source-plan edits.

Implement a reusable score-level function plus multihead attention module with
softmax and exact modes, identical QKV/output interfaces, projected tensors
[batch,heads,length,head_dim]. Return optional diagnostics without retaining
graphs in logging. SA per-head bounded parameters as contract; dt=0 override
must compute the full exact formula (do not special-case to baseline). Float64
inputs support complex128 for gradcheck; normal float32 uses complex64.
No unconditional renormalization. Use torch matrix_exp, never approximation.

Tests: all contract numerical checks across sequence lengths 4,11,15; score
magnitudes 0.1,1,3; random non-symmetric S for explicit column-state orientation
reference; finite gradients including gamma/dt and Q/K/V; gradcheck a small
double-precision score/value/phase/time case. dt=0 equality at probability,
output, and full copied-parameter multihead levels. Fixed random tiny regression
optimization at module level, <=30 Adam steps, final MSE lower than initial,
no NaNs. Use tolerances in frozen contract. Write numeric maxima as JSON or
test output alongside pytest evidence, not assertions alone.

Permitted commands: local Python/pytest, hashing, read-only inspection. CPU
threads2/inter-op1; at most300 elapsed compute seconds this block, ledger
entry with actual elapsed tests/probes. No full training. If tests fail, retain
logs and correct within spec; material spec questions return to Astra. Handoff
must list changed files, SHA256, commands/exit codes, evidence and limitations.
Freeze code when handing off to Sol. Acceptance: independent Sol PASS and all
checks with actual numerical evidence; no dependent block before acceptance.
