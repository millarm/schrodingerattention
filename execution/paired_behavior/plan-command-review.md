# Independent review — paired-behavior plan and SA resume command

## Verdict: PASS

Reviewed frozen records:

- `plan.md`: `be5e5fea4fd5f2ee0e4cb3013637127b9437409bef6d6fa993f06777e65b39be`
- `sa-resume-decision.json`: `77e3c6bbf127bcb14e030784f487a129e3e3c7d10534fbdef54ad0a837cc4ea6`
- `command.md`: `02c70d9a5ed464f57658b4f5818af0162ad19af7bd133ef5a1af8194d8c8bf8e`

The user's authorization explicitly and narrowly overrides the earlier baseline-first stop for one exploratory paired seed. It does not alter the global cap, model, optimizer, sampler, data, thresholds, test-release policy, or accepted runner.

### Resume identity and command

The proposed command points to the immutable seed-1701 Schrödinger update-1,000 checkpoint. Its byte SHA-256 is `61850806ace41a2ad6ecdbc9317d50eba4c5841d3a8fce4ed57a9d081610ca3b`, exactly matching both the owner result's final checkpoint identity and the decision's `resume_identity.checkpoint_hash`. The decision also matches:

- mode `schrodinger`, seed `1701`, update `1000`;
- initial checkpoint hash `0ef4eb59d3e6d8d3de125f8340dc9524d72f9774a7958cea85b3a06b27436feb`;
- initial model identity `ebfcd4005853e29eab693c583c01bdf645b665848525eb7a0418abb36285ad9d`;
- frozen source `bf7efbddb88bff06029369cba071d79f17340d701928b7f527baa6df7e517329`;
- prepared data `10e5f96a98b4dcb944cf81b65eb43eb4ed5a8c8211bf9d1f55af2f0bc4814e49`, dataset manifest `305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395`, and all selected-bank identities;
- accepted frozen configuration hash `870f62c96a8b0ed994d3c4d795514bf6fd513c0c771ba32750542b667155fe90`.

The output name `paired-behavior-sa-8000` is currently fresh. The command uses the reviewed owner/ledger/lock machinery and targets exactly update 8,000. This PASS authorizes one launch only; a yield is not permission to relaunch. The resulting comparison is valid only if the complete update-1–8,000 paired batch-digest sequence, source/config/input identities, common initialization, optimizer/RNG resume chain, and checkpoint chain all match the accepted softmax history.

### Scientific scope

The three blocks are coherently separated:

- Equal-update trajectories compare exposure, not CPU time. Any time alignment is checkpoint-based, at or before the common cutoff, with actual updates and no interpolation.
- Behavioral comparisons require explicit problem/state identifiers and q/route ordering before pairing; no blind array zip is acceptable. Route-set novelty uses valid exact routes and complete saved training support, while sampled attempts remain within one trained-seed replication.
- The A/B/C transfer analysis reuses the immutable matched rows, quotas and route order and scores only the missing Schrödinger side. It does not reconstruct or enlarge cohorts.

The update-8,000 temperature grid `{0.75, 1.0, 1.25}` is a predeclared, approximate validation-only descriptive quality control. Its mixture and stratum tolerances, tie rule, sampling seed/replicate and complete reporting are frozen. It is not the original 90%-quality operating-point gate, confirmatory evidence, test evaluation, or authorization for further search. An unmatched result remains unmatched rather than relaxing tolerances.

One seed can establish paired differences within this run but cannot establish a general architecture advantage, equivalence, useful creativity, or independent-seed uncertainty. Quality, diversity, uncertainty, transfer and mechanism findings must remain separate.

### Resource and execution gate

The prospective 2,200-second envelope fits within the remaining global budget and preserves the existing runner's stage-B deadline. It is a resource reallocation, not a cap increase or scientific change. Production may proceed with the exact command now; additive behavior-analysis implementation and any new inference remain separately gated by their required exact-version review.

Static review only; no training, tests, inference, or ledger charge.
