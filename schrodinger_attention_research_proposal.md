# Schrödinger Attention: Quantum-Amplitude Probability Weighting for Transformer Architectures

## Abstract

Transformer architectures rely on scaled dot-product attention in which
query-key similarity scores are converted into non-negative, normalized
weights using softmax. This paper proposes **Schrödinger Attention**, a
quantum-inspired attention mechanism in which token interactions
parameterize a learned Hamiltonian, latent attention states are
represented as complex-valued amplitudes, those amplitudes undergo
differentiable Schrödinger-style evolution, and observable attention
probabilities are obtained using the Born rule.

The architecture requires no quantum hardware: it uses conventional
complex-valued tensor operations. The central hypothesis is that phase
and interference at the attention level provide an inductive bias for
contextual reinforcement, cancellation, ambiguity and compositional
interactions that may be more efficient than conventional positive
softmax weighting.

We propose a concrete implementation and experimental programme
comparing Schrödinger Attention with matched conventional transformers.
Evaluation focuses on language-model loss and perplexity, sample and
compute efficiency, downstream reasoning, long-context retrieval,
interference-sensitive synthetic tasks, scaling behaviour and
computational cost. The core falsifiable question is: **does learned
amplitude evolution followed by Born-rule measurement provide a better
computational primitive for attention than softmax?**

## 1. Introduction

Standard transformer attention is

\[ `\mathrm{Attention}`{=tex}(Q,K,V)=
`\mathrm{softmax}`{=tex}`\left`{=tex}(`\frac{QK^T}{\sqrt{d_k}}`{=tex}`\right`{=tex})V.
\]

For query token (i),

\[ a\_{ij}`\geq0`{=tex},`\qquad `{=tex}`\sum`{=tex}*j a*{ij}=1. \]

This is effective but imposes a classical probability simplex on the
routing mechanism.

Quantum probability instead represents a state using complex amplitudes

\[ `\psi`{=tex}\_j=r_je\^{i`\theta`{=tex}\_j}, \]

with observable probability

\[ p_j=\|`\psi`{=tex}\_j\|\^2. \]

For two amplitudes,

\[ \|`\psi`{=tex}\_1+`\psi`{=tex}\_2\|\^2 =
\|`\psi`{=tex}\_1\|\^2+\|`\psi`{=tex}\_2\|\^2+
2`\operatorname{Re}`{=tex}(`\psi`{=tex}\_1`\psi`{=tex}\_2\^\*). \]

The final term represents interference. Depending on relative phase, two
signals can reinforce or cancel each other.

This motivates the research question:

> Can phase and interference provide a useful computational primitive
> inside transformer attention?

## 2. Hypothesis

Conventional attention computes

\[ y_i=`\sum`{=tex}*j a*{ij}v_j. \]

Although value vectors can contain positive and negative components, the
routing weights themselves are non-negative. Interactions such as "A
supports X, B supports X, but A and B together suppress X" must
therefore emerge indirectly through representations and subsequent
layers.

Schrödinger Attention introduces such interactions directly into
attention weighting.

Potential benefits include improved modelling of:

-   negation and contradiction;
-   ambiguity resolution;
-   competing antecedents;
-   exception handling;
-   compositional semantics;
-   long-range dependencies;
-   retrieval among plausible distractors;
-   contextual reinforcement and suppression.

## 3. Proposed Architecture

The proposed computation is

\[ Q,K `\rightarrow `{=tex}H `\rightarrow `{=tex}`\psi`{=tex}
`\rightarrow `{=tex}U`\psi `{=tex}`\rightarrow `{=tex}\|`\psi`{=tex}\|\^2
`\rightarrow `{=tex}V, \]

where (H) is a learned Hamiltonian and

\[ U=e\^{-iH`\Delta `{=tex}t}. \]

### 3.1 Query, key and value projections

Begin conventionally:

\[ Q=XW_Q,`\qquad `{=tex}K=XW_K,`\qquad `{=tex}V=XW_V. \]

### 3.2 Hamiltonian construction

Calculate

\[ S=`\frac{QK^T}{\sqrt{d_k}}`{=tex}. \]

The Hamiltonian must be Hermitian:

\[ H=H\^`\dagger`{=tex}. \]

A minimal implementation is

\[ H=`\frac{S+S^T}{2}`{=tex}. \]

A richer implementation can learn

\[ H=A+iB, \]

subject to

\[ A=A^T,`\qquad `{=tex}B=-B^T. \]

### 3.3 Initial amplitude

A conservative initialization is

\[ `\psi`{=tex}\_j(0)=
`\sqrt{\mathrm{softmax}(S)_j}`{=tex}e\^{i`\phi`{=tex}\_j}, \]

where

\[ `\phi`{=tex}=f\_`\theta`{=tex}(Q,K) \]

is learned.

This deliberately remains close to standard attention while introducing
phase.

### 3.4 Schrödinger evolution

The continuous equation is

\[ i`\frac{\partial\psi}{\partial t}`{=tex}=H`\psi`{=tex}. \]

A discrete attention operation becomes

\[ `\psi`{=tex}'=e\^{-iH`\Delta `{=tex}t}`\psi`{=tex}. \]

For Hermitian (H), (U=e\^{-iH`\Delta `{=tex}t}) is unitary and preserves
norm.

### 3.5 Born-rule measurement

Attention probabilities are

\[ a_j=\|`\psi`{=tex}'\_j\|\^2. \]

For a normalized state,

\[ `\sum`{=tex}\_j a_j=1. \]

The output remains compatible with the conventional transformer:

\[ y=`\sum`{=tex}\_j a_jv_j. \]

## 4. Practical Variants

A full matrix exponential per attention head is unlikely to be
computationally competitive, so several implementations should be
tested.

### Exact Schrödinger Attention

\[ U=e\^{-iH`\Delta `{=tex}t}. \]

Use this at short sequence lengths as the mathematical reference
implementation.

### Truncated evolution

Approximate

\[ e\^{-iH`\Delta `{=tex}t}
`\approx `{=tex}I-iH`\Delta `{=tex}t-`\frac`{=tex}12H^2`\Delta `{=tex}t^2+`\cdots`{=tex}.
\]

Compare first-, second- and fourth-order approximations.

### Cayley transform

Use

\[ U= `\left`{=tex}(I-`\frac{i\Delta t}{2}`{=tex}H`\right`{=tex})\^{-1}
`\left`{=tex}(I+`\frac{i\Delta t}{2}`{=tex}H`\right`{=tex}). \]

### Phase-only attention

Remove explicit Schrödinger evolution but retain complex amplitudes.
This determines whether phase alone provides the benefit.

### Hybrid attention

Use ordinary softmax for some heads and Schrödinger Attention for
others:

\[ `\mathrm{MultiHead}`{=tex} =
\[`\mathrm{SoftmaxHeads}`{=tex};`\mathrm{SchrödingerHeads}`{=tex}\]. \]

A hybrid architecture may ultimately be more useful than replacing all
conventional attention.

## 5. Falsifiable Hypotheses

**H1 --- Quality:** At matched parameter count and training data,
Schrödinger Attention achieves lower validation
cross-entropy/perplexity.

**H2 --- Parameter efficiency:** It reaches equivalent performance using
fewer parameters.

**H3 --- Sample efficiency:** It reaches a target loss using fewer
training tokens.

**H4 --- Reasoning:** It disproportionately improves tasks involving
contradiction, negation, ambiguity and competing evidence.

**H5 --- Long context:** It improves discrimination between relevant
context and semantically plausible distractors.

**H6 --- Hybrid specialization:** Schrödinger heads in hybrid models
learn measurably different functions from conventional heads.

**H7 --- Scaling:** Any advantage persists or increases with model and
dataset scale.

## 6. Experimental Programme

### Stage 1: Synthetic interference tasks

Construct controlled tasks in which:

-   individual clues support an answer but their conjunction changes it;
-   negation reverses a relation;
-   multiple clues provide competing evidence;
-   relevant information is surrounded by similar distractors;
-   XOR-like compositional relationships are required.

Measure convergence speed, final accuracy and generalization to unseen
compositions.

### Stage 2: Small language models

Train approximately 30M--150M parameter decoder-only models with:

-   identical tokenizer;
-   identical training corpus;
-   identical optimizer and schedule;
-   identical context length;
-   multiple random seeds.

Compare:

1.  standard transformer;
2.  phase-only attention;
3.  approximate Schrödinger Attention;
4.  exact Schrödinger Attention where feasible;
5.  hybrid softmax/Schrödinger attention.

### Stage 3: Scaling

If smaller experiments are positive, test approximately 300M and 1B
parameter models before attempting larger scales.

## 7. Fair Comparison

Three comparisons should be reported.

### Parameter matched

\[
N\_{`\mathrm{SA}`{=tex}}`\approx `{=tex}N\_{`\mathrm{baseline}`{=tex}}.
\]

### FLOP matched

Give each architecture approximately the same total training
computation.

### Wall-clock or energy matched

Give each architecture equal accelerator-hours or energy budget.

An architectural improvement is substantially more convincing if it
survives parameter- and FLOP-matched comparisons.

## 8. Primary Performance Metrics

### Validation cross-entropy

Held-out next-token loss should be the primary language-model metric.

### Perplexity

\[ PPL=e\^L. \]

### Tokens to target loss

Define

\[ T(L\^*)=
`\text{training tokens required to reach target loss }`{=tex}L\^*. \]

This measures sample efficiency.

### Compute to target loss

Define

\[ C(L\^*)= `\text{FLOPs required to reach }`{=tex}L\^*. \]

This is particularly important because an architecture that achieves
slightly better perplexity at dramatically greater computational cost
has not necessarily improved the transformer.

### Training throughput

Report tokens/second, accelerator utilization, memory consumption and
total training time.

### Inference performance

Report prefill throughput, decode throughput, latency, KV-cache
requirements and energy where measurable.

## 9. Downstream Evaluation

Use standard benchmarks covering:

-   commonsense reasoning;
-   reading comprehension;
-   natural-language inference;
-   logical reasoning;
-   mathematics;
-   code;
-   factual recall;
-   long-context retrieval.

However, generic benchmark averages alone are insufficient.

### Interference benchmark

Develop a dedicated diagnostic dataset containing paired examples where
evidence is:

1.  independently supportive;
2.  mutually reinforcing;
3.  contradictory;
4.  cancelling;
5.  irrelevant.

Measure changes in model probability as controlled combinations of
evidence are introduced.

This directly tests the proposed architectural mechanism.

## 10. Long-Context Evaluation

Test context lengths such as

\[ 2K,;4K,;8K,;16K,;32K. \]

At each length measure:

-   retrieval accuracy;
-   perplexity;
-   distractor sensitivity;
-   lost-in-the-middle behaviour;
-   latency;
-   memory use.

Distractors should be semantically similar to the correct evidence
rather than random text.

If destructive interference is useful, one potential advantage is
suppression of plausible-but-wrong contextual paths.

## 11. Scaling Laws

For model sizes such as

\[ N`\in`{=tex}{30M,100M,300M,1B}, \]

fit

\[ L(N)=L\_`\infty`{=tex}+aN\^{-`\alpha`{=tex}}. \]

Similarly for compute,

\[ L(C)=L\_`\infty`{=tex}+bC\^{-`\beta`{=tex}}. \]

A particularly important result would be evidence that

\[
`\alpha`{=tex}*{`\mathrm{SA}`{=tex}}\>`\alpha`{=tex}*{`\mathrm{baseline}`{=tex}}
\]

or

\[
`\beta`{=tex}*{`\mathrm{SA}`{=tex}}\>`\beta`{=tex}*{`\mathrm{baseline}`{=tex}}.
\]

That would suggest the architecture becomes more attractive rather than
less attractive at scale.

## 12. Ablation Studies

Required ablations include:

-   zero phase;
-   random fixed phase;
-   learned phase without Schrödinger evolution;
-   complex but non-unitary attention;
-   real orthogonal norm-preserving evolution;
-   conventional attention given equivalent additional parameters;
-   hybrid models with 0%, 25%, 50%, 75% and 100% Schrödinger heads.

These distinguish benefits arising from phase, complex representation,
unitary evolution, extra capacity or the complete mechanism.

## 13. Mechanistic Analysis

The interference contribution between two amplitudes can be measured as

\[
I\_{jk}=2`\operatorname{Re}`{=tex}(`\psi`{=tex}\_j`\psi`{=tex}\_k\^\*).
\]

Analyse whether destructive interference systematically occurs around:

-   negation;
-   contradiction;
-   competing entity references;
-   irrelevant retrieval candidates;
-   syntactic alternatives.

Test whether constructive interference occurs around:

-   agreement;
-   repeated supporting evidence;
-   coreference;
-   mutually supporting facts.

This makes the central claim mechanistically testable:

> Does the architecture perform better because it has learned useful
> interference?

## 14. Statistical Methodology

Every important experiment should use multiple random seeds.

Report:

-   mean performance;
-   standard deviation;
-   confidence intervals;
-   effect sizes;
-   paired comparisons where appropriate.

Hyperparameter-search budgets must also be comparable. An experimental
architecture should not receive substantially more optimization effort
than the baseline without this being explicitly reported.

## 15. Success Criteria

### Strong positive result

At matched compute, Schrödinger Attention achieves statistically
significant lower validation loss, better compute-to-target-loss,
improvements on interference-sensitive tasks and acceptable inference
cost.

### Very strong result

The advantage increases with model size, training tokens or context
length.

### Interesting partial result

Overall perplexity is unchanged but reasoning, contradiction handling or
long-context retrieval improves substantially. This would motivate
hybrid architectures.

### Negative result

Any gain disappears after controlling for parameters and compute, or
computational overhead overwhelms modelling improvements.

This remains scientifically useful because the hypothesis is explicitly
falsifiable.

## 16. Concrete Implementation Roadmap

### Phase 1 --- PyTorch reference implementation

Implement a custom attention module using complex tensors.

``` python
S = Q @ K.transpose(-2, -1) / sqrt(d)

H = 0.5 * (S + S.transpose(-2, -1))

amplitude = torch.sqrt(torch.softmax(S, dim=-1))
psi0 = amplitude.to(complex_dtype) * torch.exp(1j * phase)

U = torch.matrix_exp(-1j * dt * H.to(complex_dtype))
psi = U @ psi0

attention = torch.abs(psi) ** 2
output = attention @ V
```

This version should prioritize mathematical correctness rather than
speed.

### Phase 2 --- Numerical validation

Verify numerically that

\[ H=H\^`\dagger`{=tex}, \]

\[ U\^`\dagger `{=tex}U`\approx `{=tex}I, \]

and

\[ `\sum`{=tex}\_j\|`\psi`{=tex}\_j\|\^2`\approx1`{=tex}. \]

Perform gradient checks and numerical-stability tests.

### Phase 3 --- Synthetic benchmark

Train tiny models repeatedly across controlled tasks. This stage should
be cheap enough for extensive ablation and hyperparameter testing.

### Phase 4 --- 100M-class language model

Train matched baseline and experimental models. Preserve full training
curves and checkpoints.

### Phase 5 --- Efficient implementation

Only if modelling results justify it, replace exact exponentiation with
efficient approximations and ultimately fused GPU kernels.

### Phase 6 --- Scaling

Progress to several hundred million and approximately one billion
parameters only after establishing reproducible smaller-scale gains.

## 17. Engineering Challenges

The principal engineering risk is computational complexity. Naive matrix
exponentiation is substantially more expensive than softmax attention
and may introduce poor scaling with sequence length.

Other risks include:

-   complex-valued tensor throughput;
-   numerical instability;
-   optimization difficulty;
-   maintaining causality in decoder attention;
-   compatibility with FlashAttention-style kernels;
-   efficient KV caching;
-   phase degeneracies;
-   gradients through unitary evolution.

These are not reasons to reject the hypothesis, but they mean the first
objective should be demonstrating a modelling advantage before
substantial optimization work.

## 18. Important Causal-Attention Issue

Decoder-only language models require causal masking. A naive symmetric
Hamiltonian can violate causal structure because Hermiticity naturally
couples positions in both directions.

This is therefore a central architectural problem rather than a minor
implementation detail.

Early experiments should consider two routes:

1.  first test the mechanism in bidirectional or synthetic settings
    where a full Hermitian interaction matrix is legitimate;
2.  develop a causal formulation in which each query evolves an
    amplitude state only over its permitted prefix.

A practical causal implementation may treat the Hamiltonian as operating
over the key/value subspace available to each query rather than
constructing one global sequence Hamiltonian.

Solving this efficiently is likely to be one of the key technical
contributions of the work.

## 19. Relationship to Existing Research

Several adjacent research directions motivate the proposal:

-   quantum-inspired and Born-rule interpretations of attention;
-   Hilbert-space interpretations of transformer representations;
-   Schrödinger bridge formulations with mathematical similarities to
    attention;
-   transformer neural-network quantum states used to represent physical
    wavefunctions;
-   complex-valued neural networks and unitary recurrent architectures.

The proposed contribution is distinct: it treats learned Hamiltonian
evolution and Born-rule measurement as an **internal attention primitive
in a conventional trainable transformer**, and evaluates whether this
produces measurable computational or modelling advantages over standard
architectures.

A formal literature review should precede publication to establish the
precise novelty relative to rapidly developing 2025--2026 work.

## 20. Research Questions

The programme should ultimately answer five questions:

1.  **Does it work?**\
    Does Schrödinger Attention improve predictive performance?

2.  **Why does it work?**\
    Are improvements actually associated with learned interference?

3.  **Where does it work?**\
    Are gains concentrated in reasoning, contradiction, compositionality
    or long-context retrieval?

4.  **Does it scale?**\
    Do benefits persist as model size and training compute increase?

5.  **Is it economically useful?**\
    Does improved model quality exceed the computational cost of
    amplitude evolution?

## 21. Conclusion

Schrödinger Attention proposes replacing the classical probability
simplex at the heart of transformer attention with a richer latent
representation based on complex amplitudes, learned Hamiltonian dynamics
and Born-rule measurement.

The proposal does not assume that quantum mechanics is required to
explain intelligence, nor that quantum hardware is needed. Instead, it
extracts a specific mathematical property of quantum probability ---
interference between amplitudes --- and asks whether that property is
useful as an inductive bias for sequence modelling.

The hypothesis is deliberately falsifiable.

If amplitude interference provides no improvement after controlling for
parameters, training data and computation, conventional softmax remains
the superior primitive.

If, however, Schrödinger Attention demonstrates superior sample
efficiency, reasoning, long-context discrimination or scaling behaviour,
it would suggest that transformer architectures benefit from
representing contextual relationships in an amplitude space before
reducing them to classical probabilities.

The decisive experiment is therefore not whether a transformer can be
described using quantum terminology.

It is whether, under controlled conditions,

\[
`\boxed{\text{Schrödinger Attention delivers more capability per unit of compute than Softmax Attention.}}`{=tex}
\]

That is an experimentally answerable question and provides a concrete
research programme for evaluating the architecture.
