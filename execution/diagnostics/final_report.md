# Retained-checkpoint diagnostic

Status: ACCEPTED — Sol result/report audit PASS WITH EXECUTION LIMITATIONS;
see [final review](reviews/05-results.md). Authorized diagnostic complete.

## Answer

Evolution does **not** merely leave attention unchanged. Its effect is mixed
across heads and seeds, with substantial local changes in some heads. Small
net accuracy changes conceal both offsetting prediction changes and rare large
probability/loss changes. These checkpoints show **no consistent useful gain
under the frozen diagnostic benefit band**; they do not establish that evolution
is mathematically redundant or generally ineffective.

This refines, rather than overturns, the original INCONCLUSIVE screening result.
No training, tuning, evolution-strength sweep, or independent-baseline comparison
was performed. This is a same-weights normal-versus-dt0 intervention.

## Design and evidence

The [plan](../../checkpoint_diagnostic_plan.md) froze metrics and descriptive
bands before new results. We analyzed all retained step-2000 Schrödinger
checkpoints (seeds 11/22/33), each with its saved evaluation arrays: validation
seen/d4 plus test seen/d4, heldout/d4, seen/d8 and heldout/d8, separately for
XOR/COPY. There are 13,824 examples and 1,059,840 row records, including separate
head=-1 records for post-projection/hidden metrics.

Direct local comparisons hold each normal-path layer's normalized hidden state,
S and V fixed and compare evolved attention with softmax(S). Full-path dt0
comparisons separately propagate altered states through both layers. Layer-2
propagated differences are not mislabeled as fixed-input effects.

- [Immutable run summary](attempts/checkpoint-001/summary.json) contains all
  240 direct-TV cells, 120 post-projection cells, and 30 downstream cells.
- [Direct-cell table](attempts/checkpoint-001/summary.csv) identifies every
  seed/condition/operation/layer/head/all-row-or-CLS cell and its local-small flag.
- [Row arrays](attempts/checkpoint-001/rows.npz) and
  [per-example arrays](attempts/checkpoint-001/examples.npz) retain absolute and
  signed effects, identities, tails, logits, losses and predictions.
- [Figure](attempts/checkpoint-001/local_vs_downstream.png) facets seed and
  condition, colors XOR/COPY, and plots per-example mean direct TV versus full-path
  absolute probability change. Its common scale exposes rare large effects;
  it is not a substitute for per-head/CLS summaries.

## Attention changes are not uniformly small

Only 70/240 direct cells satisfy mean TV <0.01 and p95 <0.05; 170 do not.
Across these cells, mean TV ranges 0.00553–0.15551, with largest p95 0.21395.
This is probability mass redistributed, not a signed difference that cancels.
The cells are correlated summaries, not 240 independent statistical tests.

For the original primary endpoint, heldout-pair/d4 XOR, mean CLS-row TV is:

| Seed | Layer 1/head 1 | Layer 1/head 2 | Layer 2/head 1 | Layer 2/head 2 |
| --- | ---: | ---: | ---: | ---: |
| 11 | 2.077% | 2.273% | 1.997% | 1.864% |
| 22 | 15.551% | 1.672% | 0.989% | 0.818% |
| 33 | 1.544% | 0.682% | 1.240% | 0.870% |

Seed 22's layer-1/head-1 CLS p95 is 18.515%; its all-query mean/p95 are
12.303%/19.774%. This is appreciable attention redistribution, despite the
earlier near-zero net accuracy intervention result. Other heads are much closer
to softmax; a universal "attention barely changes" explanation is unsupported.

These changes reach the attention sublayer output. On primary XOR, mean direct
CLS projected-output relative RMS change for layers 1/2 is 3.22%/2.18% (seed11),
11.44%/1.53% (seed22), and 1.22%/1.20% (seed33). Reference magnitudes and absolute
RMS values are retained, so these ratios need not hide near-zero denominators.
Mean layer-2 normalized-input absolute RMS differences are 0.01824, 0.10763,
and 0.00832 respectively; layer-1 inputs agree. Thus propagated effects exist
and are measured separately from the direct comparisons.

## Net accuracy hides changed behavior

Primary heldout/d4 XOR, normal versus all-layer dt0:

| Seed | Mean absolute delta-p | p95 absolute delta-p | Prediction disagreement | Normal-minus-dt0 accuracy | CE_dt0 minus CE_normal |
| --- | ---: | ---: | ---: | ---: | ---: |
| 11 | 0.608 pp | 1.275 pp | 5.859% | 0.000 pp | -0.000362 nats |
| 22 | 1.390 pp | 4.551 pp | 1.367% | -0.195 pp | +0.000947 nats |
| 33 | 0.295 pp | 0.103 pp | 0.000% | 0.000 pp | -0.001276 nats |

Seed 11 changes 30/512 predicted classes (15 gains and 15 losses) while its
accuracy remains exactly 58.203%. Hence equal accuracy does not imply identical
decisions. Seed 22 changes 7/512 predictions (3 gains and 4 losses), losing
only one net correct prediction.
Seed 33 changes no primary predicted classes but can still change confidence:
its largest primary XOR absolute probability change is 0.34756, while p95 is
only 0.00103. A mean larger than p95 here reflects a sparse heavy tail, not an error.

Only 13/24 test seed/condition/op cells satisfy the downstream-small band
(mean absolute delta-p <0.01, p95 <0.05, disagreement <1%). Seed33 passes every
test cell; seed11/22 XOR cells do not, primarily because of disagreement or
larger probability changes. Classification labels do not imply every example
is small: for seed11 heldout/d8 COPY, maximum absolute delta-p is 0.99427,
mean absolute loss change is 0.11866 nats, and maximum is 7.20174 nats.

No test condition/operation meets the frozen noticeable-benefit requirement:
equal-seed mean loss benefit >=0.01 nats with positive benefit in at least two
seeds. Heldout/d4 XOR has mean -0.000231 nats (one positive seed); heldout/d8 XOR
has +0.002385 (two positive). COPY benefits vary in sign and have substantial
tails; its largest condition-level mean benefit is +0.007548 nats, below the band.
Do not infer useful interference from isolated beneficial examples.

The best description is **heterogeneous attention changes, mixed downstream
sensitivity, and no consistent net task benefit**. Some cells show downstream
insensitivity; others change decisions or confidence with offsetting gains and
harms. This is not uniformly negligible evolution and not proof of a particular
internal cancellation mechanism.

## Effective evolution scale

Scalar dt alone was not diagnostic. Across all stratified cells, the largest
mean operator norm of dt*H is 0.8303 and the largest example is 1.0083. Primary
seed22 layer1/head1 has mean operator norm 0.7955 and RMS eigenphase 0.2611.
Circular phase dispersion also varies (largest cell mean 0.21595, example
maximum 0.43367). These data do not support treating every head's evolution
as an infinitesimal perturbation solely because dt was conservatively initialized.

For a real Hamiltonian and exactly real zero-phase initial amplitudes, the
first-order probability change vanishes mathematically. That special-case
observation is not a conclusion about these learned, nonzero-phase checkpoints;
no phase/time sweep was needed or performed.

## Verification, execution and limitations

Implementation passed Sol inspection after focused revisions, with 19 diagnostic
tests and 67 total tests passing. Actual-run checks enforce input identities,
saved-data contents, manual/API normal and dt0 agreement, and exact retained
correct/count reproduction with CE tolerance 2e-6. Maximum observed row-sum and
unitarity errors are both 1.19209e-6. Original source/report fingerprints were
verified unchanged. Exact input/source/config identities are recorded in the
[manifest](attempts/checkpoint-001/input_manifest.json).

One all-seed invocation completed in 36.325s elapsed, charged 38.325s including
the conservative 2s interpreter allowance. Pre-run charge was 23.7s. Audit/test
overheads are recorded separately in [ledger.jsonl](ledger.jsonl); final charged
total is 81.225s of the 900s CPU ceiling (9.03%). No paid resources were used.

There was one procedural deviation: Terra printed only the command output at
the 30s tool yield and lost the returned session metadata. It did not relaunch.
The original tool exit code cannot be recovered. Completion was instead
confirmed by the runner's success record, released lock, and an exact OS query
showing recorded PID59118 absent. This is explicitly OS/runner completion
evidence, not a claim that a tool exit code was observed. See the
[run handoff](handoffs/05-run.md). Immutable outputs and their hashes were
retained; no duplicate analysis attempt was selected or overwritten.

A bookkeeping-order error is also preserved: a manually recorded post-run OS
audit allowance was inserted before the run's ledger entry because apply_patch
matched an earlier line rather than appending at EOF. Terra identified the exact
edit; the ledger's physical order must not be read as execution chronology.
No entries were deleted or reordered. An appended clarification and conservative
extra audit allowance preserve the original record and correct total accounting.

The old training-attempt overwrite/provenance limitations and invalid controlled
timing comparison remain. These are three retrospectively selected retained
endpoints on small synthetic tasks; two seeds learned XOR poorly, and descriptive
bands are not confidence intervals or general equivalence tests. The diagnostic
does not establish architecture-wide efficacy, a training-causal mechanism,
sample efficiency, or computational advantage.

Recommendation: stop this authorized checkpoint-only block. The proposed
"almost unchanged attention" explanation is not generally supported; the more
useful follow-up hypothesis is heterogeneous/poorly aligned effects with
offsetting benefits and harms. Any additional training or mechanistic sweep
requires a separate plan and authorization. The original scaling gate remains
INCONCLUSIVE, not a positive result.
