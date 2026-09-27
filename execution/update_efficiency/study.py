"""One-owner, fixed-grid update-to-common-target study.

This module deliberately has no CLI.  ``command.py`` is the only external
launcher; it binds a reviewed decision to this narrow runner.
"""
from __future__ import annotations

import hashlib
import json
import math
import argparse
from contextlib import contextmanager
from pathlib import Path

import torch

from schrodinger import route_policy_experiment as accepted
from schrodinger.route_policy import RoutePolicy
from schrodinger.route_policy_data import MapBalancedSampler, load_training, load_validation
from schrodinger.route_policy_evaluation import evaluate_proper, evaluate_rollouts
from schrodinger.route_policy_metrics import heldout_bank, q_array_hash, record_hash, serialize_candidate

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
if WORKSPACE / "schrodinger" / "route_policy_experiment.py" != Path(accepted.__file__).resolve():
    raise RuntimeError("literal project-root assertion failed")
ROOT = WORKSPACE / "execution" / "model_training_comparison"
LEDGER = ROOT / "ledger.jsonl"
ATTEMPTS = HERE / "attempts"
PLAN = HERE / "plan-v3-saturation.md"
SPEC = HERE / "spec-03-saturation.md"
DECISIONS = HERE / "decisions.md"
PREPARE = ROOT / "prepare-001"
VALIDATION_OWNER = ROOT / "replication-1702-softmax-8000"
SEEDS = (2201, 2202)
MODES = ("softmax", "schrodinger")
GRID = (0, 1200, 2000, 2400, 3600, 4000, 4800, 6000, 8000, 10000, 12000, 14000, 16000)
UPDATES = 16000
Q_WINDOW_ENDS = (8000, 10000, 12000, 14000, 16000)
CE_WINDOW_ENDS = (8000, 10000, 12000, 14000, 16000)
ORIGINAL_STAGES = {"A": 700.0, "B": 2000.0, "C": 1900.0, "D": 1300.0}
STUDY_STAGES = {"A": 1000.0, "B": 4100.0, "C": 0.0, "D": 800.0}
PREPARE_HASHES = {
    "result.json": "ff19dcc1993184f80272f84d4507f881d88ad70486981695f45fe410c41b5ae7",
    "output-manifest.json": "00e2ae7422e2a512881e6ae69ece03ccc2a3a49296dd6eb6932987567270aa69",
    "attempt.json": "85de57355a8e86c5dc778f3ce9d0d0bb4adc0d6bcecaee75cbe32946f4057649",
}
VALIDATION_RESULT_SHA = "7ed636fc07bb20da3517bcf09635b6a50c5e272e8cfa6c402fd250bd2337557e"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(value) -> bytes:
    return json.dumps(accepted._serializable(value), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def source_hashes() -> dict[str, str]:
    from execution.update_efficiency.command import authority_hashes
    return authority_hashes()


def _read_json(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise accepted.IdentityError("object artifact required")
    return value


def manifest_bound_ids() -> dict:
    """Read only COMPLETE retained metadata; never open prepared/test payloads."""
    for name, expected in PREPARE_HASHES.items():
        if sha256(PREPARE / name) != expected:
            raise accepted.IdentityError("prepare owner hash mismatch")
    attempt = _read_json(PREPARE / "attempt.json")
    manifest = _read_json(PREPARE / "output-manifest.json")
    if attempt.get("status") != "COMPLETE":
        raise accepted.IdentityError("prepare owner incomplete")
    for name in ("result.json", "attempt.json"):
        if manifest.get(name, {}).get("sha256") != PREPARE_HASHES[name]:
            raise accepted.IdentityError("prepare manifest binding mismatch")
    result = _read_json(PREPARE / "result.json")
    provenance, banks = result.get("provenance"), result.get("bank_hashes")
    if not isinstance(provenance, dict) or not isinstance(banks, dict):
        raise accepted.IdentityError("prepare metadata schema mismatch")
    ids = {"prepared_sha256": result.get("prepared_sha256"),
           "training_selected_hash": banks.get("training"), "validation_selected_hash": banks.get("validation"),
           "test_selected_hash": banks.get("test"), "manifest_sha256": provenance.get("manifest_sha256"),
           "frozen_source_hash": provenance.get("source_hash")}
    if any(not isinstance(v, str) or len(v) != 64 for v in ids.values()):
        raise accepted.IdentityError("incomplete manifest-bound input IDs")
    return ids


def _row_identity(row: dict) -> tuple:
    return (row.get("canonical"), row.get("map_id"), row.get("family"), row.get("goal"), row.get("current"), tuple(row.get("q", ())))


def validation_bank(validation, ids: dict):
    """Rebuild only validation evidence and match the retained update-zero rows."""
    if sha256(VALIDATION_OWNER / "result.json") != VALIDATION_RESULT_SHA:
        raise accepted.IdentityError("retained validation owner hash mismatch")
    attempt = _read_json(VALIDATION_OWNER / "attempt.json")
    manifest = _read_json(VALIDATION_OWNER / "output-manifest.json")
    if attempt.get("status") != "COMPLETE" or manifest.get("result.json", {}).get("sha256") != VALIDATION_RESULT_SHA:
        raise accepted.IdentityError("retained validation owner incomplete")
    stored = _read_json(VALIDATION_OWNER / "result.json")
    if stored.get("input_ids") != ids:
        raise accepted.IdentityError("retained validation input identity mismatch")
    events = stored.get("result", {}).get("events", [])
    event = next((x for x in events if x.get("update") == 0), None)
    rows = None if event is None else event.get("proper", {}).get("rows")
    if not isinstance(rows, list):
        raise accepted.IdentityError("retained validation event-0 rows missing")
    bank = heldout_bank(validation.problems)
    rebuilt = [{"canonical": c.canonical.hex(), "map_id": c.map_id, "family": c.family,
                "goal": c.goal, "current": c.current, "q": list(c.q)} for c in bank.selected]
    if [_row_identity(x) for x in rows] != [_row_identity(x) for x in rebuilt]:
        raise accepted.IdentityError("validation q/order evidence mismatch")
    if bank.selected_hash != ids["validation_selected_hash"]:
        raise accepted.IdentityError("validation selected hash mismatch")
    return bank, {"selected_hash": bank.selected_hash, "candidate_hash": bank.candidate_hash,
                  "q_hash": q_array_hash(bank.selected), "record_hash": record_hash(bank.selected),
                  "rows": len(bank.selected)}


def _finite(value): return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def validate_scoring_points(points: list[dict]) -> dict[int, dict]:
    if [p.get("update") for p in points] != list(GRID): raise ValueError("exact v3 scoring grid required")
    out = {}
    for point in points:
        metrics = point.get("metrics", point)
        values = {key: metrics.get(key) for key in ("q", "kl", "brier", "teacher_entropy")}
        challenge = metrics.get("challenge_q")
        if not all(_finite(value) for value in values.values()) or not _finite(challenge): raise ValueError("finite Q/KL/Brier/teacher-entropy/challenge required")
        out[point["update"]] = values
    return out

def _suffix(windows: list[dict], key: str) -> dict:
    """Only computed low-gain equality gets numerical tolerance; values stay raw."""
    qualifying = [row[key] <= .005 + 1e-12 for row in windows]
    suffix = len(windows)
    while suffix and qualifying[suffix - 1]: suffix -= 1
    sustained = len(windows) - suffix >= 2
    temporary = [[windows[i]["update"], windows[i + 1]["update"]] for i in range(len(windows) - 1)
                 if qualifying[i] and qualifying[i + 1] and any(not item for item in qualifying[i + 2:])]
    return {"windows": windows, "qualifying": qualifying, "status": "SUSTAINED" if sustained else "RIGHT_CENSORED",
            "first_low_window": windows[suffix]["update"] if sustained else None,
            "confirmation_update": windows[suffix + 1]["update"] if sustained else None,
            "temporary_plateaus": temporary,
            "deterioration_updates": [row["update"] for row in windows if row[key] < 0]}

def q_plateau(points: list[dict]) -> dict:
    values = validate_scoring_points(points); windows = []
    means = {u: (values[u - 4000]["q"] + values[u - 2000]["q"] + values[u]["q"]) / 3 for u in range(4000, UPDATES + 1, 2000)}
    for u in Q_WINDOW_ENDS: windows.append({"update": u, "mean_q": means[u], "gain": means[u] - means[u - 4000]})
    return _suffix(windows, "gain")

def ce_plateau(curve: list[dict]) -> dict:
    if [row.get("update") for row in curve] != list(range(1, UPDATES + 1)): raise ValueError("exact 1..16000 CE identities required")
    values = [row.get("ce") for row in curve]
    if not all(_finite(value) for value in values): raise ValueError("finite CE required")
    blocks = [{"end_update": end, "mean_ce": sum(values[end - 100:end]) / 100} for end in range(100, UPDATES + 1, 100)]
    means = {u: sum(values[u - 2000:u]) / 2000 for u in range(2000, UPDATES + 1, 2000)}; windows = []
    for u in CE_WINDOW_ENDS:
        denominator = means[u - 2000]
        if not _finite(denominator) or denominator <= 0: raise ValueError("positive finite CE denominator required")
        windows.append({"update": u, "mean_ce": means[u], "relative_improvement": (denominator - means[u]) / denominator})
    result = _suffix(windows, "relative_improvement"); result["blocks"] = blocks; result["two_k_means"] = means; return result

def quality_milestone(points: list[dict], threshold: float) -> dict:
    values = validate_scoring_points(points); passing = [u for u in GRID if values[u]["q"] >= threshold]; anomaly = GRID[0] in passing
    for i in range(1, len(GRID) - 1):
        if GRID[i] in passing and GRID[i + 1] in passing:
            return {"status": "ACQUIRED", "update": GRID[i], "confirmation_update": GRID[i + 1], "confirmation_lag": GRID[i + 1] - GRID[i], "interval": [GRID[i - 1], GRID[i]], "initial_pass_anomaly": anomaly, "passing_updates": passing}
    return {"status": "RIGHT_CENSORED" if GRID[-1] not in passing else "FINAL_UNCONFIRMED", "update": None, "confirmation_update": None, "confirmation_lag": None, "interval": None, "initial_pass_anomaly": anomaly, "passing_updates": passing}

def milestones(points: list[dict]) -> dict:
    return {"tolerant_30": quality_milestone(points, .29), "tolerant_38198": quality_milestone(points, .37198), "exact_30": quality_milestone(points, .30), "exact_38198": quality_milestone(points, .38198)}

def milestone_comparison(softmax: dict, schrodinger: dict) -> dict:
    if softmax.get("status") != "ACQUIRED" or schrodinger.get("status") != "ACQUIRED" or softmax.get("initial_pass_anomaly") or schrodinger.get("initial_pass_anomaly"):
        return {"status": "CENSORED", "sa_minus_sm_updates": None, "sa_over_sm_grid_ratio": None, "sa_over_sm_bounds": None}
    ls, us = softmax["interval"]; la, ua = schrodinger["interval"]
    unbounded = ls == 0
    return {"status": "OBSERVED", "sa_minus_sm_updates": schrodinger["update"] - softmax["update"],
            "sa_over_sm_grid_ratio": schrodinger["update"] / softmax["update"],
            "sa_over_sm_bounds": [la / us, math.inf if unbounded else ua / ls], "upper_unbounded": unbounded}

def fragility_flags(points: list[dict]) -> list[int]:
    values = validate_scoring_points(points); flagged = []
    for point in points:
        challenge = point.get("metrics", point).get("challenge_q")
        if (_finite(challenge) and challenge < .08) or values[point["update"]]["kl"] > .40: flagged.append(point["update"])
    return flagged

def early_contrast(softmax_points: list[dict], schrodinger_points: list[dict]) -> float:
    sm, sa = validate_scoring_points(softmax_points), validate_scoring_points(schrodinger_points)
    delta = lambda update: sa[update]["q"] - sm[update]["q"]
    return 100 * (delta(3600) - (delta(1200) + delta(6000)) / 2)

def _hash(value) -> bool: return isinstance(value, str) and len(value) == 64

def _owner_identity(owner: dict) -> None:
    if not isinstance(owner, dict) or not _hash(owner.get("config_hash")) or not isinstance(owner.get("input_ids"), dict) or not isinstance(owner.get("source_hashes"), dict): raise ValueError("actual owner identity required")
    if not owner["source_hashes"] or any(not isinstance(k, str) or not _hash(v) for k, v in owner["source_hashes"].items()): raise ValueError("source hash identity required")
    required_ids={"prepared_sha256", "training_selected_hash", "validation_selected_hash", "test_selected_hash", "manifest_sha256", "frozen_source_hash"}
    if set(owner["input_ids"]) != required_ids or any(not _hash(v) for v in owner["input_ids"].values()): raise ValueError("input identity required")
    bank = owner.get("bank")
    if not isinstance(bank, dict) or any(not _hash(bank.get(key)) for key in ("selected_hash", "candidate_hash", "q_hash", "record_hash")) or not isinstance(bank.get("rows"), int) or bank["rows"] <= 0: raise ValueError("bank identity required")
    summary = owner.get("summary")
    if not isinstance(summary, dict) or not _hash(summary.get("training_support_hash")): raise ValueError("training support identity required")

def validate_pair_identity(seed: int, softmax: dict, schrodinger: dict) -> None:
    if seed not in SEEDS or softmax.get("seed") != seed or schrodinger.get("seed") != seed or softmax.get("mode") != "softmax" or schrodinger.get("mode") != "schrodinger": raise ValueError("seed/mode identity mismatch")
    _owner_identity(softmax); _owner_identity(schrodinger)
    for key in ("shared_initial_digest", "config_hash", "input_ids", "source_hashes", "bank"):
        if softmax.get(key) != schrodinger.get(key): raise ValueError("paired identity mismatch")
    if not _hash(softmax.get("shared_initial_digest")): raise ValueError("shared initial digest required")
    if softmax["summary"]["training_support_hash"] != schrodinger["summary"]["training_support_hash"]: raise ValueError("paired support mismatch")
    left, right = softmax.get("batch_digests"), schrodinger.get("batch_digests")
    if not isinstance(left, list) or left != right or len(left) != UPDATES or any(not _hash(x) for x in left): raise ValueError("full paired batch prefix required")

def _pair_scores(owner: dict, scores: list[dict]) -> list[dict]:
    if not isinstance(scores, list) or [row.get("update") for row in scores] != list(GRID): raise ValueError("actual score endpoint grid required")
    compact = owner.get("points", [])
    if [row.get("update") for row in compact] != list(GRID) or any(row.get("score_sha256") != hashlib.sha256(canonical(score)).hexdigest() for row, score in zip(compact, scores)): raise ValueError("owner compact endpoint binding required")
    validate_scoring_points(scores)
    return scores

def aggregate_all(pairs: list[dict]) -> dict:
    """Pure two-owner result contract; score rows are the owned endpoint payloads."""
    if [pair.get("seed") for pair in pairs] != list(SEEDS): raise ValueError("exact ordered two-seed summary required")
    contrasts=[]; stage_rows=[]; milestone_rows={name: [] for name in ("tolerant_30", "tolerant_38198", "exact_30", "exact_38198")}; retained=[]; per_seed=[]
    for pair in pairs:
        seed=pair["seed"]; sm_bundle, sa_bundle = pair.get("softmax"), pair.get("schrodinger")
        if not isinstance(sm_bundle, dict) or not isinstance(sa_bundle, dict): raise ValueError("actual pair owner bundles required")
        sm, sa = sm_bundle.get("owner"), sa_bundle.get("owner")
        validate_pair_identity(seed, sm, sa); sm_scores=_pair_scores(sm, sm_bundle.get("scores")); sa_scores=_pair_scores(sa, sa_bundle.get("scores"))
        contrast=early_contrast(sm_scores, sa_scores); contrasts.append(contrast)
        sm_milestones, sa_milestones=milestones(sm_scores), milestones(sa_scores)
        comparison={name:milestone_comparison(sm_milestones[name], sa_milestones[name]) for name in milestone_rows}
        for name, row in comparison.items(): milestone_rows[name].append({"seed":seed, **row})
        sm_values, sa_values=validate_scoring_points(sm_scores), validate_scoring_points(sa_scores); gaps=[]
        for index, update in enumerate(GRID):
            gaps.append({"update":update,"q_gap":sa_values[update]["q"]-sm_values[update]["q"],"kl_gap":sa_values[update]["kl"]-sm_values[update]["kl"],"challenge_q_gap":sa_scores[index]["metrics"]["challenge_q"]-sm_scores[index]["metrics"]["challenge_q"]})
        per_seed.append({"seed":seed,"contrast_pp":contrast,"gaps":gaps,"milestones":{"softmax":sm_milestones,"schrodinger":sa_milestones,"comparison":comparison}}); retained.append(pair)
    for index, update in enumerate(GRID):
        rows=[item["gaps"][index] for item in per_seed]; mean_q=sum(row["q_gap"] for row in rows)/2; mean_kl=sum(row["kl_gap"] for row in rows)/2; mean_challenge=sum(row["challenge_q_gap"] for row in rows)/2
        stage_rows.append({"update":update,"per_seed":rows,"mean_q_gap":mean_q,"mean_kl_gap":mean_kl,"mean_challenge_q_gap":mean_challenge,"mixed":mean_q > 0 and (mean_kl > .02 + 1e-12 or mean_challenge < -.02 - 1e-12)})
    mean=sum(contrasts)/2; same_sign=(contrasts[0] > 0 and contrasts[1] > 0) or (contrasts[0] < 0 and contrasts[1] < 0)
    return {"pairs":retained,"per_seed":per_seed,"contrast_pp":{"values":contrasts,"mean":mean,"range":[min(contrasts),max(contrasts)],"material":abs(mean)>=1.,"same_sign":same_sign,"screen":abs(mean)>=1. and same_sign},"stagewise":stage_rows,"milestone_comparisons":milestone_rows,"inference":"descriptive_two_seed_no_df3"}


@contextmanager
def scoped_stages():
    if accepted.STAGES != ORIGINAL_STAGES or accepted.GLOBAL_CAP != 7200.0 or accepted.CARRY != 923.003597253:
        raise accepted.BudgetError("accepted resource table changed")
    prior = dict(accepted.STAGES)
    accepted.STAGES.clear(); accepted.STAGES.update(STUDY_STAGES)
    try:
        yield
    finally:
        accepted.STAGES.clear(); accepted.STAGES.update(prior)


def _checkpoint(path: Path, *, seed: int, mode: str, update: int, ids: dict, initial_hash: str, source: str, parent: str | None) -> tuple[dict, str]:
    digest = sha256(path)
    payload = torch.load(path, weights_only=False)
    identity = payload.get("identity")
    expected = {"seed": seed, "mode": mode, "source": source, "config": accepted.FROZEN_CONFIG,
                "initial_hash": initial_hash, "input_ids": ids, "update": update, "parent_hash": parent}
    if not isinstance(identity, dict) or any(identity.get(k) != v for k, v in expected.items()):
        raise accepted.IdentityError("checkpoint identity mismatch")
    if update and (not isinstance(identity["parent_hash"], str) or len(identity["parent_hash"]) != 64):
        raise accepted.IdentityError("checkpoint parent mismatch")
    return payload, digest


def _atomic(path: Path, value: dict) -> None:
    if path.exists():
        raise FileExistsError(path)
    path.write_bytes(canonical(value)); path.open("rb").close()


def _score_metrics(proper: dict, rollout: dict) -> dict:
    weighted, mixture, strata = proper["weighted"], rollout["mixture"], rollout["strata"]
    return {"q": mixture["Q"], "challenge_q": strata["challenge"]["Q"], "kl": weighted["kl"],
            "brier": weighted["brier"], "teacher_entropy": weighted["entropy_q"], "policy_entropy": weighted["entropy_p"]}

def run(*, seed: int, mode: str, decision: dict, updates: int = UPDATES, grid: tuple[int, ...] = GRID, _test_schedule: tuple[int, tuple[int, ...]] | None = None) -> dict:
    """One v3 owner: train once, then restore and score exactly the frozen grid."""
    if _test_schedule is None:
        if seed not in SEEDS or mode not in MODES or updates != UPDATES or tuple(grid) != GRID: raise PermissionError("only frozen v3 owner is authorized")
    else:
        updates, grid = _test_schedule
        if updates <= 0 or tuple(grid) != (0, updates): raise ValueError("test schedule is exact two-endpoint only")
    if decision.get("seed") != seed or decision.get("mode") != mode or decision.get("updates") != (UPDATES if _test_schedule is None else updates): raise PermissionError("decision does not bind owner")
    if decision.get("approved") is not True or decision.get("hashes") != source_hashes() or decision.get("plan_sha256") != sha256(PLAN) or decision.get("spec_sha256") != sha256(SPEC): raise PermissionError("decision source/plan binding mismatch")
    name = f"update-efficiency-{seed}-{mode}-{updates}"
    if (ROOT / "experiment.lock").exists() or (ATTEMPTS / "experiment.lock").exists() or (ATTEMPTS / name).exists(): raise RuntimeError("fresh owner/lock required")
    with scoped_stages(), accepted.OwnedAttempt.begin(ATTEMPTS, LEDGER, "B", name) as attempt:
        ids = manifest_bound_ids()
        if decision.get("input_ids") != ids or decision.get("config_hash") != accepted.config_hash(): raise PermissionError("decision input/config binding mismatch")
        accepted.configure_runtime(); training, validation = load_training(), load_validation(); bank, bank_identity = validation_bank(validation, ids)
        softmax, schrodinger, shared = accepted.paired_models(seed); model = softmax if mode == "softmax" else schrodinger
        trained = accepted.scheduled_training(model, accepted.optimizer(model), MapBalancedSampler(training.states, seed), seed=seed, source=ids["frozen_source_hash"], config=accepted.FROZEN_CONFIG, input_ids=ids, checkpoint_dir=attempt.output / "checkpoints", updates=updates, validation=None, decision={"approved": True, "kind": "main"})
        curves = trained["curves"]
        if [row["update"] for row in curves] != list(range(1, updates + 1)): raise accepted.IdentityError("full CE/batch curve required")
        expected_parent = {0: None}; checkpoints = {0: Path(trained["initial_checkpoint_path"])}
        _, initial_digest = _checkpoint(checkpoints[0], seed=seed, mode=mode, update=0, ids=ids, initial_hash=trained["initial_hash"], source=ids["frozen_source_hash"], parent=None)
        if initial_digest != trained["initial_checkpoint_hash"]: raise accepted.IdentityError("initial checkpoint digest mismatch")
        previous = initial_digest
        interval = accepted.CHECKPOINT_INTERVAL
        saved_updates = tuple(range(interval, updates + 1, interval)) + (() if updates % interval == 0 else (updates,))
        for update in saved_updates:
            path = attempt.output / "checkpoints" / f"update-{update}.pt"; checkpoints[update] = path
            expected_parent[update] = previous
            _, digest = _checkpoint(path, seed=seed, mode=mode, update=update, ids=ids, initial_hash=trained["initial_hash"], source=ids["frozen_source_hash"], parent=previous)
            if update == updates and digest != trained["final_checkpoint"]: raise accepted.IdentityError("final checkpoint digest mismatch")
            previous = digest
        points = []
        for update in grid:
            if update not in checkpoints: raise accepted.IdentityError("scoring update has no saved checkpoint")
            path = checkpoints[update]; payload, digest = _checkpoint(path, seed=seed, mode=mode, update=update, ids=ids, initial_hash=trained["initial_hash"], source=ids["frozen_source_hash"], parent=expected_parent[update])
            restored = RoutePolicy(mode); restored.load_state_dict(payload["model"]); restored.eval(); identity = (digest, mode, "update-efficiency-v3")
            proper = evaluate_proper(restored, bank, identity=identity); rollout = evaluate_rollouts(restored, validation.problems, identity=identity, seed=seed, splitcode=1, replicate=0, k=32, temperature=1., support=frozenset(training.support))
            row = {"update": update, "checkpoint_sha256": digest, "checkpoint_identity": payload["identity"], "metrics": _score_metrics(proper, rollout), "proper": accepted._serializable({k:v for k,v in proper.items() if k != "cache"}), "rollout": accepted._serializable({k:v for k,v in rollout.items() if k != "cache"})}
            _atomic(attempt.output / f"score-{update}.json", row); points.append(row)
        training_record = {**trained, "final_checkpoint_hash": trained["final_checkpoint"]}; result = {"status":"COMPLETE","seed":seed,"mode":mode,"input_ids":ids,"config_hash":accepted.config_hash(),"source_hashes":source_hashes(),"shared_initial_digest":shared,"batch_digests":[row["batch_digest"] for row in curves],"bank":bank_identity,"summary":{"training_support_hash":training.support_hash},"training":training_record,"points":[{"update":row["update"],"score_path":f"score-{row['update']}.json","score_sha256":sha256(attempt.output/f"score-{row['update']}.json")} for row in points]}
        if _test_schedule is None:
            validate_scoring_points(points)
            result["summary"].update({"q_plateau":q_plateau(points),"ce_plateau":ce_plateau(curves),"milestones":milestones(points),"fragility_flags":fragility_flags(points)})
        _atomic(attempt.output / "result.json", result); _atomic(attempt.output / "index.json", {"status":"COMPLETE","result_sha256":sha256(attempt.output/"result.json"),"scores":result["points"],"bank":bank_identity}); return result


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="python -m execution.update_efficiency.study")
    parser.add_argument("--decision", type=Path, required=True)
    args = parser.parse_args(argv)
    decision = _read_json(args.decision)
    output = run(seed=decision.get("seed"), mode=decision.get("mode"), decision=decision)
    print(json.dumps({"status": output["status"], "seed": output["seed"], "mode": output["mode"]}, sort_keys=True))


if __name__ == "__main__":
    main()
