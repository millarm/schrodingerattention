# A1 — immutable route data adapter and matched model only

Execution approved; read approval.md and frozen model_training_comparison_plan.md.
Terra creates only schrodinger/route_policy.py, schrodinger/route_policy_data.py,
tests/test_route_policy.py and tests/test_route_policy_data.py (names may be these
exact names). Preserve old code/tests/data/plans. No training runner yet. Sol
reviews this complete block before A2 and no measured training before accepted
harness/profile. Target <=20 elapsed seconds focused tests, count all attempts
against stage A400/global7200. No full data regeneration or oracle route enumeration.

## Data adapter

Read selected proposal14 training and four held-out stage artifacts plus frozen
inventory/manifest from pool512feasibility-001. Verify manifest expected hash and
every loaded artifact hash before decoding; no old failed-proposal data. Decode
explicit bytes_hex and key/value mapping JSON correctly. Training state keys are
stored (canonical bytes, CURRENT, GOAL), q values are action-key records. Reindex
to stable model records (map_id, goal, current), not swapped state/goal. Preserve
canonical orientation, family, problem IDs, support bytes/hash and selected rows.
Expose training/validation separately from an explicit final-test loading method;
no test predictions or model scoring in this block. All maps/rows are immutable.

Encode each input as float32 [12,36]: row wall flags for columns0..11, current
flags, goal flags. Exactly one current/goal marker on legal free cells, distinct
for supervised nonterminal states. N/E/S/W action IDs0/1/2/3. Legal masks [4] use
only board/walls. q arrays length4 remain normalized and zero on illegal actions;
reject nonfinite/negative/inconsistent metadata. All saved train DAG states are
used, grouped by map and sorted goal/current. Sampling draws64 map indices in one
PCG64 call, then one state index per drawn map in that order, using frozen
SeedSequence([95001,seed]); expose RNG state for resume and batch identity hash.

No scoring-bank construction in A1; A2 adds exactly the plan's byte-frozen banks.
No regeneration of training q/support. Loading manifest/inventory and adapting
the retained data counts as setup when actually executed, not uncharged training.

## Model

Implement planned CLS+12row model, d64, 2pre-norm layers, 2heads, FF128/GELU,
final LayerNorm, four logits. Shared row projection Linear(36,64,bias=True),
learned [12,64] row-position tensor and learned [1,1,64] CLS tensor (both normal
mean0,std.02). No extra CLS position; nn.Linear/LayerNorm default initialization,
LayerNorm eps1e-5, GELU exact/default. No dropout or scheduler. Same base tensors
hash/equality verified after copying by name per paired seed. Return raw logits;
shared masked_log_probs/policy helper applies local-legal mask identically for
training/scoring/rollout. Never apply an optimal-action mask.

Reuse attention_from_scores from old attention.py unchanged. SA raw_dt and
raw_gamma initial/bounds exactly plan. Softmax uses two learned per-head vectors:
exp(alpha) multiplies scores and exp(beta) multiplies V, initialized0 in rawspace.
Both have exactly8 active extra scalars across two layers/two heads. Diagnostics
default OFF on ordinary forward, explicit scheduled option only. Same-weight
dt_override=0 does not alter trained tensors and matches an unscaled same-tensor
softmax path; it is not the separately trained scaled baseline.

## Literal acceptance evidence

1. Real saved-format miniature adapter fixture catches current/goal swap, bytes/
   q-key decoding, canonical map identity, invalid metadata/hash mismatch and
   training-vs-test boundary. Actual frozen data adapter smoke may load only
   approved training/validation once within budget, with exact state/map counts.
2. Features/legality hand-checked corner/wall/current/goal examples; q illegal mass
   rejection; deterministic map-balanced sampler and restored RNG batch identity.
3. Exact base initialization equality; equal total trainable parameter counts and
   eight active scalar parameters/model; correct13tokens/4action shape. All model
   parameters receive finite gradients on a nontrivial legal-q synthetic loss.
4. Length13 numerical checks at score scales.1/1/3: Hermiticity<=1e-6,
   unitary/row<=2e-4; dt0 probabilities/output atol2e-6/rtol2e-5. Explicitly check
   diagnostics OFF avoids diagnostic routine, not merely discarding its result.
   Existing exact primitive tests can be reused selectively, no redundant suite.
5. State-dict reload logits exact/tolerance1e-6; loss uses q>0 legal log-softmax,
   CE/Brier/KL finite. No model update/optimizer smoke until A2 accepted testscope.

One complete handoff A1 with hashes, literal test mapping, full commands/tool
results and all charges. Retain yielded session and poll to explicitexit. True UTC
from datetime.now(timezone.utc) or clock, never manually fabricated timestamps.
Append UUID charge once to NEW ledger EOF, with stage A. No source edits during
Sol review; no partial-scaffold acceptance.
