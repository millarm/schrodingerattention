"""RoutePolicy with a swappable attention computation (Stage 2).

The architecture, parameter creation order and forward pass mirror
``schrodinger.route_policy.RoutePolicy`` exactly; only the attention weight
computation comes from ``schrodinger.quantum_components``. ``route_policy.py``
itself is hash-pinned and is not modified. The ``softmax`` arm reproduces the
original softmax model given the same weights (see ``from_route_policy_state``).
"""

from __future__ import annotations

import torch
from torch import Tensor, nn

from schrodinger.quantum_components import QuantumMultiheadAttention

ARMS: tuple[str, ...] = ("softmax", "wick_linear", "wick_real")
DT_INIT = 0.25


class RoutePolicyVariant(nn.Module):
    """13-token route policy (CLS + 12 grid rows) with the attention arm ``mode``."""

    def __init__(self, mode: str = "softmax", dt_init: float = DT_INIT) -> None:
        if mode not in ARMS:
            raise ValueError(f"unknown arm {mode!r}")
        super().__init__()
        self.mode = mode
        # Same creation order as RoutePolicy, so a shared seed gives identical shared tensors.
        self.row = nn.Linear(36, 64)
        self.pos = nn.Parameter(torch.empty(12, 64))
        self.cls = nn.Parameter(torch.empty(1, 1, 64))
        nn.init.normal_(self.pos, std=0.02)
        nn.init.normal_(self.cls, std=0.02)
        self.norm1 = nn.ModuleList([nn.LayerNorm(64) for _ in range(2)])
        self.attn = nn.ModuleList([QuantumMultiheadAttention(64, 2, mode, dt_init) for _ in range(2)])
        self.norm2 = nn.ModuleList([nn.LayerNorm(64) for _ in range(2)])
        self.ff = nn.ModuleList([nn.Sequential(nn.Linear(64, 128), nn.GELU(), nn.Linear(128, 64)) for _ in range(2)])
        self.final = nn.LayerNorm(64)
        self.head = nn.Linear(64, 4)

    def forward(self, x: Tensor, dt_override: float | None = None, diagnostics: bool = False) -> Tensor:
        if diagnostics:
            raise NotImplementedError("route diagnostics are only defined for the original modules")
        override = None if self.mode == "softmax" else dt_override
        z = self.row(x) + self.pos
        z = torch.cat((self.cls.expand(x.shape[0], -1, -1), z), 1)
        for norm1, attention, norm2, feedforward in zip(self.norm1, self.attn, self.norm2, self.ff):
            z = z + attention(norm1(z), override)
            z = z + feedforward(norm2(z))
        return self.head(self.final(z)[:, 0])

    def evolution_times(self) -> list[list[float]]:
        if self.mode == "softmax":
            return []
        return [attention.effective_dt().detach().tolist() for attention in self.attn]


_ATTENTION_NAMES = {"q": "q_proj", "k": "k_proj", "v": "v_proj", "o": "out_proj"}


def translate_route_policy_state(state: dict[str, Tensor]) -> dict[str, Tensor]:
    """Map an original ``RoutePolicy('softmax')`` state dict onto the variant's names."""

    translated = {}
    for name, tensor in state.items():
        parts = name.split(".")
        if parts[0] == "attn" and parts[2] in _ATTENTION_NAMES:
            parts[2] = _ATTENTION_NAMES[parts[2]]
        translated[".".join(parts)] = tensor
    return translated


def paired_arms(seed: int, arms: tuple[str, ...] = ARMS, dt_init: float = DT_INIT) -> dict[str, RoutePolicyVariant]:
    """Build every arm from the same seed and check the shared tensors are identical."""

    models = {}
    for arm in arms:
        torch.manual_seed(seed)
        models[arm] = RoutePolicyVariant(arm, dt_init)
    reference = next(iter(models.values())).state_dict()
    for arm, model in models.items():
        for name, tensor in model.state_dict().items():
            if name in reference and not torch.equal(tensor, reference[name]):
                raise AssertionError(f"shared initialisation mismatch: {arm} {name}")
    return models
