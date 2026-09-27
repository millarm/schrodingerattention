# Single pool512 production process

Exact implementation accepted by Sol01 before launch. One command:
```sh
OMP_NUM_THREADS=2 MKL_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 .venv/bin/python -m schrodinger.productive_diversity_v3_pool512 --output execution/next_level_v3_pool512/attempts/feasibility-001
```

Initial full tool result:
```json
{"chunk_id":"7a7d6b","wall_time_seconds":1.002560375,"session_id":99474,"original_token_count":0,"output":""}
```
Same-session intermediate result:
```json
{"chunk_id":"e48f9f","wall_time_seconds":60.002335042,"session_id":99474,"original_token_count":0,"output":""}
```
Final full tool result:
```json
{"chunk_id":"eda8cd","wall_time_seconds":43.102712208,"exit_code":0,"original_token_count":48,"output":"{\"manifest_sha256\":\"305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395\",\"outcome\":\"FIRST_FULL_DATASET_PASS\",\"output\":\"execution/next_level_v3_pool512/attempts/feasibility-001\"}\n"}
```

The one retained session was polled to explicit exit0; no relaunch/concurrent
compute. Runner-generated UTC2026-09-16T11:14:10.543594 through11:16:39.236205;
measured148.691623834s, plus2s allowance, uniqueledgerUUID
dbc47aff-154c-43df-ae5b-acaddad64d8d. Lock absent after explicit exit.
Prior operational748.727212044s; after-run899.418835878s.

All512maps/family reached under unchanged200000trial cap: I38962, L25404,
mixed31942 trials. Rawranking retained12–14,14–16,16–18; first failed mixed
validation, second completed all required splits, third stayed NOT_EVALUATED.
No resampling, threshold changes, pool extension beyond512 or model training.
Independent retained-results audit follows before final acceptance.
