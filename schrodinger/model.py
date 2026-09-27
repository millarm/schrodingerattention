"""Small matched bidirectional encoder classifiers."""
from __future__ import annotations

import math
import torch
from torch import Tensor, nn

from .attention import MultiheadAttention
from .data import CLS, VOCAB_SIZE


class EncoderLayer(nn.Module):
    def __init__(self, mode: str) -> None:
        super().__init__()
        self.norm1 = nn.LayerNorm(32)
        self.attention = MultiheadAttention(32, 2, mode)
        self.norm2 = nn.LayerNorm(32)
        self.feedforward = nn.Sequential(nn.Linear(32, 64), nn.GELU(), nn.Linear(64, 32))

    def forward(self, x: Tensor, dt_override: float | None = None) -> Tensor:
        attended, self.last_diagnostics = self.attention(self.norm1(x), dt_override=dt_override, return_diagnostics=True)
        x = x + attended
        return x + self.feedforward(self.norm2(x))


class TinyClassifier(nn.Module):
    def __init__(self, mode: str) -> None:
        super().__init__()
        self.mode = mode
        self.token_embedding = nn.Embedding(VOCAB_SIZE, 32)
        self.layers = nn.ModuleList([EncoderLayer(mode), EncoderLayer(mode)])
        self.final_norm = nn.LayerNorm(32)
        self.classifier = nn.Linear(32, 2)

    @staticmethod
    def positional(length: int, device: torch.device, dtype: torch.dtype) -> Tensor:
        positions = torch.arange(length, device=device, dtype=dtype).unsqueeze(1)
        indexes = torch.arange(0, 32, 2, device=device, dtype=dtype)
        angles = positions * torch.exp(indexes * (-math.log(10000.0) / 32))
        output = torch.zeros(length, 32, device=device, dtype=dtype)
        output[:, 0::2], output[:, 1::2] = torch.sin(angles), torch.cos(angles)
        return output

    def forward(self, tokens: Tensor, dt_override: float | None = None) -> Tensor:
        x = self.token_embedding(tokens) + self.positional(tokens.shape[1], tokens.device, self.token_embedding.weight.dtype)
        for layer in self.layers:
            x = layer(x, dt_override)
        return self.classifier(self.final_norm(x[:, 0]))

    def evolution_parameters(self) -> tuple[Tensor, Tensor]:
        if self.mode != "schrodinger":
            return torch.empty(0), torch.empty(0)
        dt = torch.cat([layer.attention.effective_dt().detach() for layer in self.layers])
        gamma = torch.cat([layer.attention.effective_gamma().detach() for layer in self.layers])
        return dt, gamma

    def invariant_maxima(self) -> dict[str, float]:
        values = [layer.last_diagnostics for layer in self.layers if getattr(layer, "last_diagnostics", None) is not None]
        if not values:
            return {"hermiticity": 0.0, "unitarity": 0.0, "row": 0.0}
        return {"hermiticity": max(value.max_hermiticity_error for value in values), "unitarity": max(value.max_unitarity_error for value in values), "row": max(value.max_probability_row_error for value in values)}


def paired_models(seed: int) -> tuple[TinyClassifier, TinyClassifier]:
    torch.manual_seed(seed)
    baseline = TinyClassifier("softmax")
    experimental = TinyClassifier("schrodinger")
    experimental.load_state_dict({name: tensor for name, tensor in baseline.state_dict().items() if name in experimental.state_dict()}, strict=False)
    for name, tensor in baseline.state_dict().items():
        if not torch.equal(tensor, experimental.state_dict()[name]):
            raise AssertionError(f"paired initialization mismatch: {name}")
    return baseline, experimental
