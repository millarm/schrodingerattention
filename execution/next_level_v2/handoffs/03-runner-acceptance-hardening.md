# V2 runner acceptance hardening

This supplement closes the runner safety/traceability checklist without a
production invocation. The final focused command returned exit code **0**:
`py_compile && pytest tests/test_productive_diversity_runner.py -q`, **5 passed
in 0.47s** (wall 0.596175542s).

- Existing output and existing lock each create a charged, UUID rejection record
  while preserving the external owner; no unowned lock is removed.
- Attempt timers clamp any test override to remaining budget, restore the prior
  signal/timer, charge exactly once, and preserve a completed A artifact plus
  truthful parent FAILED summary/manifest on an interrupted run.
- Technical paths finalize parent summary/manifest then re-raise without B.
  Scientific A/B outcomes retain immutable rung summaries and artifacts.
- Tuple-key dictionaries serialize as explicit key/value records, manifests bind
  recursive outputs and imported helper/source/tests/reviews/config/runtime,
  and the attempt manifest SHA is independently recomputed in test.

| SHA-256 | Path |
|---|---|
| `99a2b8d67f0dcc3ab8b367ba7ec02f8b8b2caa1320a408fe7ff71188938ce72d` | `schrodinger/productive_diversity_runner.py` |
| `8914532f1447db1aa660a94501e990ab5151ef8101e7a9d8b514a92ecf927b74` | `tests/test_productive_diversity_runner.py` |
| `dcbcf59efcc8035700c3f0fb50a8532526c79daab5aa60994ff6f65cc45df7d6` | `execution/next_level_v2/ledger.jsonl` |

V2 local verification charge is **8.745575544s**. No production inventory,
model, or training work occurred.
