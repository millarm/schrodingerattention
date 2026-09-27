# Execution complete — INCONCLUSIVE

Authorized 2026-09-15. Astra supervised and decided; Terra implemented;
Sol independently reviewed. No further training or scaling is authorized.

## Deliverables

- [Research report and recommendation](final_report.md)
- [Machine-readable summary](results/summary.json) and [CSV](results/summary.csv)
- [Learning curves](results/learning_curves.png)
- [Retained raw runs/checkpoints](results/measured/)
- [Reusable attention](../schrodinger/attention.py), [generator](../schrodinger/data.py), [training/evaluation CLI](../schrodinger/experiment.py), [numerical tests](../tests/test_attention.py), [summary CLI](../schrodinger/summarize.py)

## Accepted blocks

| Block | Status | Evidence |
| --- | --- | --- |
| 0: contract/runtime | ACCEPTED | [contract](experiment_contract.md), [contract review](reviews/00-contract.md), [runtime review](reviews/00-runtime.md) |
| 1: numerical attention | ACCEPTED | [handoff](handoffs/01-attention.md), [PASS review](reviews/01-attention.md) |
| 2: dataset/model/harness | ACCEPTED | [PASS review](reviews/02-harness.md), [handoff](handoffs/02-pair-validation.md), [verified inventory](manifests/02-current.sha256) |
| 3: execution audit | ACCEPTED as INCONCLUSIVE record | [audit](reviews/03-comparison.md), [corrected handoff](handoffs/03-comparison.md), [provenance limitations](logs/03-run-provenance.md) |
| 4: summary/decision | ACCEPTED | [PASS review](reviews/04-summary.md), [handoff](handoffs/04-summary.md), [report](final_report.md) |

The retained equal-update endpoints are internally coherent descriptive
evidence. Controlled timing and equal-time comparisons are **INVALID**:
eight training launches included duplicate paths with unproven non-overlap;
earlier attempt artifacts may be overwritten. There were five pair evaluations
(four success, one failure). No favorable duplicate selection or missing
provenance is inferred. Mean validation XOR also fails the frozen learning
adequacy gate, independently requiring INCONCLUSIVE.

## Compute accounting

Final conservative charge: **393.950634582 seconds** (6.57 minutes, 0.1094
CPU-hours) against the 14,400-second / four-hour ceiling. This includes all
recorded attempts/failures and explicit historical overhead allowances; it
is not reconstructed actual device wall time. Sum `charged_seconds` in the
[ledger](compute_ledger.jsonl); historical cumulative fields are not authoritative.
[Reconciliation notes](ledger-reconciliation.md) preserve the accounting history.

The experiment used CPU on an Apple M4 Mac mini, 10 cores, 24 GB, PyTorch
2.14.0; MPS was unavailable. The frozen endpoint was 2,000 updates / 128,000
examples per model for seeds 11, 22, and 33. [Decisions](decisions.md) retain
the specifications, corrections, acceptances, and no-rerun boundary.
