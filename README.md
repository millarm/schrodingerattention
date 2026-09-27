# Schrödinger Attention research

Experiments comparing softmax and Schrödinger attention on learned grid-route
policies, including route variation, difficult problem solving, and learning
across training updates.

## Latest reviewed results

The completed early-learning diagnostic scored saved checkpoints every 100
updates from 0–3,000 for two paired seeds. All 124 checkpoint assessments and
14 SA mechanism probes passed independent results review. No new training was
performed.

Across the fixed 800–2,000 window, mean SA-minus-softmax route success was
−0.052 percentage points, with opposite signs across seeds. KL and Brier mean
differences also had mixed seed signs. This does not establish a consistent
early SA advantage in these two pairs.

The sampled KL and Brier minima were at 900 updates for seed 2201 softmax,
700 for seed 2201 SA, and 2,600 for both seed 2202 models. Thus the earlier
sparse grid's 1,200-update minimum was not universal. From 800 to 2,000,
disagreement within oracle support increased in all four models, while the
loss of probability from oracle support changed in both directions. These
observations do not establish uniform overconfidence or a causal mechanism.

- [Accepted conclusions](execution/early_learning/scientific-closeout.md)
- [Detailed results](execution/early_learning/results.md)
- [Independent final review: PASS](execution/early_learning/reviews/07-results.md)
- [Paired numerical summary](execution/early_learning/attempts/final-paired-summary.json)
- [Completed study status](execution/early_learning/status.md)

## Earlier 16,000-update pilot

The September 27, 2026 update-count pilot completed two paired seeds, with
both models trained for 16,000 updates and evaluated at 13 fixed checkpoints.
Route quality improved beyond 8,000 updates in all four runs. However,
validation KL was lowest at the first scored nonzero checkpoint, 1,200 updates,
and was 41–61% worse by 16,000. Brier scores also worsened while policy entropy
fell. Mean entropy nevertheless remains above the oracle's, and total
probability outside oracle support decreases. These aggregate results do not
establish uniform overconfidence or its cause. Later route-quality gains
therefore do not establish better generalization.
The primary quality milestones showed no consistent update-saving advantage
across seeds. Neither model met the chosen Q plateau rule by 16,000.

- [Earlier pilot report](execution/update_efficiency/scientific-closeout.md)
- [Independent final review: PASS](execution/update_efficiency/reviews/12-two-pair-closeout.md)
- [Checkpoint measurements and paired comparisons](execution/update_efficiency/runtime-evidence-006-two-pair-scientific-transcription.md)
- [Study status and evidence](execution/update_efficiency/status.md)
- [Four completed runs and saved scores](execution/update_efficiency/attempts/)

## Research direction

The 200,000-update continuation is **on hold at the user's request** following
[PR #1's critique](https://github.com/millarm/schrodingerattention/pull/1).
No long-run training started. The previous
[continuation plan](execution/update_efficiency/plan-v4-200k.md) is historical;
its launch authority is revoked by the
[hold decision](execution/long_horizon_200k/hold-decision.md).

Read the [early-learning addendum](research/early_learning_refocus_2026-09-27.md)
for the reasoning behind the completed diagnostic. Its findings are linked above.
No further experiment is running, and no 200,000-update results exist. A future
confirmation would need a frozen design, fresh seeds, and independent tuning or
calibration data.

The [probability-diagnostics follow-up](research/probability_diagnostics_followup_2026-09-27.md)
adds state-level analyses of KL changes and distinguishes oracle-support errors
from disagreement among supported actions, following the reviewer's response.

## Paper and research history

- [Research paper](research/schrodinger_attention_research_paper.md)
- [Research paper PDF](output/pdf/schrodinger_attention_research_paper.pdf)
- [Next research steps PDF](output/pdf/next_research_steps.pdf)
- [Original proposal](schrodinger_attention_research_proposal.md)
- [Agent execution protocol](agent_execution_protocol.md)

The paper and PDFs predate both the update-count pilot and the early-learning
diagnostic. Read the accepted conclusions above for the latest findings.

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
For the early-learning diagnostic, the reviewed source, tests, provenance records,
ledger and final paired summary are included. Its large raw per-checkpoint and
probe outputs remain local. The detailed report preserves its original
pre-review wording; the separate final PASS and accepted conclusions record its
completed review without changing the report's audited hash.
Virtual environments, caches, model checkpoints, NumPy archives, and selected
raw artifacts larger than 10 MiB are excluded by `.gitignore`. Their local
copies are retained. Manifests and historical reports can therefore reference
files absent from this repository; this is not a complete execution archive.
Some historical provenance also records absolute paths from the research host.
