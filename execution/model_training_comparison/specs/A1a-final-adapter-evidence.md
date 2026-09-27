# A1a bounded respecification after two incomplete A1 revisions

Parent authorizes one fresh-context same-model Terra replacement; previous Terra
is completed/inactive. Roles/science/budget unchanged. This is not a gate waiver
or Astra implementation exception. Root cause: repeated handoffs reported closure
while the adapter test file remained unchanged and handoff hashes/counts stale.
Do not repeat broad instructions; finish the literal remaining assertions below.

Accepted model source must remain byte-identical:
schrodinger/route_policy.py SHA95cb7463693c7ac696d9034eaf16a155c0363f38e819cbe56c00408d49b170c4.
Current adapter SHA135919596ca2535a02169da956acdc1d39a0ba2f651027c0fa31b3307fe9b7ad.
Current model-test SHA7d7b01be98c2b394eb22c8cafca88f3394ac97593150459904f7314e0a28f42e
already adds nonzero dt=.11 at length13, separate from dt0 equivalence.
Adapter-test SHA078f0e7f7ab23825101546dc1d8b1abe643d85cb9610837f1f18cf79eceaaf47
is unchanged since prior review, so its promised evidence is absent.

Only edit route_policy_data.py and the two new route-policy tests, plus new A1a
handoff/ledger records. No model architecture edits, oldfile edits, A2 or training.

## Remaining source boundary

Preserve existing immutable dataclasses/support metadata. Ensure held-out stage
wrappers have exact expected family sequence (routine I8,L8; mixed I4L4), selected
row family matches wrapper, stage proposal14/outcomeOK, and wrong split/stage is
rejected. Training must have homogeneous families only. Enforce duplicate selected
problem/state rejection, current/goal free and within0..143, exact start/goal/length/M
membership in corresponding inventory shortlist. Mnovel required integer0..M for
heldout (routine0; challenge>=4 and1/4..3/4), absent/None for training. Support
must be sorted unique nonempty action bytes; recompute its exact2byte-length-prefix
hash and compare saved hash. No new oracle enumeration or data selection.

## Literal tests that must actually be added

1. Actual saved smoke: train32946states,1024problems,64maps (32I/32L); support63517
   entries/hashb3feead79ea397f3b1be56ac1b601428cedf620157e2740a93cc15946f00ccc3.
   validation512problems (384routine/128mixed), test2048 (1536routine/512mixed),
   map counts24+8 and96+32 respectively. All three split identitysets disjoint;
   train states sorted(map_id,goal,current); frozen dataclass mutation fails;
   heldoutMnovel retained and trainingMnovelNone. No model score on test.
2. Small temporary saved-format fixture through real loader/hash functions (not
   mocking those functions): exact bytes_hex/current-goal/q-key decode. Corrupt
   artifact bytes without updating manifest =>hashfailure. Mutate manifestbound
   fixture facts with matching testmanifest hashes to exercise loader validation:
   malformedstatekey, inventorymap/pair mismatch, blocked/outofrange endpoints,
   duplicate state/problem, wrongfamilywrapper, supporthash mismatch and invalid
   Mnovel. Fixture override of ATTEMPT/MANIFEST_SHA only is allowed. Never edit
   production artifacts. Valid reversed states are not intrinsically illegal;
   assert exact current/goal decoding and reject an inconsistent/illegal-q swap.
3. Model tests: legal probabilities sum1, illegal probabilities exactly0,
   illegalq rejects, proper CE/Brier/KL finite; alreadyacceptedallmaskfalse check
   remains. Print/assert actual max Hermiticity/unitarity/row errors at dt=.11,
   plus max dt0 output/probability error against same-tensor unscaledsoftmax.
4. Keep acceptedbothmodelgradient/sharedtensors/scalars/diagnosticsoff evidence.
   Beforehandingoff verify fileactuallycontains eachassertion, not merely testcount.

Target<=20s newfocusedtests withinA400; everyattempt fulltoolresult/exit and charge
once NEWledger, trueUTC. AllknownpriorA compute24.720889377s; global947.724486630s.
No ambiguoushistoricalrewrites. Write NEW handoffs/A1a-final.md with CURRENTfour
hashes, exacttestnames/lineassertions, rawnumericalmaxima, literalcounts, allnew
attempts/walls/UUIDs and linkpriorreconciledledger. Sol exactreview still required.
If this specific closure cannotcomplete, report exactremainingproblem, not a
self-imposed turndeadline or another false completehandoff.
