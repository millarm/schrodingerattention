# Fixed 200,000-update continuation

2026-09-27. Astra prospective amendment for the user's request to run much
longer. “200,000 generations” means **200,000 total optimizer training updates
per model**, including the completed 16,000, not generated answers or additional
independent seeds. This authorizes a new local extension, superseding the old
16k stopping boundary only for this study. Historical evidence stays intact.
Astra specifies and accepts, GPT-6 Luna implements and operates, GPT-6 Sol
independently reviews. No production before exact implementation PASS.

## Fixed design

Continue seeds 2201 and 2202, both softmax and Schrödinger, to exactly 200,000
total updates: 184,000 new updates per owner. Order remains 2201 softmax,
2201 Schrödinger, 2202 Schrödinger, 2202 softmax, one compute process at a time.
Reuse the accepted model, data, map-balanced stream, batch64, AdamW lr .001,
clipping and initial tensors. Do not tune, replace seeds, access final tests,
change representation, or introduce new tasks. These are continuations of two
existing exploratory pairs, not four new independent replications.

The accepted checkpoint contains model, optimizer, sampler state, torch CPU RNG,
update identity and parent hash; the accepted resume interface restores these.
Require exact resume binding to each reviewed initial and 16k checkpoint and a
bounded split-versus-uninterrupted test. If exact resume is unavailable, stop
the launch gate and specify a same-seed restart from zero with the same horizon
and budget; do not silently reset optimizer or RNG while calling it continuation.

Score the full original13-point grid and every2,000 updates from18,000 through
200,000 (105 points total). Reuse the immutable original13 scores and checkpoints
with explicit lineage rather than reevaluating them. New scores use the identical
512 validation problems,1024-state proper bank, T1/K32, split1/replicate0 and
common uniforms. Aggregation remains equal maps/strata/seeds and .8/.2 mixture.
Keep accepted every100-update checkpoint retention and durable per-update CE
and batch digests. Validation never feeds the optimizer.

## Endpoints and interpretation

Extend exactly the previous Q estimator M(u)=[Q(u−4000)+Q(u−2000)+Q(u)]/3,
G(u)=M(u)−M(u−4000), at every2k end from8k through200k. Low gain is G≤.005;
the final two windows198k/200k must qualify for a sustained finite-horizon
plateau. Report earlier consecutive qualifying windows followed by a rebound,
negative gains as deterioration, and right-censoring when final windows fail.
Extend the same sampled-CE2k means/relative improvement rule and final-two
confirmation. No observed plateau or quality crossing stops training.

Retain primary tolerated Q milestones .29 and .37198, exact .30/.38198
sensitivities, consecutive-point acquisition, grid bounds, censoring, KL>.40
and challenge Q<.08 fragility flags, and positive-Q conflict margins .02nat
KL/−.02 challenge Q. Report all Q/KL/Brier/challenge curves, per-seed differences,
and fixed16k→200k,100k→200k,180k→200k changes. Sustained late learning is
descriptive evidence in these fixed windows, not a newly tuned threshold.
The historical early curvature contrast is retained but is not new evidence.
Do not select the best checkpoint retrospectively as the primary result.
Longer route-quality improvement can coexist with worse proper scores; earlier
validation-KL worsening makes this distinction central. Two seeds do not support
population-level significance, and reused validation limits generalization.

## Prospective resources

Historical ledger remains byte-for-byte frozen at SHA256
ddfe5b2df043d940b1dcbf30ed367483abac1a5935863d123a1e9c6267229da2,
qualified debit5855.153244667692/7200s, including its existing uncertainty.
Do not transfer unused historical budget or reset its accounting.

Create a separate zero-carry ledger under execution/long_horizon_200k, explicitly
recording this new allocation and the historical reference. New hard cap21600s
(6 local elapsed compute-hours): A300s development/smoke/tests, B21000s
production, D300s audit. Per-owner full external envelopes3500s softmax and7000s
Schrödinger include startup, scoring, integrity, cleanup and finalization.
No paid compute. Expected training core from the actual16k records is about
7612s for all continuations; conservatively scaling whole prior owner charges
by184k/16k and adding50% gives approximately5.2h, hence the6h cap. This is a
ceiling, not a runtime claim. Keep one process and two CPU threads.

Prior checkpoint directories are about142MB per16k owner; retained100-update
checkpoints add about6.5GB total. Disk has about245GiB available. Require at
least12GiB free before each owner and reserve/check available production budget
before launch. After the first complete pair, remaining second-pair envelopes
must fit; additionally1.5×observed same-mode external charges must fit those
envelopes. Resource/integrity failure stops with partial/censored evidence;
no outcome gate, automatic retry, replacement or horizon shortening.

## Launch and monitoring

Separate new modules/owners preserve all historical implementation and artifacts.
Reuse the accepted external watchdog's verified process-group cleanup. All
attempts, including failures/tests, are charged exactly once in the new ledger;
no ambiguous finalization releases the reservation. Bind decisions to exact
source, plan/spec/review hashes, ledger EOF, inputs and resume checkpoints.

Luna may launch an accepted sequential batch coordinator as a persistent local
process. It writes its PID, owner progress and explicit terminal records,
checks sources/budget/cleanup between owners and stops on any failure. Durable
curves/checkpoints survive loss of the conversation. Parent may register a
quiet heartbeat to inspect meaningful completion/failure and request audit;
monitoring does not grant retries or changes. Do not claim completion until
all four owner terminals, complete paired digests and final Sol audit pass.
