"""Generic quantum-inspired attention components and their classical twins.

This module implements component C1 of
``research/reviews/quantum-inspired-directions-2026-09-27.md``: a Hermitian
Hamiltonian built from the full query--key score matrix. It also implements
the three controls that component must beat. Nothing here depends on a task;
every operator is derived from token content through the ordinary Q/K
projections.

Row convention matches ``schrodinger.attention``: each query row is an
amplitude state over keys and evolves as ``psi0 @ U.T``.

Variants
--------
``softmax``
    Conventional attention (baseline).
``c1``
    ``H = [(S + S^T) + i (S - S^T)] / (2 sqrt(L))``, ``U = exp(-i dt H)``,
    ``A = |sqrt(softmax(S)) @ U^T|^2``.
``c1_phasefree``
    Phase-free twin: the antisymmetric (imaginary) part of H is dropped. This
    equals the original Schrödinger attention with zero phase.
``c1_wick``
    Imaginary-time twin: ``exp(-dt H)`` replaces ``exp(-i dt H)`` and rows are
    renormalised. It keeps the same operator but has no unitarity or
    interference.
``c1_dephased``
    Fully dephased twin: the same unitary, but applied incoherently as the
    classical transition matrix ``|U|^2`` (doubly stochastic) to the softmax
    probabilities.

Component C3 (Trotterised dephasing knob), with ``K`` substeps of length
``dt / K``. Each substep first dephases, ``rho -> (1 - lambda) rho +
lambda diag(rho)``, then evolves, ``rho -> V rho V^dagger``; the weights are
the final ``diag(rho)``. Dephasing first makes ``lambda = 1`` classical from
the start.
``c3``
    ``lambda = sigmoid(raw_lambda)`` learned per head (initially 0.5).
``c3_classical``
    Classical twin: ``lambda = 1`` (a K-step Markov chain with transition
    ``|V|^2``). The coherent twin (``lambda = 0``) is exactly ``c1``.

Component C4 (amplitude-level value mixing). Values are complex
(``v[..., :d/2] + i v[..., d/2:]``) and the output is the real and imaginary
parts of ``coef @ v_complex``, so contributions from different keys can
cancel. Every C4 variant uses ``sqrt(softmax(S))`` at ``dt = 0``.
``c4``
    ``coef = sqrt(softmax(S)) @ U^T`` with C1's unitary (complex).
``c4_magnitude``
    No-cancellation twin: ``coef = |c4 coef|`` (real, non-negative).
``c4_real``
    Signed classical twin: ``coef = Re(c4 coef)``, renormalised to unit norm.
    Real signed weights can cancel without complex numbers.
``c4_wick``
    Imaginary-time twin: ``exp(-dt H)`` in place of ``U``, renormalised.
``c4_dephased``
    Fully dephased twin: ``coef = sqrt(softmax(S) @ |U|^2 ^T)``.
"""

from __future__ import annotations

import math
from typing import Literal

import torch
from torch import Tensor, nn

QuantumVariant = Literal["softmax", "c1", "c1_phasefree", "c1_wick", "c1_dephased"]
VARIANTS: tuple[str, ...] = ("softmax", "c1", "c1_phasefree", "c1_wick", "c1_dephased")
_QUANTUM = VARIANTS[1:]
C3_VARIANTS: tuple[str, ...] = ("c3", "c3_classical")
C4_VARIANTS: tuple[str, ...] = ("c4", "c4_magnitude", "c4_real", "c4_wick", "c4_dephased")
# Stage D (classical leads). Readout family: coefficient vectors applied to
# real values, all with softmax's alpha/beta scalars. Operator family:
# imaginary-time score-operator mixing with a learned evolution time.
READOUT_VARIANTS: tuple[str, ...] = ("softmax_t2", "sqrt_softmax", "maa_p2", "maa_p11", "sigmoid")
OPERATOR_VARIANTS: tuple[str, ...] = ("wick_real", "wick_linear")
ALL_VARIANTS: tuple[str, ...] = VARIANTS + C3_VARIANTS + C4_VARIANTS + READOUT_VARIANTS + OPERATOR_VARIANTS
TROTTER_STEPS = 2


def _complex_dtype(real_dtype: torch.dtype) -> torch.dtype:
    if real_dtype == torch.float64:
        return torch.complex128
    if real_dtype == torch.float32:
        return torch.complex64
    raise TypeError(f"scores must be float32 or float64, got {real_dtype}")


def hamiltonian(scores: Tensor, hermitian: bool) -> Tensor:
    """Return the complex Hamiltonian for each score matrix.

    With ``hermitian=False`` only the symmetric part is kept, as in
    ``schrodinger.attention``. With ``hermitian=True`` the antisymmetric part
    becomes the imaginary part, so directional information is retained.
    """

    length = scores.shape[-1]
    transposed = scores.transpose(-2, -1)
    real = 0.5 * (scores + transposed) / math.sqrt(length)
    complex_dtype = _complex_dtype(scores.dtype)
    if not hermitian:
        return real.to(complex_dtype)
    imaginary = 0.5 * (scores - transposed) / math.sqrt(length)
    return torch.complex(real, imaginary).to(complex_dtype)


def quantum_weights(scores: Tensor, dt: Tensor | float, variant: str) -> Tensor:
    """Return row-stochastic attention weights ``[..., L, L]`` for ``variant``.

    ``dt`` broadcasts against ``scores[..., :1, :1]`` (for example per-head
    ``[1, heads, 1, 1]``). At ``dt == 0`` every variant reduces to softmax.
    """

    if variant == "softmax":
        return torch.softmax(scores, dim=-1)
    if variant not in _QUANTUM:
        raise ValueError(f"unknown variant {variant!r}")
    complex_dtype = _complex_dtype(scores.dtype)
    probabilities = torch.softmax(scores, dim=-1)
    # exp(log_softmax / 2) is the numerically stable square root: its backward
    # pass stays finite where softmax underflows to zero.
    amplitude = torch.exp(0.5 * torch.log_softmax(scores, dim=-1)).to(complex_dtype)
    h = hamiltonian(scores, hermitian=variant != "c1_phasefree")
    dt_tensor = torch.as_tensor(dt, dtype=scores.dtype, device=scores.device).to(complex_dtype)
    if variant == "c1_wick":
        propagator = torch.matrix_exp(-dt_tensor * h)
        evolved = (amplitude @ propagator.transpose(-2, -1)).abs().square()
        return evolved / evolved.sum(dim=-1, keepdim=True)
    unitary = torch.matrix_exp(-1j * dt_tensor * h)
    if variant == "c1_dephased":
        transition = unitary.abs().square()
        return probabilities @ transition.transpose(-2, -1)
    return (amplitude @ unitary.transpose(-2, -1)).abs().square()


def c3_weights(scores: Tensor, dt: Tensor | float, dephasing: Tensor | float, steps: int = TROTTER_STEPS) -> Tensor:
    """Row-stochastic weights from the Trotterised dephasing channel (C3).

    ``dephasing`` is lambda in [0, 1] and broadcasts like ``dt``. With
    ``lambda = 0`` this equals ``quantum_weights(scores, dt, "c1")``.
    """

    complex_dtype = _complex_dtype(scores.dtype)
    amplitude = torch.exp(0.5 * torch.log_softmax(scores, dim=-1)).to(complex_dtype)
    h = hamiltonian(scores, hermitian=True)
    dt_tensor = torch.as_tensor(dt, dtype=scores.dtype, device=scores.device).to(complex_dtype)
    step = torch.matrix_exp(-1j * (dt_tensor / steps) * h)
    step_dagger = step.conj().transpose(-2, -1)
    length = scores.shape[-1]
    lam = torch.as_tensor(dephasing, dtype=scores.dtype, device=scores.device)
    lam = lam.unsqueeze(-1) if lam.ndim else lam
    # rho[..., row, j, k] = a_j conj(a_k) for each query row's amplitude state.
    rho = amplitude.unsqueeze(-1) * amplitude.conj().unsqueeze(-2)
    eye = torch.eye(scores.shape[-1], dtype=scores.dtype, device=scores.device)
    keep = (1 - lam) + lam * eye
    batch_shape = rho.shape[:-3]
    for _ in range(steps):
        rho = rho * keep.to(complex_dtype)
        # V rho_i V^dagger for every row i as two large matmuls instead of L
        # small broadcast ones: stack the rows' matrices side by side.
        stacked = rho.permute(*range(len(batch_shape)), -2, -3, -1).reshape(*batch_shape, length, length * length)
        left = (step @ stacked).reshape(*batch_shape, length, length, length).permute(
            *range(len(batch_shape)), -2, -3, -1
        )
        rho = left @ step_dagger.unsqueeze(-3)
    return torch.diagonal(rho, dim1=-2, dim2=-1).real


def c4_coefficients(scores: Tensor, dt: Tensor | float, variant: str) -> Tensor:
    """Per-row mixing coefficients over keys for a C4 variant (complex dtype)."""

    if variant not in C4_VARIANTS:
        raise ValueError(f"unknown C4 variant {variant!r}")
    complex_dtype = _complex_dtype(scores.dtype)
    amplitude = torch.exp(0.5 * torch.log_softmax(scores, dim=-1)).to(complex_dtype)
    h = hamiltonian(scores, hermitian=True)
    dt_tensor = torch.as_tensor(dt, dtype=scores.dtype, device=scores.device).to(complex_dtype)
    if variant == "c4_wick":
        evolved = amplitude @ torch.matrix_exp(-dt_tensor * h).transpose(-2, -1)
        return evolved / torch.linalg.vector_norm(evolved, dim=-1, keepdim=True)
    unitary = torch.matrix_exp(-1j * dt_tensor * h)
    if variant == "c4_dephased":
        weights = torch.softmax(scores, dim=-1) @ unitary.abs().square().transpose(-2, -1)
        return weights.clamp_min(1e-20).sqrt().to(complex_dtype)
    evolved = amplitude @ unitary.transpose(-2, -1)
    if variant == "c4_magnitude":
        return evolved.abs().to(complex_dtype)
    if variant == "c4_real":
        real = evolved.real
        return (real / torch.linalg.vector_norm(real, dim=-1, keepdim=True).clamp_min(1e-12)).to(complex_dtype)
    return evolved


def c4_mix(coefficients: Tensor, values: Tensor) -> Tensor:
    """Mix complex values ``v[..., :d/2] + i v[..., d/2:]``; return real/imag parts."""

    half = values.shape[-1] // 2
    complex_values = torch.complex(values[..., :half], values[..., half:]).to(coefficients.dtype)
    mixed = coefficients @ complex_values
    return torch.cat((mixed.real, mixed.imag), dim=-1)


def readout_coefficients(scores: Tensor, variant: str) -> Tensor:
    """Real per-row mixing coefficients for the Stage D readout variants.

    ``maa_p`` is Mass-Aware Attention (Yu and Ha, 2026): softmax weights
    divided by their Lp norm, so the output magnitude keeps how many keys are
    attended. ``sqrt_softmax`` equals sqrt(softmax(S)), which is the p = 2
    case at temperature 2. ``sigmoid`` uses the bias -log(L) (Ramapuram et
    al., 2025).
    """

    if variant == "softmax_t2":
        return torch.softmax(0.5 * scores, dim=-1)
    if variant == "sqrt_softmax":
        return torch.exp(0.5 * torch.log_softmax(scores, dim=-1))
    if variant in ("maa_p2", "maa_p11"):
        power = 2.0 if variant == "maa_p2" else 1.1
        weights = torch.softmax(scores, dim=-1)
        return weights / torch.linalg.vector_norm(weights, ord=power, dim=-1, keepdim=True)
    if variant == "sigmoid":
        return torch.sigmoid(scores - math.log(scores.shape[-1]))
    raise ValueError(f"unknown readout variant {variant!r}")


def operator_weights(scores: Tensor, dt: Tensor | float, variant: str) -> Tensor:
    """Row-stochastic weights for the Stage D operator variants.

    ``wick_real`` is imaginary-time evolution under the real symmetric H (no
    antisymmetric part, so a real propagator). ``wick_linear`` truncates the
    complex imaginary-time propagator to first order, ``I - dt H``.
    ``c1_wick`` in ``quantum_weights`` is the full complex version.
    """

    complex_dtype = _complex_dtype(scores.dtype)
    amplitude = torch.exp(0.5 * torch.log_softmax(scores, dim=-1)).to(complex_dtype)
    dt_tensor = torch.as_tensor(dt, dtype=scores.dtype, device=scores.device).to(complex_dtype)
    if variant == "wick_real":
        propagator = torch.matrix_exp(-dt_tensor * hamiltonian(scores, hermitian=False))
    elif variant == "wick_linear":
        h = hamiltonian(scores, hermitian=True)
        propagator = torch.eye(scores.shape[-1], dtype=complex_dtype, device=scores.device) - dt_tensor * h
    else:
        raise ValueError(f"unknown operator variant {variant!r}")
    evolved = (amplitude @ propagator.transpose(-2, -1)).abs().square()
    return evolved / evolved.sum(dim=-1, keepdim=True)


def total_variation(weights: Tensor, reference: Tensor) -> Tensor:
    """Mean per-row total-variation distance between two attention tensors."""

    return 0.5 * (weights - reference).abs().sum(dim=-1).mean()


class QuantumMultiheadAttention(nn.Module):
    """Drop-in multihead self-attention for any of ``VARIANTS``.

    Every variant has the same Q/K/V/O projections and two learned scalars
    per head, so parameter counts match exactly. Each variant has a per-head
    score scale ``alpha``. The second scalar is a per-head value scale
    ``beta`` for softmax (as in ``schrodinger.route_policy``) and a bounded
    evolution time for the quantum variants, ``dt = 0.5 * sigmoid(raw_dt)``,
    initialised at 0.05 to match the original component (``dt_init``).
    ``c3`` has one more scalar per head, the dephasing strength
    ``lambda = sigmoid(raw_lambda)``.
    """

    def __init__(self, d_model: int, num_heads: int, variant: str = "softmax", dt_init: float = 0.05) -> None:
        super().__init__()
        if d_model <= 0 or num_heads <= 0 or d_model % num_heads:
            raise ValueError("d_model must be positive and divisible by num_heads")
        if not 0 < dt_init < 0.5:
            raise ValueError("dt_init must lie in (0, 0.5)")
        if variant in C4_VARIANTS and (d_model // num_heads) % 2:
            raise ValueError("C4 variants need an even head dimension")
        if variant not in ALL_VARIANTS:
            raise ValueError(f"unknown variant {variant!r}")
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.variant = variant
        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.alpha = nn.Parameter(torch.zeros(num_heads))
        if variant == "softmax" or variant in READOUT_VARIANTS:
            self.beta = nn.Parameter(torch.zeros(num_heads))
        else:
            fraction = 2 * dt_init
            self.raw_dt = nn.Parameter(torch.full((num_heads,), math.log(fraction / (1 - fraction))))
        if variant == "c3":
            self.raw_lambda = nn.Parameter(torch.zeros(num_heads))
        self.last_weights: Tensor | None = None
        self.last_scores: Tensor | None = None

    def effective_dt(self) -> Tensor:
        if self.variant == "softmax" or self.variant in READOUT_VARIANTS:
            raise RuntimeError(f"{self.variant} attention has no evolution time")
        return 0.5 * torch.sigmoid(self.raw_dt)

    def effective_lambda(self) -> Tensor:
        if self.variant != "c3":
            raise RuntimeError("only c3 has a learned dephasing strength")
        return torch.sigmoid(self.raw_lambda)

    def forward(self, inputs: Tensor, dt_override: float | None = None) -> Tensor:
        if inputs.ndim != 3 or inputs.shape[-1] != self.d_model:
            raise ValueError("inputs must have shape [batch, length, d_model]")
        batch, length, _ = inputs.shape

        def split(projected: Tensor) -> Tensor:
            return projected.reshape(batch, length, self.num_heads, self.head_dim).transpose(1, 2)

        q, k, v = (split(layer(inputs)) for layer in (self.q_proj, self.k_proj, self.v_proj))
        heads = (1, self.num_heads, 1, 1)
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)
        scores = scores * torch.exp(self.alpha).reshape(heads)
        if self.variant == "softmax" or self.variant in READOUT_VARIANTS:
            weights = (
                torch.softmax(scores, dim=-1) if self.variant == "softmax" else readout_coefficients(scores, self.variant)
            )
            v = v * torch.exp(self.beta).reshape(heads)
        else:
            dt = self.effective_dt().reshape(heads) if dt_override is None else dt_override
        if self.variant in C4_VARIANTS:
            coefficients = c4_coefficients(scores, dt, self.variant)
            weights = coefficients.abs().square()
            mixed = c4_mix(coefficients, v)
        else:
            if self.variant == "c3":
                weights = c3_weights(scores, dt, self.effective_lambda().reshape(heads))
            elif self.variant == "c3_classical":
                weights = c3_weights(scores, dt, 1.0)
            elif self.variant in OPERATOR_VARIANTS:
                weights = operator_weights(scores, dt, self.variant)
            elif self.variant != "softmax" and self.variant not in READOUT_VARIANTS:
                weights = quantum_weights(scores, dt, self.variant)
            mixed = weights @ v
        self.last_weights = weights.detach()
        self.last_scores = scores.detach()
        attended = mixed.transpose(1, 2).reshape(batch, length, self.d_model)
        return self.out_proj(attended)


class ProbeEncoder(nn.Module):
    """Small pre-norm bidirectional encoder with a CLS readout, for probes."""

    def __init__(
        self,
        vocab_size: int,
        max_length: int,
        num_classes: int,
        variant: str,
        d_model: int = 32,
        num_heads: int = 2,
        num_layers: int = 1,
        dt_init: float = 0.05,
    ) -> None:
        super().__init__()
        self.variant = variant
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.position = nn.Parameter(torch.randn(max_length, d_model) * 0.02)
        self.norm1 = nn.ModuleList(nn.LayerNorm(d_model) for _ in range(num_layers))
        self.attention = nn.ModuleList(
            QuantumMultiheadAttention(d_model, num_heads, variant, dt_init) for _ in range(num_layers)
        )
        self.norm2 = nn.ModuleList(nn.LayerNorm(d_model) for _ in range(num_layers))
        self.feedforward = nn.ModuleList(
            nn.Sequential(nn.Linear(d_model, 2 * d_model), nn.GELU(), nn.Linear(2 * d_model, d_model))
            for _ in range(num_layers)
        )
        self.final_norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, num_classes)

    def forward(self, tokens: Tensor, dt_override: float | None = None) -> Tensor:
        x = self.embedding(tokens) + self.position[: tokens.shape[1]]
        for norm1, attention, norm2, feedforward in zip(
            self.norm1, self.attention, self.norm2, self.feedforward
        ):
            x = x + attention(norm1(x), dt_override)
            x = x + feedforward(norm2(x))
        return self.head(self.final_norm(x[:, 0]))
