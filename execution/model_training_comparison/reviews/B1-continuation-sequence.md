# B1 additive authorization — conditional baseline ladder

## Verdict: PASS (prospective, conditional)

The accepted B1 authorization extends to the remaining frozen, plan-prescribed **softmax seed-1701 baseline-only** ladder: resume the immutable update-2,000 checkpoint to update 4,000 and, only if at least one mandatory primary usability gate still fails there, resume that immutable checkpoint to update 8,000.

This proportional authorization is supported by the completed update-2,000 result: greedy quality `0.5364583333333334` and T=1, K=32 quality `0.2713541666666667`, both decisively below the unchanged `0.80` and `0.70` thresholds. Brier is `0.15684205072991808`. Because the primary conjunction already fails, an operating-point search cannot make the complete usability gate pass at this checkpoint.

The authorization is valid only while all of these conditions hold:

- source, configuration, input identities, seed, optimizer/replay state, and batch stream remain unchanged;
- each resume starts from the exact preceding accepted softmax checkpoint and preserves its checkpoint-chain identity;
- each command has one uniquely recorded launch and explicit terminal result;
- before each launch, its conservative forecast fits within the remaining stage-B allocation;
- no Schrödinger continuation, main-seed release, test inference, or source modification occurs.

After update 4,000, continue to 8,000 only if greedy quality is below `0.80` **or** T=1 quality is below `0.70`. If both primary thresholds pass, stop immediately for the full operating-point and remaining-learning-gate review; this prospective approval does not authorize bypassing those gates. Stop in all cases at update 8,000 and perform one independent final result/checkpoint-chain audit before any later scientific decision.

The stated conservative forecasts—less than 110 seconds for the update-2,000-to-4,000 segment plus endpoint and less than 130 seconds for the update-4,000-to-8,000 segment plus endpoint—fit comfortably within the reported stage-B balance of `1796.986114833015` seconds. No computation was performed for this records-only authorization and no ledger charge is due.
