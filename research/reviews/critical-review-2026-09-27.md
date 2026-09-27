# Critical review of the Schrödinger attention research record

2026-09-27. Scope: `research/schrodinger_attention_research_paper.md`, the
fresh-seed replication (`execution/seed_replication/`), and the 16,000-update
pilot (`execution/update_efficiency/scientific-closeout.md` and
`runtime-evidence-006-two-pair-scientific-transcription.md`). I also read the
implementation in `schrodinger/attention.py` and `schrodinger/route_policy.py`.

The existing Sol reviews check whether the reports are accurate and restrained,
and they are. This review asks a different question: whether the study design
and analysis can answer the research question, and what the data show that the
reports do not say. All numbers below are recomputed from values committed in
this repository. The analysis script is at the end. No training, inference or
final-test access was performed.

The stated SHA-256 values for `attention.py`, `route_policy.py`,
`route_policy_metrics.py`, and the pool-512, seed-replication and D1 reports
match the current files.

## Summary

The reports are careful and do not overclaim. The main problems are in the
design:

1. **Every endpoint sits past the best observed held-out proper scores.**
   The best observed validation KL is at 1,200 updates in all four pilot runs.
   That is the first scored checkpoint after initialisation, so the true
   minimum may be earlier or later. KL gets worse from there on. The 8k and
   16k comparisons, and the planned 200k run, therefore compare models whose
   held-out proper scores keep getting worse.
2. **One-checkpoint endpoints are dominated by checkpoint-to-checkpoint noise.**
   Within one seed pair, the paired ΔQ swings by about ±1.5 pp between adjacent
   checkpoints. That is similar to the between-seed SD of 1.84 pp.
3. **Four pairs could not have detected the effect that motivated the study.**
   The minimum detectable effect is about 4 pp at 80% power. The discovery
   effect was 2.94 pp.
4. **The mechanism has not been measured in the models that were compared.**
   The learned Δt and γ of the route-policy models, and how far their
   attention moves from softmax, are not reported.
5. **Three independently trained ablations are missing:** γ=0, Δt fixed at
   its initial value, and a different Hamiltonian.

Items 1–3 can be addressed mostly with data that already exists (saved
checkpoints and rescoring). None of them needs a larger model.

## 1. Best observed held-out KL is at ~1,200 updates

From the committed KL table (nats, validation, teacher-relative):

| Owner | best observed KL | at update | KL at 8k | KL at 16k |
|---|---:|---:|---:|---:|
| 2201 softmax | 0.2889 | 1200 | 0.3705 | 0.4074 |
| 2201 Schrödinger | 0.2969 | 1200 | 0.3743 | 0.4474 |
| 2202 Schrödinger | 0.2842 | 1200 | 0.3744 | 0.4567 |
| 2202 softmax | 0.2877 | 1200 | 0.3935 | 0.4550 |

Q at T=1 keeps rising while KL rises by 41–61% between 1,200 and 16,000
updates. The values were checked against the committed `score-*.json` files.
1,200 is the first nonzero scored checkpoint, so the grid does not locate the
true minimum or when the worsening starts. Denser scoring of the retained
checkpoints (every 100 updates) is needed. The pattern is consistent with a
policy that fits 64 training maps and generalises less well
to held-out maps. Sampled-route Q at T=1 rewards sharpening
where the argmax is right, and KL penalises it where the argmax is wrong.
Brier also worsens in all four runs (0.142–0.147 → 0.149–0.168). Mean policy
entropy falls from 0.48–0.51 to 0.38–0.40 nats. That end point is close to the
teacher entropy of 0.372, so in aggregate the policies are *not* sharper than
the oracle. The KL rise therefore looks more like probability mass moving
onto wrong actions on some held-out states than uniform overconfidence.
None of this shows that *all* later Q gains
come from confidence alone, and teacher-relative KL measures more than
calibration. The
closeout mentions the KL worsening between 8k and 16k. It does not state that
KL was already worse by the next scored point after 1.2k. The 200k plan (`plan-v4-200k.md`) calls this
"central" but still extends the same regime by 12.5×.

Consequences:

- "8000 updates was too early" holds for Q only. For proper scores, both
  architectures were past their best observed values by 2,000 updates.
- Architecture differences measured deep in this regime may reflect how each
  model overfits, not how well it learns the route policy.
- The 200k continuation is likely to measure mostly overfitting dynamics. It
  should not be run as specified until the points below are addressed.

**Actions.**

- Report every endpoint with a matched-calibration control. Fit a per-model
  temperature on a *training-side* held-out split to minimise KL, then report Q
  at that temperature. Alternatively, report Q at the KL-optimal checkpoint
  chosen on a split that is not the scoring panel.
- Before any 200k run, add a regime check: either more training maps (the
  pool-512 construction can supply them) or explicit regularisation, applied
  identically to both modes.
- State in the closeout and README that the best observed validation KL is at
  1.2k (the first scored checkpoint) in all four runs.

## 2. Checkpoint noise is similar to the between-seed variance

Paired ΔQ (SA − softmax, pp) at 8k, 10k, 12k, 14k and 16k:

- 2201: +1.33, +1.39, −1.68, −0.98, +1.04. Mean +0.22, SD 1.44.
- 2202: +0.34, +2.83, −0.85, +1.61, +2.63. Mean +1.31, SD 1.56.

2201 softmax alone goes from 42.35% at 12k to 39.50% at 14k. A within-pair SD
of about 1.5 pp at fixed seed is close to the between-seed SD of 1.837 pp at
8k. Much of the "seed variance" in the primary result may therefore be
checkpoint jitter rather than stable differences between seeds.

Consequences:

- The primary endpoint (one checkpoint at 8k) is much noisier than it needs to
  be.
- The update-saving milestone analysis uses "first two consecutive grid points
  above threshold". Its resolution is 400–2,000 updates, and the reported
  update differences (±1,600, ±2,000) are about one grid step. The
  sign-flipping between seeds is what jitter of this size would produce. The
  closeout's "no stable update-saving factor" is correct, but the reason is
  that the measurement cannot resolve one, not that there is evidence of none.

**Actions.**

- Use a predeclared late-window average (for example mean Q over the last 5
  scored checkpoints) or checkpoint weight averaging (EMA/SWA) as the primary
  per-seed endpoint. Checkpoints every 100 updates are already retained, so this
  mostly costs scoring time, not training.
- Estimate the within-seed checkpoint variance explicitly, and report it next to
  the between-seed variance.
- For milestone analyses, fit a smoothed curve per run (for example monotone
  isotonic or a saturating fit) and read crossings from the fit, with bootstrap
  over checkpoints. Do not use first-passage on a noisy grid.

## 3. Power and pooled evidence

With paired SD 1.837 pp (fresh 8k), a two-sided α=0.05 paired t-test at 80%
power needs:

| True ΔQ | Pairs needed |
|---:|---:|
| 3 pp | 6 |
| 2 pp | 9 |
| 1 pp | 29 |
| 0.5 pp | 108 |

**Caveat on these numbers.** They treat the four-pair SD as known. With 3
degrees of freedom, a 95% interval for the true SD is roughly 1.0–6.8 pp. At
those two ends, detecting 1 pp needs about 11 or about 371 pairs. The table
also assumes an approximately normal paired difference, one checkpoint as the
endpoint, and the same evaluation panel. Treat it as an order of magnitude.
A confirmation study should set its sample size from a precision target,
estimated with the variance-reduced endpoint of §2, and ideally from a pilot
estimate of the SD with more pairs.

With n=4, the 80%-power minimum detectable effect is about 4 pp. The fresh
replication therefore did not fail to replicate a 2.94 pp effect in any
informative sense. It could not have detected one reliably. The paper's
wording ("did not reproduce", "inconclusive") is accurate, but the paper should
give this number. `next_research_steps.md` asks for a power calculation without
giving one. The table above is that calculation. Reducing checkpoint noise
(§2) would lower these counts.

**Pooling at 8k.** Seeds 2201 and 2202 are fresh pairs on the same model,
data, optimizer and validation panel. At 8k their ΔQ values are +1.33 and
+0.34. Adding them to 1702–1705 gives six fresh pairs: mean −0.02 pp, SD 1.60,
descriptive 95% interval [−1.70, +1.66]. Neither report shows this. The
honest single-sentence summary of the 8k endpoint is "no difference, with an
interval of ±1.7 pp".

**Early-training sign pattern (hypothesis, not confirmation).** Paired ΔQ at
the first scored checkpoint (1k for 1702–1705, 1.2k for 2201/2202) is positive
in 6 of 6 fresh pairs: +0.22, +1.69, +0.09, +0.85, +2.65, +0.43, mean +0.99 pp.
The two-sided sign-test p is 0.031. Appendix F of the paper flagged the early
advantage before the pilot ran, so the pilot's 1.2k point partly tests it on
new seeds. Caveats: 1701 at 1k was −0.39 pp (6/7, p=0.125), 1.2k is not 1k,
both pilot seeds were negative at 2k, and the checkpoint was not predeclared as
an endpoint. This is the most consistent directional pattern in the record,
and it falls in the only regime where held-out KL is near its best (§1). It
should become the predeclared primary endpoint of the next confirmation study,
not a claim now.

## 4. The mechanism is unmeasured in the route-policy models

The paper reports TV redistribution for the XOR classifier diagnostic. For the
route-policy models that the main comparison uses, it reports neither the
learned per-head Δt and γ nor attention TV(A, softmax(S)).

This matters because the evolution is structurally a bounded perturbation:

- Δt = 0.5·sigmoid(raw) ∈ (0, 0.5], initialised at 0.05. H is divided by
  √L ≈ 3.6 on top of the usual 1/√d_head.
- **With γ = 0 the effect of evolution is second order in Δt.** A first-order
  expansion gives A_j ≈ p_j + 2Δt Σ_k H_jk √(p_j p_k) sin(γ(S_ik − S_ij)).
  Numerically, doubling Δt quadruples TV when γ=0 and doubles it when γ=0.3
  (script below).
- **The phase contains no information beyond p.** Because the phase is γ·S,
  within a row ψ0 = p^(1/2 + iγ) up to a row-global phase (checked to 1e-15).
  The complex state is fully determined by the softmax distribution. The only
  new information SA brings is the operator H, which is shared by every query
  row. The "latent complex state" framing in §1 of the paper overstates this.
  SA is a fixed, score-derived, unitary-constrained remixing of softmax
  probabilities.
- With random 13×13 scores, TV from softmax ranges from about 0.003 (initial
  Δt, γ; score SD 1) to about 0.55 (Δt=0.5, γ=π; score SD 3). Where the trained
  models sit in that range is the key unknown mechanism fact.

**Actions.** Report the learned Δt and γ per layer/head for every
route-policy owner, and whether they approach their bounds. Also report the
distribution of ‖Δt·H‖₂ and per-head TV(A, softmax) on validation. Checkpoints
are retained locally, so this is an inference-only diagnostic.

## 5. Design choices that need justification or ablation

- **Hamiltonian roles.** H_jk = (S_jk + S_kj)/(2√L) uses the score of *query
  token j* against *key token k* as the coupling between *keys* j and k. It
  also discards the antisymmetric part of S. This works because self-attention
  has square S, but the choice is not motivated. Alternatives such as
  H = KKᵀ/√d or a separately projected Hamiltonian would test whether the
  specific coupling matters.
- **Missing independently trained ablations.** The paper correctly says a
  same-weights Δt=0 run is not a causal ablation, but none of these was
  trained: (a) γ fixed at 0, which leaves second-order evolution only;
  (b) Δt frozen at 0.05; (c) SA with a non-score Hamiltonian. Without them,
  "SA changes learned behaviour" cannot be attributed to interference rather
  than to extra learnable scalars and different gradient flow.
- **"Matched" scalars are not functionally matched.** Softmax α/β
  (`route_policy.py:10,16`) only reparameterise q/k/v scale, which the linear
  layers can already express. SA's Δt/γ add a new functional form. Both also
  receive AdamW weight decay 0.01 toward raw=0, which biases SA toward
  Δt→0.25 and γ→0. The paper should state this or exclude those scalars from
  weight decay.
- **Untuned shared learning rate.** Both modes use lr 1e-3 with no sweep. Any
  architecture comparison at one learning rate is confounded with how
  sensitive each architecture is to that learning rate. Run at least a
  three-point per-mode sweep on a tuning split.
- **Numerical robustness (minor).** `torch.sqrt(softmax(S))` has an infinite
  backward at p=0. Given the score scales here, float32 underflow is unlikely,
  but `exp(0.5·log_softmax(S))` is the stable form. Because H is real
  symmetric, `eigh` gives U = V·exp(−iΔtΛ)·Vᵀ. That is cheaper and exactly
  unitary, which would reduce the 3.2× cost at no scientific cost.

## 6. Cost-adjusted reading of existing data

Using the pilot curves and the 3.22× core-time ratio, softmax at 16k updates
costs about the same as SA at about 5k updates. Mean Q is 39.38% for softmax
at 16k, against 34.30% (4.8k) and 35.33% (6k) for SA. On equal compute,
softmax leads by about 4–5 pp on the only curves that allow this comparison.
The paper says SA is "not cost-neutral". It could state this directly, as a
descriptive two-seed observation.

## 7. Validation-panel reuse

The same 32 validation maps (512 problems) were used for the discovery pair,
the four-pair replication, D0, D1 temperature selection and scoring, the
38.198% milestone threshold (the softmax mean from 1702–1705), and the pilot.
The reports acknowledge reuse in each place. Cumulatively, the panel is no
longer a clean held-out set for any SA-favourable subgroup (challenge pass@32,
early checkpoints, map 344). The untouched final-test split is the right
place for exactly one predeclared confirmation, and it should be used for
nothing else.

## 8. Reporting and hygiene issues

These are hashed, reviewed records, so the fixes should go in successor
documents. Editing the records in place would break the recorded SHA-256s.

- `scientific-closeout.md` has about ten missing spaces before numbers
  ("and13 scoring points", "between8000 and16000", "Production
  used1066…"). It reads as a text-processing defect.
- Nine Markdown files link to absolute host paths (`/Users/gmh-company/…`),
  for example the trajectories link in `seed_replication/final_report.md`.
  These do not resolve in the repository.
- The paper's operational debit (4764.4/7200 s) is stale relative to the
  closeout (5855.2/7200 s). The README notes the paper predates the pilot. The
  paper should carry a dated "superseded by" note, or be updated in a new
  version.
- The paper does not mention the pilot at all. A short addendum should cover
  the six-pair pooled 8k estimate, the 6/6 early sign pattern, and the best
  observed KL at 1.2k.

## 9. Recommended next study (replaces the 200k continuation)

1. Inference-only first, on existing checkpoints: learned Δt/γ, TV(A, softmax),
   ‖ΔtH‖, late-window averaged Q, and within-seed checkpoint variance.
2. Freeze a confirmation design: primary endpoint ΔQ averaged over a
   predeclared early window (for example 800–2,000 updates) with a KL co-primary.
   Use n from the §3 table for the target effect after §2 variance reduction,
   fresh seeds, and final-test maps scored once.
3. In the same study, train ablations (γ=0, frozen Δt, alternative H) and a
   three-point per-mode learning-rate sweep on a tuning split.
4. Report an equal-compute comparison alongside the equal-update one.

## Appendix: recomputation script

Run with numpy and scipy. The inputs are transcribed from
`seed_replication/final_report.md`, `seed_replication/trajectories.md` and
`update_efficiency/runtime-evidence-006-two-pair-scientific-transcription.md`.

```python
import numpy as np, scipy.linalg as sl
from scipy import stats
rng = np.random.default_rng(0)

def sa(S, dt, g):  # mirrors schrodinger/attention.py for one head
    L = S.shape[-1]; p = np.exp(S - S.max(-1, keepdims=True)); p /= p.sum(-1, keepdims=True)
    U = sl.expm(-1j * dt * (S + S.T) / (2 * np.sqrt(L)))
    return p, np.abs((np.sqrt(p) * np.exp(1j * g * S)) @ U.T) ** 2

S = rng.normal(0, 2, (13, 13)); p, _ = sa(S, .1, .3)
r = (np.sqrt(p) * np.exp(.3j * S)) / p ** (.5 + .3j)
print(np.abs(r / r[:, :1] - 1).max())            # ~1e-15: phase is a function of p
for g in (0., .3):
    tv = [0.5 * np.abs(sa(S, d, g)[1] - p).sum(-1).mean() for d in (1e-3, 2e-3)]
    print(g, tv[1] / tv[0])                       # 4.0 (second order) vs 2.0

six = [-2.521, -0.059, -1.068, 1.852, 1.328125, 0.338541667]   # 8k, fresh pairs
m, s = np.mean(six), np.std(six, ddof=1); h = stats.t.ppf(.975, 5) * s / 6 ** .5
print(m, s, m - h, m + h)                         # -0.02, 1.60, [-1.70, 1.66]
early = [0.223, 1.688, 0.094, 0.845, 2.649739583, 0.426432292]
print(stats.binomtest(6, 6).pvalue)               # 0.031
```
