# Independent Sol review — research paper

Source document: `research/schrodinger_attention_research_paper.md`  
Source SHA-256: `ed43f1705b0ea1dacf72b722dcb10c4a446e329f8a92375ec0ad0afbc15ed79e`

D1_DOCUMENT_REVIEW_VERDICT: PASS

## Findings

No blocking factual, statistical, chronological, citation, or authorization issue was found in the exact reviewed document.

1. **Initial screen and timing provenance — accurate.** The paper reproduces the retained three-seed XOR means (70.90% softmax, 72.92% exact SA, +2.02 pp), the unmet +3 pp efficacy and 80% adequacy gates, the non-regressing COPY result, and the approximately −0.065 pp normal-minus-dt0 primary change. It does not reuse the invalid historical timing/equal-time evidence: output-directory reuse, unconfirmed process completion, and unrecoverable attempt-specific non-overlap are explicitly retained as limitations.
2. **Benchmark chronology and gates — accurate.** The paper correctly distinguishes the initial 6/512 novelty failure, the two failed 8×8 allocation rungs, the first 12×12 pool's seven-map challenge-test shortfall, and the eventual frozen 512-per-family expansion. The accepted split counts (64 training maps/1,024 problems; 24 routine plus 8 challenge validation maps/512 problems; 96 routine plus 32 challenge test maps/2,048 problems) and 12/12/8 validation family composition agree with the primary construction report. It correctly labels these as oracle opportunities, not generated novelty.
3. **Discovery versus replication — properly separated.** Seed 1701 is reported as exploratory discovery (+2.94 pp overall T=1 Q; +5.38 pp cohort-C Q), not pooled with fresh seeds 1702–1705. The fresh primary mean (38.198% softmax, 37.749% SA, −0.449 pp), SD 1.837 pp, interval [−3.372, +2.474] pp, positive-pair count, transfer/greedy results, and 3.22× mean core-time ratio trace to the fresh-replication report. The narrative correctly treats early-checkpoint patterns and the discovery seed as hypothesis-generating.
4. **D0/D1 reuse and selection — accurately bounded.** D0 is identified as a no-new-inference analysis of the same four seeds and eight challenge-validation maps. D1 is correctly described as the same reused panel with a symmetric five-temperature grid, 40 cells, single-draw routine and challenge floors at paired SM T=1 minus 2 pp, and no exact quality matching. The selected pass@32 means (51.367% versus 52.148%), paired deltas, seed interval [−5.050, +6.612] pp, conditional map interval [−1.758, +3.711] pp, and two-positive-pair count match the D1 report/audit. Panel reuse and temperature-selection optimism are not hidden.
5. **Metric definitions and scientific claims — disciplined.** Q, pass@K, `U_valid/K`, all-valid solution coverage (`valid_headroom`), and strict novel-route coverage (`coverage`) are kept distinct. The route-novelty definition and its equivalence/support boundary agree with the benchmark. The paper does not turn different policies, attention TV, entropy, pass@32, or oracle opportunity into a creativity or general-planning claim. Same-weights dt0 is correctly limited to an inference intervention and not presented as an independently trained causal baseline.
6. **Cost and qualified accounting — accurate.** The valid route-study core timings are not mixed with the invalid initial classifier timing. The paper describes 3.22× as a narrow exact-CPU reference cost, not a universal kernel estimate. The qualified operational debit `4764.416447001050/7200` is correctly identified as including a 300-second administrative uncertainty allowance rather than physical runtime, and the document warns against summing inherited/intermediate totals.
7. **Test-release and authorization wording — correct.** The reserved route-policy final-test split is described structurally but no model-bearing final-test result is claimed. D1 is not relabeled as confirmation, and the paper authorizes neither final-test access, D2, additional training, language-model scaling, nor a production approximation.
8. **Links, hashes, and related work — verified.** Every repository-relative link resolves in the current snapshot. The stated hashes for attention, route-policy, metrics, pool-512 report, fresh replication report, D1 report, and independent D1 audit match the current files. The external links resolve to Vaswani et al.'s *Attention Is All You Need*, Nahid et al.'s *Q-Interference*, and Reinhardt and Hauser's *A Quantum Roadmap for Softmax Attention*; the short descriptions are consistent with their arXiv abstracts. The paper explicitly calls the two 2026 works adjacent, non-exhaustive preprints and makes no priority claim.

## Non-blocking publication actions

- If distributed outside the repository, attach an immutable repository commit/archive identifier; relative links and local SHA-256 values require the snapshot, as the paper already notes.
- Record the cited arXiv versions/access date in a conventional bibliography before formal publication, because the two 2026 preprints may be revised.
- Preserve the current wording that the D1 map interval is conditional on the reused eight-map panel and fixed selections. The independent D1 audit recomputed its inputs and seed uncertainty but did not rerun the PCG64 bootstrap quantiles.

## Review boundary

This verdict accepts fidelity and restraint of the Markdown research record, not the underlying hypothesis, a priority claim, peer-reviewed publication status, or authorization for further work. Review was read-only apart from this file: no tests, model inference, experiments, training, final-test access, D2 work, or ledger writes were performed.
