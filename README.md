# Schrödinger Attention research

Experiments comparing softmax and Schrödinger attention on learned grid-route
policies, including route variation, difficult problem solving, and learning
across training updates.

## Latest reviewed results

The September 27, 2026 update-count pilot completed two paired seeds, with
both models trained for 16,000 updates and evaluated at 13 fixed checkpoints.
Route quality improved beyond 8,000 updates in all four runs. However,
validation KL was lowest at the first scored nonzero checkpoint, 1,200 updates,
and was 41–61% worse by 16,000. Brier scores also worsened while policy entropy
fell. Later route-quality gains therefore do not establish better generalization.
The primary quality milestones showed no consistent update-saving advantage
across seeds. Neither model met the chosen Q plateau rule by 16,000.

- [Latest research report](execution/update_efficiency/scientific-closeout.md)
- [Independent final review: PASS](execution/update_efficiency/reviews/12-two-pair-closeout.md)
- [Checkpoint measurements and paired comparisons](execution/update_efficiency/runtime-evidence-006-two-pair-scientific-transcription.md)
- [Study status and evidence](execution/update_efficiency/status.md)
- [Four completed runs and saved scores](execution/update_efficiency/attempts/)

## Current direction: early learning

The 200,000-update continuation is **on hold at the user's request** following
[PR #1's critique](https://github.com/millarm/schrodingerattention/pull/1).
No long-run training started. The previous
[continuation plan](execution/update_efficiency/plan-v4-200k.md) is historical;
its launch authority is revoked by the
[hold decision](execution/long_horizon_200k/hold-decision.md).

Read the [early-learning addendum](research/early_learning_refocus_2026-09-27.md)
for the corrected interpretation and next questions. The next block will inspect
saved checkpoints in the first 3,000 updates to compare learning rates, find the
sampled minimum, and bracket where proper scores begin worsening. New evaluations require a reviewed
specification; no 200,000-update results exist.

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
