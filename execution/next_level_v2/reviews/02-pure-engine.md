# Productive-diversity v2 pure-engine review

## Verdict: CHANGES REQUIRED

The pure engine implements the central deterministic mechanics correctly, but it does not yet preserve enough evidence to enforce one frozen dataset requirement, and its ladder helper loses the exact scientific failure identities. One explicit oracle-count invariant and the corresponding focused regressions are also missing. These are bounded pure-engine corrections; no production inventory, wrapper, model, or training work is authorized by this verdict.

## Exact versions reviewed

- Current accepted plan (title/status-only changes after scientific acceptance): `productive_diversity_v2_plan.md`, SHA-256 `110fabfe4b94df5f73d51a85a3e00acf074fceb525e75815702c2f010fffec7e`
- Current accepted Stage 0 contract (title/status-only changes after scientific acceptance): `execution/next_level_v2/specs/00-dataset-contract.md`, SHA-256 `1dc21a4314e6d66510eb31ba176d673ab44709925f5155da189e436f8900a9c4`
- Acceptance provenance: `execution/next_level_v2/decisions.md` records scientific plan SHA-256 `3eb46fa905793da806acf05cdafb02db96e6137d7c5d2dbe8c5c004b74f56dce` and contract SHA-256 `81af0064d865ce7f16ddf16a4389349a4eb357be23fa6890bd49c7ac7696adba`
- Handoff: `execution/next_level_v2/handoffs/00-pure-engine.md`, SHA-256 `334a6301f964848e29f535e5321f1848648c89e461abfc1cb76c9e136e5212d6`
- Implementation: `schrodinger/productive_diversity_data.py`, SHA-256 `1d05d26073426c86a45e2c29483cf11d03e96db96ef3370261db3ca79d264a55`
- Focused tests: `tests/test_productive_diversity_data.py`, SHA-256 `65375fbb6515108b2c28f83732495616ec841bd97adf7747890a19bc429481ab`

## Required corrections

1. **Provide auditable component kind/orientation coverage.** `pool_family` retains only the D4-canonical union bytes and `inventory` therefore cannot yet establish the frozen plan requirement that both primitive shapes and all rotations occur in selected training. Because accepted components are orthogonally disconnected, deterministic connected-component reconstruction from canonical walls is sufficient; no pre-canonical draw frame needs to be retained. Add a pure helper that classifies the two I orientations and four L missing-corner orientations in canonical coordinates, plus a small fixture. The later wrapper must gate and report coverage of all 2+4 orientations across selected training maps without changing draw, rejection, identity, sorting, or selection semantics.

2. **Preserve both rung failure identities.** When A and B fail, `first_passing_rung` raises `DATASET_LADDER_FAILED` with only each exception's `evidence`; both `ConstructionFailure.outcome` values are discarded, and the first exception is absent from the cause chain. Store `{outcome, evidence}` for each rung so the wrapper can persist the exact two scientific stop reasons and distinguish which gates ran. Test two different A/B outcomes and their exact retained payloads. Keep technical exceptions uncaught and prohibit B after them.

3. **Enforce BFS multiplicity versus complete enumeration.** `eligible_novelty_pairs` and `novelty_for` assume that the enumerated route count equals frozen candidate `M`, yet the former divides by `M` and neither function checks equality. Add an exact invariant before eligibility/novelty classification. A mismatch is a technical/oracle-integrity failure, not evidence of dataset infeasibility and must not advance the ladder. Test both the valid equality and an injected mismatch with a specific technical failure.

4. **Close the focused regression evidence for these corrections.** The current ladder test cannot detect finding 2 and there are no orientation-coverage or mismatched-multiplicity tests. Add the focused fixture tests from findings 1–3. Exact rung allocation/split-count integration belongs to the already-separated wrapper block; production feasibility must not be tested in this correction.

## Accepted static checks retained

- Pool RNG uses `PCG64(SeedSequence([80000, rung_index, family_code]))`, draws components in family order with replacement, applies overlap/touch/D4-duplicate rejection order, and globally sorts canonical identities.
- Candidate enumeration uses explicit board size, the frozen length and `16 <= M <= 256` bounds, ordered start/goal pairs, and deterministic sorting.
- Split map and problem streams use the frozen seeds and distinct final stream components. Problem streams are consumed continuously by family in sorted map/ascending-length order.
- Hamilton allocation and the shared deterministic reverse-edge residual flow enforce global quotas and 16-per-map capacity without per-family flow separation.
- Training supervision deduplicates nonterminal shortest-DAG states and uses exact completion-count q targets. Support contains every nonempty suffix of every selected shortest route, is sorted, length-delimited for hashing, and is not truncated.
- Held-out eligibility is oracle-only; routine and challenge thresholds, endpoint inclusivity, prior-split exclusions, bounded fact/signature caching, first-PASS stopping, and propagation of ordinary technical exceptions otherwise match the contract.

## Independent checks and charge

I independently recomputed SHA-256 identities and performed a complete static source/test trace against the accepted plan and Stage 0 contract. I did not run pytest or any pool/inventory command because the static findings already determine the verdict. Independent charged compute: **0 seconds**. Terra's reported five-test result and `3.671836167s` ledger total were inspected but not independently rerun.

Production pool supply, construction feasibility, runtime, and output artifacts remain **NOT EVALUATED**.
