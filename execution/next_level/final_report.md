# Next-level feasibility result

Status: ACCEPTED — [Sol results/report audit PASS](reviews/07-feasibility-results.md).
The authorized plan completed at its Stage0 stop; no model was built or trained.

## Result

**FEASIBILITY_FAILED_NOVELTY.** This frozen benchmark does not provide enough
structurally novel correct solutions for the planned productive-diversity test.
The execution goal's prescribed stopping gate was reached; this is not a
negative result about Schrödinger attention, usable learning, or creativity.

| Feasibility item | Observed | Required | Result |
| --- | ---: | ---: | --- |
| Eligible canonical maps | 794 | Enough for disjoint frozen splits | Pass |
| Training / validation / ID / IL problems | 1,024 / 128 / 256 / 512 | Same | Pass |
| IL problems with >=4 novel shortest routes | 6 / 512 (1.17%) | >=256 / 512 (50%) | Fail |
| IL maps containing those qualifying problems | 3 / 32 | >=16 / 32 | Fail |

The inventory contains86 II,378 LL and330 IL maps, all with at least16 eligible
start/goal pairs. The fixed seeded selections and training-derived distance/
path-count bin matching completed. No alternative maps were tried after seeing
novelty, and no thresholds, equivalences or support definitions were relaxed.

## Why this test cannot demonstrate the proposed effect

The training dataset exposes10,314 distinct supervised state/goal inputs.
Enumerating **all** shortest suffixes from the training shortest-path DAGs
produced598 canonical route signatures. Canonicalization includes rotations,
reflections, reversal and translation invariance, exactly as planned.

Among512 unseen-composition IL problems:

- 502 have no structurally novel shortest route under that definition.
- 10 have at least one; only6 have the required four or more.
- There are5,062 distinct correct shortest routes in total, but only43 have
  signatures absent from the training suffix support.

New obstacle-map IDs therefore do not generally imply new route structures in
this small construction. Counting outputs as "original" merely because they
solve a new map would have made novelty largely vacuous. The pretraining gate
prevented such a claim and avoided spending the training budget on a test with
insufficient qualifying cases.

This is evidence about **the frozen selected dataset under the strict novelty
definition**, not a proof that no other selection, larger domain, richer route
representation or different creative task could work. Nor does it show a model
has memorized these routes: no model was trained. The support comparison is an
exact benchmark-property calculation, not a behavioral measurement.

## What ran and what did not

After independent contract and implementation review, one real feasibility
invocation ran:

`.venv/bin/python -m schrodinger.route_feasibility --output execution/next_level/attempts/feasibility-001`

The full command result reported exit code0. No session was yielded, no relaunch
occurred, and the immutable attempt reports COMPLETE with no exception. Its
scientific outcome is a failed novelty gate; successful execution does not mean
the benchmark passed. Elapsed compute was10.7859s, charged12.7859s including the
declared2s startup allowance. Pre-run test/review charge was35.1064s, giving
47.8922s before final audit/report charges. Including Sol's5s audit and a2s
supervisor closeout allowance, final charged total is54.8922s:9.15% of the600s
Stage0 ceiling and0.76% of the7,200s overall ceiling.

Fixture tests, including one earlier injected-data subprocess that used the
shared ledger before isolation was corrected, are separately identified and
charged. That fixture did not enumerate the real map inventory or produce a
second scientific dataset. Earlier incomplete implementations and a novelty-
record cardinality regression were caught before this real run; the accepted
version preserves all512 IL problem records. No prior study outputs were changed.

Not performed: baseline learnability pilot, model construction, optimizer
training, five-seed comparison, temperature sampling, quality–diversity curves,
calibration/distribution-fit measurements, or dt0 interventions. Those stages
were conditional on feasibility PASS and were therefore not authorized to proceed.

## Reproducible evidence

- [Approved plan](../../next_level_learning_plan.md) and
  [frozen Stage0 contract](specs/00-feasibility-contract.md).
- [Implementation acceptance](reviews/06-cardinality-acceptance.md) and
  [single-run handoff](handoffs/09-feasibility-001.md).
- [Gate summary](attempts/feasibility-001/summary.json),
  [map inventory](attempts/feasibility-001/inventory.json),
  [split/bin records](attempts/feasibility-001/splits.json), and
  [per-problem route/novelty records](attempts/feasibility-001/novelty.json).
- [Complete training state/q records](attempts/feasibility-001/training_states.json)
  and [canonical suffix support](attempts/feasibility-001/support.bin).
- [Manifest](attempts/feasibility-001/manifest.json) binds source, tests, plan,
  specifications/reviews and output hashes; [attempt record](attempts/feasibility-001/attempt.json)
  binds that manifest, command, timing and outcomes; [ledger](ledger.jsonl)
  records separate charges.

## Decision

Stop this authorized plan at its feasibility gate. The user's productive-
diversity theory remains untested, not refuted. A useful next proposal would
first establish substantial held-out solution-structure support with an exact
oracle, while retaining correctness and matched-quality controls; only then
would learning experiments be informative. Changing the task or novelty
definition is a new scientific plan, not an automatic continuation of this one.
