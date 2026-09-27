# V2 Stage 0 pure-data engine handoff

This first block adds only the new pure-data module and its injected-fixture
tests. It adds no CLI, attempt wrapper, artifact writer, production inventory,
model, or training code; previous source and artifacts were not edited.

## Implemented pure engine

- Frozen A/B rung, family, length, pool and split-stream constants; n=8-only
  geometry/oracle calls; deterministic sorted triomino placements and bounded
  component pool rejection order (overlap, touch, D4 duplicate).
- Globally canonical map IDs, candidate enumeration, disjoint map splits,
  continuous per-family map/problem PCG64 streams, Hamilton integer quotas and
  global deterministic residual flow with map capacity 16.
- Exact DAG q supervision, all nonempty shortest suffix-signature support and
  digest, routine/challenge novelty criteria, and a pure ladder that advances
  to B only after an ordinary construction failure.
- Bounded `OracleCache` stores only BFS facts and route signatures (never full
  route lists). Stratum eligibility now considers only requested families and
  nonexcluded maps, shares the bounded cache with selected-record novelty, and
  preserves frozen selection semantics.

## Injected-fixture tests

- `test_explicit_n8_pool_component_rejections_d4_and_replay`: explicit n=8,
  positions beyond cell 35, replay, overlap/touch rejection precedence and D4.
- `test_candidates_q_and_support_use_explicit_n8_and_independent_routes`:
  exact route multiplicity, q values/sums within 1e-12 and brute suffix support.
- `test_hamilton_nonuniform_reverse_flow_and_continuous_family_problem_streams`:
  literal nonuniform quotas, reverse-edge flow and continuous RNG consumption.
- `test_split_exclusions_support_and_exact_novelty_ratio_endpoints`: disjoint
  family splits; real-signature routine 0 and challenge .25/.75 endpoints.
- `test_training_engine_global_flow_exact_counts_and_ladder_policy`: legitimate
  earliest length-flow failure, A-to-B only for construction failures, first-A
  pass stop, and no B after a technical exception.

## Commands, charge, and scope limit

Final focused command:

```text
.venv/bin/python -m py_compile schrodinger/productive_diversity_data.py && \
  .venv/bin/python -m pytest tests/test_productive_diversity_data.py -q
```

It returned explicit exit code **0**: **5 passed in 0.59s**, external wall
0.721122625s. No production-scale pool generation occurred. The separate v2
ledger retains every small local verification run/failure and totals
**3.671836167s**, below the 150s Stage-0 test ceiling.

| SHA-256 | Path |
|---|---|
| `1d05d26073426c86a45e2c29483cf11d03e96db96ef3370261db3ca79d264a55` | `schrodinger/productive_diversity_data.py` |
| `65375fbb6515108b2c28f83732495616ec841bd97adf7747890a19bc429481ab` | `tests/test_productive_diversity_data.py` |
| `110fabfe4b94df5f73d51a85a3e00acf074fceb525e75815702c2f010fffec7e` | `productive_diversity_v2_plan.md` |
| `1dc21a4314e6d66510eb31ba176d673ab44709925f5155da189e436f8900a9c4` | `execution/next_level_v2/specs/00-dataset-contract.md` |
| `751d1198d6554e0979a35fc5ba7c499947af205ba07038e6271aac97190b3a28` | `execution/next_level_v2/reviews/01-plan-contract.md` |
| `d5f83b2949eb41d1a4fe942e2cccc40d8307968eace4e27ed4e2a504f1ac6dca` | `execution/next_level_v2/ledger.jsonl` |

This handoff does not assert production dataset feasibility. A later accepted
block may add only the minimal wrapper/artifact/attempt integration.
