# Experiment contract — FROZEN v2

Accepted after Sol PASS on2026-09-15, before implementation or comparative results. Original
plan thresholds are unchanged; decisions below make their application explicit.

## Data

Vocabulary: CLS, XOR, COPY, SEP; 12 distinct query-key tokens; 24 atomic fact
tokens `(key,value)` for binary values. No padding. Sequence is
`CLS OP key_a key_b SEP shuffled_facts`. Keys a and b are distinct and both
facts occur exactly once. XOR target is value(a) XOR value(b); COPY target is
value(a), with b an ignored query field and its fact a background control.
All remaining facts use distinct keys. Distractor count d means facts beyond
the two designated keys: train d uniformly in {2,3,4}; long evaluation d=8.
Lengths 9,10,11 are separate homogeneous batches; long length 15. Every batch
has exactly half each operation and exactly balanced binary labels within
each operation. Choose the label first, choose a fair value(a), then derive
value(b) for XOR; for COPY set value(a)=label and sample value(b) fairly.
Randomize query order for XOR and all fact orders. Sample distinct extra keys
uniformly and their values fairly.

An unordered key pair {a,b}, integer IDs 0..11, is held out exactly when
`(a+b) % 5 == 0`. Exclude both query orders from training for BOTH operations.
All other pairs are seen; sample eligible unordered pairs uniformly, then
choose their query orientation uniformly for both operations. Assert every
individual key has training coverage. For training draw one d uniformly from
{2,3,4} per batch using the batch RNG, independent of operation and label.
Fixed validation uses seen pairs and d=4: 256 XOR plus 256 COPY examples.
Final test conditions: seen/d=4, heldout/d=4, seen/d=8, heldout/d=8;
each has 512 XOR and 512 COPY balanced examples. Fixed evaluation seeds
1729 (validation) and 2718 (test). Use independent generators with seeds1729
for validation, 2718 for seen/d4, 2719 for heldout/d4, 2720 for seen/d8,
2721 for heldout/d8. Build each condition in balanced blocks of64, shuffle
rows independently within each block, and deduplicate by rejection within the
same operation/label cell. Freeze generated dataset hashes before training.
Disallow duplicate token sequences within each evaluation split and overlap
between validation and final test. Training rejects any token sequence in
either evaluation set, using hashes; final labels never drive training or
selection. Paired seeds share identical streamed batches generated from seed
100000+seed and identical fixed evaluations. Record evaluation dataset hashes.

## Models and optimizer

Two bidirectional pre-norm residual encoder layers, d_model=32, heads=2,
d_head=16, feedforward=64 with GELU, final LayerNorm and CLS linear binary
classifier. Learned token embeddings; fixed sinusoidal positional encoding
supports length 15 without untrained learned positions. No dropout. Q/K/V and
output linear projections have biases. Corresponding parameters copied from
one initialization per paired seed; verify bitwise equality of corresponding
tensors and disclose actual total/trainable parameter counts. SA adds eight
trainable scalars (two parameters times two heads times two layers); this tiny
capacity mismatch is accepted and no inert baseline parameters are added.
Seeds [11,22,33]. Float32 real tensors, complex64 amplitudes/exponentials.

Exact attention follows early_experiment_plan.md, including H division by
sqrt(length) and row evolution psi0 @ U.transpose(-2,-1), never adjoint.
Per layer/head dt=0.5*sigmoid(raw_dt), initialized dt=0.05;
gamma=pi*tanh(raw_gamma), initialized effective gamma=0.1. Initialize
raw_dt=log(0.1/0.9) and raw_gamma=atanh(0.1/pi), giving effective dt=0.05;
verify effective initial values within1e-7. No probability renormalization.
Intervention substitutes literal dt=0 at inference, preserving all parameters.
AdamW lr=0.001, betas=(0.9,0.999), eps=1e-8, weight_decay=0.01;
constant LR, gradient norm clipping 1.0. Batch size64. No tuning allowance.
One training job at a time; CPU threads2/inter-op1. Deterministic CPU operations.

## Run budgets and timing

Profile 20 representative steps per model after 5 warmups, without inspecting
accuracy; include in compute ledger. Initial maximum 2000 updates/model/seed.
Before measured runs choose largest of {500,1000,2000} for which profiling
projects all six training runs plus 50% overhead below 3600 seconds. If 500
does not fit, report feasibility blocker. This bounded resource-only choice
is a predeclared amendment recorded before any comparative result.
Evaluate fixed validation at step0, every100 updates and final; checkpoint
those same steps. No early stopping for accuracy, no best-checkpoint selection.
NaN/Inf or norm invariant error above tolerance aborts affected run and records
failure. Training target: all six final checkpoints within hard ceiling14400
elapsed compute seconds, including profiling, smoke, failures, tests, evaluation.
Stop starting work at 13800 seconds, leaving 600 seconds for summaries.

Training clock includes generation, forward/backward, optimizer; evaluation
and checkpoint I/O excluded and separately measured. Record end-to-end time.
Equal-update comparison uses final common update N. Equal-training-wall-time
endpoint for each pair is T=min(final training seconds of both models), with
each model evaluated at latest logged checkpoint with cumulative training
time <=T. Record actual times, slack, and checkpoint/update discretization;
do not label these exactly time-matched if unequal. Step0 is a valid censored
endpoint. End-to-end efficiency reported separately; no FLOP/energy equality.
Alternate run order: seed11 baseline first, seed22 Schrodinger first, seed33
baseline first. Profile results do not select hyperparameters beyond N.

## Endpoints and frozen gate

Primary: equal-update final heldout-pair/d=4 XOR accuracy. Secondary screening
endpoint: final seen-pair/d=8 XOR accuracy. Report all four conditions per op,
validation CE, and equal-time endpoints, without endpoint substitution.
Sample efficiency: first logged validation seen XOR accuracy >=90% or >=95%;
examples=step*64. Never reached is right-censored, not zero or infinity used
in averages. Compare each threshold only when both models reach it in all
three seeds. Sampling resolution is 6400 examples. A >=20% mean relative
reduction qualifies with positive reduction in at least two seeds. Accuracy gate
is >=0.03 mean paired improvement on primary OR declared secondary, with
positive improvement in at least two paired seeds on the qualifying endpoint.
COPY material regression: mean paired change below -0.02 on either heldout/d4
or seen/d8 COPY, or any individual change below -0.05, vetoes continuation.
Meaningful intervention: for an accuracy-qualified endpoint, disabling dt
removes >=50% of positive mean advantage and lowers SA accuracy >=0.01;
for sample-efficiency qualification use validation XOR at its qualifying
first-target checkpoints, requiring >=0.01 mean dt=0 drop and positive drop
in at least two seeds. Always report final dt=0 results on all conditions.

Learning adequacy: if neither model reaches mean final validation XOR >=0.80,
return INCONCLUSIVE (failure to learn) rather than a negative mechanism claim.
Missing paired runs, invalid metrics, or absent required intervention evidence
also yield INCONCLUSIVE. Otherwise apply plan's stop/continue interpretations.
Severe overhead is >3x mean training time per equal update; tolerable <=3x.
Only recommendations are authorized after this block, not further experiments.

## Numerical and artifact requirements

CPU numerical checks: H Hermiticity max error<=1e-6; U adjoint U identity and
Born row sums <=2e-4 in complex64 representative score RMS {0.1,1,3}; finite
forward and all parameter gradients at these magnitudes. dt=0 probabilities
and outputs atol=2e-6 rtol=2e-5. Double/complex128 small gradcheck eps1e-6,
atol1e-5 rtol1e-3. Explicit column-state reference test detects transpose errors.
Optimization smoke must decrease fixed-batch loss, remain finite, and exercise
checkpoint reload equality atol1e-6 and dt=0 intervention. Training invariants
recorded every evaluation and fail if max unitarity or row error>2e-3.

Deliver modules, generator, CLI, tests, machine-readable config/runtime,
per-step JSONL including training loss/timing and validation points, per-seed
final evaluation JSON, checkpoints, compute ledger, raw logs, learned dt/gamma,
invariant errors, parameter counts. CPU peak RSS is process resident-memory
proxy (platform units documented), device memory N/A; do not invent precision.
Summary CSV/JSON with sample mean, sample SD (ddof1), individual paired
differences, censored targets, and a PNG learning curve with all seed curves.
Use execution/results/ for outputs; reviews/handoffs include SHA256 hashes.
