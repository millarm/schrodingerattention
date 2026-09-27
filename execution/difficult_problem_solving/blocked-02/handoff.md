# D0 retained-diagnostic implementation handoff

- Plan SHA-256: `c31c3ee84131ec4e96dbbd42e073a4ec96be63a0b3fc65058a18275714c035fe`
- `analyze.py` SHA-256: `63ecc9c8106c4b313053e0d79fce141fba6629224bd72e0c88f616c6cd761fe7`
- `test_difficult_problem_solving.py` SHA-256: `299b3b2770f0c9b1c7beab2a63c0f6c48a143d8d504e9c256556ce78e5120e05`

The additive D0 module accepts no seed/checkpoint/test options. It uses only
the four fixed fresh seeds, both reviewed owners, retained 1k/2k/4k/8k events,
and validation data. It caches the eight authority-validated owner records,
uses the accepted direct-hex route adapter/verifier, and does not import model
or checkpoint-loading code or any final-test loader.

It calculates all six finite-bag K values, prefix sensitivity, JSON-safe valid-route
counts, distinct-route metrics, duplicate concentration with explicit nulls for
unsolved bags, geometry labels, per-problem support and conditional summaries,
equal-map stratum/geometry summaries, K32 paired challenge map values (16 problems
per map), and the prospective exact-four-seed/eight-map leave-one-map-out gate. The output retains the route-order
limitation and scope flags, source/plan/helper hashes, owner authority evidence,
and argv. The D0 owner uses the authoritative root/ledger and reviewed resource
table with a 56-second alarm; it has not been run.

Focused test command: `.venv/bin/python -m pytest -q tests/test_difficult_problem_solving.py`
returned exit 0: `7 passed in 5.64s`, full tool wall `5.9s` (following earlier
successful `4 passed` / `5.3s` primitive/interface run). It covers finite
bag identities/impossible combinations, prefixes and duplicate/null handling,
equal-map weighting/geometry boundaries, zero/concentrated leave-one-map-out
gate failures, and real retained eight-owner authority parsing with no inference
or test loader, plus JSON-safe composed metrics/support and exact gate input.
Both unique stage-A ledger rows retain full walls. Totals are A `476.50181791697105`,
B `2286.76600491805`, C `0`, D `479.89767720810573`, global `4166.169097296126`.
