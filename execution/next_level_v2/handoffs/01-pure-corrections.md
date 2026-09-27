# V2 pure-engine correction handoff

This closes the three Sol review02 findings only. No runner, artifact wrapper,
production pool, model, or training code was added or executed.

1. **Canonical component/frame audit.** `wall_components`,
   `classify_component`, and `family_component_orientations` reconstruct
   disconnected canonical wall components and classify I as H/V and L by its
   missing 2x2 corner (TL/TR/BL/BR). Malformed component count, shape, or
   family-kind mismatch raises `OracleIntegrityError`. `orientation_coverage`
   exposes auditable selected-map coverage, while
   `require_training_orientation_coverage` makes missing 2+4 coverage a frozen
   scientific `ConstructionFailure` for the later training selection gate.
   `test_canonical_component_orientation_classification_and_family_validation`
   covers all six orientations and technical family mismatch.

2. **Ladder evidence/taxonomy.** Both scientific rung failures now survive as
   `{outcome, evidence}` under A/B in `DATASET_LADDER_FAILED`; its explicit
   cause is the original A failure. Technical exceptions remain uncaught, so B
   is not attempted. `test_training_engine_global_flow_exact_counts_and_ladder_policy`
   checks A-fail/B-pass, first-A-pass stopping, technical-no-B, and exact
   distinct A/B retained payloads. Taxonomy is now restricted: only frozen map
   supply, length flow, and missing training orientation coverage are
   `ConstructionFailure`; pool identity, count, and oracle mismatches are
   technical errors.

3. **Route multiplicity integrity.** Both `eligible_novelty_pairs` and
   `novelty_for` verify `len(enumerated routes) == candidate M` before any
   novelty ratio or classification. A mismatch raises `OracleIntegrityError`.
   `test_candidate_multiplicity_mismatch_is_technical_before_novelty_classification`
   exercises both paths and proves the ladder does not start B.

Focused command:

```text
.venv/bin/python -m py_compile schrodinger/productive_diversity_data.py && \
  .venv/bin/python -m pytest tests/test_productive_diversity_data.py -q
```

Final execution returned explicit exit code **0**: **7 passed in 0.66s**
(external wall 0.782155209s). A preceding focused pass was also 7 passed in
0.58s (wall 0.704541792s); both records are retained in the v2 ledger. No
production data generation occurred. Cumulative v2 local verification charge is
**5.158533168s**, below the 150s ceiling.

| SHA-256 | Path |
|---|---|
| `6c9c4099c1b98d486511087c3c50d72ab3b885e9b58ad019911b47741efb3ed5` | `schrodinger/productive_diversity_data.py` |
| `93ba9890c72b6e63300ab247aa85d0bb8cedbe84c552f0d56b67e401134db471` | `tests/test_productive_diversity_data.py` |
| `3d4de5d5c66ca99bb0d0cf0d3fad3fa6561141b73065958956a2b66f575bf64e` | `execution/next_level_v2/ledger.jsonl` |
| `67d28a6d6884da6cfa4980a320534774e9a87ee523cbec56d4258b49f47588de` | `execution/next_level_v2/specs/00-dataset-contract.md` |
| `e902cefe792bb8ca0f6412d923181fd71a6b7da4786a73365f4ce5025e510950` | `execution/next_level_v2/reviews/02-pure-engine.md` |

The separately specified runner block was read for scope only and remains
unimplemented pending Sol acceptance of this pure correction.
