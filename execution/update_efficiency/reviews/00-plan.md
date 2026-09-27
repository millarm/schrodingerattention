# Sol independent protocol review — update efficiency plan

**Plan SHA-256:** `d1e1443d0dffe1fbf0f90a120c8acbc03dd5555167f65b20e01a16c0d9f1bae5`

**Implementation specification SHA-256:**
`9830d0ac638e9bd4b088589098bbe4a75054739775e0c8d00cb4ff82d7141acd`

**Verdict: PASS.**

Static protocol review only. I read the plan, current study status, execution
protocol, accepted training seam, evaluator interfaces and relevant accepted
reviews. I did not import project code, run tests or training, inspect final-test
payloads, append a ledger entry, or edit implementation sources.

## Additive wrapper specification feasibility

`spec-01-wrapper.md` is feasible against the inspected accepted interfaces and
is sufficiently bounded for Terra implementation. Its four-file implementation
scope leaves the accepted model, data, optimizer, trainer, evaluator and old CLI
unchanged. The one-seed/one-mode owner can call the accepted pure seams directly,
so the old CLI's seed-1701 authorization guard need not and must not be bypassed.
The separate stdlib process driver has a narrow supervision/accounting role and
does not create a second scientific training path. Reuse of reviewed pure
watchdog helpers is acceptable only through the specified helper-level boundary;
the D1 execution/decision/reconciliation policy is out of scope.

The composed fixture and literal tests cover the relevant integration risks:
real accepted train/checkpoint/restore/evaluator/serializer/owner behavior in a
test-only short schedule, production-default immutability, identity mutations,
paired stream and initialization checks, endpoint uniqueness, partial records,
manifest-finalization failures, timeout cleanup, resource reservation, and
unreachability of `_prepared_ids`, final-test loaders and the old CLI. The
10-second focused smoke plus 30-second focused suite fits the stage-A100 ceiling,
with failures and any inspected correction still chargeable inside that same
ceiling. No production release follows from the specification or its tests;
exact implementation review remains mandatory.

One binding detail must be literal in the implementation/handoff, not selected
dynamically: identify the canonical retained metadata owner and validation-only
hash evidence by exact path and SHA-256 (the accepted production lineage names
`execution/model_training_comparison/prepare-001`). If another retained COMPLETE
owner is intended, Astra must name it before tests. This is not permission to
parse `prepared.json`: only already-bound owner/manifest metadata and copied
historical IDs may be read. The choice must not be made from observed study
results. The implementation must also show how its local prospective stage table
is checked against the imported original constants and current ledger prefix
without mutating accepted module-global policy for unrelated commands. These are
concrete acceptance details within the present specification, not requests for
a broader framework.

## Scientific design

The plan answers a bounded update-count question rather than architectural or
runtime superiority. It correctly labels the 30% target as an early-learning
milestone with a one-point lower Q tolerance, retains the exact 30% crossing as
sensitivity only, and expressly excludes mature-8k parity, wall-clock/FLOP/energy
claims, broad planning claims and final-test generalization.

The primary checkpoint rule is coherent and prospective. For each seed/model,
the earliest nonzero 500-update grid point passing overall Q, mixture KL and the
challenge floor must be followed by a second passing grid point. The earliest
rule implies that the preceding scored point failed (apart from the separately
handled grid-0 anomaly), so `(previous, acquisition]` is a valid resolution
interval. No interpolation or monotonicity is assumed. A lone pass at 4000 is
correctly unconfirmed; non-acquisition remains censored rather than imputed to
4000. The all-four-pair table, earlier/same/later/unresolved counts, paired
differences, ratio bounds and prohibition on a completers-only four-pair summary
are appropriate for the coarse grid.

The promising-signal screen is also suitably limited: all four pairs must be
evaluable, at least three must favor SA, the median upper-grid ratio must be at
most 0.8, and at least three conservative interval upper ratios must be below
one. The plan does not turn a failed four-pair screen into equivalence or a
strong significance claim. Seeds—not checkpoints, states, problems or sampled
routes—are the training replication units.

The paired design is fair and reproducible: seeds 2201–2204 jointly determine
initialization, minibatch stream and evaluation uniforms; architectures share
the paired tensors and stream; model order alternates; both modes always train
to 4000; and evaluation is retrospective on an identical fixed grid. Continuing
after an early crossing prevents adaptive stopping from changing training
exposure or checkpoint availability. Reused validation maps and their resulting
conditional interpretation are disclosed.

## Accepted-interface fit

The proposed narrow wrapper fits the accepted interfaces without changing them.
`scheduled_training(..., validation=None)` creates the initial checkpoint,
performs the unchanged optimizer/sampler updates, writes per-update batch
digests, and saves every 100 updates (including 4000), while omitting its
unrelated scheduled evaluator/probe events. The fixed 0,500,...,4000 checkpoints
can then be loaded and scored after training with accepted `evaluate_proper` and
`evaluate_rollouts` surfaces. `evaluate_proper` exposes teacher-relative KL,
Brier and teacher entropy with problem-to-equal-map-to-stratum 0.8/0.2
aggregation; `evaluate_rollouts` supports the frozen seed, split 1, replicate 0,
T=1, K=32 construction and exposes overall mixture and challenge-stratum Q.

The no-final-test boundary is explicit: only manifest-bound COMPLETE retained
owners may supply identities; accepted hash-checking training/validation loaders
are used; `_prepared_ids`, test-loader calls and prepared JSON parsing are
forbidden. Scoring inside the same owned attempt, immutable unique attempt names,
locks, complete terminal records and no relaunch of a yielded process give the
implementation an auditable ownership boundary.

Implementation acceptance must preserve these literal details:

- Verify seeds 2201–2204 have no prior owner or checkpoint before any launch,
  and reject rather than overwrite or choose replacements.
- Record and compare the shared-initial digest and every paired update's batch
  digest before accepting a pair; retain model order only as the frozen
  alternating schedule, never as a result-dependent choice.
- Bind every loaded scoring checkpoint to seed, mode, update, source, accepted
  training config, initial identity, checkpoint-chain identity and the same
  manifest-bound input IDs. Retain the new study-plan hash separately; do not
  mutate the accepted training config merely to replace its historical plan
  identity.
- Define target fields directly from accepted outputs: overall
  `rollout.mixture.Q`, challenge `rollout.strata.challenge.Q`, and weighted
  teacher-relative `proper.weighted.kl`. Assert finite raw and aggregate scores,
  expected bank/problem cardinalities and frozen bank hashes before setting a
  pass flag.
- Implement the median of four upper-grid ratios with an explicit conventional
  even-sample definition, preserve infinite bounds when the SM lower endpoint is
  zero, and keep exact-Q sensitivity and isolated-crossing fields descriptive;
  neither may feed the primary acquisition result.
- Exercise only bounded synthetic/fixture tests before production. Exact
  implementation, ownership/failure behavior, checkpoint binding, target flags,
  censoring, interval arithmetic, all-four aggregation and the final-test
  prohibition require a separate Sol PASS before B1.

## Resource and launch review

The resource arithmetic is consistent with the current qualified ledger headroom.
Starting from `4764.416447001050 / 7200` leaves
`2435.583552998950` seconds. The prospective A/B/D allowances are
100/1600/100 seconds, totaling 1800 and leaving approximately 635.58 seconds
globally unallocated. Moving 400 seconds from the previously available D ceiling
to B yields A1000/B3900/C0/D1000: existing plus proposed maxima are A960.001,
B3886.766 and D794.646, each within its amended ceiling. This is a transfer
inside the existing global cap, not a reset or extension.

The staged gate is valid: B1 is the complete fixed seed-2201 pair and is part of
the primary study; B2 may proceed only when 1.5 times the observed complete
per-mode attempt cost forecasts all remaining fixed runs inside the remaining B
allocation. Continuation is resource/integrity-only and cannot depend on target
crossing or which architecture appears better. All failed attempts count, one
process runs at a time, and numerical/provenance failure or budget exhaustion
stops without automatic retry. CPU seconds remain accounting metadata only.

## Non-blocking limitations

The target and guard margins are practical, newly selected diagnostics rather
than validated equivalence margins. Four paired seeds and 500-update resolution
can readily leave the result unresolved. The reused validation population means
even a passing screen is a promising conditional early-update signal, not
untouched-map confirmation, mature-quality parity or general architectural
superiority. The plan states each limitation adequately.
