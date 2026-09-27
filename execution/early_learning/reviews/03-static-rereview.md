# Block 1 amendment implementation static rereview

2026-09-27. Reviewer: GPT-6 Sol. **Verdict: CHANGES REQUIRED** on this exact frozen version. The 10-second smoke and 60-second targeted suite should not start yet: several analytic fixtures deterministically violate their own legal-action masks. This was a static read-only review. No imports, tests, inference, training, ledger initialization, or 200,000-update work occurred.

## Exact `command.authority_hashes()` inventory

I independently computed SHA-256 of every file listed in `command.py:80-101` using a read-only standard command.

| Key | SHA-256 |
| --- | --- |
| command | `14de2e4d1fd92b726f4260da92f3fdb13b27f14d15bfbdf1d74ca7f7d324798c` |
| study | `ab03a2041c9491998f08c0749ef644ab2b8cd78f5f778f2b07572a102eb828e0` |
| tests | `8f0b520dd8c5188956acd4a98c203545e4db632341abf73a4c7b4d76643ff346` |
| inventory | `0ccf9c4ae4201d8ccbe9037785a2efc2eb4b9b9246bc7fdbec8fd09d2d769d5b` |
| plan | `fcfc12a9a250a85391259cbff3bd2bd62a8a429e8b0a1615944ad40682f9be5f` |
| spec | `b0bf16e0caaf1407fd72c148622b73826f998885fb124be77da24cdd88be90cc` |
| methodology_review | `c4f796a0333a7d28c33508507595a81fe07c26af9fd763f57c446ca038b2a113` |
| methodology_acceptance | `694caa52e7a762acdae645cebe869f9cd9b2f6b95895851bd1efd21c1945c0db` |
| amendment | `51563625cc2b171f4e70757fbe05eb8cacf050ab1f47e9d3b07eeae790490842` |
| amendment_spec | `2aef1209f183b1b702fae8d353d328fe02aeaa0fd7bc449385d651aebe83b4da` |
| amendment_methodology_review | `6ead804a56dbd23f4b3e797984108c4f7d8c931785b4980dd5962f30a4942959` |
| amendment_acceptance | `e84d5ecca402da7970eef6429c9dee9c029d47b201b443c16562348baa34e812` |
| research_refocus | `05b11395c7c0fd518cd80672ed1835aed1555102c090a74cfe4ff43023ff41b0` |
| protocol | `983a63fd480510994721d980ee866f08e3cba6b767fcbadd5cef7491d437d1c5` |
| accepted_driver | `e228b53fb52f3a944e6e523e9ce3340c5abb3c02cc16ad2e07729972b1877d84` |
| watchdog | `ad5e3030ce148283c2576fa5fb376c512a8f7474bcc5e62e8e2d4e6d749900b2` |
| accepted_model | `95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4` |
| accepted_experiment | `10cfc1a9a5e21856fd4e80f7c81b7b9243c104d452f10fc2a0062d4b4998036b` |
| accepted_data | `676b8de313fb9c667497b307704b21f137ac55a18e1e19c81be399d3f02e4bb7` |
| accepted_evaluation | `fd5cd438e0fbd103857933418008a7c5936b379488857ac6bfa7370aa8ad18ec` |
| accepted_metrics | `a471ae2c40973cb15584f924061b3ace24ef5af3b1e31702b79056055f317e34` |
| attention | `e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a` |
| feasibility | `da36b0150c0b255b7e5482d7dc016505054d9632c8fb3a21d06c2d201bfedbf4` |

## Required bounded corrections

1. **Analytic fixture's mask and p disagree.** `tests/test_early_learning.py:50` makes action 3 illegal for every synthetic state, while `_scored_fixture` at lines 55-63 and several explicit p vectors assign it positive probability. `study.statewise_scores` correctly rejects this at `study.py:155-156`, so the statewise analytic tests fail before their intended assertions. Make the synthetic legal masks and every p vector consistent; retain the separate masked tie-order test.
2. **Terminal fsync uncertainty can release the reservation.** `_durable_certain` at `command.py:213-221` returns true after `_durable` raises if the JSON is readable. A failure of the directory fsync after `os.replace` leaves the file readable without proving durable directory state. In check/audit/owner exception paths a later `FAILED_DRIVER` terminal can also overwrite an uncertain earlier terminal and set `terminal=True`. Preserve a terminal-uncertain flag and retain the lock after any failed terminal write/fsync; readable JSON alone is not durable proof.
3. **Group component closure is only reported.** `study.statewise_transitions` computes each group's `A_contribution+B_contribution−additive_kl_contribution` at lines 253-259 but never enforces the amendment spec's absolute 1e−10 group/component reconstruction tolerance. Validate every group residual, including empty groups, before recording a transition.
4. **Owner overhead reconciliation omits its preassigned identity.** `_append_overhead` at `command.py:592-610` accepts an existing same-session/same-amount row without checking that the row's `entry_id` equals this attempt's `entry_id` argument. Require the preassigned ID and matching row fields before treating overhead as certainly accounted; ambiguous pre-existing rows must retain the reservation.

## Prior findings and amendment requirements verified statically

The earlier invalid tampered-checkpoint fixture now provides identity and the full grid. The composed fixture selects both validation strata, while the production 512/1,024 panels remain intact. SIGTERM handling surrounds all external watchdog children, the D audit now has a separate externally bounded worker, and the targeted suite includes a tiny SA probe and descendant-timeout cleanup test. Production/audit decisions require a distinct hash-bound Astra acceptance artifact. Check/audit charges preassign one UUID, and uncertain ledger append reconciliation uses that identity. These changes address the structure of the seven previous findings subject to the certainty corrections above.

The statewise code identifies states without q in the uniqueness key, then separately requires unchanged q and accepted legal masks. It uses the original map/stratum weights, legal argmax tie order, all four transition groups and the fixed 30 adjacent plus 800→2,000 comparisons. Partial positive-q action with exported p=0 makes decomposition unavailable; components are not clipped. Weighted `1−m` is checked against saved nonoptimal mass, and the original per-owner KL aggregate is checked against statewise KL. Raw curves and statewise records remain available for audit. I found no new training, optimizer, backward, or final-test path. No runtime duration or numerical outcome is claimed by this static review.

DRIVER_REVIEW_VERDICT: CHANGES REQUIRED
