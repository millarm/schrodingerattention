# Independent final audit — paired-behavior auxiliary analysis

## Verdict: PASS

The single owned auxiliary attempt completed successfully, its immutable records are internally consistent, and `final_report.md` accurately limits the one-seed findings.

Reviewed frozen artifacts:

- `paired-behavior-analysis-001/paired_behavior.json`: `b5820508ac6c562c288aaf78f20991c5d385c8039189b1c1a1feef922401ff6b`
- `paired-behavior-analysis-001/output-manifest.json`: `7036f44d3ed5df5e1cce0217dc923ac6a2dabeca7526464e82c96848a2fef20d`
- pre-review `execution/paired_behavior/final_report.md`: `77243038f75ab238c04dd068cd872b53edad2fe652b92cee79af4496ae0506cf`
- job source: `8d695dc4383024b85db06eb03d25937d786787b32610dea42905c3e48c5bef92`
- analysis source: `1d7d2339c382fd4cea6b76b84a5ca6074ca01561a7fb2c9df9e76fee1fc0758a`
- governing plan: `be5e5fea4fd5f2ee0e4cb3013637127b9437409bef6d6fa993f06777e65b39be`

### Provenance and completeness

- Every output-manifest entry exists and matches its SHA-256; the terminal attempt is `COMPLETE` with one retained explicit exit 0.
- The output binds the accepted source/configuration/prepared/data identities, the 8,000-update batch-digest aggregate, exact softmax/Schrödinger checkpoint hashes, 512-problem validation order, and scheduled updates 1,000/4,000/8,000.
- Frozen support hash `2bcde9c3...` and existing softmax A/B/C result hash `46ca7f60...` match their accepted immutable artifacts. The embedded softmax support and checkpoint identities match the newly scored Schrödinger cohorts.
- The only temperature grid entries are retained T=1 plus the two authorized new Schrödinger evaluations at 0.75 and 1.25. No extra search point or model-bearing test inference appears.

### Independent metric checks

- All 1,024 paired state records per checkpoint are finite and aligned. Recomputed within-map then 80/20 state summaries match the retained TV and proper-score aggregates. At update 8,000, TV is `0.09689408`; softmax/Schrödinger KL is `0.39555924`/`0.38343907`.
- Each checkpoint retains 512 greedy problem rows and 512 K32 route-set rows, including raw sets and normalized Q/pass/U/V metrics. The update-8,000 values agree with the independently accepted read-only audit.
- Every A/B/C architecture side retains exactly 768 matched states and 144 route problems. Recomputed paired differences match the stored summaries. At update 8,000, Schrödinger-minus-softmax T1 differences are A `+0.0047743`, B `+0.0269097`, C `+0.0538194`; greedy differences are A `−0.0347222`, B `+0.0486111`, C `+0.0972222`. Schrödinger KL is lower in all three, but the A greedy regression rules out uniform improvement.
- The predeclared quality-control target is softmax T1 quality `0.3422526`. Schrödinger qualities at 0.75/1/1.25 are `0.4420736`/`0.3716634`/`0.2981608`; T=1 is correctly selected as closest. Its `0.0294108` mixture gap exceeds the 0.02 tolerance, so `matched=false` is correct even before considering stratum tolerances. The grid is not extended.
- The retained mechanism record has mean `CE(dt0)-CE(normal) = −0.0175657` at update 8,000: dt0 is better on that small fixed probe average. The report states the sign correctly and does not treat this same-trained-model counterfactual as causal evidence for or against a trained architecture.

### Scientific interpretation

Equal-update evidence shows a behavioral difference in this one run: Schrödinger has modestly higher overall validation route success at update 8,000 and different state/route outputs, while costing about 3.27× softmax training-core time. It does not have higher T=1 unique or attempt-level valid-novel yield at the same temperature.

The 0.75 point has higher novelty but much higher quality, so it cannot support a quality-controlled novelty advantage. The quality-control grid is explicitly approximate, retrospective and validation-only—not the original confirmatory quality gate.

A/B/C results descriptively favor Schrödinger more on B/C route success, but cohort multiplicity/geometry confounds remain and A greedy performance is worse. One paired seed cannot establish a general architecture advantage, equivalence, useful creativity, causal mechanism, or independent-seed uncertainty. The historical route-order limitation remains accurately disclosed.

### Accounting

Independent final audit charge: `4.7` seconds, UUID `F6D543E5-E22A-4D1F-AB48-6F25EBF77C97`. Post-audit global operational debit is `2065.331896587045` of `7200` seconds.
