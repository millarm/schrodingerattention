# D1 literal evaluator-smoke handoff — static only

`tests/test_difficult_problem_solving_d1.py` SHA-256:
`99049e972e0d58d55cfe122591b30d5ca5b88b6edcf58ea70b1f87267c485958`

Unchanged source SHA-256:
`b881a7068ab9f82b92220bc87b3d166a78d8c482fd5044e1c61bde322792d5b0`

Unchanged watchdog SHA-256:
`96aa33a1fc6268276d6d0879545b9d974b14fd73d2452d5b1e22e519e5815bf2`

Only `test_actual_evaluator_counter_and_common_uniform_warm_cache` was changed.
It now uses the accepted 144-byte all-open map and `Problem` shape, derives the
east index from `ACTIONS`, and sends deterministic east-only logits through the
accepted evaluator and actual `CountingModel`. Lines 33–40 assert exactly one
cold forward/batch state, 32 valid one-action east byte routes, 32 actions, Q=1,
and U_valid=1/32. Lines 42–47 assert zero new warm/T=.5 forwards or states and
the identical ordered routes. Lines 48–50 assert repeated common-uniform digest
equality and different-seed inequality.

Commands not run: tests, Python imports, checkpoint loads, inference, production,
and ledger writes. This narrow test change is not full repair completion, static
PASS, or smoke-run authorization.
