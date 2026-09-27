# V2 runner final correction handoff

No production inventory, model, or training command was run. The final combined
focused command already completed with explicit exit 0: `.venv/bin/python -m
pytest tests/test_productive_diversity_data.py tests/test_productive_diversity_runner.py -q`
— 14 passed in 0.63s (wall 0.725237625s).

| Sol finding | Function(s) | Direct assertion / boundary |
|---|---|---|
| Real composed path | `run_rung`, `training_dataset`, `training_states_and_support`, `novelty_for` | Tiny composed test does not replace `run_rung`; injected selection only, real explicit-8x8 orientation gate, q/support hash/state artifact and real routine novelty run in all four stratum callbacks. Full production count/flow feasibility is explicitly not claimed. |
| Status/count/config provenance | `run_rung`, `_manifest` | Per-rung `NOT_EVALUATED`/COMPLETE stages, observed/required counts, frozen rung seeds/families/lengths/pool/caps/order and recursive output/source hashes. |
| Technical/deadline finalization | `execute`, `Attempt.persist` | Technical exception produces parent FAILED summary/manifest and no B; deadline after completed A artifact preserves A file plus parent summary/manifest. |
| Ownership/write safety | `Attempt.__enter__`, `reject`, `cleanup`, `persist` | Existing output/lock and post-lock mkdir race are charged REJECTED while foreign owner survives; injected attempt-log fault yields exactly one FAILED ledger charge, timer/owned lock cleanup. |
| Shared bounded cache / challenge predicate | `OracleCache`, `stratum`, `run_rung` | One cache is passed through all four strata. The real .25/.75 challenge predicate remains in the pure-engine real-oracle fixture; composed runner fixture intentionally asserts routine novelty only and does not fabricate challenge feasibility. |

Current SHA-256:

| Hash | Path |
|---|---|
| `e2e2b93a72afac114f68c1add3881aaa89898dbeb1f6a22c2ac00cf3a8faae09` | `schrodinger/productive_diversity_data.py` |
| `628aa0e784b4712cae3d8c81cb79f5aacb877b6d4edb3c7dac9e9fb54adac73f` | `schrodinger/productive_diversity_runner.py` |
| `93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471` | `tests/test_productive_diversity_data.py` |
| `eba489e559b3c0344c3d03c86ab81190733c35952dcd7edd9b43fa08970f66eb` | `tests/test_productive_diversity_runner.py` |
| `85365eca0ef71b23996ec78513673cf4cc443af96f81835040a2b6524201d5de` | `execution/next_level_v2/ledger.jsonl` |

All completed focused commands are append-only charged in the v2 ledger. Its
cumulative verification charge is **10.071845336s**; no prior row was altered.
