"""Stage 2 runner: one attention arm on the pool-512 map benchmark.

Protocol and endpoints are fixed in ``stage2-spec.md``. This reuses the
repository's ``train_step``, ``evaluate_proper`` and ``evaluate_rollouts``
unchanged, verifies the regenerated training bank against its recorded hash
before training, and never loads the final-test split.

Usage:
  python execution/classical_leads/stage2_train.py --arm wick_linear \
      --seeds 3001 3002 --regen REGEN_DIR --out execution/classical_leads/stage2_results
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from schrodinger.route_policy_data import MapBalancedSampler, features, legal_mask, load_validation  # noqa: E402
from schrodinger.route_policy_evaluation import _state, evaluate_proper, evaluate_rollouts  # noqa: E402
from schrodinger.route_policy_experiment import (  # noqa: E402
    configure_runtime, optimizer, train_step, validation_probe_candidates,
)
from schrodinger.route_policy_metrics import heldout_bank, training_bank  # noqa: E402
from schrodinger.route_policy_variants import ARMS, paired_arms  # noqa: E402
from schrodinger.route_policy_experiment import bank_payload  # noqa: E402
from schrodinger.quantum_components import total_variation  # noqa: E402
from verify_training_bank import RECORDED, load_regenerated_training, regenerated_reads  # noqa: E402

PROPER_POINTS = tuple(range(0, 8001, 100))
ROLLOUT_POINTS = tuple(range(0, 3001, 200)) + tuple(range(4000, 8001, 1000))
MECHANISM_POINTS = (2000, 8000)
ARM_SCALARS = ("beta", "raw_dt")


def shared_digest(model) -> str:
    parts = [t.detach().numpy().tobytes() for name, t in sorted(model.state_dict().items())
             if not name.endswith(ARM_SCALARS)]
    return hashlib.sha256(b"".join(parts)).hexdigest()


def mechanism_readout(model, candidates) -> dict:
    """Attention TV from same-score softmax, and policy TV under dt = 0 (0 for softmax)."""
    states = [_state(c.canonical, c.map_id, c.family, c.current, c.goal) for c in candidates]
    x = torch.tensor(np.stack([features(s) for s in states]))
    mask = torch.tensor(np.stack([legal_mask(s) for s in states]))
    with torch.inference_mode():
        logits = model(x)
        attention_tv = [float(total_variation(a.last_weights, torch.softmax(a.last_scores, -1))) for a in model.attn]
        zero = model(x, dt_override=0.0)
    probs = torch.softmax(logits.masked_fill(~mask, float("-inf")), -1)
    probs0 = torch.softmax(zero.masked_fill(~mask, float("-inf")), -1)
    policy_tv = 0.5 * (probs - probs0).abs().sum(-1)
    return {"attention_tv_by_layer": attention_tv, "policy_tv_dt0_mean": float(policy_tv.mean()),
            "greedy_disagreement_dt0": float((probs.argmax(-1) != probs0.argmax(-1)).float().mean())}


def run(arm: str, seed: int, args, training, validation, bank, probe) -> dict:
    model = paired_arms(seed, (arm,))[arm]
    initial = shared_digest(model)
    opt = optimizer(model)
    sampler = MapBalancedSampler(training.states, seed)
    support = frozenset(training.support)
    chain = hashlib.sha256()
    core_seconds = 0.0
    proper, rollouts, mechanism = [], [], {}
    started = time.perf_counter()

    def evaluate(update: int) -> None:
        ident = (f"stage2-{arm}-{seed}", arm, update)
        if update in PROPER_POINTS:
            weighted = evaluate_proper(model, bank, identity=ident)["weighted"]
            proper.append({"update": update, "kl": weighted["kl"], "brier": weighted["brier"],
                           "core_seconds": core_seconds, "dt": model.evolution_times()})
        if update in ROLLOUT_POINTS:
            sampled = evaluate_rollouts(model, validation.problems, identity=ident, seed=seed, splitcode=1,
                                        k=32, support=support)["mixture"]
            greedy = evaluate_rollouts(model, validation.problems, identity=ident, seed=seed, splitcode=1,
                                       k=1, greedy=True, support=support)["mixture"]
            rollouts.append({"update": update, "Q": sampled["Q"], "pass_at_k": sampled["pass_at_k"],
                             "greedy_Q": greedy["Q"], "core_seconds": core_seconds})
        if update in MECHANISM_POINTS:
            mechanism[str(update)] = mechanism_readout(model, probe)

    evaluate(0)
    for update in range(1, args.updates + 1):
        step = train_step(model, opt, sampler)
        core_seconds += step["training_core_seconds"]
        chain.update(step["batch_digest"].encode())
        evaluate(update)
    return {
        "arm": arm, "seed": seed, "updates": args.updates, "dt_init": 0.25,
        "shared_initial_digest": initial, "batch_digest_chain": chain.hexdigest(),
        "training_core_seconds": core_seconds, "wall_seconds": time.perf_counter() - started,
        "proper": proper, "rollouts": rollouts, "mechanism": mechanism,
        "parameter_count": sum(p.numel() for p in model.parameters()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--regen", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--updates", type=int, default=8000)
    args = parser.parse_args()
    configure_runtime()
    training = load_regenerated_training(args.regen)
    selected = bank_payload(training_bank(training.states))["selected_hash"]
    if selected != RECORDED:
        raise SystemExit(f"training bank hash mismatch: {selected}")
    with regenerated_reads(args.regen):
        validation = load_validation()
    bank = heldout_bank(validation.problems)
    probe = validation_probe_candidates(bank)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    args.out.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        result = run(args.arm, seed, args, training, validation, bank, probe)
        result["provenance"] = {"training_selected_hash": selected, "git_commit": commit, "torch": torch.__version__,
                                "numpy": np.__version__, "python": platform.python_version(),
                                "threads": torch.get_num_threads(), "interop_threads": torch.get_num_interop_threads()}
        path = args.out / f"stage2-{args.arm}-s{seed}-u{args.updates}.json"
        path.write_text(json.dumps(result, indent=1))
        print(f"{path.name}: core {result['training_core_seconds']:.0f}s wall {result['wall_seconds']:.0f}s", flush=True)


if __name__ == "__main__":
    main()
