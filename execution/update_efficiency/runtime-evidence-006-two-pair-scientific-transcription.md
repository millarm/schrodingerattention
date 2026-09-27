# Runtime evidence 006 — two-pair scientific transcription

Date: 2026-09-27. This is a transcription and elementary paired arithmetic
from the four already-complete, integrity-checked owners. It uses no new
evaluation, estimator, model/study import, or runtime. It is supplied for
independent Sol audit and Astra interpretation; it is not a definitive research
decision.

Revision note: this static correction supersedes the prior version at SHA-256
`799cda3854602893be13a303ebad87acb4fe93ce94c6ed68fcde7a021c1596c0`. It
corrects the seed-2202 exact-30% pair arithmetic, clarifies grid-value
provenance, and adds conservative interval-derived ratio bounds. No source,
ledger, runtime, or underlying owner artifact changed. This revision also
supersedes the intermediate corrected version at SHA-256
`a6a283d3500254af261952dbc4121da3e257a86c1183285cdab9638e488e0d08` by adding
stagewise paired quality gaps and acquisition diagnostics.

Operational and integrity evidence remains in
[`runtime-evidence-004-2201-production-pair.md`](runtime-evidence-004-2201-production-pair.md)
and [`runtime-evidence-005-2202-and-pair-summaries.md`](runtime-evidence-005-2202-and-pair-summaries.md).
Their current SHA-256 values are `326244f94a7d915d8a190277586484ca5120c448c8084770bf7be7faecac3ff2`
and `8ff910238e556d35bd224669a5540421cfe87b1517452ba7b3ef1c3219d1d8f9`.
The accepted implementation review is `reviews/10-platform-implementation.md`
(SHA-256 `5771da86fbc7ec3631938a1cec8968bd0c0f2eeb1cfa3bedf6574905f8d76048`);
the second-pair resource gate is `second-pair-resource-gate.md` (SHA-256
`a9ce35aaf2974bc79fbfce052caad93e8b783cb2b1f778208d1fd542a4efcaeb`).
The four result JSON SHA-256 values, in table order below, are:

| Owner | Result SHA-256 |
| --- | --- |
| 2201 softmax | `53665a21c0d4db741d3aee3196dae7a682f5866f006b0b7db308cd326a407884` |
| 2201 Schrödinger | `990f7d32950d53b6b2ba1c58a47ea3a721e21d0242686ebcc776eff2afb5941a` |
| 2202 Schrödinger | `6b11f3558f9fa9772efa2bcd41e9fd7219ff9b9ac2d019a9a7f48366c51432a9` |
| 2202 softmax | `b3dd6a06253a3c3eb9931a1213c39a89533c21bb6d5053fe58328b636ee8845b` |

## Fixed grid values

Column order for each table is updates `0, 1200, 2000, 2400, 3600, 4000,
4800, 6000, 8000, 10000, 12000, 14000, 16000`. Values are transcribed from
the saved `score-<update>.json` files for the indicated owners, not recomputed.
Owner order is consistently 2201 softmax,
2201 Schrödinger, 2202 Schrödinger, 2202 softmax.

### Q

| Owner | Q at the 13 grid points, in order |
| --- | --- |
| 2201 softmax | 0.00006510416666666667, 0.255419921875, 0.3113606770833333, 0.30859375, 0.3045735677083334, 0.34158528645833336, 0.3392252604166667, 0.37636718750000003, 0.3816080729166667, 0.39130859375000004, 0.4234537760416667, 0.39500325520833335, 0.3985514322916667 |
| 2201 Schrödinger | 0.00006510416666666667, 0.28191731770833334, 0.29671223958333337, 0.28662109375000006, 0.31396484375, 0.3512858072916667, 0.36044921875, 0.36079101562500004, 0.3948893229166667, 0.4051920572916667, 0.4066243489583334, 0.38523763020833335, 0.40900065104166666 |
| 2202 Schrödinger | 0.0, 0.25813802083333337, 0.295263671875, 0.29913736979166666, 0.3364420572916667, 0.3409505208333334, 0.3255696614583334, 0.3458170572916667, 0.36888020833333335, 0.39055989583333334, 0.384814453125, 0.4317708333333334, 0.415234375 |
| 2202 softmax | 0.0, 0.2538736979166667, 0.3001790364583333, 0.28175455729166665, 0.31025390625, 0.3097819010416667, 0.32740885416666665, 0.35944010416666666, 0.36549479166666665, 0.362255859375, 0.3932779947916667, 0.415625, 0.3889811197916667 |

### KL

| Owner | KL at the 13 grid points, in order |
| --- | --- |
| 2201 softmax | 0.8710910624875743, 0.2888761013987698, 0.30712099711117397, 0.3204293347185113, 0.3513833117659669, 0.31089811475995166, 0.32118311244713443, 0.34487472946284264, 0.37053917348288573, 0.3945991751483267, 0.39283787835180634, 0.4282831863963749, 0.4073837601192799 |
| 2201 Schrödinger | 0.871089732428469, 0.296851797134713, 0.2973704358483893, 0.32643282034997706, 0.34390239083522683, 0.3368994223721664, 0.3432059859256332, 0.3738459351118681, 0.37432028808331375, 0.42057883202124774, 0.4288813183533159, 0.41330478829577766, 0.447383435837588 |
| 2202 Schrödinger | 0.8599603205513244, 0.2841779478097869, 0.3411926798498638, 0.3172358565764209, 0.3307386983326489, 0.32903028168878046, 0.36883641375758347, 0.34395345783949116, 0.37438273858842147, 0.390968714389028, 0.4356678656511987, 0.44241421915444995, 0.456706166254046 |
| 2202 softmax | 0.8599267443651144, 0.2876626662459529, 0.3220687567042711, 0.30962539885154455, 0.3207873088877578, 0.3299670182218324, 0.3227385309304559, 0.344658072594924, 0.3934873109196884, 0.39773946219541617, 0.4147427023078981, 0.45752484185671793, 0.45498360726941345 |

### Challenge Q

| Owner | Challenge Q at the 13 grid points, in order |
| --- | --- |
| 2201 softmax | 0.0, 0.091552734375, 0.09716796875, 0.1328125, 0.119873046875, 0.117431640625, 0.13037109375, 0.1572265625, 0.16259765625, 0.13916015625, 0.176513671875, 0.156005859375, 0.147705078125 |
| 2201 Schrödinger | 0.0, 0.097412109375, 0.10107421875, 0.10791015625, 0.10693359375, 0.121337890625, 0.14404296875, 0.146728515625, 0.14404296875, 0.170166015625, 0.148681640625, 0.142333984375, 0.158935546875 |
| 2202 Schrödinger | 0.0, 0.091796875, 0.124755859375, 0.108642578125, 0.146728515625, 0.1298828125, 0.135986328125, 0.144775390625, 0.1484375, 0.1376953125, 0.162353515625, 0.162109375, 0.1630859375 |
| 2202 softmax | 0.0, 0.08349609375, 0.124267578125, 0.124267578125, 0.12646484375, 0.114990234375, 0.119140625, 0.1513671875, 0.166015625, 0.160888671875, 0.170166015625, 0.1640625, 0.170166015625 |

## Plateau outcomes and milestone records

For all four owners, both `q_plateau` and `ce_plateau` are
`RIGHT_CENSORED`; `first_low_window` and `confirmation_update` are null. The
saved five-window Q qualification arrays (in owner order above) are
`[false,false,false,false,false]`, `[false,false,false,false,true]`,
`[false,false,false,false,false]`, `[false,false,false,false,false]`.
The CE arrays are `[false,false,false,false,false]` for every owner. Even the
one final qualifying Q window for 2201 Schrödinger does not meet the required
consecutive-window confirmation. Thus Q and CE plateau updates were not
observed by 16,000; these are right-censored at the horizon, not plateau
confirmations at that boundary.

Milestone rows transcribe saved result summaries. Interval endpoints are the
saved bracketing grid updates; lag is confirmation minus acquisition. Initial
anomaly is false for every row. No milestone below is censored.

The exact thresholds are 0.30 and 0.38198; the tolerant thresholds are 0.29
and 0.37198, respectively. These remain separate outcome definitions.

| Owner | Metric / threshold | Status | Acquisition update | Confirmation | Lag | Bracketing interval | Initial anomaly |
| --- | --- | --- | ---: | ---: | ---: | --- | --- |
| 2201 softmax | exact 30% | ACQUIRED | 2000 | 2400 | 400 | [1200, 2000] | false |
| 2201 softmax | tolerant 30% | ACQUIRED | 2000 | 2400 | 400 | [1200, 2000] | false |
| 2201 softmax | exact 38.198% | ACQUIRED | 10000 | 12000 | 2000 | [8000, 10000] | false |
| 2201 softmax | tolerant 38.198% | ACQUIRED | 6000 | 8000 | 2000 | [4800, 6000] | false |
| 2201 Schrödinger | exact 30% | ACQUIRED | 3600 | 4000 | 400 | [2400, 3600] | false |
| 2201 Schrödinger | tolerant 30% | ACQUIRED | 3600 | 4000 | 400 | [2400, 3600] | false |
| 2201 Schrödinger | exact 38.198% | ACQUIRED | 8000 | 10000 | 2000 | [6000, 8000] | false |
| 2201 Schrödinger | tolerant 38.198% | ACQUIRED | 8000 | 10000 | 2000 | [6000, 8000] | false |
| 2202 Schrödinger | exact 30% | ACQUIRED | 3600 | 4000 | 400 | [2400, 3600] | false |
| 2202 Schrödinger | tolerant 30% | ACQUIRED | 2000 | 2400 | 400 | [1200, 2000] | false |
| 2202 Schrödinger | exact 38.198% | ACQUIRED | 10000 | 12000 | 2000 | [8000, 10000] | false |
| 2202 Schrödinger | tolerant 38.198% | ACQUIRED | 10000 | 12000 | 2000 | [8000, 10000] | false |
| 2202 softmax | exact 30% | ACQUIRED | 3600 | 4000 | 400 | [2400, 3600] | false |
| 2202 softmax | tolerant 30% | ACQUIRED | 3600 | 4000 | 400 | [2400, 3600] | false |
| 2202 softmax | exact 38.198% | ACQUIRED | 12000 | 14000 | 2000 | [10000, 12000] | false |
| 2202 softmax | tolerant 38.198% | ACQUIRED | 12000 | 14000 | 2000 | [10000, 12000] | false |

Saved proper/challenge quality at each distinct owner/acquisition update is
transcribed from that owner's `score-<update>.json`; rows deduplicate
milestones sharing an owner and update, with every corresponding threshold
shown. The frozen fragility flag is `KL > 0.40 nat OR challenge Q < 0.08`;
it does not change the acquisition threshold or crossing update.

| Owner | Acquisition update | Threshold(s) acquired | Q | Proper KL (nat) | Proper Brier | Challenge Q | Fragility flag |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- |
| 2201 softmax | 2000 | exact 30%; tolerant 30% | 0.3113606770833333 | 0.30712099711117397 | 0.14970264153707558 | 0.09716796875 | false |
| 2201 softmax | 6000 | tolerant 38.198% | 0.37636718750000003 | 0.34487472946284264 | 0.15152005411566072 | 0.1572265625 | false |
| 2201 softmax | 10000 | exact 38.198% | 0.39130859375000004 | 0.3945991751483267 | 0.16016369722461765 | 0.13916015625 | false |
| 2201 Schrödinger | 3600 | exact 30%; tolerant 30% | 0.31396484375 | 0.34390239083522683 | 0.15239953118823893 | 0.10693359375 | false |
| 2201 Schrödinger | 8000 | exact 38.198%; tolerant 38.198% | 0.3948893229166667 | 0.37432028808331375 | 0.1525591851384479 | 0.14404296875 | false |
| 2202 Schrödinger | 2000 | tolerant 30% | 0.295263671875 | 0.3411926798498638 | 0.1604841047727099 | 0.124755859375 | false |
| 2202 Schrödinger | 3600 | exact 30% | 0.3364420572916667 | 0.3307386983326489 | 0.15476772017228624 | 0.146728515625 | false |
| 2202 Schrödinger | 10000 | exact 38.198%; tolerant 38.198% | 0.39055989583333334 | 0.390968714389028 | 0.1555501711831784 | 0.1376953125 | false |
| 2202 softmax | 3600 | exact 30%; tolerant 30% | 0.31025390625 | 0.3207873088877578 | 0.1515773714253085 | 0.12646484375 | false |
| 2202 softmax | 12000 | exact 38.198%; tolerant 38.198% | 0.3932779947916667 | 0.4147427023078981 | 0.15624249541065927 | 0.170166015625 | true (KL > 0.40 nat) |

## Paired descriptive arithmetic

Differences below are Schrödinger minus softmax acquisition updates within a
seed; ratios are Schrödinger divided by softmax. They are simple arithmetic on
the recorded milestones, with only two seeds, not uncertainty estimates.

| Milestone | Seed | Difference (updates) | Ratio |
| --- | ---: | ---: | ---: |
| Exact 30% | 2201 | +1600 | 1.8 |
| Exact 30% | 2202 | 0 | 1.0 |
| Tolerant 30% | 2201 | +1600 | 1.8 |
| Tolerant 30% | 2202 | -1600 | 0.555556 |
| Exact 38.198% | 2201 | -2000 | 0.8 |
| Exact 38.198% | 2202 | -2000 | 0.833333 |
| Tolerant 38.198% | 2201 | +2000 | 1.333333 |
| Tolerant 38.198% | 2202 | -2000 | 0.833333 |

Across the two seeds, mean difference is +800 updates for exact 30%, 0 for
tolerant 30% and tolerant 38.198%, and -2000 for exact 38.198%. Tolerant 30%
and tolerant 38.198% have opposite signs across seeds; exact-30% has a
positive then zero contrast, while the two exact-38.198% contrasts favor
earlier Schrödinger acquisition in both recorded seeds. These are descriptive
two-seed summaries. Exact and tolerant thresholds are deliberately kept
distinct.

Conservative paired ratio bounds are formed from the saved bracketing
intervals, not point estimates. For SA interval `[La, Ua]` and SM interval
`[Ls, Us]`, the reported bound is `[La/Us, Ua/Ls]`:

| Milestone | Seed | Conservative SA/SM ratio bound |
| --- | ---: | ---: |
| Exact 30% | 2201 | [1.2, 3.0] |
| Exact 30% | 2202 | [0.666667, 1.5] |
| Tolerant 30% | 2201 | [1.2, 3.0] |
| Tolerant 30% | 2202 | [0.333333, 0.833333] |
| Exact 38.198% | 2201 | [0.6, 1.0] |
| Exact 38.198% | 2202 | [0.666667, 1.0] |
| Tolerant 38.198% | 2201 | [1.0, 1.666667] |
| Tolerant 38.198% | 2202 | [0.666667, 1.0] |

Recorded Q at 8k and 16k, and the recorded 8k-to-16k change:

| Owner | Q8000 | Q16000 | Q16000 − Q8000 |
| --- | ---: | ---: | ---: |
| 2201 softmax | 0.3816080729166667 | 0.3985514322916667 | +0.016943359375 |
| 2201 Schrödinger | 0.3948893229166667 | 0.40900065104166666 | +0.014111328125 |
| 2202 Schrödinger | 0.36888020833333335 | 0.415234375 | +0.046354166667 |
| 2202 softmax | 0.36549479166666665 | 0.3889811197916667 | +0.023486328125 |

Paired Q differences (Schrödinger minus softmax) are +0.013281250 at 8k and
+0.010449219 at 16k for seed 2201, and +0.003385417 at 8k and +0.026253255
at 16k for seed 2202. The change in paired difference from 8k to 16k is
-0.002832031 for 2201 and +0.022867839 for 2202; direction/magnitude are not
consistent across these two seeds. These endpoint differences do not imply
plateau behavior.

As the fixed early-curvature screen requested by the plan, define paired
`ΔQ(u) = Q_Schrodinger(u) − Q_softmax(u)` and
`C = ΔQ(3600) − (ΔQ(1200) + ΔQ(6000))/2`. Direct substitution from the grid
gives C=+0.39306640625 pp for seed 2201 and C=+3.086751302083335 pp for seed
2202 (equal-seed mean +1.7399088541666675 pp; range +0.39306640625 to
+3.086751302083335 pp). Both signs are positive and `|mean C| >= 1 pp`, so
this meets the plan's same-sign/material-curvature descriptive screen; it is
not statistical confirmation and does not supersede milestone or plateau
status.

The full stagewise paired diagnostic reports each seed's `ΔQ` in percentage
points, equal-seed mean `ΔQ`, and equal-seed mean KL and challenge-Q gaps
(Schrödinger minus softmax; KL in nat, challenge Q in pp). The frozen mixed
label applies only when mean paired Q gain is positive and either mean KL gap
is greater than +0.02 nat or mean challenge-Q gap is below -2 pp. These are
practical descriptive margins, not equivalence tests.

| Updates | Seed 2201 ΔQ (pp) | Seed 2202 ΔQ (pp) | Mean ΔQ (pp) | Mean KL gap (nat) | Mean challenge-Q gap (pp) | Fixed label |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 0.000000000 | 0.000000000 | 0.000000000 | +0.00001612306355 | 0.000000000 | — |
| 1200 | +2.649739583 | +0.426432292 | +1.538085938 | +0.00224548864989 | +0.708007812 | positive Q, not mixed |
| 2000 | -1.464843750 | -0.491536458 | -0.978190104 | +0.00468668094140 | +0.219726562 | — |
| 2400 | -2.197265625 | +1.738281250 | -0.229492187 | +0.00680697167817 | -2.026367188 | — (mean Q gain is not positive) |
| 3600 | +0.939127604 | +2.618815104 | +1.778971354 | +0.00123523425708 | +0.366210938 | positive Q, not mixed |
| 4000 | +0.970052083 | +3.116861979 | +2.043457031 | +0.01253228553958 | +0.939941406 | positive Q, not mixed |
| 4800 | +2.122395833 | -0.183919271 | +0.969238281 | +0.03406037815281 | +1.525878906 | mixed (KL conflict) |
| 6000 | -1.557617187 | -1.362304687 | -1.459960937 | +0.01413329544680 | -0.854492188 | — |
| 8000 | +1.328125000 | +0.338541667 | +0.833333333 | -0.00766172886542 | -1.806640625 | positive Q, not mixed |
| 10000 | +1.388346354 | +2.830403646 | +2.109375000 | +0.00960445453327 | +0.390625000 | positive Q, not mixed |
| 12000 | -1.682942708 | -0.846354167 | -1.264648437 | +0.02848430167241 | -1.782226562 | — |
| 14000 | -0.976562500 | +1.614583333 | +0.319010417 | -0.01504451040143 | -0.781250000 | positive Q, not mixed |
| 16000 | +1.044921875 | +2.625325521 | +1.835123698 | +0.02086111735147 | +0.207519531 | mixed (KL conflict) |

At update 2400 mean challenge-Q gap is below -2 pp, but mean Q gain is
negative, so the frozen positive-Q mixed rule does not apply. At update 4800,
mean Q gain is +0.96923828125 pp while mean KL is worse by +0.03406037815281
nat, so the gain is mixed. The 16000 mean Q gain is likewise mixed because
the mean KL gap is +0.02086111735147 nat, just above the +0.02 margin.

The saved diagnostics do not support claiming that 16,000 updates is enough
to establish saturation: every Q and CE plateau remains right-censored, and
the latest Q-window confirmation rule is unmet for all owners. The Q values
continue to differ from 8k to 16k, but this finite-endpoint movement alone
cannot establish whether or when a plateau will occur. Milestone contrasts
also diverge by seed for some thresholds. Interpretation should therefore
remain cautious and limited to this two-seed pilot.

## Identity, integrity, charges, and budget closeout

All four authorized fixed owners are COMPLETE, UUID-matched to their immutable
ledger charge, use the exact 13-point grid, have fully closed 179-file output
manifests, and have verified process-group cleanup. Per-seed pair identity
matches on shared initial digest, all 16,000 batch digests, config hash, input
IDs, source hashes, full bank identity, and training-support hash; common
config/input/source/bank/support identities also match across seeds. The
seed-specific shared-initial digests are 2201
`ced35b599a1d161a24e726c4e6288cac9e17fbfae64a7cc1fb18eddf4487d0fa` and 2202
`bc45ada0dea9f1a31f5a11961fc53abcef945a06c6790e0085cfcef68ff8ce8e`.
Detailed exact identity fields and manifests are preserved in evidence 004,
evidence 005, owner results and immutable decisions. No owner retries,
replacements, or duplicate launches occurred.

Ledger EOF is `ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2`
(158 rows). Its immutable B owner rows retain the accepted
`FINALIZATION_UNCERTAIN` pre-final-artifact lifecycle status; matching UUIDs,
COMPLETE owner artifacts, closed manifests and reviewed driver validation
establish the successful terminals. No ledger row was modified. Final stage
totals A/B/C/D are 884.3443774547214 / 3353.1594254599418 / 0 /
694.6458445000296 seconds; qualified global debit is 5855.153244667692 /
7200 seconds. Four B owner charges total 1066.3934205418918 seconds. Detailed
owner elapsed/charge figures, driver terminals and cleanup proofs are in
evidence 004 and 005. This closes only the explicitly authorized 2201/2202
pilot; it authorizes no further runs.
