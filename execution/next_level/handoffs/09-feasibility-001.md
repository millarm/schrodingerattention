# Stage 0 authorized feasibility invocation: feasibility-001

Exactly one authorized invocation was launched:

```text
.venv/bin/python -m schrodinger.route_feasibility --output execution/next_level/attempts/feasibility-001
```

The tool returned an explicit exit code **0** after 12.473s wall time; it did
not yield a session identifier and was not relaunched. The attempt's own
elapsed time was 10.785864792000211s, with 2.0s startup allowance and charged
time 12.785864792000211s. Its timer/ledger entry began from 35.10637700000516s
and ended at 47.89224179200537s, within the Stage-0/global caps.

The process execution completed, but its scientific result is a stop:

| Field | Value |
|---|---|
| execution status | `COMPLETE` |
| scientific outcome | `FEASIBILITY_FAILED_NOVELTY` |
| qualifying IL problems | 6 (required >=256) |
| qualifying IL maps | 3 (required >=16) |
| downstream action | stopped; no alternate maps, model, training, or rerun |

The attempt has evaluated manifest binding and all expected artifacts. SHA-256:

| SHA-256 | Artifact |
|---|---|
| `a221add32428be9f74921b2f5f432c64fcbff08d2b1060339ce2fa4a7d7171a3` | `attempt.json` |
| `df7ff28b308c3bbba16f57d59e53a4e729d9d1e8be9adf5ae2a4d6773f9e0ab4` | `inventory.json` |
| `fb30ad5570ce595cd536e9a750a03f436ab2a1a8d06804e49da95b41d910597e` | `manifest.json` |
| `e907bafab1fdf0f0f52d8dc36fd4d8317649e292331526da8f651cb7e7257678` | `novelty.json` |
| `e8cad99f923a935f41df222872ad99e9907c8dd8b8db3fdac4e56822fcb81d8f` | `selection.json` |
| `5eed3f6addb193d3ca934e9e0c2f0ad656c13523f9bfd3c38ab9b359ae9774cb` | `splits.json` |
| `beef914fe8512dc939850ff62d1b87e973035dd247144664cfe6c5f9caa67f08` | `summary.json` |
| `8e800a7f457e6e2ff6ea3bb9e67a03b504c56f17e2d7a2163421cab441aaa9ee` | `support.bin` |
| `451f76bb3bb1cf42dc84db622e25787324303c7abc77ede673a2169195158355` | `training_states.json` |
| `ff35171c4239b0eb48cd6f068e50e280a388b2532d3011b314e64f742744081e` | `execution/next_level/ledger.jsonl` |

The `attempt.json` binds the output manifest SHA-256
`fb30ad5570ce595cd536e9a750a03f436ab2a1a8d06804e49da95b41d910597e` and its
non-circular output hash table. No files from this output were overwritten.
