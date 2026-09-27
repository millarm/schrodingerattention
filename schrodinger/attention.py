"""Exact and conventional attention primitives for the bounded reference run."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

import torch
from torch import Tensor, nn


AttentionMode = Literal["softmax", "schrodinger"]


@dataclass(frozen=True)
class AttentionDiagnostics:
    """Detached numerical values suitable for logging without graph retention."""

    max_hermiticity_error: float
    max_unitarity_error: float
    max_probability_row_error: float
    effective_dt: Tensor | None = None
    effective_gamma: Tensor | None = None


def _complex_dtype(real_dtype: torch.dtype) -> torch.dtype:
    if real_dtype == torch.float64:
        return torch.complex128
    if real_dtype == torch.float32:
        return torch.complex64
    raise TypeError(f"attention scores must be float32 or float64, got {real_dtype}")


def _diagnostics(h: Tensor, u: Tensor, probabilities: Tensor) -> AttentionDiagnostics:
    size = h.shape[-1]
    identity = torch.eye(size, dtype=u.dtype, device=u.device)
    hermitian_error = (h - h.conj().transpose(-2, -1)).abs().amax().detach().item()
    unitarity_error = (
        u.conj().transpose(-2, -1) @ u - identity
    ).abs().amax().detach().item()
    row_error = (probabilities.sum(dim=-1) - 1).abs().amax().detach().item()
    return AttentionDiagnostics(hermitian_error, unitarity_error, row_error)


def attention_from_scores(
    scores: Tensor,
    values: Tensor,
    phase: Tensor | None = None,
    dt: Tensor | float = 0.0,
    mode: AttentionMode = "softmax",
    *,
    return_diagnostics: bool = False,
) -> tuple[Tensor, Tensor] | tuple[Tensor, Tensor, AttentionDiagnostics | None]:
    """Apply attention to pre-projected tensors.

    ``scores`` has shape ``[batch, heads, length, length]`` and ``values`` has
    shape ``[batch, heads, length, head_dim]``. In exact mode each query row is
    a key-amplitude state, so evolution is deliberately ``psi0 @ U.T``.
    """

    if scores.ndim != 4 or values.ndim != 4:
        raise ValueError("scores and values must both be rank-4 tensors")
    if scores.shape[:3] != values.shape[:3] or scores.shape[-1] != values.shape[-2]:
        raise ValueError("incompatible score and value shapes")
    if mode not in ("softmax", "schrodinger"):
        raise ValueError(f"unknown attention mode {mode!r}")

    probabilities = torch.softmax(scores, dim=-1)
    if mode == "softmax":
        output = probabilities @ values
        if return_diagnostics:
            return output, probabilities, None
        return output, probabilities

    if phase is None:
        phase = torch.zeros_like(scores)
    if phase.shape != scores.shape:
        raise ValueError("phase must match scores exactly")

    length = scores.shape[-1]
    complex_dtype = _complex_dtype(scores.dtype)
    hamiltonian = 0.5 * (scores + scores.transpose(-2, -1)) / math.sqrt(length)
    hamiltonian = hamiltonian.to(complex_dtype)
    dt_tensor = torch.as_tensor(dt, dtype=scores.dtype, device=scores.device)
    unitary = torch.matrix_exp((-1j * dt_tensor * hamiltonian).to(complex_dtype))
    psi0 = torch.sqrt(probabilities).to(complex_dtype) * torch.exp((1j * phase).to(complex_dtype))
    psi1 = psi0 @ unitary.transpose(-2, -1)
    born_probabilities = psi1.abs().square()
    output = born_probabilities @ values
    if return_diagnostics:
        return output, born_probabilities, _diagnostics(hamiltonian, unitary, born_probabilities)
    return output, born_probabilities


class MultiheadAttention(nn.Module):
    """Matched conventional or exact multihead self-attention reference module."""

    def __init__(self, d_model: int, num_heads: int, mode: AttentionMode = "softmax") -> None:
        super().__init__()
        if d_model <= 0 or num_heads <= 0 or d_model % num_heads:
            raise ValueError("d_model must be positive and divisible by num_heads")
        if mode not in ("softmax", "schrodinger"):
            raise ValueError(f"unknown attention mode {mode!r}")
        self.d_model = d_model
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.mode = mode
        self.q_proj = nn.Linear(d_model, d_model, bias=True)
        self.k_proj = nn.Linear(d_model, d_model, bias=True)
        self.v_proj = nn.Linear(d_model, d_model, bias=True)
        self.out_proj = nn.Linear(d_model, d_model, bias=True)
        if mode == "schrodinger":
            raw_dt = math.log(0.1 / 0.9)
            raw_gamma = math.atanh(0.1 / math.pi)
            self.raw_dt = nn.Parameter(torch.full((num_heads,), raw_dt))
            self.raw_gamma = nn.Parameter(torch.full((num_heads,), raw_gamma))

    def effective_dt(self) -> Tensor:
        if self.mode != "schrodinger":
            raise RuntimeError("softmax attention has no evolution-time parameter")
        return 0.5 * torch.sigmoid(self.raw_dt)

    def effective_gamma(self) -> Tensor:
        if self.mode != "schrodinger":
            raise RuntimeError("softmax attention has no phase parameter")
        return math.pi * torch.tanh(self.raw_gamma)

    def forward(
        self,
        inputs: Tensor,
        *,
        dt_override: float | Tensor | None = None,
        return_diagnostics: bool = False,
    ) -> Tensor | tuple[Tensor, AttentionDiagnostics | None]:
        if inputs.ndim != 3 or inputs.shape[-1] != self.d_model:
            raise ValueError("inputs must have shape [batch, length, d_model]")
        batch, length, _ = inputs.shape
        def split_heads(projected: Tensor) -> Tensor:
            return projected.reshape(batch, length, self.num_heads, self.head_dim).transpose(1, 2)

        q, k, v = (split_heads(layer(inputs)) for layer in (self.q_proj, self.k_proj, self.v_proj))
        scores = q @ k.transpose(-2, -1) / math.sqrt(self.head_dim)
        diagnostics: AttentionDiagnostics | None = None
        if self.mode == "softmax":
            attended, _ = attention_from_scores(scores, v, mode="softmax")
        else:
            gamma = self.effective_gamma().reshape(1, self.num_heads, 1, 1)
            evolution_time: Tensor | float = (
                self.effective_dt().reshape(1, self.num_heads, 1, 1)
                if dt_override is None
                else dt_override
            )
            result = attention_from_scores(
                scores,
                v,
                phase=gamma * scores,
                dt=evolution_time,
                mode="schrodinger",
                return_diagnostics=return_diagnostics,
            )
            if return_diagnostics:
                attended, _, diagnostics = result
                diagnostics = AttentionDiagnostics(
                    diagnostics.max_hermiticity_error,
                    diagnostics.max_unitarity_error,
                    diagnostics.max_probability_row_error,
                    self.effective_dt().detach().clone(),
                    self.effective_gamma().detach().clone(),
                )
            else:
                attended, _ = result
        output = attended.transpose(1, 2).reshape(batch, length, self.d_model)
        output = self.out_proj(output)
        if return_diagnostics:
            return output, diagnostics
        return output
