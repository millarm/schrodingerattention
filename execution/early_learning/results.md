# Early-learning descriptive results

Source: the completed paired audit only,
`attempts/final-paired-summary.json` (SHA-256
`c2091f89171a8ab2aa3f3733c33234ec7f05ad92cb288cd7026384d857a394ba`), plus
its hash-bound per-owner score/probe artifacts. No new scoring or analysis run
was performed for this note. Sol's independent results review remains pending.

## Primary window: updates 800–2,000

The primary window contains 13 equally spaced checkpoints. Q is shown as
percentage points; its slope is percentage points per 1,000 updates. KL and
Brier values/slopes retain their raw units. Within the two observed seed pairs,
SA-minus-softmax signs vary as shown below; equal-seed averages are descriptive.

| Seed / mode | Q mean (%) | Q slope (pp / 1,000) | KL mean | KL slope / 1,000 | Brier mean | Brier slope / 1,000 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2201 softmax | 28.881 | 4.029 | 0.294356 | 0.015419 | 0.145732 | 0.001468 |
| 2201 SA | 29.024 | 2.202 | 0.294174 | 0.014670 | 0.144838 | 0.000795 |
| 2202 SA | 26.974 | 5.198 | 0.299907 | 0.006902 | 0.149104 | −0.005916 |
| 2202 softmax | 27.220 | 5.516 | 0.297641 | −0.000007 | 0.147611 | −0.003221 |

| SA − softmax | Equal-seed mean difference | Per-seed mean differences (2201, 2202) | Equal-seed slope difference | Per-seed slope differences (2201, 2202) |
| --- | ---: | ---: | ---: | ---: |
| Q | −0.052 pp | +0.143 pp, −0.246 pp | −1.072 pp / 1,000 | −1.827, −0.318 pp / 1,000 |
| KL | +0.001042 | −0.000183, +0.002266 | +0.003080 / 1,000 | −0.000749, +0.006910 / 1,000 |
| Brier | +0.000300 | −0.000893, +0.001493 | −0.001684 / 1,000 | −0.000673, −0.002695 / 1,000 |

No single architecture wins all measures: paired Q mean and KL mean differences
have opposite signs across the two seeds; Brier means also differ in sign,
while the paired Brier slope differences are both negative. These are two
existing seed pairs, not independent-population uncertainty estimates.

## Sampled minima and companion measures

| Seed / mode | Sampled minimum KL (update) | Sampled minimum Brier (update) |
| --- | ---: | ---: |
| 2201 softmax | 0.266121 (900) | 0.134691 (900) |
| 2201 SA | 0.270978 (700) | 0.137396 (700) |
| 2202 SA | 0.282969 (2,600) | 0.138215 (2,600) |
| 2202 softmax | 0.275013 (2,600) | 0.135220 (2,600) |

Each listed minimum is a minimum on the sampled 0–3,000 grid only, with a
single listed checkpoint tie; it is not an interpolated or true continuous
minimum. In the primary window, challenge-Q means were 10.36% / 10.58% for
2201 softmax / SA and 10.12% / 10.20% for 2202 softmax / SA. Greedy overall-Q
means were 54.92% / 54.61% for 2201 softmax / SA and 52.98% / 53.09% for 2202
softmax / SA. Policy-entropy means were 0.48985, 0.48818, 0.48900 and 0.49076
in those same owner pairings; teacher-entropy mean was 0.37229 in each owner.
These summaries do not establish calibration or confidence quality.

## Statewise KL changes, 800→2,000

The fixed legal-argmax groups partition each owner's weighted KL change.
`A = −log(m)` and `B = KL + log(m)`; the component columns below are their
weighted changes. For each owner, ΔA + ΔB reconstructs ΔKL to numerical
tolerance.

| Seed / mode | ΔKL | ΔA | ΔB |
| --- | ---: | ---: | ---: |
| 2201 softmax | +0.012667 | −0.001232 | +0.013899 |
| 2201 SA | −0.005512 | −0.011145 | +0.005632 |
| 2202 SA | +0.026928 | +0.001965 | +0.024963 |
| 2202 softmax | +0.028945 | +0.000762 | +0.028183 |

The paired SA-minus-softmax differences in each group's contribution to
800→2,000 ΔKL were:

| Group | Equal-seed mean difference | Per-seed differences (2201, 2202) |
| --- | ---: | ---: |
| on→on | −0.000063 | −0.004237, +0.004111 |
| on→off | −0.002997 | −0.003961, −0.002033 |
| off→on | −0.004703 | −0.000522, −0.008884 |
| off→off | −0.002335 | −0.009460, +0.004789 |

`on` means the legal argmax is in oracle support. The on→off and off→on
contribution differences are negative in both observed pairs; on→on and
off→off vary in sign. This is a decomposition of descriptive endpoint changes,
not a causal explanation.

## Mechanism probe, descriptive only

The accepted local SA probe ran at 0, 500, 1,000, 1,500, 2,000, 2,500 and
3,000 for each SA owner (14 fixed-weight snapshots total). Across those
snapshot-level summaries, mean all-row attention TV was about 0.0302, mean CLS
TV about 0.0225, mean full-policy TV under `dt=0` about 0.00535, mean
`dt·H` spectral norm about 0.503, and mean greedy disagreement about 0.00837.
These are existing 128-candidate probe-panel summaries; they are not
independent replications or trained ablations. The `dt=0` comparison is local
dependence at fixed weights, not a causal effect. Softmax has no applicable
SA-specific probe.

## Scope and limitations

The audit comprises four owners, 124 checkpoint points, 124 greedy evaluations,
16 reused proper/Q cells, 108 new proper/Q cells and 14 SA probes. Q measures
valid-route fraction, not full-distribution agreement with the oracle. Rising
Q alone, entropy movement, or local fixed-weight mechanism effects do not prove
confidence-driven overfitting or causation. With only two existing seed pairs,
there are no p-values, population confidence intervals, calibration claims,
or independent-seed uncertainty estimates.
