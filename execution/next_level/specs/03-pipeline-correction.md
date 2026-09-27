# Stage0 correction C1 — scientific pipeline and serialization only

Sol found that the purported B handoff had no pipeline/schema tests and retained
hardcoded quotas, unserializable records, missing artifacts and exception-based
scientific failures. Root cause: implementation claims were not checked against
an executable end-to-end fixture. Do not submit the same core tests as pipeline
evidence. This is the first bounded correction following Sol implementation
review; science/selection stays frozen and no full inventory is authorized.

First finish ONLY the pure feasibility pipeline + artifact writer:

- Compute four actual joint training fractions and Hamilton quotas once for
  each whole split (validation128,ID256,IL512). A single flow spans all selected
  maps in that split. Preserve balanced map families and exactly16 pairs/map;
  RNG remains separate continuously consumed per-family stream with per-cell
  permutations. No .25 constants or independent II/LL quota allocations.
- Convert every emitted structure to a documented JSON-native schema. Store
  flow/capacities as lists of records with map_id, distance_bin, logM_bin and
  integer value, not tuple dictionary keys; walls as integer lists, routes/
  signatures as action integer lists or hex bytes. A JSON round trip must work.
- Persist selection/quotas/capacities/flow BEFORE later gates; a supply/bin
  failure returns scientific execution_status COMPLETE with exact evidence and
  later metrics NOT_EVALUATED. Do not throw JSON/ValueError for ordinary gate
  failure. Runtime/numerical exceptions remain failures, distinct from science.
- Add deduplicated (map,current,goal) training-state records with exact four-q
  vectors; full training suffix support and its length-prefixed hash; route,
  signature,M,M_novel records for validation,ID andIL, not IL alone.
- Emit independent files inventory.json,selection.json,splits.json,
  training_states.json,support.bin,novelty.json,summary.json,manifest.json.
  Manifest includes current source/tests/plan/contracts/reviews hashes, actual
  runtime versions and output hashes (exclude self/attempt to avoid circularity).
  Early failure writes all available evidence; unavailable files/fields listed
  NOT_EVALUATED rather than fictitious empty computed results.

Mandatory tests: literal nonuniform training histogram quotas; cross-family
flow where separate family quotas would fail; no duplicate/cross-split maps;
fixture whole pipeline+writer with JSON reload and exact artifact membership;
scientific supply/bin/novelty failure schemas; training DAG/q and suffix support;
all three evaluation split novelty records. Tiny injected inventories/config
are allowed in tests; CLI exposes no override of frozen real counts or gates.
No full6x6 enumeration as a test. <=20s extra fixture tests.

Do not fix/claim Attempt safety in this substep; that is a subsequent narrow
correction. End with an honest C1-only handoff and mapped fixture assertions,
not a Stage0-ready claim. Astra then activates C2 safety, followed by Sol review.
