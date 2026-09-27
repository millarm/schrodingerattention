# Block 3 comparison handoff

Block 3 has **eight successful measured training attempts** (including duplicate-path seed22-softmax and seed33-Schrödinger follow-ups) and **five pair-evaluation attempts** (**four success, one failed** seed22 `raw JSONL extends beyond completed checkpoint`). Duplicate output paths may have overwritten prior checkpoints/JSONL; process non-overlap is unproven after 30-second waits. Therefore timing and equal-time comparisons are **INVALID**. Full chronology, failures, surviving paths, and limitations are in [`../logs/03-run-provenance.md`](../logs/03-run-provenance.md).

The surviving final artifacts have internally matching paired stream, initialization, and evaluation identities for seeds 11, 22, and 33. Equal-update descriptive metrics may be inspected only as internally valid surviving artifacts; they are not a clean six-run comparison because of the provenance limitations above.

No implementation changes were made in Block 3. This handoff supports an **INCONCLUSIVE** audit, not a valid timing/equal-time research conclusion.
