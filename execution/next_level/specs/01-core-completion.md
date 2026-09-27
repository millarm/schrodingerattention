# Stage0 completion substep A — exact core/selection

The initial Terra handoff is NOT accepted: its CLI emits INVENTORIED_ONLY and
omits the selected dataset, support, novelty gate and required safety. Complete
Stage0 in narrow substeps, followed by one final Sol implementation review.
This substep may end with an explicitly partial progress handoff; it is not
permission for full inventory execution or a claim of Stage0 completion.

Fix only pure core/selection helpers and their fixture tests first:

1. Replace the greedy no-reverse-edge allocator with genuine Edmonds–Karp on
   source/map/cell/sink residual graph. Add a fixture where a prior allocation
   must be reassigned through reverse edges to reach full flow.
2. Bins accept separate distance and M arrays: distance median and log2(M)
   median, not median/log of the same input. Add tied-median fixture.
3. Problem selection consumes one RNG stream per split/family continuously
   across maps then cells in frozen order; do not reinitialize it per map.
   Training uses full candidate-list permutations; evaluation uses separate
   cell-list permutations after exact flow. Add literal seeded replay fixture
   including two maps and two cells; map selection enforces >=16 eligibility.
4. q target has exactly four entries (illegal actions zero); verify all shortest
   routes have product probability1/M on a nontrivial branching fixture.
   Add independent brute-force small-board oracle comparison and all-prefix/
   suffix support coverage, plus verifier collision/too-long/early-goal cases.
5. Geometry/canonicalization remains frozen. Preserve prior source files.

No CLI run/full6x6 enumeration. <=20s additional fixture tests. Report explicit
partial completion of substep A with hashes and evidence; Astra will then issue
substep B integration/safety. Do not expand into models or training.
