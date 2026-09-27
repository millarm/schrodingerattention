# Independent results review — three-way checkpoint diagnosis

## Verdict: PASS

The single owned diagnostic completed successfully, its immutable evidence is internally consistent, and `threeway_baseline_diagnosis.md` gives a scientifically bounded interpretation. This is a descriptive checkpoint diagnosis from one trained seed, not a causal decomposition or architecture comparison.

Reviewed frozen artifacts:

- `threeway-diagnosis-001/threeway_diagnosis.json`: `46ca7f60bca1ec2a5224d479623b0b69385f36f9acb69e55f3da895c444b9720`
- `threeway-diagnosis-001/matched_support.json`: `2bcde9c3823a41cc0a0ac7c4383ef1323658ca47b5b7a53336f4f4e2adf9babc`
- `threeway-diagnosis-001/output-manifest.json`: `19522d35fe30a2ec3a1317b0416ed0ec3a17abcf0bfbc21b7d1d4b13afdebefa`
- pre-review `threeway_baseline_diagnosis.md`: `405285e594993d4e634e7141eaf782d69eae0088c2685f7bc73f28df1eb65bfc`
- implementation source: `7b2a53d37bcae421fbd82ba3c174c0f9f812a051f583faceb8fc6ef7095620ef`

### Independent evidence checks

- Every owner-manifest entry exists and matches its SHA-256. The terminal attempt is complete and the command had one retained explicit exit 0.
- `matched_support.json` truthfully reports `MATCHED_SUPPORT_SUFFICIENT`, with all 24 fixed triplets retained: 12 I and 12 L, zero exclusions. The identical support embedded in the result exactly matches the pre-inference artifact.
- Each cohort contains 144 route problems and 768 selected states—six routes and 32 states per retained triplet. For every triplet and both matching levels, actual quota sums exactly equal retained identity counts, and counts are identical across A/B/C.
- Against the complete saved training states: every selected A state is present, no selected B state overlaps, and every selected B goal is absent from the complete saved per-map goal set. No C canonical map appears in the training maps.
- Checkpoints are exactly the accepted softmax update-1,000/4,000/8,000 hashes `329fcd95...`, `af2d6912...`, and `3a6e06fc...`, under the frozen source/configuration/prepared/input and common initial identity.
- Every raw proper-score array is finite and has 768 rows. Independently recomputed within-map then equal-map KL equals the retained aggregate for all nine checkpoint/cohort cells.
- Each cohort/checkpoint has 144 greedy attempts and 4,608 T=1 attempts. Independently recomputed exact-route success matches the retained values. At 8,000, A/B/C T=1 success is `0.5499132`/`0.4832899`/`0.3914931`; greedy success is `0.8263889`/`0.6736111`/`0.5902778`.

### Interpretation

At update 8,000 the descriptive ordering A→B→C is consistent across KL, Brier, nonoptimal mass, greedy success and T=1 success. This supports a late transfer/generalization gap: seen pairs score best, new map-specific goals on familiar maps are intermediate, and held-out routine maps score worst.

The trajectory prevents a simplistic “training always harms transfer” account. T=1 exact-route success improves for all three cohorts between 1,000 and 8,000, while C proper distribution fit worsens from 4,000 to 8,000 and C greedy success also falls over that last interval. Proper scoring and rollout behavior therefore need not move together.

The result is not a causal ranking of goal versus map limitations. Although route length, immediate optimal-action count, state counts and family are jointly matched, route multiplicity remains markedly different: mean A/B/C counts `95.30`/`372.69`/`91.63`, maxima `256`/`3,820`/`248`. Full geometry, downstream branching and original selection mechanisms also remain unmatched. B goals are map-specifically unexposed, not globally unseen coordinate tokens. C maps are rank-paired, not geometrically identical.

All findings use retrospective subsets from one trained seed. Maps, states and sampled attempts are not independent training replications. No novelty, creativity, mixed-composition, Schrödinger-advantage or causal representation claim follows. The report makes these limits explicit and proposes no automatic follow-on work.

### Accounting

Independent audit charge: `4.5` seconds, UUID `B74644B3-955B-4273-B5A1-C4D482B4C8EE`. Final three-way diagnostic debit is `37.398222998982` of `120` seconds. Global operational debit is `1784.099195462031` of `7200` seconds.
