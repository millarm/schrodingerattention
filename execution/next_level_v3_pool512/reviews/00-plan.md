# Review 00 — pool512 plan and minimal-extension contract

**Verdict: PASS (prospective contract; no generation authorized by this review).**

Reviewed exact versions:

- `productive_diversity_v3_pool512_plan.md` SHA256
  `271e53a82144f3bfe39dbca8dc53cf35147adf387964e4204830cb1edfa0b500`
- `execution/next_level_v3_pool512/specs/00-minimal-extension.md` SHA256
  `bd0bb698726302403ec66b5481782c92bef3022abf446fe566773623bc4fdc4b`
- bound prior ledger SHA256
  `c2812c96c8a3e457cdc68403c3e498bd296b199a7ceefc9149273b44e6133563`

The amendment changes only the predeclared pool target from 256 to 512 canonical
maps per family.  It correctly reruns global IDs, shortlists, ranking, training
selection, full training-suffix support, and held-out selection.  Thus it does
not assume that the old best proposal or its 33 qualifying mixed maps survive.
All task geometry, RNG streams and caps, ranking rules, split sizes, novelty and
quality predicates, proposal order, and scientific-stop semantics remain fixed.

The deterministic-prefix language is scientifically sound with one important
interpretation to enforce in implementation and audit: `pool_family` returns
canonical-sorted maps, so the required map relation is set inclusion of every
old 256-map family pool in its new pool, not positional row-prefix equality.
The separately persisted bounded draw-prefix rows must agree over their common
available length.  Neither check permits reseeding, refilling, or continuing from
the old endpoint under a different stream.

The additive implementation boundary is proportionate.  Importing the accepted
data and safety helpers while copying only the literal-configuration orchestration
avoids mutation of old globals and artifacts.  Review must require that injected
tiny-fixture artifacts are explicitly treated as test evidence: a configured
limit of 512 must not be described as 512 observed maps.  Production evidence
must show the actual per-family pool counts/trials in its pool artifacts and bind
the effective limit, source paths/hashes, prior manifest, and prior ledger.  This
is already entailed by the contract's truthful provenance and genuine-fixture
language; it is recorded here to prevent the test seam from becoming scientific
evidence.

Budget arithmetic is consistent.  One ledger row can carry the global-only
443.384519002 seconds while charging the inherited stage debit301.747054625
seconds, yielding stage prior301.747054625 and global prior745.131573627 exactly
once under the accepted parser.  After reserving120 audit +30 finalization +2
startup seconds, the predevelopment execution deadline is1146.252945375 seconds.
The 180-second cumulative development cap leaves75.151706333 seconds, while the
stated <=30-second target is appropriately stricter.  No live extension or
double carry is allowed.

No scientific or provenance ambiguity requires amendment before implementation.
Implementation acceptance still must exercise the literal512/default arguments,
map-subset/common-draw-prefix property, isolated new paths and ledger rejection
cases, truthful fixture provenance, unchanged old bytes, safety behavior, and
complete manifest hashes.  Production remains gated on a separate exact-version
implementation PASS.
