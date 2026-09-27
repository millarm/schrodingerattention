# Four fresh paired-seed replications — frozen before results

User authorization, 2026-09-19: “Replicate across training seeds.” Astra plans
and supervises, fresh-context Terra implements only narrow additive wrappers,
Sol independently reviews. Earlier Astra implementation exceptions have ended.
No changes to frozen model, dataset, optimizer, batch size, exposure, final-test
restriction or original 7200-second total cap. Preserve all discovery artifacts.

## Fixed design and estimands

Fresh seeds **1702,1703,1704,1705**, each softmax and Schrödinger trained from
paired initialization to exactly **8000 updates** (512,000 sampled state
exposures). Use the existing reviewed trainer, common per-seed minibatch prefix
and evaluation uniforms. Fixed sequential run order:
1702 SM→SA; 1703 SA→SM; 1704 SM→SA; 1705 SA→SM.
No outcome-based seed selection or early stopping. A genuine budget/technical
failure is an incomplete replication, not permission to choose replacement seeds.

**Primary endpoint:** full-validation T=1/K32 exact valid-route quality at8000,
equal-map routine/challenge80/20 mixture, paired difference SA−SM per seed.
Report all four differences, their fresh-seed mean, sample SD, range, direction
count and descriptive95% paired-t interval mean±3.182446×SD/√4 (df3). The
interval's normality assumption is weak with n=4; no map/sample pseudoreplication
or claim of definitive statistical proof. Seed1701 is discovery, shown separately.
The seed varies initialization, training stream and decoding uniforms together;
it is not an initialization-only replication. Within-pair streams are common.
Greedy comparisons avoid decoding Monte Carlo noise. Four positive signs alone
do not establish a two-sided5% significance result.
An optional pooled-five summary is exploratory and must not replace the fresh
primary estimate. No p-values or selective seed removal.

Key secondary endpoints at8000: frozen unseen-routine-map cohortC transfer,
then A/B transfer, fullvalidation U_novel/K, V_novel/K, U_valid/K, properKL/Brier,
entropy versus teacher ambiguity, per-problem complementary greedy outcomes and
valid-route overlap, training core time and end-to-end cost. Retain1k/2k/4k/8k
fullvalidation trajectories from the reviewed trainer; do not introduce a new
training harness. Secondary comparisons are descriptive/unadjusted, not separate
confirmatory successes. Both models must be scored on the frozen ABC rows for
EVERY fresh seed; discovery softmax scores cannot substitute.

## Frozen analysis and control

Reuse the accepted paired-behavior helpers and exact saved ABC support hash
`2bcde9c3823a41cc0a0ac7c4383ef1323658ca47b5b7a53336f4f4e2adf9babc`.
No cohort reconstruction:24 triplets,144 routes/768 states per cohort. Original
map/goal exposure and geometry/multiplicity qualifications remain. New outputs
retain explicit problem identities; historical fullvalidation route order relies
on manifest-bound producer/dataset order plus verifier corroboration, with the
accepted all-invalid permutation limitation stated.

Use each fresh seed in ALL rollout uniform calls, pair models at identical seed,
splitcode1 fullvalidation/C and splitcode0 A/B, replicate0,K32. Assert exact
checkpoint seed/mode/update/source/config/input identity, shared initial tensors,
all8000 minibatch digests and checkpoint/sampler lineage. Immutable event hashes
and full state/q order bind stored fullvalidation results. No repeated original
fullvalidation inference. At8k only, repeat the SAME grid SA T=.75,1,1.25 versus
its paired SM T1: two new SA fullvalidation rollout calls, nearest mixtureQ,
lowerT tie break, then |ΔQ|≤.02 mixture and≤.03 in both strata. If unmatched,
report all points and no quality-controlled novelty claim; no expanded search.

## Measured forecast and prospective resource allocation

Starting global debit2065.331896587045/7200; remaining5134.668103412955 seconds.
Seed1701 measured charged training segments sum477.173082417 seconds per pair
(SM189.765040709,SA287.408041708), including six fullvalidation events and owner
allowances. Four fresh pairs at1.5× conservative overhead predict2863.038494502
seconds. Fresh uninterrupted runs remove repeated setup rather than add events.
No new profiling training is necessary. Four bounded analysis jobs≤124 seconds
each including allowances=496; development80, audits150, final contingency200.
Total planning envelope3789.038494502<5134.668103413. This is a forecast, not
permission to exceed the global cap or hide overruns. Actual costs/remaining
budget are checked before every launch; reserve the complete remaining fixed
sequence using this forecast, not observed model quality.

Explicit ledger attribution: all eight training attempts are stageB; development
and focused tests (≤80 seconds) are stageA; all analysis jobs (≤496), independent
audits (≤150) and any finalization/contingency allowance (≤200) are stageD.
Thus projected stage totals are B3343.811576919<3500, A491.401817917<700,
D1096.153399000<1300. No attempt is charged to a stage by convenience afterward.
“One compute job” means serialized execution, not one owner for the whole study:
every training/analysis attempt has its own immutable output and explicit exit.

Existing ledger debits: B480.773082417,D250.153399000,A411.401817917.
Prospective resource-only transfer1500 seconds from unused C to B changes stage
ceilings from A700/B2000/C1900/D1300 to **A700/B3500/C400/D1300**. Same total,
same carry923.003597253, same global7200 and original ledger. Accepted source
files remain unchanged. The original CLI's pilot guard restricts fresh runs to
seed1701/1000 updates; it must NOT be patched or bypassed by pretending these are
old pilot commands. A small reviewed replication entrypoint validates exact fresh
seed1702–1705, mode and8000 authorization, asserts old ceilings and installs the
resource-only table, then calls the accepted paired_models/scheduled_training/
OwnedAttempt seams directly with unchanged scientific arguments. The original
CLI guard remains intact; the new authority is explicit in this amendment.
Bind wrapper/resource/decision hashes in new command records; do not pretend the
wrapper is part of the original frozen source hash. Analysis uses this same
ledger/owner, at most120-second alarm plus4-second allowances per seed.

## Bounded implementation and gates

1. Sol reviews plan and resource amendment. Terra first provides only the small
   replication entrypoint with tests showing strict fresh-seed/update authorization,
   unchanged scientific config and seed/mode forwarding to accepted seams.
   Sol exact PASS precedes the first training command.
2. Training follows the fixed order with unique `replication-SEED-MODE-8000`
   outputs under the existing root/lock/ledger. Full command/session results and
   explicit terminal exits; never relaunch a yielded process. One compute job.
   Terra may write the additive analysis while training runs but may not run
   tests/inference concurrently. No second approval needed for fixed routine runs.
3. Analysis parameterization is a small separate job: source/checkpoint/event
   bindings for fresh seed, accepted pure comparisons, BOTH models on frozen
   ABC at8k, two quality-control calls, raw and equal-map outputs. Reuse accepted
   helpers rather than copy a new framework or discovery-only hardcoded paths.
   Literal tests must reject wrongseed/checkpoint, exercise actual retained
   record interfaces, and show requested seed reaches both model rollout calls.
   Sol reviews exact version before each job's shared-code use; no partial
   handoffs called complete. Two correction cycles then bounded blocker/respec.
4. Sol audits identities, fresh-seed paired endpoints/statistics, transfer and
   quality-control interpretation. Final report separates discovery from fresh
   replications and reports cost/limitations. No final-test access, newseeds,
   model/data resizing or automatic subsequent experiment.
