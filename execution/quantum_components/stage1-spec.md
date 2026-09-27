# Stage 1 probe specification: component C1

2026-09-27. Written before the main runs. Plan:
`research/reviews/quantum-inspired-directions-2026-09-27.md` (revision 2).

## What is compared

The variants from `schrodinger/quantum_components.py`:

- `softmax`: the baseline.
- `c1`: Hermitian H from the full score matrix.
- The twins `c1_phasefree`, `c1_wick` and `c1_dephased`.

All variants have identical parameter counts. Within a seed they share the
initial weights and the minibatch stream (both tested). The model is
`ProbeEncoder`: pre-norm, d=32, 2 heads, feed-forward width 64, CLS readout.
Training uses AdamW (lr 1e-3, weight decay 0.01), gradient clipping at 1.0,
batch 128 and freshly sampled data. Evaluation uses a fixed held-out set of
2,048 examples.

## Probes and fixed settings

| Probe | Settings | Steps / evaluation interval | Chance / heuristic level |
|---|---|---|---|
| order (**C1's designated probe**) | L=16, 1 layer | 600 / 50 | 0.5 |
| parity | k=3, L=16, 1 layer | 1,500 / 250 | 0.5 |
| exclude | L=16, 2 layers | 1,500 / 250 | 0.75 (majority-vote heuristic) |

Order is C1's designated probe because C1's only new ingredient is the
antisymmetric (directional) part of the score matrix.

## Seeds

Seeds 0–4. Seed 999 was used for calibration and is excluded from every
result.

## Endpoints and pass rule

The **primary endpoint** is held-out accuracy averaged over the evaluations in
the second half of training. The secondary endpoints are the window-averaged
cross-entropy and the learned Δt trajectory.

C1 passes a probe if both of the following hold against **each** of softmax,
`c1_phasefree`, `c1_wick` and `c1_dephased`:

- the paired window-accuracy difference is positive in at least 4 of 5 seeds;
- the mean paired difference is at least 1 pp.

C1 carries into Stage 2 only if it passes its designated probe, order.
Passing parity or exclude is reported as secondary. Five seeds are a screen,
not a population estimate: no p-values.

## Disclosures

- Difficulty was calibrated on seed 999, and is meant to use softmax alone.
  During the first calibration pass, however, `c1` was also run on seed 999
  at 600 steps. On order it scored 1.000 against softmax's 0.881; on the
  original parity and multiplexer settings both variants scored 1.000. That
  C1 result was seen before this spec was written. The later calibrations
  (parity k=3; exclude replacing the multiplexer, which was too easy; order at
  600 steps) used softmax only.
- The order setting (600 steps) was chosen as the softmax setting that is not
  saturated: 0.881 at 600 steps, 0.969 at 800 and 0.999 at 1,500.
- Environment: Python 3.11, torch 2.14.0+cpu (as pinned) and numpy 2.4.6. The
  pinned numpy 2.5.3 needs Python 3.12 or later. Two torch threads per
  process.
