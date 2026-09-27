# Block 2: bounded corrections and statewise KL arithmetic

2026-09-27. Astra specification. Implement only after Sol passes
amendment-01-statewise-kl.md. The plan/spec 1 remain historical and binding except
where this explicit amendment adds analysis. The 200k hold is unchanged.

## Required implementation corrections

Resolve all seven findings in reviews/01-static.md within the existing early
study files/tests. Do not edit accepted model/evaluator/watchdog sources.

1. Repair the tampered-checkpoint fixture so valid identity/full-grid metadata
   reaches the intended hash rejection.
2. Tiny composed fixtures must include routine and challenge examples in both
   their proper and rollout panels. Preserve production panels exactly.
3. Install the accepted SIGTERM-to-exception cleanup behavior for every external
   child, including smoke/suite and audit. Add one tiny descendant cleanup check.
4. Preassign one charge UUID per attempt. After an uncertain append, reconcile
   that identity rather than appending a new UUID. Ambiguous uniqueness,
   cleanup or terminal durability retains the reservation. Reuse the accepted
   driver's certainty rules rather than adding broad new machinery.
5. Production and audit decisions must bind a distinct Astra exact-version
   acceptance artifact naming Sol's implementation review and current hashes.
   Decision constructors may not manufacture acceptance themselves.
6. Add a tiny SA probe fixture with finite outputs, expected records and exact
   no-mutation checks inside inference_mode. Keep the suite under 60 seconds.
7. Run the D-stage audit under an actual external deadline, including startup,
   cleanup and finalization. Its unchanged allowance is 240 seconds.

## Added analysis, without added model calls

Implement the complete amendment's per-state weighting, four argmax transition
groups, nonoptimal_mass series and exact two-component KL decomposition using
existing saved proper rows/arrays. Retain stable IDs, legal masks, oracle q,
saved p/KL, weights and components. Derive legal masks with accepted data logic
inside owned inference and store them once; the later arithmetic audit can use
that bound bank metadata without importing neural modules.

Add pure functions and analytic tests for deterministic legal argmax ties;
multiple positive-q oracle actions; all four transition groups; an empty group;
unequal map/state counts demonstrating correct original weights; changed/missing
state IDs or q; component reconstruction; zero support mass and invalid arrays.
Do not infer legality from p>0 or q>0. Test at least one case where aggregate
nonoptimal mass decreases while KL increases, so interpretation cannot silently
equate those quantities. No new full-panel inference fixture is needed.

Use absolute tolerances: normalized p/q and weight sums 1e−10; mixture/group and
component reconstruction 1e−10; checkpoint q agreement 1e−12. Allow m up to
1+1e−12 and components down to −1e−10 solely for floating-point diagnostics;
report raw values and residuals, without clipping. Nonfinite/zero m makes the
decomposition explicitly unavailable, never an omitted state. Existing invalid
score/identity inputs remain integrity failures. Numerical tolerances may not
be loosened after inspecting results without a documented amendment.

Compute all 30 adjacent comparisons and 800→2000 for every owner. Report
per-owner results first; paired seed differences and equal-seed mean/range may
summarize the fixed 800→2000 comparison, with no significance or causal claim.
Keep the originally declared window means/slopes and raw curves as the primary
diagnostic summaries. No post-hoc checkpoint selection or worst-state filtering.

## Gates and budget

Include this spec and amendment in the exact source-authority hash set along
with the new methodological review. Preserve previously reviewed documents.
Luna freezes code/tests and a handoff with exact hashes; Sol reviews static
safety; Astra accepts before the originally planned 10-second smoke and
60-second targeted suite. All remain within A 120 seconds. Exact implementation
PASS and Astra acceptance precede production. B 1,440 / D 240 / total 1,800
seconds remain unchanged, zero spent so far. No automatic retry or additional
test run is granted by this document. This is the first bounded correction
cycle for early-learning implementation; further failures require a concrete
reviewed repair, not an open-ended testing loop.
