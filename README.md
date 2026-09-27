# Schrödinger Attention research

Experiments comparing softmax and Schrödinger attention on learned grid-route
policies, including route variation, difficult problem solving, and learning
across training updates.

## Latest reviewed results

The September 27, 2026 update-count pilot completed two paired seeds, with
both models trained for 16,000 updates and evaluated at 13 fixed checkpoints.
Route quality improved beyond 8,000 updates in all four runs. Neither model
met the sustained plateau rule by 16,000. The primary quality milestones showed
no consistent update-saving advantage across seeds. Some route-quality gains
coincided with worse validation KL; the report explains these tradeoffs.

- [Latest research report](execution/update_efficiency/scientific-closeout.md)
- [Independent final review: PASS](execution/update_efficiency/reviews/12-two-pair-closeout.md)
- [Checkpoint measurements and paired comparisons](execution/update_efficiency/runtime-evidence-006-two-pair-scientific-transcription.md)
- [Study status and evidence](execution/update_efficiency/status.md)
- [Four completed runs and saved scores](execution/update_efficiency/attempts/)

The [200,000-update continuation plan](execution/update_efficiency/plan-v4-200k.md)
is being implemented and reviewed. It proposes continuing the same two pairs
from their 16,000-update checkpoints. This snapshot does not contain completed
200,000-update results.

## Paper and research history

- [Research paper](research/schrodinger_attention_research_paper.md)
- [Research paper PDF](output/pdf/schrodinger_attention_research_paper.pdf)
- [Next research steps PDF](output/pdf/next_research_steps.pdf)
- [Original proposal](schrodinger_attention_research_proposal.md)
- [Agent execution protocol](agent_execution_protocol.md)

The paper and PDFs predate the latest update-count pilot. Read the latest
research report above for that study's findings.

## Code and local setup

The implementation is in `schrodinger/`, tests in `tests/`, and experiment
specifications, review records, and measurement drivers in `execution/`.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The implementation uses two Torch CPU threads and one interop thread. The
original bounded workflow uses `.venv/bin/python -m schrodinger smoke` or
the `profile` subcommand. Measured study runs use the decisions and resource limits
documented in their execution directories; installing dependencies alone does
not recreate those local artifacts.

## Artifact coverage

Git contains source, plans, review records, papers, summaries, and selected raw
measurement records, including the latest 16,000-update score JSON files.
Virtual environments, caches, model checkpoints, NumPy archives, and selected
raw artifacts larger than 10 MiB are excluded by `.gitignore`. Their local
copies are retained. Manifests and historical reports can therefore reference
files absent from this repository; this is not a complete execution archive.
Some historical provenance also records absolute paths from the research host.
