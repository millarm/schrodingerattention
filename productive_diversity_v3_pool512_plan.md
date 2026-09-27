# Frozen single512-map pool expansion — dataset only

User authorized “Expand the pool” on2026-09-16. This prospective amendment makes
one change to productive_diversity_v3_plan.md: target512 canonical maps per family
instead of256 (1536total). All other scientific gates remain fixed. Astra plans/
supervises, Terra implements, Sol independently reviews. The previous narrow
Astra implementation exception is completed and does not apply here. Original
plans, protocol, source and reviewed artifacts remain unchanged.

## Fixed construction

Retain12×12 grids, eight separated triomino components, literal familiesIIIIIIII,
LLLLLLLL,IIIILLLL; same PCG64 pool seed93000/family streams and200000trial cap.
Extend each stream to512 accepted canonical maps, or its existing trial cap; no
refill, new seed, adaptive extension or fill-until-pass. Maps returned by the
generator are canonical-sorted, so old256 maps must be a subset, not necessarily
the first256 returned rows. Audit old/new draw prefixes and inclusion after run.

Global sorted IDs are recomputed over the expanded pool. This can change seeded
shortlists, chosen training problems, complete training-suffix support and novelty.
The earlier33 qualifying mixed maps are not promised to remain qualifying. Do not
salvage the earlier best window or append only missing held-out rows.

Keep shortlist cap64/seed93001, split seeds94001/94002/94003, candidate lengths12–20,
four windows12–14/14–16/16–18/18–20 and three quotas(6,5,5)/(5,6,5)/(5,5,6).
Run the full frozen raw-capacity ranking, retain at most3 distinct windows, and
attempt them in the same deterministic order. Training32 homogeneous maps/family;
validation12routine/family+8mixed; test48routine/family+32mixed. Eachmap16pairs.
Exact all-training-suffix structural novelty, routineMnovel0 and challengeMnovel>=4
with1/4<=Mnovel/M<=3/4 remain unchanged. Orientation, cross-split canonical
disjointness, length matching and every original scientific stop remain fixed.

## Resource and execution boundary

Carry prior operational745.131573627s exactly once into the same7200s ceiling;
retain1600s dataset stage with prior debit301.747054625s. Remaining stage
1298.252945375s includes all new development, run and audit. Cumulative development
cap180s, conservatively treating104.848293667s as already used; target<=30new
development seconds. Retain120s independent audit and30s finalization plus2s
startup reserve. No live extension, paid resources, training or architecture work.

New records at execution/next_level_v3_pool512; one unique frozen production
attempt after plan and exact implementation PASS. Shared old safety/selection
code may be imported unchanged. No mutation of old module globals/old ledgers.
Single owned lock, fail-if-output-exists, full command/session/exit retention and
chronological unique charges apply. Only one compute job at a time.

Audit the retained outcome within120s, adapting accepted spec04: exact
source/config/output hashes,512limit manifest, old256map inclusion/draw-prefix,
saved-inventory ranking, all selected metadata/quotas/disjointness/support hashes,
up to60 oracle route/novelty pairs and32q states. Clearly report sampling limits.
No pool/proposal regeneration in audit. Stop at reviewed full dataset PASS or
frozen construction/resource failure; either is an outcome, not permission for
another expansion. No neural learning claim follows dataset readiness.
