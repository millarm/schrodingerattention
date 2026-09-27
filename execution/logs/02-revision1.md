# Block 2 revision 1 execution log

Superseded Block 2 artifacts remain preserved. Revision smoke, profile, mode-selected train, checkpoint evaluation, and pair evaluation were run locally. One throughput profile attempt failed before work began because `eval_count=0` was treated as an evaluation request; it was corrected to skip evaluation and the rerun completed. No measured comparison run was started.

The latest verification command was `python -m pytest -q`, exit 0, with 29 tests passed in 1.03 seconds. Revision3 smoke and corrected profile exited 0.
