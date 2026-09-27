# Amendment 1 independent methodology review

2026-09-27. Reviewer: GPT-6 Sol. **Verdict: PASS** for the exact amendment and correction spec below, with the numerical interpretation stated here. This is a methodology gate only. The seven findings in `01-static.md` remain open; no implementation PASS, model inference, tests, training, ledger initialization or 200,000-update work follows from this review.

## Exact documents inspected

| Document | SHA-256 |
| --- | --- |
| `execution/early_learning/amendment-01-statewise-kl.md` | `51563625cc2b171f4e70757fbe05eb8cacf050ab1f47e9d3b07eeae790490842` |
| `execution/early_learning/spec-02-corrections-and-kl.md` | `2aef1209f183b1b702fae8d353d328fe02aeaa0fd7bc449385d651aebe83b4da` |
| `research/probability_diagnostics_followup_2026-09-27.md` | `86f3ed527828af861a286d65269fb55e197077e2cbe02a51a4738df04107d110` |
| `README.md` | `76a4a93d9e6f66c4c30dc63645babacb78c13ef014e645a3f4dac4b87db6bd6b` |
| Existing `plan.md` | `fcfc12a9a250a85391259cbff3bd2bd62a8a429e8b0a1615944ad40682f9be5f` |
| Existing `spec-01-dense-scoring.md` | `b0bf16e0caaf1407fd72c148622b73826f998885fb124be77da24cdd88be90cc` |
| Prior methodology review `00-methodology.md` | `c4f796a0333a7d28c33508507595a81fe07c26af9fd763f57c446ca038b2a113` |
| Open static review `01-static.md` | `42d06106676e7c53acb0e91c1cc54cd6ef2cc092ea4616f6bcf204321d3f974f` |

Hashes were computed by a read-only standard SHA-256 command. I read the amendment, spec and root documents in full. I did not re-review unfinished implementation code. The linked PR comment could not be fetched in this environment; the reviewed documents contain the specific follow-up claims, and this review assesses their stated method rather than independently attesting the comment text.

## Assessment

The four legal-argmax on/off groups are exhaustive and disjoint at every fixed adjacent 100-update pair and at 800→2,000. Matching the same 1,024 state identities, q values and legal masks across checkpoints prevents state substitution. The tie order matches the accepted up/right/down/left action order. Oracle support is exactly positive q, which is distinct from legal action support. The plan fixes all comparisons before new scores and forbids worst-state filtering or favorable endpoint selection.

Original per-state weights are computed from the full fixed bank, with equal states per map, equal maps per stratum and the unchanged 0.8/0.2 mixture. Thus group prevalence sums to one and signed contributions sum to the weighted KL change. Reporting both additive contribution and conditional mean avoids treating a selected group's average as its contribution. Empty groups retain zero prevalence/contribution and a null conditional mean. Routine/challenge contributions should retain their original mixture weights and close to the same total.

For normalized q and p, `m=sum(p[a] for q[a]>0)` gives the exact identity `KL(q||p)=-log(m)+KL(q||p|S)` when the exported distribution supports the arithmetic. Using saved finite KL to calculate `B=KL+log(m)` avoids reconstructing small log terms from rounded p. The absolute 1e−10 normalization/closure tolerances, 1e−12 q-identity tolerance, and narrow allowance for raw floating residuals are prospective and proportionate. The implementation must not clip components to force closure. Reconstruction `A+B=KL` is algebraic by this definition; independent identity checks should also compare weighted `1−m` with the saved nonoptimal-mass series and verify group/stratum sums before interpreting components.

The amendment's rule to mark unsupported exported-mass arithmetic unavailable includes **any** action with `q[a]>0` but exported `p[a]<=0`, even if total `m>0`: finite saved KL cannot establish a finite conditional KL from such an exported distribution. Nonfinite/negative p, failed normalization, changed q/legal masks, or missing states remain input-integrity failures. Zero or unresolvably small positive m, with otherwise valid saved scores, makes the decomposition unavailable for the affected checkpoint and all transitions requiring it; it never licenses silently omitting a state or renormalizing the remainder. Add this partial-support-zero case to the focused analytic tests alongside the zero-total-support case.

The follow-up correctly retracts a blanket overconfidence interpretation. Falling aggregate nonoptimal mass and policy entropy above the oracle mean are compatible with worsening KL, and neither establishes individual-state calibration or a cause of route-quality gains. The new groups and components remain descriptive observations on correlated states and checkpoints. Per-owner results precede any two-seed paired summaries; no states, maps, heads or adjacent pairs become independent training replications. The existing 1,800-second zero-carry budget, owner order, tiny 10/60-second checks, and final-test/training hold remain unchanged.

## Root document assessment

`probability_diagnostics_followup_2026-09-27.md` and README distinguish aggregate observations from statewise hypotheses and do not claim uniform confidence, calibration or a causal mechanism. No root-document correction is required for this methodology gate.

AMENDMENT_METHODOLOGY_REVIEW_VERDICT: PASS
