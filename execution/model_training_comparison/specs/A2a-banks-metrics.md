# A2a — fixed scoring banks and route metrics

After A1 acceptance, Terra creates additive schrodinger/route_policy_metrics.py
and tests/test_route_policy_metrics.py, using A1's accepted public interfaces.
No production training or new dataset generation. Existing plan fully controls
metrics; this specification only freezes implementable details before scores.
Target <=20s focused tests within shared A400/global7200; all actual attempts count.

1. Build scoring/probe banks exactly per plan section4: serialized candidate bytes,
   SHA256 rank/collision tie, first32/map, train savedDAG candidates versus held-out
   union of selected goals with all reachable nonterminal free cells. BFS/q may be
   computed on saved maps with explicitn12; never rebuild training support. q-array
   hash uses contiguous little-endian float64[N,4] in selected bank order, with
   the candidate-ID hash alongside it. Store bank/candidate/probe IDs and hashes.
   Test exact known serialization bytes, deterministic selection, <32 map weights,
   repeated-goal dedup and no independent rotation of map/current/goal.

2. Stable local-legal CE/KL/Brier/H(p)/H(q)/nonoptimal-action mass. Aggregate actual
   equal states/map, equal maps/stratum and0.8/0.2 mixture. q is never an action
   mask/input feature. Test irreducible entropy, q==p proper scores, illegal action
   zero, no0*(-inf), exact weighting and zero-reference improvement NA.

3. Exact verifier/rollout over fixed selected problems: goal first/16move stop,
   shortest completion only. Uniform sequences exactly plan95002 seed/split/map/
   start/goal/replicate/sample then16step values. Greedy fixedN,E,S,W ties. Sample
   by inverse CDF, last legal action catches rounding tail; never choose forbidden
   actions or supply optimal mask. Uniform-legal and own-initial controls share
   exact streams. Save per-attempt action sequences, valid/novel flags; U compares
   exact action tuples, novelty uses accepted canonical_signature and full saved
   training-suffix set. Cached logits must be keyed by model/checkpoint/intervention
   identity and map/goal/current, never reuse across changed weights. Same raw
   logits may serve temperatures. No verifier-guided repair/resampling.

4. Metrics Q=Vvalid/K, Unovel/K,Uvalid/K,Vnovel/K,pass@K,coverage,validduplicate
   concentration and (Vvalid-Uvalid)/K. Map/problem/stratum weighting as plan;
   NA denominator rules literal. Validate with a hand-verifiable small synthetic
   action-policy fixture containing valid duplicate, distinct novel, known and
   invalid routes, plus real accepted route problem. No learned policy required.

5. Operating-point helper: fixedbounds[.25,3], up to8bisections, sameuniforms,
   targetQ=.9/tolerance.005. Evaluate endpoints first; if bracket missing or any
   observed quality increase as temperature rises, use nearest fixed-grid point
   {.5,.75,1,1.25,1.5,2}, lowerT ties. Otherwise at each midpoint stop if tolerance
   met; after8 use nearest evaluated candidate (lowerT ties), ineligible if not
   matched. Record all evaluations/fallback and never relax tolerance. Entropy
   targetSA T1, samebounds/iterations/grid, monotonicity direction reversed, tolerance
   .01nats; no test fitting. Test all branches using pure prescribed functions.

Complete handoff and Sol review before downstream harness acceptance. Bounded
metrics implementation only; no plots/main bootstrap or unused framework yet.
