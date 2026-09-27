# 02d exact evidence assertion

The only source change is the existing parameterized short-circuit test at `tests/test_productive_diversity_v3_data.py:267-271`. In the concrete OK/training + scientific held-out failure parameter case it asserts returned `out["evidence"][0]["stages"]`: routine I family/result, routine L family/NOT_EVALUATED result, all later stages NOT_EVALUATED, and exactly one I held-out call.

Focused command exited 0: 26 passed in 0.76s; full wall 0.8986825s, ledger UUID `53f6a8ff-b3b8-4b89-8c9f-5c38ff136cb3`.

Module SHA-256 unchanged: `4aa4779877781f2b0211397c3938185ad6ec5154040fecdef3d9f7eac7e84f08`.

Test SHA-256: `27eaf0a9a06ce662a2b715c281b3045fdd4bd454c1b7bcdd5204a4b61cc99b01`.
