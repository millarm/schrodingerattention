"""Stage 1 mechanism probes for the generic quantum attention components.

Synthetic, task-agnostic sequence classification problems. Every variant in
``schrodinger.quantum_components.VARIANTS`` is trained with the same seed,
initialisation and minibatch stream, so comparisons within a seed are paired.

Probes (vocabulary 0 = CLS, 1..6 = filler):
  parity  one bit token each from groups A, B (and C when --k 3), placed at
          random positions; label = XOR of the bits (signed pairwise).
  exclude three candidate bit tokens at random non-adjacent positions; two
          are vetoed by a V token placed immediately after them. Label = the
          bit of the one candidate that is not vetoed ("attend to a candidate
          unless it is vetoed"). Solving it needs token-to-token interaction.
  order   one A token and one B token at random positions; label = whether A
          comes first (direction-sensitive relation).

Usage:
  python execution/quantum_components/probes.py --probe parity --seeds 0 1 2 3 4 \
      --variants softmax c1 --out execution/quantum_components/results
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from torch import Tensor

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from schrodinger.quantum_components import ALL_VARIANTS, VARIANTS, ProbeEncoder  # noqa: E402

FILLER = 6
VOCAB = 1 + FILLER + 8


def sample(probe: str, batch: int, length: int, k: int, generator: torch.Generator) -> tuple[Tensor, Tensor]:
    tokens = torch.randint(1, 1 + FILLER, (batch, length), generator=generator)
    order = torch.argsort(torch.rand(batch, length, generator=generator), dim=1)
    rows = torch.arange(batch)
    bits = torch.randint(0, 2, (batch, 3), generator=generator)
    base = 1 + FILLER
    if probe == "parity":
        for group in range(k):
            tokens[rows, order[:, group]] = base + 2 * group + bits[:, group]
        labels = bits[:, :k].sum(1) % 2
    elif probe == "exclude":
        slots = torch.argsort(torch.rand(batch, length // 2, generator=generator), dim=1)[:, :3] * 2
        keep = torch.randint(0, 3, (batch,), generator=generator)
        for candidate in range(3):
            tokens[rows, slots[:, candidate]] = base + bits[:, candidate]
            vetoed = keep != candidate
            tokens[rows[vetoed], slots[vetoed, candidate] + 1] = base + 4
        labels = bits[rows, keep]
    elif probe == "order":
        tokens[rows, order[:, 0]] = base
        tokens[rows, order[:, 1]] = base + 2
        labels = (order[:, 0] < order[:, 1]).long()
    else:
        raise ValueError(f"unknown probe {probe!r}")
    cls = torch.zeros(batch, 1, dtype=torch.long)
    return torch.cat((cls, tokens), 1), labels


@torch.no_grad()
def evaluate(model: ProbeEncoder, tokens: Tensor, labels: Tensor) -> dict[str, float]:
    model.eval()
    logits = model(tokens)
    model.train()
    return {
        "accuracy": (logits.argmax(-1) == labels).float().mean().item(),
        "ce": torch.nn.functional.cross_entropy(logits, labels).item(),
    }


def run(args: argparse.Namespace, variant: str, seed: int) -> dict:
    torch.manual_seed(1000 + seed)
    model = ProbeEncoder(VOCAB, args.length + 1, 2, variant, args.d_model, args.heads, args.layers, args.dt_init)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    stream = torch.Generator().manual_seed(2000 + seed)
    held_out = sample(args.probe, args.eval_size, args.length, args.k, torch.Generator().manual_seed(99))
    curve, started = [], time.perf_counter()
    for step in range(1, args.steps + 1):
        tokens, labels = sample(args.probe, args.batch, args.length, args.k, stream)
        loss = torch.nn.functional.cross_entropy(model(tokens), labels)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        if step % args.eval_every == 0:
            point = {"step": step, **evaluate(model, *held_out)}
            if variant != "softmax":
                point["dt"] = [a.effective_dt().detach().tolist() for a in model.attention]
            if variant == "c3":
                point["lambda"] = [a.effective_lambda().detach().tolist() for a in model.attention]
            curve.append(point)
    window = [p for p in curve if p["step"] > args.steps // 2]
    return {
        "probe": args.probe, "variant": variant, "seed": seed, "k": args.k, "length": args.length,
        "steps": args.steps, "layers": args.layers, "d_model": args.d_model,
        "window_accuracy": sum(p["accuracy"] for p in window) / len(window),
        "window_ce": sum(p["ce"] for p in window) / len(window),
        "dt_init": args.dt_init, "final_accuracy": curve[-1]["accuracy"],
        "seconds": time.perf_counter() - started, "curve": curve,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", choices=("parity", "exclude", "order"), required=True)
    parser.add_argument("--variants", nargs="+", default=list(VARIANTS), choices=ALL_VARIANTS)
    parser.add_argument("--dt-init", type=float, default=0.05)
    parser.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2, 3, 4])
    parser.add_argument("--k", type=int, default=2)
    parser.add_argument("--length", type=int, default=16)
    parser.add_argument("--steps", type=int, default=3000)
    parser.add_argument("--batch", type=int, default=128)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--d-model", type=int, default=32)
    parser.add_argument("--heads", type=int, default=2)
    parser.add_argument("--layers", type=int, default=1)
    parser.add_argument("--eval-every", type=int, default=250)
    parser.add_argument("--eval-size", type=int, default=2048)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    args.out.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        for variant in args.variants:
            result = run(args, variant, seed)
            tag = "" if args.dt_init == 0.05 else f"-dt{args.dt_init:g}"
            name = f"{args.probe}-k{args.k}-L{args.length}{tag}-{variant}-s{seed}.json"
            (args.out / name).write_text(json.dumps(result, indent=1))
            print(f"{name}: window acc {result['window_accuracy']:.4f} ({result['seconds']:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
