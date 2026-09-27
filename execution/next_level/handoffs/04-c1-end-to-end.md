# C1 end-to-end correction — partial handoff

Still C1 only: C2 safety has not been advanced or claimed complete.

- `schrodinger/route_feasibility.py`:
  `70c42285c2a64569b7e78028c07920825f364a1ecfaf7ee8746f6ab75bc766fc`
- `tests/test_route_feasibility.py`:
  `bdb38592422ab0eeee9c2ad6c14bdd5c60173f126c52713637d2de334f914944`
- `execution/next_level/ledger.jsonl`:
  `e6d2a83b0c19406184521f42c8167490e5bfb1a1e676eddef39deb9787f1c00b`

Concrete C1 repairs:

- Evaluation selections are converted from tuple candidates into complete
  map/family/walls/start/goal/distance/M records before novelty analysis.
- Supervised q states are exactly the union of nonterminal states satisfying
  `d(start,state)+d(state,goal)=d(start,goal)`, not arbitrary goal-reachable
  states.
- `test_tiny_injected_whole_pipeline_all_eval_novelty_and_dag_states` runs a
  real injected tiny pipeline through selection, flow, training q/support,
  validation/ID/IL novelty, scientific novelty failure, JSON-native artifact
  writing and JSON reload. It asserts all three evaluation split keys, unique
  train maps, q normalization, support hash, and COMPLETE result semantics.

The legacy `_evaluation_pairs`/`feasibility` helpers are explicitly marked
deprecated and unreachable; `main` invokes `pipeline` only.

Commands: focused **8 passed in 0.64s**; full **75 passed in 1.74s**. No full
inventory or training was run. Next-level ledger total is **16.0s**.
