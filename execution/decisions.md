# Supervisory decisions

2026-09-15: Approved protocol and source plans read completely. macOS ARM64,
10 logical CPUs visible. System, Homebrew, and bundled Python lack PyTorch.
Use a local isolated runtime; exact complex matrix exponentiation requires CPU
unless an accelerator is demonstrated compatible. Original files preserved.

2026-09-15 17:07 UTC: Block0 ACCEPTED after Sol PASS on runtime and contractv2.
Contract SHA256 `2a4964` prefix (full hash in review) is frozen together with
PCG64/SeedSequence binding in Block2 spec. Formal v1 findings preserved;
scientific gate restored to mean threshold and positive direction in2/3 seeds.
Hardware Apple M4 10 cores24GB, CPU. Authorize Terra Block1 specification now.
Charge3.006 seconds for all Block0 runtime/reviewer numerical checks.

2026-09-15: Block1 ACCEPTED after Sol PASS on frozen attention implementation
`e1ce15be10caf4b2165191f9835256602f4f7b8bd11bffa94f676eac40b0fd6a`.
Independent23 tests pass; H error0, U6.557e-7, row5.960e-7, dt0 output2.384e-7.
Orientation counterexample difference0.01951 and gradcheck passed. Fixed-batch
MSE1.066010 ->0.336738. Charge10s Terra (conservative command-startup allowance)
plus1.5s Sol; cumulative14.506s. Authorize Block2 spec, including bounded smoke
and throughput-only profiling. No full comparison before review/acceptance.

2026-09-15: Parent requested status-only contract label correction. Title now
FROZEN v2 and opening sentence records acceptance. No scientific content changed.
Reviewed substantive version remains `2a49643fa9ec08b50a7b6c24edb55fe1c8e80eee62956c71a9b0a4f9f444d5b2`;
current status-labelled file SHA256 is
`5ea6cda81fa8f95f3e2a9c39e9ca47d34ca6134697bca3305967e6f31d8507de`.

2026-09-15: Block2 NOT ACCEPTED. Sol CHANGES REQUIRED identified eight groups
of incomplete contract implementation, including CLI, timing/ledger, dataset,
invariants, artifacts/tests, and positional encoding. Authorize revision1 under
02-harness-revision.md addressing full review. Prior smoke/profile are superseded
for acceptance and budget sizing (timing omitted generation). No measured run
was performed; frozen scientific contract unchanged. Charge Sol1.9s review.

2026-09-15: Block2 revision1 not accepted after Sol found six residual groups.
Root cause of repeated incomplete work: Terra delivered incremental scaffolding
and partial milestone turns without mapping every contract acceptance criterion
to executable regression evidence. Astra repeatedly resumed implementation and
withheld acceptance; initial tests passed while omitting critical lifecycle
paths. The remaining defects are implementation/evidence gaps, not a scientific
or hardware infeasibility finding. No requirement is waived and no measured
run is authorized. Under protocol's bounded-revision rule Astra issues a new
focused specification02-harness-revision2.md covering six concrete residual
groups with dedicated tests and a single complete handoff. Terra retains sole
implementation ownership, Sol independent review, Astra acceptance. If another
review remains unresolved, explicitly assess cause and bound next work rather
than continuing an unexamined loop.

2026-09-15: Revision2 review surfaced a narrowly remaining completed-stream
validation gap in pair_evaluate. Root cause: the previous identity regression
covered initialization/config/data/mode mismatches but not divergence in the
actual training stream or completed update count. Current smoke streams match,
but accidental divergence would not be rejected. Issue a newly bounded
02-pair-validation.md for that function and two explicit mismatch tests;
do not waive pairing or proceed to measured runs before Sol accepts. Historical
preparation accounting reconciled to180s conservatively charged (50.3793s in
existing charge records plus129.6207s overhead allowance), preserving history.

2026-09-15 18:18 UTC: Block2 ACCEPTED after final Sol PASS
review SHA256 `e44c7da53514e1919d6938464f6c5a30495855697065f42a3c45adcf2235dad2`.
All31 inventory entries verified; full48 tests plus focused7-test independent
evidence valid; paired102step smoke and diagnostics/identities accepted.
Frozen implementation experiment.py SHA256
`cf75e1b35fe6fb1fb462d78d415ea60115dcd267957303ef56427861ae55c288`.
Add Sol final1.3s to211.14572s audited prep =212.44572s charged before runs.

Resource-only N decision BEFORE measured comparison: corrected throughput
profile execution/results/block2-revision2/profile/profile.json gives20 timed
steps0.089429791s softmax and0.287108629s exact (generation included).
Projection3 pairs *2000 updates *(sum step means)*1.5 =169.4423s, below3600s.
Choose largest declared candidate N=2000, batch64 =>128000 examples per run.
No hyperparameter tuning, scientific threshold/seed/split change. Authorize
Block3 six runs in order seed11softmax/exact, seed22exact/softmax,
seed33softmax/exact, then common-time evaluation. No implementation changes.

2026-09-15: Sol Block3 audit found eight measured training attempts rather than
the authorized six in Terra's handoff. Two duplicate jobs reused output paths;
Terra reports artifact-existence polling without proof of prior process exit.
Potential overlap and overwritten attempt provenance are unresolved. Parent
explicitly directs no rerunning and no invented provenance or favorable-result
selection. Halt further training; preserve all remaining artifacts/ledger and
honest attempt record03-run-provenance.md. Sol will assess internally valid
endpoints and timing limitations. Unverifiable attempt timing/comparability
must be reported as invalid/uncertain and makes overall result INCONCLUSIVE
under the frozen missing/invalid-evidence rule, independently of XOR adequacy.

2026-09-15: Block3 ACCEPTED as reviewed INCONCLUSIVE execution record after
Sol PASS audit93a3dfdee8b8e5f4c79546f6a137daafdcbed105c9deeeb15e1cd8ec05979360.
This acceptance explicitly does NOT validate controlled timing/equal-time:
those endpoints are INVALID. Retained equal-update artifacts are internally
coherent descriptive evidence.8train attempts and5pair attempts(4success/1fail)
are documented, earlier duplicate versions overwritten/unrecoverable. Mean
validation XOR baseline0.71875/SA0.73698 fails frozen0.80 adequacy; primary
gain0.02018 and secondary0.01628 below0.03. Authorize Block4 summary only,
carrying audit validity flags; no further training. ChargeSol audit2.0s;
cumulative382.95063s before summary.

2026-09-15: Block4 ACCEPTED after Sol final PASS
`1301e057145c5091c22cfefa2bb83ac6916733a2bd77127a0277fe7c714f3a24`.
All20 summary input hashes, output hashes, descriptive means/SD/paired metrics,
target censoring, intervention/COPY checks, normal numerical maxima and figure
verified. Astra final_report interpretation independently checked by Sol.
Final outcome INCONCLUSIVE; no scaling/further training authorized. Retained
equal-update metrics descriptive; controlled timing/equal-time INVALID.
Final charged budget393.950634582s includes0.6s initial Block4 review and0.4s
final re-review, with prior conservative allowances explicit. Initial work
complete: accepted implementation, numerical checks, audited available results,
reviews, curves and final research decision linked in status.md.
