# Authorized checkpoint diagnostic run 001

## Single-launch and completion provenance

The sole authorized analysis invocation was launched once:

```text
.venv/bin/python -m schrodinger.checkpoint_diagnostic --output execution/diagnostics/attempts/checkpoint-001
```

The launch tool was called with a 30-second yield, but its rendered response
contained only Matplotlib cache warnings: no `session_id`, `exit_code`, or
`functions.wait` cell ID was returned because the wrapper rendered `r.output`
rather than the complete command result. This is an explicit tool-provenance
limitation; no relaunch occurred.

Read-only OS completion evidence, obtained after the launch:

- `attempt.json`: `status: success`, `error: null`, PID **59118**, elapsed
  **36.325354833003075s**, charged **38.325354833003075s**, start
  `2026-09-15T19:47:42.206602+00:00`, end `2026-09-15T19:48:18.112789+00:00`.
- The global diagnostic lock was absent.
- Escalated `ps -p 59118 -o pid,ppid,etime,command` rendered an explicit tool
  result with **exit_code 1** and only its header, proving the recorded PID was
  absent. This, plus the successful final attempt record and absent lock, is
  OS-level completion evidence—not a substitute for the unavailable original
  tool exit code.

## Artifacts and hashes

| SHA-256 | Artifact |
|---|---|
| `79dbf48fd17f65bd78ecb04b528bc33d449dfb0a555961e46194b8a4b9a54482` | `attempt.json` |
| `ed678bb78eff3ed8d0fb2ec423ed1b1c0b57ac08e6bef7ecb5c9020eb10d8b20` | `input_manifest.json` |
| `8b9ba74643de22c383f7c3e6f0af6a9995254a23f229c5e41302177806e833ea` | `runtime.json` |
| `7e5dc48f2663e08110517e82dc14887079b47bbe30bf189556bcf146eac1c9c9` | `rows.npz` |
| `4c76334579532bbfbb5629d1cb3282870b09eda5419b78eb05d752fcb602ea5e` | `examples.npz` |
| `2e81d2037604287dfe3a041f42ba2aa31e9ca410ec91d23c1b36a8fe10ebd9b5` | `summary.json` |
| `3568b1315531634cca1e6a2a2b0fea65c8eadb788b92190c6fbfc1947224b632` | `summary.csv` |
| `e857568b047fd5005fa344fd7d9d87da62189918e64d8bf35abb521be838abd7` | `local_vs_downstream.png` |

All paths above are under
`execution/diagnostics/attempts/checkpoint-001/`. The run produced 1,059,840
row records, 13,824 per-example records, 240 direct cells, 120 projected cells,
and 30 downstream cells. Numerical checks passed for all 15 seed/condition
sets; maximum stored row error was 1.1920928955078125e-06 and maximum stored
unitarity error was 1.1920928955078125e-06.

## Frozen outputs requiring results audit

- `uniformly_local_small` is **false**.
- Every test-condition/op `noticeable_benefit` flag is **false**; these are raw
  retrospective diagnostic outputs, not a new training decision.
- Full stratified values, direct-cell flags, downstream loss/probability tails,
  and manifests remain in the immutable attempt artifacts for Sol audit.

## Ledger

The attempt charged 38.325354833003075s including its 2-second startup
allowance. A conservative 1.0s read-only OS completion audit was appended after
the attempt. `execution/diagnostics/ledger.jsonl` hash after that audit is
`e6eaa6efb0b9379758ef32d51f0364a56fda97c853d5d0e5e03642b3c69fe1c0`.
No additional analysis run was launched.
