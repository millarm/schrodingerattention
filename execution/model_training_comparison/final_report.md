# Model training comparison — completed exploratory study

**Outcome: prescribed baseline-usability gate stop.** Both architectures learn,
but this study does not demonstrate a Schrödinger advantage or useful creativity.
The implementation blocker was resolved and the experiment actually ran. Final
independent results review: **Sol PASS** ([D-final](reviews/D-final.md)).

## Direct answers

**Does Schrödinger learn? Yes, on this one paired seed.** Its held-out Brier score
fell from0.45874 to0.17502; KL(q||p) fell from0.83877 to0.34705. T=1 valid
shortest-route yield rose from0% to20.78%. This is meaningful learning relative
to its initialization and the observed uniform-legal control (both0% sampled
valid-route yield), but below the predefined usability threshold. It is not yet
a robust multi-seed demonstration or a model that reliably solves the task.

**Does it get there differently? Mechanically and computationally, yes; better,
not demonstrated.** At equal1,000 updates, its scores are close to but slightly
worse than softmax. Its measured training-core cost was3.32× higher on this CPU.
The learned evolution changes attention and final probabilities measurably; it
is not the nearly inactive perturbation seen in the earlier classifier experiment.

**Does it yield more useful novelty? Not established.** At equal exposure its
unique valid novel yield is0.415% versus softmax0.488% of sampling attempts. No
quality-matched comparison, seed-level confidence interval, or test release was
reached. This one negative descriptive difference neither proves nor disproves
the proposed small architecture effect. Entropy or invalid outputs are not novelty.

## Fair paired comparison: seed1701,1,000 updates each

Identical shared initialization and all1,000 minibatch digests were independently
verified. Both have70,540 parameters,64 examples/update, fixed architecture and
optimizer. Equal update count means64,000 sampled state exposures, about1.94
dataset-size equivalents, not literal exhaustive epochs under the map-balanced
sampler. All scores below are validation only, map-weighted80% routine/20%
challenge. K32 and temperature1 are fixed. Lower proper scores are better.

| Metric at1,000 | Softmax | Schrödinger |
|---|---:|---:|
| Brier against exact multi-solution teacher q |0.172393|0.175023|
| KL(q||p), nats |0.344901|0.347049|
| Greedy exact shortest-route quality |49.84%|49.01%|
| T1 valid-shortest-route yield |21.17%|20.78%|
| Routine / challenge T1 quality |24.88% /6.32%|24.50% /5.93%|
| Unique valid novel /32 attempts |0.488%|0.415%|
| Unique valid /32 attempts |17.98%|17.81%|
| Novel valid attempt mass (duplicates included) |0.581%|0.488%|
| Invalid attempt rate |78.83%|79.22%|
| Duplicate-valid attempt rate |3.192%|2.970%|
| Known fraction among valid attempts |97.25%|97.65%|
| Training-core seconds |4.750|15.792|
| Entire training-attempt elapsed seconds |68.398|90.683|

The majority of *valid* outputs is known, but the majority of all sampled attempts
is invalid. Therefore the known-valid fraction alone is not a usability success.
No equivalence claim follows from close scores. One independently trained pair is
the replication unit;512 validation problems do not supply512 training seeds.

## Learning dynamics and equal measured time

![Paired learning curves](/Users/gmh-company/codex/schrodinger/execution/model_training_comparison/learning_curves.svg)

At500 updates softmax/SA Brier is0.187984/0.194841; valid-route yield is
17.50%/16.78%. The small novelty ordering reverses between500 and1,000:
0.361%/0.396% at500 versus0.488%/0.415% at1,000. These checkpoint fluctuations
are descriptive, not evidence of a stable gain.

The final equal-time point uses softmax update1,000 at4.750111 core seconds and
SA update300 at4.727015 seconds (SA slack0.49%). No interpolation was used:

| Equal-core-time endpoint | Softmax1,000 | SA300 |
|---|---:|---:|
| Brier |0.172393|0.228011|
| KL(q||p) |0.344901|0.428331|
| T1 valid-route yield |21.17%|9.89%|
| Unique valid novel /32 |0.488%|0.195%|

The measured compute-efficiency comparison favors softmax here. Earlier targets
c/4,c/2,3c/4 used exactly the saved selections in [B1 review](reviews/B1-pair-1000.md).
The first two targets and SA's3c/4 selection exceed10% slack and are coarse
descriptions only; c/4 SA is its real initial checkpoint, not extrapolated training.
All six additional checkpoint evaluations are retained in `equal-time-*` attempts.

Training CE is available at every update; plotted solid lines are100-update means
of map-balanced minibatches. Dashed validation CE uses a fixed scoring bank and
different mixture/teacher-entropy distribution. Full scheduled training-bank
CE/KL/Brier was not recorded: this is an instrumentation limitation. Do not read
the numerical train-versus-validation CE gap as a controlled generalization gap.
Validation teacher entropy is0.372289 nats, so raw validation CE includes that
irreducible component; KL subtracts it. Initial-to-first500-checkpoint Brier20%
improvement crossings are interval-censored in(0,500], not known exact update times.

## What changed inside Schrödinger attention?

The fixed128-state validation mechanism bank shows mean same-hidden-state attention
TV0.0303% at initialization,4.594% at500,4.107% at1,000. At1,000, p95 row TV is
11.80%, mean CLS TV3.130%, and mean projected-output relative RMS difference3.992%.
Mean full-policy TV against the same trained model with dt=0 is2.428% (p95 9.419%);
greedy action disagreement is3.125% of the128 probes. The train64 and validation128
probe artifacts remain separately identified, with per-layer/head/raw distributions.

Mean spectral norm of dt*H grew from0.03089 to0.76726, and mean relative phase
dispersion from0.02147 to0.66742. Thus a scalar dt alone would miss the learned
evolution strength. Numerical invariants pass the frozen thresholds throughout.
On this probe bank, mean CE(dt0)-CE(normal)=-0.02754 nats: disabling evolution
slightly improves this particular sampled proper-score average. This is not a
full-route ablation, an independently trained softmax baseline, or causal proof
about training. It does not establish that evolution adds useful diversity.

## Prescribed continuation and stopping gate

The plan explicitly allows softmax-only continuation after the paired diagnostic.
SA is intentionally not trained beyond1,000 unless the baseline passes; later
softmax results are not an equal-exposure architecture comparison.

| Softmax updates | Greedy quality | T1 quality | Validation Brier | Validation KL |
|---:|---:|---:|---:|---:|
|1,000|49.84%|21.17%|0.17239|0.34490|
|2,000|53.65%|27.14%|0.15684|0.32638|
|4,000|53.65%|29.60%|0.14822|0.32939|
|8,000|53.85%|34.23%|0.16180|0.39556|

Neither mandatory80% greedy nor70% T1 gate passes by8,000. Training stops as
specified, despite ample remaining compute. The80%/70% crossings are right-censored
beyond8,000 for softmax and beyond the observed1,000 for SA; never replace them
with the maximum update as if crossed. Baseline training CE continues downward
(last100-update mean0.38654), while validation proper scores worsen after their
best recorded values. This is descriptive evidence to investigate, not proof of
which encoding, optimization or distribution issue caused the plateau.

The90%-quality operating point, five-pair power pilot, ten-pair confirmatory study,
quality/entropy-matched decoding curves and model-bearing test evaluation are
**NOT_EVALUATED**, not failures inferred from missing data. No threshold, seed,
model setting, dataset or sampling count was relaxed. Longer-run SA usability
remains unknown. No broad claim about language-model creativity is supported.

## Evidence, review and budget

[Raw summary](raw_summary.json) binds the immutable result-file hashes and includes
all scheduled/selected metrics plus training-CE block means. Full per-problem/
per-map outputs, sampler identities, gradient/control summaries, optimizer/RNG
checkpoints and file manifests remain in every attempt. [Command record](production-command-record.md)
indexes retained sessions; every scientific command was launched once and polled
to explicit exit0 before the next launch. Accepted source/configuration and data
were unchanged during production; no final-test model scores were obtained.

Implementation PASS: [A2b3](reviews/A2b3-00.md). Runtime PASS: [A3](reviews/A3-profile-00.md).
Paired result PASS: [B1](reviews/B1-pair-1000.md). Conditional continuation:
[B1 sequence](reviews/B1-continuation-sequence.md). Final results audit:
[D-final PASS](reviews/D-final.md).

Final reviewed operational debit1721.887721588062 seconds of7200, including the
single inherited923.003597253 debit, all recorded tests/failures/profile/runs and
explicit conservative allowances. New stages: A411.4018179169711,
B288.0485042089946, D99.43380220909603, C0. This is not entirely exact measured
time: allowances are labeled in the append-only ledger. Final independent audit
charged4.5 seconds. Remaining5478.112278411938 seconds. The stop is scientific,
not resource exhaustion.

Recommended next proposal: investigate baseline spatial encoding and held-out
generalization under a new frozen diagnostic plan before scaling the SA comparison.
Do not automatically enlarge grids, relax gates, add SA training or claim the
present results demonstrate creativity. No further work is executed in this cycle.
