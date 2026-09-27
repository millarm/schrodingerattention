# Three-way diagnosis implementation handoff

No inference, training, test-set access, or production attempt was run.

`threeway_diagnosis_job.py` (`410a285f6acd63b19da78e33caad621612e598f21786c62ccd372e7faf53caed`) implements the frozen A/B/C construction: canonical-byte ranked fixed map triplets, map-local unseen B goals from exact BFS, direct start-q route bins, state DAG bins, deterministic three-cohort round-robin quotas, A/B complete saved-state overlap checks, and an eight-triplet-per-family pre-inference stop. The complete candidate counts, quotas, retained identities, cohort hashes, and exclusions are saved to `matched_support.json` before checkpoints are loaded. Matched banks are direct `ScoreBank` records, so no secondary selection/downsampling can change state rows. B uses exact BFS `M` and `Mnovel=None`.

If support passes, the only inference checkpoints are 1000/4000/8000, guarded against the common initial checkpoint identity. Proper scores retain CE/KL/Brier/nonoptimal mass rows plus routine/family/per-map aggregates; greedy and T1/K32 retain exact route attempts. A/B use split code 0 and C split code 1, with supplied saved training support.

Focused tests (`1cb8dfee092facf07bab29a78a1396e592287cc07752e38e90804bea3c4b5a82`) passed: `3 passed in 0.69s` via `.venv/bin/python -m pytest -q tests/test_threeway_diagnosis.py`. They cover the literal prefix, real open-12x12 BFS/q and map-local suffix goal exclusion, cross-map coordinate behavior, A/B overlap failure, deterministic unequal-supply joint quotas, and unsupported-triplet exclusion. The existing ledger records the earlier failed/pass development attempts; this implementation did not add an inference charge.

Sol review is required before any diagnostic job is authorized.
