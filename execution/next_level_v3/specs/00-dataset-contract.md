# V3 dataset contract — FROZEN / ACCEPTED after Sol00 PASS

All details below are frozen before any production inventory or proposal scores.
Task/criteria/budget are productive_diversity_v3_plan.md. No model work here.

## Geometry, pools and shortlists

Use n=12 explicitly in every geometry/BFS/route/verifier call. Reuse accepted
dimension-parametric route_feasibility helpers; never v2 helpers with hidden N=8.
Direct individual placements: all12*10*2=240 I placements, all11*11*4=484 L
placements. Sort each list by ascending cell tuples. Validate direct enumeration
against exhaustive old helper for n=3,4,5 and exact n=12 counts; do not exhaust
C(144,3) repeatedly at runtime. Cache immutable placement lists per n.

Family codes I^8=0,L^8=1,I^4L^4=2 (literal strings8 I,8 L,4 I then4 L).
PCG64(SeedSequence([93000,family_code])) per pool. Each trial draws one placement
index per letter independently with replacement in family-string order. Reject
overlap first, orthogonal inter-component touching second, duplicate D4 identity
third. Stop at256 maps or200000 trials/family; no refill. Save all trial/rejection
counts and canonical maps. Globally sort canonical bytes and assign map IDs.
Canonical walls have24 cells, exactly eight valid separated components and the
declared family. Invalid geometry/family/collision is technical, not supply failure.

BFS each free goal to inventory reachable ordered pairs, sorted(start,goal),
distance12..20 inclusive and16<=M<=256. For each map/length, initialize
PCG64(SeedSequence([93001,map_id,length])), permute the complete sorted list,
retain first64 or all if smaller. Save raw counts, permutation/retained pair IDs,
distance/M and candidate ordering. All later choices use these fixed shortlists.

## Ranking joint capacity proposals

Windows (12,13,14),(14,15,16),(16,17,18),(18,19,20). Quota tuples in canonical
order (6,5,5),(5,6,5),(5,5,6). A raw-eligible map has at least its per-length
quota in its shortlist. Count eligible maps for every family. Necessary totals
are92/92/40 respectively. Score is min(count_I/92,count_L/92,count_mixed/40),
compared as exact rational fractions. Infeasible raw counts exclude a proposal.
Enumeration-cost tie is the exact rational mean M over all retained shortlist
pairs on those raw-eligible maps across the three lengths/families (smaller wins).
Then lower window start, then earlier quota tuple in the canonical order wins.
Select the best quota for each window, sort the surviving distinct windows by
the same score-descending/cost-ascending/lexical order, retain at most three.
Write full12-proposal ranking, counts, scores, tie costs and chosen order before
computing any training support. If none survive, RAW_JOINT_CAPACITY_FAILED.

## Resolving training-support dependence and held-out selection

Each proposal uses window_start as its stable ID, not its rank. Split seeds:
train94001,validation94002,test94003. Map stream per family/split:
PCG64(SeedSequence([split_seed,window_start,family_code,0])). Permute globally
ID-sorted candidate maps once, scan in that order. No later new permutation.
For training scan raw-quota-eligible maps, take first32/family; for each length
take the first q pairs from that map's frozen shortlist. Check complete training
orientation support. Build deduplicated nonterminal DAG states/q and complete
canonical nonempty suffix support; hash it. No support truncation.

Held-out order: validation routine(I^8 then L^8), validation mixed challenge,
test routine(I^8 then L^8), test mixed challenge. Required maps12+12,8,48+48,32.
Exclude earlier split identities; each family's stream is initialized once per
split/proposal. Scan raw-quota-eligible maps in the frozen permutation. For each
map visit lengths ascending and candidate pairs in frozen shortlist order.
Enumerate all shortest routes exactly, validate M, count signatures absent from
this proposal's complete support. Routine Mnovel=0, challenge Mnovel>=4 and
.25<=Mnovel/M<=.75. Accept first q qualifying pairs for each length; stop that
length once quota filled. If a length exhausts its shortlist, reject map and
continue. Commit map only after every length passes. Save scanned IDs, per-length
candidate examination/acceptance counts, reasons, selected exact pairs, and every
selected route's M/Mnovel. Remaining unscanned maps are NOT_EVALUATED, not failed.

Caches may retain individual action-string canonical signatures, BFS facts,
per-pair signatures and eligibility keyed by exact support hash. Bound memory;
never confuse proposal supports. Recommended maxima65536 action signatures,
512 BFS/pair entries each; cache changes must preserve exact outcomes and scan
order. Persist profile counters for oracle calls/routes/cache hits and elapsed
time; no speculative performance-based architecture choices.

First full PASS fixes all IDs/quotas/support before models. Only raw/held-out
finite-supply or training-orientation shortage permits next frozen proposal.
Technical/oracle/count/hash/deadline/budget failure stops, no next proposal.
Three scientific failures stop, no extra windows/maps/shortlists. No claim of
global impossibility from this bounded sufficient construction.

## Implementation/review sequence and acceptance evidence

New files only: schrodinger/productive_diversity_v3_data.py,
schrodinger/productive_diversity_v3_runner.py, corresponding test files and
execution/next_level_v3 records. Original/v2 behavior and artifacts untouched.
Terra owns all code/tests; Astra specs/decisions; Sol independent review.

Block1 pure12x12 geometry/pools/shortlists/ranking with tiny exact fixtures,
then Sol review. Block2 complete proposal support/lazy quota selection with
oracle-backed small success and predicate failures, then Sol review. Block3
narrow runner/evidence wrapper reusing reviewed safety behavior, then Sol review.
No production generation before all three current blocks PASS. Test-only
dimension/count fixtures allowed via internal interfaces, never CLI relaxation.
Every handoff names exact source/test hashes, commands, actual assertions,
exit codes, resource charges and limits; no claiming mocked whole-pipeline PASS.

Required tests: direct shapes versus exhaustive small n; n12 cells>63; separated
eight-component pools/seeds/rejections; canonical identities; all12 proposal
rank/ties and distinct-window truncation; identical16-problem length quotas per
map; full support/q; correct support-keyed cache behavior; lazy scan deterministic
prefix/early stop; selected training/held-out identity separation; actual valid
routine AND partial-novel challenge composed fixture; negative M/novelty/quota/
family/count/leakage assertions; technical-not-next-proposal; immutable strict
JSON/hash config manifest; same-process lock/deadline/rejection/log-fault paths,
and full explicit CLI exit/completion. Reuse tests where sound, don't merely
rename data that violates novelty predicates.

Dataset-stage ceiling1600s including all tests/audits, within carried global7200s.
Development tests cumulatively<=180s and each command timeout<=60s; exact elapsed
plus disclosed startup allowance charged once. Audit/generation budgets use the
remaining stage/global amounts and reserve30s for finalization. Carry-forward
443.384519002s is a budget debit, not newly measured time; isolate new ledger.
No overlapping compute, complete full command result/session polling discipline.
