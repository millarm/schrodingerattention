# Productive-diversity v2 plan and dataset-contract review

## Verdict: PASS

The corrected scientific plan and frozen dataset-only contract are mutually consistent and suitable for gated implementation. The five prior findings are resolved without expanding the model comparison or weakening the strict novelty definition. The first execution stage remains proportionate: build and review only the 8×8 data/oracle engine, then the minimal isolated wrapper, before one authorized ladder invocation. No model scaffold or training is permitted before a reviewed dataset PASS.

## Exact documents reviewed

- Corrected plan: `productive_diversity_v2_plan.md`, SHA-256 `3eb46fa905793da806acf05cdafb02db96e6137d7c5d2dbe8c5c004b74f56dce`
- Dataset contract: `execution/next_level_v2/specs/00-dataset-contract.md`, SHA-256 `81af0064d865ce7f16ddf16a4389349a4eb357be23fa6890bd49c7ac7696adba`
- Prior review: `execution/next_level_v2/reviews/00-plan.md`, SHA-256 `bfb8db015a4b34f47d0bfbf20d5667b0607d355464e876da958c0ebdc7ad6793`
- Accepted prior benchmark report used only as motivation: `execution/next_level/final_report.md`, SHA-256 `99384ef4110e1eef8000cb1b8fedbe95524b5662ac4efc917ff5d464ca5b4bc6`

## Closure and consistency checks

- **Power:** the main endpoint remains one K32 result per problem. Pilot seed effects average four independent K32 replicates, while the planning variance restores the missing three quarters of conservatively upper-bounded within-seed Monte Carlo variance. Separate chi-square bounds, the single-K32 MC-SD limit, ten-seed t calculation, raw replicate reporting, and proxy-only interpretation are exact.
- **Quality:** routine equivalence, 1 pp overall noninferiority, and 2 pp challenge noninferiority are independent conjunctive gates. The 80% routine weight therefore cannot conceal a material challenge-quality loss.
- **Aggregation:** valid, known-valid, novel-valid, and distinct-route counts are aggregated problem-to-map-to-stratum before fixed 0.8/0.2 weighting. Known-valid mass is a ratio of weighted attempt masses; repeated novel attempts affect `V_novel` but not `U_novel`; zero/NA behavior for conditional fractions, support coverage, and duplicate concentration is explicit.
- **Dataset ladder:** rung A and then B are dataset-only, use one 8×8 task, and stop at the first PASS. B is allowed only after a preserved scientific construction failure, never after timeout/runtime failure or model information. Both failures stop without adding another rung.
- **Families and sizes:** rung A fixes equal III/LLL routine and IIL/ILL challenge allocations; rung B fixes IIII/LLLL routine and IILL challenge allocation. Training, validation, and test map/problem counts are exact, every selected map supplies 16 problems, canonical maps cannot cross splits, and held-out eligibility is oracle-only.
- **Length matching:** training receives uniform Hamilton quotas over every allowed integer length, one residual flow across all 64 maps, and at least 16 examples per length. Each evaluation stratum Hamilton-scales the actual training proportions and uses one global map-to-length residual flow. No map replacement, bin merging, or outcome-driven relaxation is allowed.
- **Novelty:** completion counts, all supervised-DAG suffixes, strict D4/translation/reversal signatures, routine `M_novel=0`, challenge `M_novel>=4` and ratio `[.25,.75]`, and full support hashing preserve the accepted conservative definition. The plan's primitive/orientation coverage requirement remains binding and should be recorded in the dataset audit.
- **8×8 isolation:** every geometry, BFS, candidate, replay, and flow call must receive `n=8`; action-string signatures correctly remain geometry-free. New v2 files and ledgers are isolated from all 6×6 artifacts. Regression coverage beyond cell 35 guards against accidental old defaults.
- **Budget:** the 7,200-second forecast includes trainings, checkpoints, caches, every decoding/control path, Python rollout and uniqueness/signature work, score banks, bootstrap, serialization, audit, and reserve. Stage 0 is capped at 900 seconds; implementation tests at 150 seconds with 120-second per-command limits. Failed rungs, tests, and audits are charged.
- **Execution safety:** fresh immutable outputs, owned O_EXCL lock, interrupting stage/global deadlines, strict JSON, exact manifests, isolated fixture ledgers, full command results, observed exit status, and no relaunch-on-yield are required. Scientific construction failures are distinct from technical/budget failures.

## Implementation boundary

Terra may first implement only `schrodinger/productive_diversity_data.py`, its focused tests, and new v2 records. Pure interfaces may accept small injected fixtures, but production counts/gates remain frozen and production-scale generation is prohibited during tests. The second block is only the minimal artifact/attempt wrapper and injected CLI integration. Each complete block requires independent review; partial scaffolding is not acceptance evidence.

## Unknowns preserved by this PASS

Pool supply, flow feasibility, strict novelty strata, full support enumeration cost, row-token learnability, pilot variance, runtime forecast, and the 1 pp architecture effect remain unknown. A dataset, learning, power, quality, or runtime gate failure is a valid stopping result, not permission to alter the rung, threshold, family mix, or novelty definition.

No pool generation, dataset construction, model creation, pilot, training, or evaluation was performed during this document review.

