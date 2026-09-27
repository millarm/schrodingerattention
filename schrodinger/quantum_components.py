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
"""

from __future__ import annotations

import math
from typing import Literal

import torch
from torch import Tensor, nn

QuantumVariant = Literal["softmax", "c1", "c1_phasefree", "c1_wick", "c1_dephased"]
VARIANTS: tuple[str, ...] = ("softmax", "c1", "c1_phasefree", "c1_wick", "c1_dephased")
_QUANTUM = VARIANTS[1:]


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
    initialised at 0.05 to match the original component.
    """

    def __init__(self, d_model: int, num_heads: int, variant: str = "softmax") -> None:
        super().__init__()
        if d_model <= 0 or num_heads <= 0 or d_model % num_heads:
            raise ValueError("d_model must be positive and divisible by num_heads")
        if variant not in VARIANTS:
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
        if variant == "softmax":
            self.beta = nn.Parameter(torch.zeros(num_heads))
        else:
            self.raw_dt = nn.Parameter(torch.full((num_heads,), math.log(0.1 / 0.9)))
        self.last_weights: Tensor | None = None
        self.last_scores: Tensor | None = None

    def effective_dt(self) -> Tensor:
        if self.variant == "softmax":
            raise RuntimeError("softmax attention has no evolution time")
        return 0.5 * torch.sigmoid(self.raw_dt)

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
        if self.variant == "softmax":
            weights = torch.softmax(scores, dim=-1)
            v = v * torch.exp(self.beta).reshape(heads)
        else:
            dt = self.effective_dt().reshape(heads) if dt_override is None else dt_override
            weights = quantum_weights(scores, dt, self.variant)
        self.last_weights = weights.detach()
        self.last_scores = scores.detach()
        attended = (weights @ v).transpose(1, 2).reshape(batch, length, self.d_model)
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
    ) -> None:
        super().__init__()
        self.variant = variant
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.position = nn.Parameter(torch.randn(max_length, d_model) * 0.02)
        self.norm1 = nn.ModuleList(nn.LayerNorm(d_model) for _ in range(num_layers))
        self.attention = nn.ModuleList(
            QuantumMultiheadAttention(d_model, num_heads, variant) for _ in range(num_layers)
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
