"""One bounded, fresh-pair analysis; never a training or final-test command."""
from __future__ import annotations

import argparse
import hashlib
import json
import signal
import sys
import time
from pathlib import Path

import torch

from execution.paired_behavior.analysis import (equal_map_summary, load_matched_support,
    paired_greedy, paired_states, state_summary, valid_route_sets)
from execution.paired_behavior.job import (_event, _frozen_abc, _storedproper,
    _storedroutes, _without_cache)
from execution.model_training_comparison.threeway_diagnosis_job import _exact_bank
from schrodinger import route_policy_experiment as accepted
from schrodinger.route_feasibility import signature
from schrodinger.route_policy import RoutePolicy
from schrodinger.route_policy_data import load_training, load_validation
from schrodinger.route_policy_evaluation import evaluate_proper, evaluate_rollouts
from schrodinger.route_policy_metrics import heldout_bank

from execution.seed_replication import train as replication_train


ROOT = replication_train.ROOT
UPDATES = (1000, 2000, 4000, 8000)
SUPPORT_SHA256 = "2bcde9c3823a41cc0a0ac7c4383ef1323658ca47b5b7a53336f4f4e2adf9babc"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict:
    return json.loads(path.read_text())


def _owner(seed: int, mode: str) -> str:
    return f"replication-{seed}-{mode}-8000"


def _manifest_file(owner: Path, relative: str) -> str:
    manifest = _read(owner / "output-manifest.json")
    path = owner / relative
    if not path.is_file() or manifest.get(relative, {}).get("sha256") != _sha(path):
        raise accepted.IdentityError("owner manifest hash mismatch")
    return _sha(path)


def _owner_authority(record: dict, *, seed: int, mode: str, ids: dict) -> dict:
    """Bind a consumed result to the reviewed wrapper and exact authorization."""
    decision_path = replication_train.HERE / "decisions" / f"{seed}-{mode}.json"
    decision = _read(decision_path)
    replication_train._validate_authorization(decision, seed=seed, mode=mode,
                                              prepared_sha256=ids["prepared_sha256"])
    wrapper = record.get("wrapper_provenance")
    resource = record.get("resource_provenance")
    wrapper_path = Path(replication_train.__file__).resolve()
    expected_argv = ["-m", "execution.seed_replication.train", "--seed", str(seed),
                     "--mode", mode, "--decision", str(decision_path.relative_to(replication_train.WORKSPACE))]
    if not isinstance(wrapper, dict) or wrapper != {**wrapper,
        "wrapper_path": str(wrapper_path), "wrapper_sha256": _sha(wrapper_path),
        "replication_plan_path": str(replication_train.PLAN.resolve()),
        "replication_plan_sha256": replication_train.PLAN_SHA256,
        "resource_limits": replication_train.REPLICATION_STAGES,
        "resource_limits_sha256": replication_train._json_sha256(replication_train.REPLICATION_STAGES)}:
        raise accepted.IdentityError("owner wrapper provenance mismatch")
    if not isinstance(resource, dict) or resource != {"original_limits": replication_train.ORIGINAL_STAGES,
        "installed_limits": replication_train.REPLICATION_STAGES,
        "resource_limits_sha256": replication_train._json_sha256(replication_train.REPLICATION_STAGES)}:
        raise accepted.IdentityError("owner resource provenance mismatch")
    if record.get("decision_sha256") != _sha(decision_path):
        raise accepted.IdentityError("owner decision hash mismatch")
    provenance = record.get("provenance", {})
    if provenance.get("source_hash") != ids["frozen_source_hash"] or provenance.get("prepared_sha256") != ids["prepared_sha256"]:
        raise accepted.IdentityError("owner accepted source/provenance mismatch")
    if wrapper.get("actual_argv", [])[1:] != expected_argv or provenance.get("argv") != wrapper.get("actual_argv"):
        raise accepted.IdentityError("owner command argv authorization mismatch")
    return {"decision_path": str(decision_path.resolve()), "decision_sha256": _sha(decision_path),
            "wrapper_sha256": _sha(wrapper_path), "plan_sha256": _sha(replication_train.PLAN),
            "resource_limits_sha256": replication_train._json_sha256(replication_train.REPLICATION_STAGES),
            "accepted_source_hash": provenance["source_hash"]}


def _owner_record(root: Path, seed: int, mode: str, ids: dict) -> tuple[Path, dict, dict, dict]:
    directory = root / _owner(seed, mode)
    if _read(directory / "attempt.json").get("status") != "COMPLETE":
        raise accepted.IdentityError("fresh owner is not terminal COMPLETE")
    _manifest_file(directory, "attempt.json")
    _manifest_file(directory, "result.json")
    record = _read(directory / "result.json")
    if record.get("input_ids") != ids or record.get("parameter_count", 0) <= 0:
        raise accepted.IdentityError("fresh owner input/provenance mismatch")
    return directory, record, record["result"], _owner_authority(record, seed=seed, mode=mode, ids=ids)


def _checkpoint(root: Path, seed: int, mode: str, ids: dict) -> tuple[dict, str, dict]:
    directory, record, result, authority = _owner_record(root, seed, mode, ids)
    relative = "checkpoints/update-8000.pt"
    digest = _manifest_file(directory, relative)
    payload = torch.load(directory / relative, weights_only=False)
    identity = payload.get("identity", {})
    expected = {"seed": seed, "mode": mode, "update": 8000,
                "source": ids["frozen_source_hash"], "config": accepted.FROZEN_CONFIG,
                "input_ids": ids, "initial_hash": result.get("initial_hash")}
    if any(identity.get(key) != value for key, value in expected.items()):
        raise accepted.IdentityError("fresh final checkpoint identity mismatch")
    initial_relative = "checkpoints/initial.pt"
    initial_digest = _manifest_file(directory, initial_relative)
    initial = torch.load(directory / initial_relative, weights_only=False)
    initial_identity = initial.get("identity", {})
    if initial_identity != {**expected, "update": 0, "parent_hash": None}:
        raise accepted.IdentityError("fresh initial checkpoint identity mismatch")
    if accepted.state_hash_from_state(initial["model"]) != identity["initial_hash"]:
        raise accepted.IdentityError("fresh initial state digest mismatch")
    if result.get("initial_checkpoint_hash") != initial_digest or result.get("final_checkpoint") != digest:
        raise accepted.IdentityError("fresh result/checkpoint digest mismatch")
    return payload, digest, {"initial": initial_digest, "final": digest, "identity": identity,
                             "shared_initial_digest": record.get("shared_initial_digest"),
                             "authority": authority, "_initial_state": initial["model"]}


def _curves(root: Path, seed: int, mode: str) -> list[dict]:
    directory = root / _owner(seed, mode)
    _manifest_file(directory, "checkpoints/curves.jsonl")
    rows = [json.loads(line) for line in (directory / "checkpoints/curves.jsonl").read_text().splitlines() if line]
    if len(rows) != 8000 or [row.get("update") for row in rows] != list(range(1, 8001)):
        raise accepted.IdentityError("fresh curve update sequence is not exact 1..8000")
    return rows


def validate_pair(root: Path, seed: int, ids: dict) -> dict:
    sm_payload, sm_hash, sm_identity = _checkpoint(root, seed, "softmax", ids)
    sa_payload, sa_hash, sa_identity = _checkpoint(root, seed, "schrodinger", ids)
    if not isinstance(sm_identity["shared_initial_digest"], str) or sm_identity["shared_initial_digest"] != sa_identity["shared_initial_digest"]:
        raise accepted.IdentityError("fresh pair shared initialization mismatch")
    shared = {key: value for key, value in sm_identity["_initial_state"].items()
              if key in sa_identity["_initial_state"]}
    if not shared or not all(torch.equal(value, sa_identity["_initial_state"][key]) for key, value in shared.items()):
        raise accepted.IdentityError("fresh pair shared initial tensors mismatch")
    observed_shared_digest = hashlib.sha256(b"".join(value.detach().cpu().numpy().tobytes()
                                                      for _, value in sorted(shared.items()))).hexdigest()
    if observed_shared_digest != sm_identity["shared_initial_digest"]:
        raise accepted.IdentityError("fresh pair shared initial digest mismatch")
    sm_rows, sa_rows = _curves(root, seed, "softmax"), _curves(root, seed, "schrodinger")
    if [row["batch_digest"] for row in sm_rows] != [row["batch_digest"] for row in sa_rows]:
        raise accepted.IdentityError("fresh pair batch prefix mismatch")
    digest = hashlib.sha256("".join(row["batch_digest"] for row in sm_rows).encode()).hexdigest()
    return {"sm_payload": sm_payload, "sa_payload": sa_payload,
            "checkpoint_hashes": {"sm": sm_hash, "sa": sa_hash},
            "checkpoint_identity": {"sm": sm_identity["identity"], "sa": sa_identity["identity"]},
            "initial_checkpoint_hashes": {"sm": sm_identity["initial"], "sa": sa_identity["initial"]},
            "owner_authority": {"sm": sm_identity["authority"], "sa": sa_identity["authority"]},
            "shared_initial_digest": sm_identity["shared_initial_digest"],
            "batch_prefix": {"updates": 8000, "digest_sha256": digest}}


def _model(payload: dict) -> RoutePolicy:
    model = RoutePolicy(payload["identity"]["mode"])
    model.load_state_dict(payload["model"])
    model.eval()
    return model


def _route_rows(model: RoutePolicy, problems: tuple, *, identity: tuple, seed: int, split: int, support: frozenset) -> dict:
    greedy = evaluate_rollouts(model, problems, identity=identity, seed=seed, splitcode=split,
                               replicate=0, greedy=True, k=1, support=support)
    k32 = evaluate_rollouts(model, problems, identity=identity, seed=seed, splitcode=split,
                            replicate=0, k=32, support=support)
    return {"greedy": _without_cache(greedy), "t1_k32": _without_cache(k32)}


def _abc_score(model: RoutePolicy, bank, problems: tuple, *, identity: tuple, seed: int, split: int, support: frozenset) -> dict:
    proper = evaluate_proper(model, bank, identity=identity)
    routes = _route_rows(model, problems, identity=identity, seed=seed, split=split, support=support)
    rows = []
    for candidate, probability in zip(proper["rows"], proper["arrays"]["p"]):
        rows.append({"canonical": candidate.canonical, "map_id": candidate.map_id, "family": candidate.family,
                     "goal": candidate.goal, "current": candidate.current, "q": candidate.q, "p": probability})
    return {"proper": _without_cache(proper), "proper_rows": rows,
            "greedy": routes["greedy"], "t1_k32": routes["t1_k32"],
            "problem_ids": [{"canonical": p.canonical.hex(), "map_id": p.map_id, "family": p.family,
                              "start": p.start, "goal": p.goal} for p in problems]}


def _abc_compare(sm: dict, sa: dict) -> dict:
    states = paired_states(sm["proper_rows"], sa["proper_rows"])
    summary = state_summary(states)
    sm_q, sa_q = sm["t1_k32"]["strata"]["routine"]["Q"], sa["t1_k32"]["strata"]["routine"]["Q"]
    return {"sm": sm, "sa": sa, "state": summary,
            "quality": {"sm": sm_q, "sa": sa_q, "sa_minus_sm": sa_q - sm_q}}


def _stored_summary(root: Path, seed: int, bank, problems: tuple, support: frozenset) -> dict:
    out = {}
    for update in UPDATES:
        sm_event = _event(root, _owner(seed, "softmax"), update)
        sa_event = _event(root, _owner(seed, "schrodinger"), update)
        sm_states, sm_proper = _storedproper(sm_event, bank)
        sa_states, sa_proper = _storedproper(sa_event, bank)
        sm_greedy, sm_g_raw = _storedroutes(sm_event, "greedy", problems)
        sa_greedy, sa_g_raw = _storedroutes(sa_event, "greedy", problems)
        sm_k32, sm_k_raw = _storedroutes(sm_event, "t1_k32", problems)
        sa_k32, sa_k_raw = _storedroutes(sa_event, "t1_k32", problems)
        item = {"proper": {"sm": sm_proper["weighted"], "sa": sa_proper["weighted"]},
                "proper_raw": {"sm": sm_proper, "sa": sa_proper},
                "t1": {"sm": sm_k_raw, "sa": sa_k_raw},
                "greedy": paired_greedy(sm_greedy, sa_greedy),
                "event_bindings": {"sm": sm_event["_binding"], "sa": sa_event["_binding"]}}
        if update == 8000:
            states = paired_states(sm_states, sa_states)
            routes = []
            for index, problem in enumerate(problems):
                routes.append({"family": problem.family, "map_id": problem.map_id,
                               **valid_route_sets(sm_k32[index * 32:(index + 1) * 32],
                                                  sa_k32[index * 32:(index + 1) * 32], support, signature)})
            metrics = tuple(key for key in routes[0] if key not in {"family", "map_id", "raw_sets"})
            item["paired_8000"] = {"states": state_summary(states), "route_sets": equal_map_summary(routes, metrics),
                                    "stored_routes": {"sm": sm_k_raw, "sa": sa_k_raw}}
            item["primary_delta_sa_minus_sm"] = sa_k_raw["mixture"]["Q"] - sm_k_raw["mixture"]["Q"]
        out[str(update)] = item
    return out


def _quality_control(sa: RoutePolicy, problems: tuple, *, identity: tuple, seed: int, support: frozenset,
                     sm_stored: dict, sa_stored: dict) -> dict:
    target = sm_stored["mixture"]["Q"]
    target_strata = {name: sm_stored["strata"][name]["Q"] for name in ("routine", "challenge")}
    grid = []
    for temperature, raw in ((1.0, sa_stored),
                             (0.75, evaluate_rollouts(sa, problems, identity=identity, seed=seed, splitcode=1,
                                                       replicate=0, k=32, support=support, temperature=0.75)),
                             (1.25, evaluate_rollouts(sa, problems, identity=identity, seed=seed, splitcode=1,
                                                       replicate=0, k=32, support=support, temperature=1.25))):
        clean = _without_cache(raw)
        grid.append({"temperature": temperature, "quality": clean["mixture"]["Q"],
                     "strata_quality": {name: clean["strata"][name]["Q"] for name in ("routine", "challenge")},
                     "raw": clean})
    selected = min(grid, key=lambda row: (abs(row["quality"] - target), row["temperature"]))
    matched = abs(selected["quality"] - target) <= .02 and all(
        abs(selected["strata_quality"][name] - target_strata[name]) <= .03 for name in target_strata)
    return {"target_sm_t1_quality": target, "target_sm_strata": target_strata, "grid": grid,
            "selected_temperature": selected["temperature"], "matched": matched}


def _compose_output(*, seed: int, ids: dict, pair: dict, stored: dict, abc: dict, qc: dict,
                    argv: list[str], elapsed_seconds: float) -> dict:
    helper_paths = (Path("execution/paired_behavior/analysis.py"), Path("execution/paired_behavior/job.py"),
                    Path("execution/model_training_comparison/threeway_diagnosis_job.py"))
    return {"status": "COMPLETE", "seed": seed, "input_ids": ids,
            "pair": {key: value for key, value in pair.items() if not key.endswith("payload")},
            "stored_fullvalidation": stored, "frozen_abc": abc, "quality_control": qc,
            "route_binding_limitation": "Historical route rows omit start/goal; immutable owner/dataset order binds them and the verifier corroborates validity, but cannot distinguish all-invalid permutations.",
            "source_hashes": {"execution/seed_replication/analyze.py": _sha(Path(__file__)),
                              "execution/seed_replication/train.py": _sha(Path(replication_train.__file__)),
                              "execution/seed_replication/plan.md": _sha(replication_train.PLAN),
                              **{str(path): _sha(path) for path in helper_paths}},
            "actual_argv": list(argv), "elapsed_seconds": elapsed_seconds}


def run(*, seed: int, root: Path = ROOT, argv: list[str] | None = None) -> dict:
    if seed not in replication_train.SEEDS:
        raise PermissionError("only frozen fresh seeds 1702--1705 are analyzable")
    root = Path(root)
    if root != ROOT:
        raise PermissionError("analysis root is fixed to the authoritative production root")
    replication_train.install_replication_resource_limits()
    accepted.configure_runtime()
    with accepted.OwnedAttempt.begin(root, root / "ledger.jsonl", "D", f"replication-{seed}-analysis") as attempt:
        signal.setitimer(signal.ITIMER_REAL, min(120.0, signal.getitimer(signal.ITIMER_REAL)[0]))
        started = time.perf_counter()
        _, ids = accepted._prepared_ids(root / "prepare-001" / "prepared.json")
        pair = validate_pair(root, seed, ids)
        training, validation = load_training(), load_validation()
        support = frozenset(training.support)
        bank = heldout_bank(validation.problems)
        stored = _stored_summary(root, seed, bank, validation.problems, support)
        sm, sa = _model(pair["sm_payload"]), _model(pair["sa_payload"])
        frozen_path = root / "threeway-diagnosis-001" / "matched_support.json"
        if _sha(frozen_path) != SUPPORT_SHA256:
            raise accepted.IdentityError("frozen ABC support hash mismatch")
        frozen = load_matched_support(frozen_path)
        abc_banks, abc_routes = _frozen_abc(frozen)
        abc = {}
        for index, name in enumerate("ABC"):
            split = 0 if name in "AB" else 1
            sm_score = _abc_score(sm, abc_banks[index], abc_routes[index], identity=(pair["checkpoint_hashes"]["sm"], "sm-abc", 8000), seed=seed, split=split, support=support)
            sa_score = _abc_score(sa, abc_banks[index], abc_routes[index], identity=(pair["checkpoint_hashes"]["sa"], "sa-abc", 8000), seed=seed, split=split, support=support)
            abc[name] = _abc_compare(sm_score, sa_score)
        qc = _quality_control(sa, validation.problems, identity=(pair["checkpoint_hashes"]["sa"], "sa-qc", 8000),
                              seed=seed, support=support, sm_stored=stored["8000"]["t1"]["sm"],
                              sa_stored=stored["8000"]["t1"]["sa"])
        output = _compose_output(seed=seed, ids=ids, pair=pair, stored=stored, abc=abc, qc=qc,
                                 argv=list(sys.argv if argv is None else argv), elapsed_seconds=time.perf_counter() - started)
        accepted._write_json(attempt.output / "analysis.json", output)
    complete = _read(attempt.output / "attempt.json")
    if complete.get("status") != "COMPLETE":
        raise accepted.ArtifactError("successful analysis attempt artifact missing")
    return output


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m execution.seed_replication.analyze")
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args(argv)
    result = run(seed=args.seed, argv=[sys.executable, "-m", "execution.seed_replication.analyze", *(sys.argv[1:] if argv is None else argv)])
    print(json.dumps({"status": result["status"], "output": str(ROOT / f"replication-{args.seed}-analysis")}, sort_keys=True))


if __name__ == "__main__":
    main()
