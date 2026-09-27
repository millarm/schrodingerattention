# Completed-run pair validation handoff

Current pair helper SHA-256: `schrodinger/experiment.py` `cf75e1b35fe6fb1fb462d78d415ea60115dcd267957303ef56427861ae55c288`; pair tests `e701e44dbdc3e3e3417b2b26fb5207c2b6f250abdbe68a7e4a430eadd2c5a216`; current existing-102 pair artifact `execution/results/block2-revision2-final/pair-validation.json` `0a372b495a064accb850dbe73ff3a13663c5851804f865349f61640c791776af`.

`pair_evaluate` now rejects incomplete/empty streams, raw JSONL beyond final checkpoint, unequal final completed steps, mismatched completed stream digest, data/seed/mode/config/source/initial identity mismatch before endpoint evaluation. It emits verified final steps and identities. Full suite command `.venv/bin/python -m pytest -q` exited 0: 47 passed in 1.27s. Existing102 command `python -m schrodinger pair-evaluate --checkpoint execution/results/block2-revision2-final/softmax --other execution/results/block2-revision2-final/schrodinger --output execution/results/block2-revision2-final/pair-validation.json` exited 0.

No training code changed; the existing 102-step checkpoints retain their training source hash, while this handoff records the current evaluator hash. No measured comparison ran.

Evidence-only update: the complete checksum inventory is [`../manifests/02-current.sha256`](../manifests/02-current.sha256). Canonical audited preparation charge is 211.145719958 seconds (180 + 30 allowance + current measured command charge), while original ledger history remains preserved.
