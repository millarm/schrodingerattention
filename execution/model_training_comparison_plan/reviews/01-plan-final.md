# Review 01 — final model-training comparison plan

**Verdict: PASS (plan only; execution remains unauthorized).**

Reviewed exact `model_training_comparison_plan.md` SHA256:
`5ece45cdb11f860ae64933225f284297cff59aa544c6730b247138c660cc8ff0`.
No implementation, test, profiling, diagnostic, or training command was run.

Both findings from review00 are closed:

1. Quality is now unambiguously `Q = V_valid/K`, counting every exact valid
   shortest completion including repeats.  Greedy is K1; T1, controls,
   checkpoint gates, temperature matching, noninferiority/equivalence and final
   outcomes are K32.  Problem/map/stratum weighting, per-stratum handling,
   replicate0/common-uniform use, initial and uniform-legal controls, pilot
   replicate handling, and the distinction from `U_valid/K` are frozen.  The
   challenge headroom statistic is explicitly mean `U_valid/M`.

2. Sampled score-bank construction is reproducible at byte level.  Candidate
   state distributions, `(goal,current)` deduplication, reachability, canonical
   orientation, exact tag/map/integer encoding, digest ordering and collision
   tie-break are specified.  Full candidate and selected lists, exact q arrays,
   hashes, counts and serialization version are persisted.  Maps with fewer than
   32 states retain equal map weight through actual `1/N_map`; empty banks stop as
   technical failures.  Banks are frozen before scores and preserve test release.

The added scheduled T1/K32 route metrics provide dynamics evidence without
selecting checkpoints or temperatures.  Numerical acceptance is correctly
operation-specific: representative unitary/row error `<=2e-4`, Hermiticity
`<=1e-6`, dt0 `atol=2e-6, rtol=2e-5`, and scheduled runtime abort at unitary/row
error `>2e-3`.  Expensive invariant/mechanism probes remain detached from the
ordinary training timing loop while batch finiteness checks remain active.

The paired seed1701-to-1000 amendment, baseline-selected exposure T, paired data
and uniforms, fresh main seeds, validation-only choices, censoring/equal-time
rules, temperature/entropy/dt0 controls, five-pilot variance gate, ten-pair main
inference, and separate usability/dynamics/novelty/mechanism conclusions remain
fair and appropriately qualified.  The budget still starts at923.003597253 of
7200 seconds and the prospective allocations sum exactly to the remaining
6276.996402747 seconds, with explicit profiling/forecast stops and audit reserves.

This PASS establishes that the plan is sufficiently frozen and reviewable.  It
does not establish runtime feasibility, usable learning, novelty, equivalence,
or architecture advantage, and it does not authorize execution.
