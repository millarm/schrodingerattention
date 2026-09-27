# Early Schrödinger Attention Experiment Plan

## Objective

Run the smallest credible experiment that can determine whether exact
Schrödinger Attention shows enough of a modelling advantage to justify further
research.

The first experiment will use a tiny bidirectional encoder on a synthetic
interference-sensitive task. It will not use a decoder-only language model,
because the proposal's causal Hamiltonian formulation remains unresolved. This
keeps the experiment focused on the central hypothesis: whether learned phase,
unitary evolution, and Born-rule measurement provide a useful attention
primitive.

## Experiment

Train a small two-layer encoder classifier on a procedurally generated keyed
retrieval task. Each example contains a query and a shuffled collection of
key-value facts, for example:

```text
[CLS] XOR key_3 key_7 [SEP]
key_1=0 key_7=1 key_3=1 key_9=0 ...
```

The model must retrieve the values associated with the two queried keys and
predict their XOR. Include a `COPY` operation as a simple retrieval control.

Dataset conditions:

- Train with two to four distractor facts.
- Evaluate in-distribution with the same number of distractors.
- Evaluate out-of-distribution with eight distractors.
- Hold out a subset of key pairs while ensuring that every individual key is
  represented during training.
- Randomize fact order.
- Use fixed-length sequences to avoid padding and masking complications.
- Generate data deterministically from recorded random seeds.

The XOR subset tests composition and cancellation. The COPY subset checks
whether either architecture merely has better or worse basic retrieval.

## Models

Compare two models:

1. A standard softmax-attention encoder.
2. An exact Schrödinger-attention encoder.

Both models will use identical:

- token and positional embeddings;
- model width, head count, layer count, and feed-forward width;
- Q, K, and V projection dimensions;
- classifier heads;
- initialization seeds where parameters correspond;
- optimizer, learning-rate schedule, batches, and stopping rules.

Use a deliberately small configuration, such as two layers, four heads,
`d_model = 64`, and a feed-forward width of 128. The exact values may be reduced
if needed to keep the experiment within its runtime cap.

## Minimal Schrödinger Attention

For each attention head, compute:

```python
S = Q @ K.transpose(-2, -1) / sqrt(d_head)
P = softmax(S, dim=-1)

H = 0.5 * (S + S.transpose(-2, -1)) / sqrt(sequence_length)
phase = gamma_per_head * S
psi0 = sqrt(P) * exp(1j * phase)

U = matrix_exp(-1j * dt_per_head * H)
psi1 = psi0 @ U.transpose(-2, -1)
A = abs(psi1) ** 2
Y = A @ V
```

Use complex64 and exact `matrix_exp`. Initialize the per-head evolution time
`dt` conservatively and constrain it to a stable range. The per-head `gamma`
and `dt` scalars add negligible capacity.

The multiplication orientation is important. Each row of `psi0` is a
key-amplitude state for one query, so evolution must act on the key dimension.
The proposal's illustrative `U @ psi0` expression would mix query rows;
`psi0 @ U.T` evolves each row's state.

At `dt = 0`, `U` is the identity and the Born probabilities exactly recover
ordinary softmax attention:

```text
abs(psi0)^2 = softmax(S)
```

This nested relationship provides both a correctness test and a useful
inference-time intervention.

## Numerical Checks

Complete these checks before training:

- Verify `H` is Hermitian within numerical tolerance.
- Verify `U.conj().T @ U` is the identity within numerical tolerance.
- Verify every row of `abs(psi1) ** 2` sums to one.
- Verify `dt = 0` produces the same attention probabilities and output as the
  softmax baseline.
- Run a small double-precision gradient check.
- Verify finite forward values and gradients across representative score
  magnitudes.
- Verify a short optimization smoke test reduces loss without NaNs.

Do not use unconditional probability renormalization to conceal norm drift
before these invariants pass. If a small defensive renormalization is later
used in training, record the pre-renormalization error.

## Runs

Run three paired seeds initially. For each seed, use the same generated data
stream and corresponding parameter initialization for both models.

Train under two budgets:

1. Equal training examples or optimizer updates, to measure sample efficiency.
2. Equal wall-clock time, to expose the cost of exact matrix exponentiation.

Cap the entire initial run at approximately three to four accelerator-hours.
If only CPU or a slow complex-tensor backend is available, reduce model size
and sequence length rather than increasing the cap.

## Measurements

Record for every run:

- validation cross-entropy;
- XOR and COPY accuracy;
- accuracy on held-out key pairs;
- accuracy with the longer distractor sequence;
- examples required to reach 90% and 95% XOR accuracy;
- examples per second and wall-clock time;
- peak device memory;
- learned `dt` and `gamma` values;
- maximum Hermiticity, unitarity, and probability-normalization errors.

After training, evaluate the Schrödinger model again with `dt = 0`. This is a
cheap mechanistic intervention. If disabling evolution does not remove an
observed advantage, the result is not evidence that Schrödinger evolution
caused the gain.

Report the mean, standard deviation, and paired per-seed differences. Three
seeds are sufficient for this screening gate, but not for a publication-level
statistical claim.

## Decision Gate

Continue research if Schrödinger Attention achieves either:

- at least a three-percentage-point mean improvement on held-out-pair or
  longer-distractor XOR accuracy; or
- at least 20% fewer training examples to reach the same XOR accuracy.

The signal must appear in at least two of the three paired seeds, COPY accuracy
must not regress materially, and setting `dt = 0` should remove a meaningful
part of the advantage.

Interpret the result as follows:

- **No consistent modelling advantage:** stop. A larger language-model
  experiment is not justified.
- **Modelling advantage but severe wall-clock disadvantage:** test one cheap
  approximation, starting with second-order truncated evolution.
- **Modelling advantage with tolerable overhead:** expand to several synthetic
  tasks and five seeds.
- **Improvement unaffected by setting `dt = 0`:** investigate capacity or
  optimization effects rather than attributing the result to interference.

## Deliverables

The work block should produce:

- one reusable attention module;
- one deterministic synthetic-data generator;
- one training and evaluation entry point;
- one numerical test file;
- raw per-step and per-seed results in a machine-readable format;
- one learning-curve figure;
- one short result summary containing the stop/continue decision.

## Explicitly Deferred Work

Do not include the following in this first block:

- causal or decoder-only attention;
- language-model training;
- learned complex Hamiltonians;
- multiple evolution approximations;
- broad downstream or long-context benchmarks;
- kernel optimization;
- parameter scaling.

These become worthwhile only if the exact bidirectional experiment produces a
repeatable modelling signal.
