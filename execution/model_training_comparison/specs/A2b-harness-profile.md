# A2b — training, timing, immutable attempts and first cost gate

After A1/A2a accepted, Terra creates additive schrodinger/route_policy_experiment.py
and focused tests. Reuse reviewed pure helpers; do not mutate old runner globals
or reuse its hardcoded443carry/1600stage deadline. Implementation test target<=30s
inside A400. Small synthetic optimizer tests are allowed; no measured pilot until
Sol accepts current exact harness and profile results. No main-inference framework
before pilots prove worth continuing; later bounded blocks implement main summaries.

## Minimal commands and artifact boundaries

Provide prepare, smoke, profile, train and evaluate for fixed frozen route config.
prepare verifies selected manifest/hash, adapts training/validation, saves frozen
banks and identifies testbank without testmodelpredictions. Every command uses a
new immutable output directory, one shared new-run lock and complete attemptrecord.
profile only throwawayseed1699; train accepts prescribedpilot/mainseeds and target
updates, optional explicit validated resumecheckpoint. Supervisory decisionrecord
controls whetherpilot/mainauthorized, never inferauthorizationfromfilesystempresence.
Print compact strictJSON, return nonzero onfail, keep actualsession/exit externally.

Source/provenance includes newmodules/tests/specs/reviews, approvedplanhash,
additiveapproval and acceptedinputmanifest/artifacthashes, Python/torch/numpy/OS/
CPU/threadcounts, command/executable, actualmodelparametercounts/sharedinitdigest,
data/bank/support/streamhashes. Never overwrite oldsource or output. Complete
checkpoints bind model/optimizer/globalupdate/samplerRNG/torchRNG/timing and parent
checkpointchain. A resumed model must reproduce uninterrupted nextbatches/weights
and initial identity. No fallback to a checkpoint from another seed/mode/source.

## Budgets and failure behavior

Newledger exactlyone carried923.003597253globaldebit, thenactualcharges+explicit
allowances. Rejectmissing/duplicatecarry, duplicateUUIDs, nonfinite/negativecharges.
Read stage A/B/C/D actuals separately; allcarryglobal-only. Stageceilings400/2000/
2200/1300, total7200, residualreserve376.996402747. No old1600budget assumptions.
Deadline before eachcommand=min(stageleft,globalleft-reservedfinalaudit120) minus
30failure-finalization and2startupallowance; record exactderiveddeadline/reserves.
After each major operation checkdeadline and use an interrupting timer too. Timer
must not prevent best-effort failure log/ledger/ownedlockcleanup (disable its
expired timer for bounded finalization, never resume training afterdeadline).
OneUUID appended once in true order, actualUTC from processclock. Full measured
command time plus boundedstartup allowance; no doublecountphase timings.
On failure preserve lastcompletecheckpoint plus exception/reachedstage; return
nonzero; no successsummary withoutmandatoryattemptrecord. Tests use temp ledgers.

## Training and checkpoint metrics

CPUfloat32/complex64, torchthreads2/inter1, fixedAdamW/batch64/clip1 fromplan.
Train step order: materializebatch→zero_grad→forward/legalqCE→backward→finitecheck
→preclipgrad summaries when due→clip→optimizer.step→finiteparametercheck.
Time actual phases, excluding scheduledgradsummary extraction/logging from core
trainingseconds without subtracting estimatedcosts. Include clip/finitechecks and
data materialization. Record everyupdate CE plus detached scalar metadata outside
coretimer. Per100updates savedcheckpoint and preclipglobal/groupnorms, update/weight
ratios, clippingfrequency, dt/gamma oralpha/beta. No expensiveunitarity/eigenprobes
inordinaryforward. Store initialcheckpoint and allscheduled500/1000/etc evaluations.

At scheduledvalidationchecks evaluate fullselectedvalidationproblems: greedy and
T1K32 quality/novel-valid/diversity/invalid/duplicate metrics; proper32/mapbanks and
fixedmechanismprobes perplan. Cache rawlogits by checkpoint/intervention/map/goal/
current. Batch allmissingstates acrossactive rollouts rather than one neuralforward
peraction; no q/optimalmask input. Cache correctness tests compare cached/uncached
smallfixture exactly. Timing reports cachebuild/rollout/uniqueness/proper/probe/I/O
separately and end-to-end; no claimed FLOP/energy equality. Save perproblem metrics
and rawattempts for independent audits, avoid retaining giant autogradgraphs.

Independent baseline/control inference is not training. All initialweights and
uniformlegal controls scored with sameK/streams. Testdata predictions forbidden
until final mainrelease. Future equal-time evaluation uses existing100step checkpoints
<=cutoff with reportedslack, no trainingrelaunch or interpolatedmodeloutputs.

## Smoke/profile and forecast before paired1701

Unit/smoke acceptance: genuineadapterbatch, bothmodels5optimizerupdates, finite
parameters/allgrads, completecheckpointreload/resumeequivalence, a tiny complete
routeevaluation with knowncontrols and requiredmetrics, dt0numerical/probefidelity,
scientificfailure vs technicalfailure distinction, immutableoutput/lock/logerrors,
carry/stage/global arithmetic and timercleanup. Profile/smoke code reviewed before
standalonepostacceptance invocation. Profilingweights neverjoinpilot.

Actual profile1699:5warmup+20measuredtrainupdates/model (counterbalanceddeclared
order: softmaxthenSA for1699), no diagnosticforward in measuredsteps. Profile the
first2canonicalmaps pervalidationfamily (I/L/mixed), alltheir16problems, greedy/
T1K32, proportionalproperbanks, fixedprobe subset andcheckpointwrite. Record full
actualcost, perstratumproblem/state counts and checkpointbytes. Thisfixedsubset
is runtime-only, not a learnabilitygate. Datasetmodelquality is not inspected to
changeconfiguration. No testmodelpredictions.

Forecast each1000update model from1.5× measuredmean stepcost; include every100step
checkpoint write plus0/500/1000evaluation/control/probe work, initialization/setup,
fullvalidation stratumcost extrapolated from measuredperproblem values, and ledger/
serialization/audit. Use conservative larger perproblemstratumcost for any missing
profilecell. Report median/p95 too, no fabricated linearity guarantee. If paired
entryplusremainingAwork/finalaudit/reserve cannotfit B/global, plannedRESOURCESTOP;
do notshrinkmodel,batch,steps,validation,K,mechanism orgoals torescueit.

One complete A2b handoff, Sol exactPASS, then Astra-authorized unique smoke/profile
attempt. Sol reviews actualforecast before firstmeasured1701 pair. After each
learningcheckpoint supervisor checksremainingbudget; no live deadlineextension.

## Sol preflight acceptance clarifications

prepare may construct/hash test bank IDs and oracle q but must never invoke a
model on test inputs. Any test-model evaluate call must require an explicit
supervisor final-release decision binding the frozen config/banks and all20
completed main checkpoints (ten paired seeds at frozenT), plus accepted pilot/
power/runtime gates. Validate those identities/completion records; a directory's
existence is not release authorization. A negative test proves missing/incomplete
release refuses test inference. No testmodel endpoint in smoke/profile/pilot.

Forecast artifacts list temperature-work arithmetic explicitly: endpoints plus
up to8midpoints, possible6gridfallback, fixedcurves, entropy-matching and dt0/
rematching, across all relevantpolicies/seeds. Reusing rawlogits avoids duplicate
neural inference but never removes categoricalrollout/aggregation/signature cost
or silentlyshrinks prescribedcandidatepoints. Initial-entry forecast counts its
actualcheckpointwork; mainforecast includes everyremainingcontrolledendpoint.

Tests assert separate corestep/proper-score/route/mechanism/numericalprobe/I/O
timing fields and completeend-to-end time. Forecast uses actualmeasuredstratum
cells and the conservative missing-cell rule, not an average that omits challenge
work. These clarify existing plan acceptance, not new scientific endpoints.
