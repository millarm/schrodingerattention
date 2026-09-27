"""Inference-only dense scoring of immutable early checkpoints.

Neural dependencies are imported only after the external driver session has
been authenticated. This module never trains, constructs an optimizer, or
opens the final-test panel.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[1]
INVENTORY = HERE / "inventory.json"
OLD = WORKSPACE / "execution" / "update_efficiency" / "attempts"
LEDGER = HERE / "ledger.jsonl"
ATTEMPTS = HERE / "attempts"
UPDATES = tuple(range(0, 3001, 100))
REUSED = (0, 1200, 2000, 2400)
PROBE_UPDATES = (0, 500, 1000, 1500, 2000, 2500, 3000)
SEEDS = (2201, 2202)
MODES = ("softmax", "schrodinger")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read(path: Path) -> dict:
    value = json.loads(Path(path).read_text())
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value


def _durable(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + "." + str(os.getpid()))
    raw = json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)


def _identity(row: dict) -> tuple:
    return (row.get("canonical"), row.get("map_id"), row.get("family"),
            row.get("goal"), row.get("current"), tuple(row.get("q", ())))


def _stable_id(row: dict) -> tuple:
    return (row.get("canonical"), row.get("map_id"), row.get("family"),
            row.get("goal"), row.get("current"))


def _finite(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _argmax_legal(probabilities: list[float], legal_mask: list[bool]) -> int:
    if len(probabilities) != 4 or len(legal_mask) != 4 or not any(legal_mask):
        raise ValueError("four legal action probabilities/mask required")
    if any(not _finite(value) or value < 0 for value in probabilities):
        raise ValueError("invalid action probabilities")
    if abs(sum(probabilities) - 1.0) > 1e-10:
        raise ValueError("action probabilities are not normalized")
    legal = [i for i, value in enumerate(legal_mask) if value]
    return max(legal, key=lambda action: probabilities[action])


def statewise_metadata(bank_rows: list[dict], legal_masks: list[list[bool]]) -> list[dict]:
    """Bind stable state identities, accepted legal masks, and fixed weights."""
    if len(bank_rows) != len(legal_masks) or not bank_rows:
        raise ValueError("nonempty aligned state/legal bank required")
    normalized = []
    seen = set()
    maps_by_stratum: dict[str, set[int]] = {"routine": set(), "challenge": set()}
    states_per_map: dict[tuple[str, int], int] = {}
    for row, mask in zip(bank_rows, legal_masks):
        ident = _stable_id(row)
        if ident in seen:
            raise ValueError("duplicate state identity")
        seen.add(ident)
        q = list(row.get("q", ()))
        if len(q) != 4 or any(not _finite(v) or v < 0 for v in q) or abs(sum(q) - 1.0) > 1e-10:
            raise ValueError("invalid oracle distribution")
        if len(mask) != 4 or any(type(v) is not bool for v in mask):
            raise ValueError("invalid legal action mask")
        if any(q[i] > 0 and not mask[i] for i in range(4)):
            raise ValueError("oracle support is not legal")
        stratum = "challenge" if row["family"] == "IIIILLLL" else "routine"
        map_id = row["map_id"]
        maps_by_stratum[stratum].add(map_id)
        states_per_map[(stratum, map_id)] = states_per_map.get((stratum, map_id), 0) + 1
        normalized.append({"id": {"canonical": row["canonical"], "map_id": map_id,
                    "family": row["family"], "goal": row["goal"], "current": row["current"]},
            "q": q, "legal_mask": mask, "map_id": map_id, "family": row["family"],
            "stratum": stratum})
    if not maps_by_stratum["routine"] or not maps_by_stratum["challenge"]:
        raise ValueError("routine and challenge strata are both required")
    for row in normalized:
        s = row["stratum"]
        row["weight"] = ((0.8 if s == "routine" else 0.2) /
            len(maps_by_stratum[s]) / states_per_map[(s, row["map_id"])])
    if abs(sum(row["weight"] for row in normalized) - 1.0) > 1e-10:
        raise ValueError("fixed state weights do not sum to one")
    return normalized


def statewise_scores(rows: list[dict], arrays: dict, metadata: list[dict]) -> dict:
    """Join saved statewise p/KL/mass to immutable state IDs; no model call."""
    normalized_rows = []
    for row in rows:
        if isinstance(row, dict):
            normalized_rows.append(row)
        else:
            canonical = row.canonical.hex() if isinstance(row.canonical, bytes) else row.canonical
            normalized_rows.append({"canonical": canonical, "map_id": row.map_id,
                "family": row.family, "goal": row.goal, "current": row.current, "q": list(row.q)})
    ids = [_stable_id(row) for row in normalized_rows]
    expected_ids = [_stable_id(meta["id"]) for meta in metadata]
    if len(set(ids)) != len(ids) or ids != expected_ids:
        raise ValueError("missing, duplicated, or reordered stable state identity")
    for row, meta in zip(normalized_rows, metadata):
        q = row.get("q", ())
        if len(q) != 4 or any(not _finite(value) for value in q) or any(
                abs(float(a) - float(b)) > 1e-12 for a, b in zip(q, meta["q"])):
            raise ValueError("checkpoint oracle q differs from stable bank identity")
    n = len(metadata)
    probs, kls, nonoptimal = arrays.get("p"), arrays.get("kl"), arrays.get("nonoptimal_mass")
    if not all(isinstance(values, list) and len(values) == n for values in (probs, kls, nonoptimal)):
        raise ValueError("saved p/KL/nonoptimal arrays do not match the fixed bank")
    out, unavailable = [], []
    for index, meta in enumerate(metadata):
        p, q, legal = probs[index], meta["q"], meta["legal_mask"]
        if (not isinstance(p, list) or len(p) != 4 or any(not _finite(v) or v < 0 for v in p)
                or abs(sum(p) - 1.0) > 1e-10):
            raise ValueError("saved policy distribution is invalid or unnormalized")
        if any(p[action] != 0 for action in range(4) if not legal[action]):
            raise ValueError("saved policy assigns probability to an illegal action")
        if any(q[a] > 0 and not legal[a] for a in range(4)):
            raise ValueError("oracle support/action mask mismatch")
        kl, saved_nonoptimal = kls[index], nonoptimal[index]
        if not _finite(kl) or not _finite(saved_nonoptimal):
            raise ValueError("saved per-state KL/nonoptimal mass is nonfinite")
        mass = sum(p[a] for a in range(4) if q[a] > 0)
        if mass > 1.0 + 1e-12:
            raise ValueError("oracle support mass exceeds one")
        expected_nonoptimal = sum(p[a] for a in range(4) if q[a] == 0)
        if abs(expected_nonoptimal - saved_nonoptimal) > 1e-10:
            raise ValueError("saved nonoptimal mass disagrees with exported p")
        argmax = _argmax_legal(p, legal)
        zero_supported = any(q[a] > 0 and p[a] <= 0 for a in range(4))
        reason = "exported p is zero on positive-q action" if zero_supported else None
        if mass == 0 and reason is None:
            reason = "zero oracle-support mass"
        if not _finite(mass) or mass <= 0:
            reason = reason or "nonfinite or nonpositive oracle-support mass"
        if reason:
            unavailable.append({"state_id": meta["id"], "reason": reason})
        a_component = -math.log(mass) if not reason and mass > 0 and _finite(mass) else None
        b_component = kl + math.log(mass) if not reason and mass > 0 and _finite(mass) else None
        if a_component is not None and b_component is not None and min(a_component, b_component) < -1e-10:
            raise ValueError("KL component is below the accepted floating diagnostic tolerance")
        out.append({**meta, "p": p, "kl": kl, "saved_nonoptimal_mass": saved_nonoptimal,
            "support_mass": mass, "A": a_component, "B": b_component,
            "component_reconstruction_residual": (a_component + b_component - kl)
                if a_component is not None and b_component is not None else None,
            "argmax_action": argmax, "argmax_in_oracle_support": q[argmax] > 0})
    weight_total = sum(row["weight"] for row in out)
    if abs(weight_total - 1.0) > 1e-10:
        raise ValueError("state weights changed or fail normalization")
    weighted_nonoptimal = sum(row["weight"] * row["saved_nonoptimal_mass"] for row in out)
    weighted_one_minus_support = sum(row["weight"] * (1.0 - row["support_mass"]) for row in out)
    mass_residual = weighted_one_minus_support - weighted_nonoptimal
    if abs(mass_residual) > 1e-10:
        raise ValueError("weighted 1-mass disagrees with saved nonoptimal-mass series")
    available = not unavailable
    result = {"states": out, "decomposition_available": available,
        "unavailable_states": unavailable, "weighted_nonoptimal_mass": weighted_nonoptimal,
        "weighted_one_minus_support_mass": weighted_one_minus_support,
        "nonoptimal_mass_validation_residual": mass_residual,
        "weighted_kl_from_states": sum(row["weight"] * row["kl"] for row in out)}
    if available:
        weighted_kl = result["weighted_kl_from_states"]
        weighted_a = sum(row["weight"] * row["A"] for row in out)
        weighted_b = sum(row["weight"] * row["B"] for row in out)
        result.update({"weighted_kl_from_states": weighted_kl, "weighted_A": weighted_a,
            "weighted_B": weighted_b, "component_reconstruction_residual": weighted_a + weighted_b - weighted_kl})
        if abs(weighted_a + weighted_b - weighted_kl) > 1e-10:
            raise ValueError("A+B does not reconstruct saved weighted KL")
    else:
        result["decomposition_unavailable_reason"] = unavailable
    return result


def statewise_transitions(earlier: dict, later: dict, label: str) -> dict:
    left, right = earlier["states"], later["states"]
    if len(left) != len(right):
        raise ValueError("state bank size changed across checkpoints")
    groups = {"on_on": [], "on_off": [], "off_on": [], "off_off": []}
    for a, b in zip(left, right):
        if any(a.get(key) != b.get(key) for key in ("id", "q", "legal_mask", "weight", "stratum")):
            raise ValueError("state identity/q/mask/weight changed across checkpoints")
        g = ("on_" if a["argmax_in_oracle_support"] else "off_") + ("on" if b["argmax_in_oracle_support"] else "off")
        groups[g].append((a, b))
    total_change = sum(b["weight"] * (b["kl"] - a["kl"]) for a, b in zip(left, right))
    result = {"label": label, "decomposition_available": earlier["decomposition_available"] and later["decomposition_available"],
        "weighted_kl_change": total_change, "groups": {}, "stratum_contributions": {}}
    for name, members in groups.items():
        prevalence = sum(a["weight"] for a, _ in members)
        contribution = sum(a["weight"] * (b["kl"] - a["kl"]) for a, b in members)
        result["groups"][name] = {"count": len(members), "weighted_prevalence": prevalence,
            "additive_kl_contribution": contribution,
            "conditional_weighted_mean": contribution / prevalence if prevalence else None}
        for stratum in ("routine", "challenge"):
            subset = [(a, b) for a, b in members if a["stratum"] == stratum]
            result["stratum_contributions"].setdefault(stratum, {})[name] = sum(
                a["weight"] * (b["kl"] - a["kl"]) for a, b in subset)
    if abs(sum(row["weighted_prevalence"] for row in result["groups"].values()) - 1.0) > 1e-10:
        raise ValueError("four transition groups are not exhaustive")
    group_change = sum(row["additive_kl_contribution"] for row in result["groups"].values())
    if abs(group_change - total_change) > 1e-10:
        raise ValueError("transition contributions do not reconstruct weighted KL change")
    result["group_closure_residual"] = group_change - total_change
    for group, data in result["groups"].items():
        stratum_total = sum(result["stratum_contributions"][stratum][group]
                            for stratum in ("routine", "challenge"))
        data["stratum_closure_residual"] = stratum_total - data["additive_kl_contribution"]
        if abs(data["stratum_closure_residual"]) > 1e-10:
            raise ValueError("routine/challenge contributions do not reconstruct group contribution")
    if result["decomposition_available"]:
        result["component_changes"] = {}
        for component in ("A", "B"):
            change = sum(a["weight"] * (b[component] - a[component]) for a, b in zip(left, right))
            result["component_changes"][component] = change
            for group, members in groups.items():
                result["groups"][group][component + "_contribution"] = sum(
                    a["weight"] * (b[component] - a[component]) for a, b in members)
        for data in result["groups"].values():
            data["component_reconstruction_residual"] = (
                data["A_contribution"] + data["B_contribution"] - data["additive_kl_contribution"])
            if abs(data["component_reconstruction_residual"]) > 1e-10:
                raise ValueError("group A+B does not reconstruct its additive KL contribution")
        result["component_change_residual"] = sum(result["component_changes"].values()) - total_change
        if abs(result["component_change_residual"]) > 1e-10:
            raise ValueError("delta A + delta B does not reconstruct delta KL")
    else:
        result["decomposition_unavailable_reason"] = {
            "earlier": earlier.get("unavailable_states", []),
            "later": later.get("unavailable_states", [])}
    return result


def _sample_sd(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = sum(values) / len(values)
    return math.sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))


def _mean_slope(points: list[dict], key: str) -> dict:
    if not points or any(not _finite(row.get("metrics", {}).get(key)) for row in points):
        raise ValueError("complete finite diagnostic window required")
    xs = [row["update"] / 1000.0 for row in points]
    ys = [row["metrics"][key] for row in points]
    xbar, ybar = sum(xs) / len(xs), sum(ys) / len(ys)
    denominator = sum((x - xbar) ** 2 for x in xs)
    if denominator == 0:
        raise ValueError("window has no x variation")
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / denominator
    residuals = [y - (ybar + slope * (x - xbar)) for x, y in zip(xs, ys)]
    return {"mean": sum(ys) / len(ys), "slope_per_1000_updates": slope,
            "residual_sd": _sample_sd(residuals),
            "residual_sd_definition": "sample standard deviation; denominator n-1",
            "n": len(points)}


def _window(points: list[dict], lo: int, hi: int) -> list[dict]:
    rows = [row for row in points if lo <= row.get("update", -1) <= hi]
    expected = list(range(lo, hi + 1, 100))
    if [row.get("update") for row in rows] != expected:
        raise ValueError(f"missing or unordered cells in fixed window {lo}..{hi}")
    return rows


def _minimum(points: list[dict], key: str) -> dict:
    values = [(row["update"], row["metrics"][key]) for row in points]
    minimum = min(value for _, value in values)
    ties = [update for update, value in values if abs(value - minimum) <= 1e-12]
    intervals = []
    start = previous = ties[0]
    for update in ties[1:]:
        if update != previous + 100:
            intervals.append([start, previous])
            start = update
        previous = update
    intervals.append([start, previous])
    return {"minimum": minimum, "tie_updates": ties, "contiguous_intervals": intervals}


def summarize_owner(points: list[dict]) -> dict:
    if [row.get("update") for row in points] != list(UPDATES):
        raise ValueError("exact 31-point grid required")
    if any(any(not _finite(row.get("metrics", {}).get(key)) for key in
               ("q", "kl", "brier", "teacher_entropy", "policy_entropy", "greedy_q", "challenge_q", "nonoptimal_mass"))
               for row in points):
        raise ValueError("all score cells must be finite")
    windows = {"primary_800_2000": (800, 2000), "early_0_1000": (0, 1000),
               "middle_1000_2000": (1000, 2000), "late_2000_3000": (2000, 3000)}
    result = {}
    for name, (lo, hi) in windows.items():
        rows = _window(points, lo, hi)
        result[name] = {key: _mean_slope(rows, key) for key in ("q", "kl", "brier", "nonoptimal_mass")}
        result[name]["entropy_and_greedy_means"] = {
            key: sum(row["metrics"][key] for row in rows) / len(rows)
            for key in ("teacher_entropy", "policy_entropy", "greedy_q")}
    result["sampled_minima"] = {key: _minimum(points, key) for key in ("kl", "brier")}
    result["raw_points"] = points
    return result


def summarize_pairs(owners: list[dict]) -> dict:
    if [(row.get("seed"), row.get("mode")) for row in owners] != [
            (2201, "softmax"), (2201, "schrodinger"),
            (2202, "schrodinger"), (2202, "softmax")]:
        raise ValueError("all four fixed owners in fixed order are required")
    by = {(row["seed"], row["mode"]): row for row in owners}
    metrics = ("q", "kl", "brier", "nonoptimal_mass")
    windows = ("primary_800_2000", "early_0_1000", "middle_1000_2000", "late_2000_3000")
    paired = {}
    for window in windows:
        paired[window] = {}
        for metric in metrics:
            mean_differences, slope_differences, raw_gap_sd, residual_sd = [], [], [], []
            for seed in SEEDS:
                sm = by[(seed, "softmax")]["summary"][window][metric]
                sa = by[(seed, "schrodinger")]["summary"][window][metric]
                mean_differences.append(sa["mean"] - sm["mean"])
                slope_differences.append(sa["slope_per_1000_updates"] - sm["slope_per_1000_updates"])
                smp = _window(by[(seed, "softmax")]["points"], *{
                    "primary_800_2000": (800, 2000), "early_0_1000": (0, 1000),
                    "middle_1000_2000": (1000, 2000), "late_2000_3000": (2000, 3000)}[window])
                sap = _window(by[(seed, "schrodinger")]["points"], *{
                    "primary_800_2000": (800, 2000), "early_0_1000": (0, 1000),
                    "middle_1000_2000": (1000, 2000), "late_2000_3000": (2000, 3000)}[window])
                gaps = [a["metrics"][metric] - b["metrics"][metric] for a, b in zip(sap, smp)]
                raw_gap_sd.append(_sample_sd(gaps))
                gap_points = [{"update": left["update"], "metrics": {metric: gap}}
                              for left, gap in zip(sap, gaps)]
                residual_sd.append(_mean_slope(gap_points, metric)["residual_sd"])
            paired[window][metric] = {"per_seed_mean_difference_sa_minus_sm": mean_differences,
                "equal_seed_mean_difference": sum(mean_differences) / 2,
                "mean_difference_range": [min(mean_differences), max(mean_differences)],
                "per_seed_slope_difference": slope_differences,
                "equal_seed_slope_difference": sum(slope_differences) / 2,
                "slope_difference_range": [min(slope_differences), max(slope_differences)],
                "per_seed_raw_gap_sd": raw_gap_sd,
                "raw_gap_sd_definition": "sample standard deviation; denominator n-1",
                "per_seed_residual_sd": residual_sd,
                "residual_sd_definition": "sample standard deviation of OLS residuals; denominator n-1"}
    statewise_pairs = {}
    for name in ("on_on", "on_off", "off_on", "off_off"):
        per_seed = []
        for seed in SEEDS:
            sm = by[(seed, "softmax")].get("statewise_800_2000")
            sa = by[(seed, "schrodinger")].get("statewise_800_2000")
            if not sm or not sa:
                per_seed.append(None)
            else:
                per_seed.append(sa["groups"][name]["additive_kl_contribution"] -
                    sm["groups"][name]["additive_kl_contribution"])
        available = [value for value in per_seed if value is not None]
        statewise_pairs[name] = {"per_seed_sa_minus_sm_contribution": per_seed,
            "equal_seed_mean": sum(available) / len(available) if len(available) == 2 else None,
            "range": [min(available), max(available)] if len(available) == 2 else None}
    return {"owners": owners, "paired_sa_minus_softmax": paired,
            "paired_statewise_800_2000": statewise_pairs,
            "inference": "descriptive_two_existing_seed_pairs_no_population_inference"}


def _verify_session(decision_path: Path, session_path: Path, nonce: str, argv: list[str]) -> tuple[dict, dict]:
    from execution.early_learning import command
    decision = _read(decision_path)
    capability = _read(session_path)
    if not session_path.is_file() or capability.get("nonce") != nonce:
        raise PermissionError("driver session nonce mismatch")
    if not command.LOCK.exists() or os.getppid() != capability.get("parent_pid"):
        raise PermissionError("live driver reservation/parent required")
    try:
        os.kill(capability["parent_pid"], 0)
    except (OSError, KeyError, TypeError) as error:
        raise PermissionError("driver parent is not live") from error
    if capability.get("decision_sha256") != sha256(decision_path) or capability.get("decision_path") != str(decision_path.resolve()):
        raise PermissionError("session decision identity mismatch")
    if capability.get("argv") != argv or argv[:5] != decision.get("argv"):
        raise PermissionError("session argv identity mismatch")
    if (capability.get("stage"), capability.get("seed"), capability.get("mode")) != ("B", decision.get("seed"), decision.get("mode")):
        raise PermissionError("session owner identity mismatch")
    if capability.get("review") != decision.get("review"):
        raise PermissionError("session review identity mismatch")
    if command.sha256(INVENTORY) != capability.get("inventory_sha256") or decision.get("inventory_sha256") != capability.get("inventory_sha256"):
        raise PermissionError("session inventory identity mismatch")
    if command.ledger_eof() != capability.get("ledger_sha256") or decision.get("ledger_sha256") != capability.get("ledger_sha256"):
        raise PermissionError("ledger EOF changed after reservation")
    hashes = command.authority_hashes()
    if hashes != decision.get("source_hashes") or hashes != capability.get("source_hashes"):
        raise PermissionError("reviewed source hashes changed")
    command.review_ok(decision, hashes)
    if time.monotonic() >= capability.get("deadline_monotonic", 0):
        raise PermissionError("owner deadline expired")
    if decision.get("approved") is not True or decision.get("kind") != "production" or decision.get("stage") != "B":
        raise PermissionError("study accepts supervised production decisions only")
    return decision, capability


def _owner_entry(inventory: dict, seed: int, mode: str) -> dict:
    rows = [row for row in inventory.get("owners", []) if row.get("seed") == seed and row.get("mode") == mode]
    if len(rows) != 1:
        raise ValueError("inventory owner missing or duplicated")
    return rows[0]


def _validate_original(entry: dict) -> tuple[Path, dict, dict]:
    owner = WORKSPACE / entry["path"]
    for name, digest in entry["files"].items():
        path = owner / name
        if not path.is_file() or sha256(path) != digest:
            raise ValueError("original owner artifact binding mismatch: " + name)
    result = _read(owner / "result.json")
    if result.get("status") != "COMPLETE" or result.get("seed") != entry["seed"] or result.get("mode") != entry["mode"]:
        raise ValueError("original owner incomplete or identity mismatch")
    if any(result.get(key) != value for key, value in entry["identity"].items()):
        raise ValueError("original scientific identity mismatch")
    training = result.get("training", {})
    if training.get("initial_hash") != entry["initial_hash"] or training.get("initial_checkpoint_hash") != entry["initial_checkpoint_sha256"]:
        raise ValueError("original initial identity mismatch")
    return owner, result, training


def _audit_paired_stream(inventory: dict) -> dict[int, str]:
    results = {}
    for entry in inventory["owners"]:
        owner, result, _ = _validate_original(entry)
        results[(entry["seed"], entry["mode"])] = (owner, result)
    stream_hashes = {}
    for seed in SEEDS:
        sm, sa = results[(seed, "softmax")][1], results[(seed, "schrodinger")][1]
        for key in ("input_ids", "config_hash", "shared_initial_digest", "bank", "source_hashes"):
            if sm.get(key) != sa.get(key):
                raise ValueError(f"paired original {key} mismatch for seed {seed}")
        left, right = sm.get("batch_digests"), sa.get("batch_digests")
        if not isinstance(left, list) or len(left) != 16000 or left != right:
            raise ValueError(f"paired original 16,000-step stream mismatch for seed {seed}")
        stream_hashes[seed] = hashlib.sha256("".join(left).encode()).hexdigest()
    return stream_hashes


def _audit_checkpoints(entry: dict, result: dict, model, torch, accepted,
                       fixture_updates: tuple[int, ...] | None = None) -> tuple[dict[int, dict], dict[int, Path]]:
    owner = WORKSPACE / entry["path"]
    identity = result["input_ids"]
    initial_hash = result["training"]["initial_hash"]
    source = identity["frozen_source_hash"]
    previous = None
    identities, paths = {}, {}
    expected_points = entry["checkpoints"]
    if [pair[0] for pair in expected_points] != list(UPDATES):
        raise ValueError("inventory checkpoint grid mismatch")
    for update, expected_sha in expected_points:
        path = owner / "checkpoints" / ("initial.pt" if update == 0 else f"update-{update}.pt")
        if not path.is_file() or sha256(path) != expected_sha:
            raise ValueError(f"checkpoint file hash mismatch at update {update}")
        expected = {"seed": entry["seed"], "mode": entry["mode"], "source": source,
            "config": accepted.FROZEN_CONFIG,
            "initial_hash": initial_hash, "input_ids": identity,
            "update": update, "parent_hash": previous}
        if fixture_updates is None or update == 0 or update in fixture_updates:
            payload = torch.load(path, map_location="cpu", weights_only=False)
            got = payload.get("identity")
            if got != expected:
                raise ValueError(f"checkpoint parent/identity chain mismatch at update {update}")
            if update == 0:
                model.load_state_dict(payload["model"])
                if accepted.state_hash(model) != initial_hash:
                    raise ValueError("initial model state hash mismatch")
            del payload
        else:
            # Private runtime fixtures still verify every original file hash
            # and expected chain link, but load tensor payloads only when used.
            got = expected
        identities[update] = {"identity": got}
        paths[update] = path
        previous = expected_sha
    return identities, paths


def _metrics(proper: dict, rollout: dict, greedy: dict) -> dict:
    weighted = proper["weighted"]
    return {"q": rollout["mixture"]["Q"],
        "challenge_q": rollout["strata"]["challenge"]["Q"],
        "greedy_q": greedy["mixture"]["Q"],
        "greedy_challenge_q": greedy["strata"]["challenge"]["Q"],
        "kl": weighted["kl"], "brier": weighted["brier"],
        "teacher_entropy": weighted["entropy_q"], "policy_entropy": weighted["entropy_p"]}


def _validate_frozen_source_identity(identity: dict, hashes: dict) -> None:
    aliases = {"accepted_route_policy.py": "accepted_model",
        "accepted_route_policy_experiment.py": "accepted_experiment",
        "accepted_route_policy_data.py": "accepted_data",
        "accepted_route_policy_evaluation.py": "accepted_evaluation",
        "accepted_route_policy_metrics.py": "accepted_metrics",
        "attention": "attention", "feasibility": "feasibility"}
    old = identity.get("source_hashes", {})
    if not isinstance(old, dict) or any(old.get(source) != hashes[current]
            for source, current in aliases.items()):
        raise ValueError("accepted model/data/evaluator bytes differ from original run")


def run(*, decision_path: Path, session_path: Path, nonce: str, argv: list[str],
        _fixture: dict | None = None) -> dict:
    decision, capability = _verify_session(decision_path, session_path, nonce, argv)
    # Imports are deliberately delayed until after the driver has reserved and
    # authenticated this child within its fixed external envelope.
    import torch
    from schrodinger import route_policy_experiment as accepted
    from schrodinger.route_policy import RoutePolicy
    from schrodinger.route_policy_data import RouteState, legal_mask, load_training, load_validation
    from schrodinger.route_policy_evaluation import evaluate_proper, evaluate_rollouts, mechanism_probe
    from schrodinger.route_policy_metrics import heldout_bank, serialize_candidate, training_bank

    accepted.configure_runtime()

    seed, mode = decision.get("seed"), decision.get("mode")
    if seed not in SEEDS or mode not in MODES or decision.get("updates") != 3000:
        raise PermissionError("fixed early-learning owner required")
    if decision.get("envelope_seconds") != {"softmax": 300.0, "schrodinger": 360.0}[mode]:
        raise PermissionError("exact external owner envelope required")
    inventory = _read(INVENTORY)
    if decision.get("inventory_sha256") != sha256(INVENTORY):
        raise PermissionError("inventory changed")
    entry = _owner_entry(inventory, seed, mode)
    if decision.get("owner_inventory_entry") != entry:
        raise PermissionError("owner decision does not bind exact inventory entry")
    owner, result, _ = _validate_original(entry)
    _validate_frozen_source_identity(result, decision["source_hashes"])
    if result.get("config_hash") != accepted.config_hash():
        raise ValueError("accepted training configuration differs from original owner")
    ids = result["input_ids"]
    validation = load_validation()
    if len(validation.problems) != 512:
        raise ValueError("exact validation panel of 512 problems required")
    if _fixture is None:
        scoring_problems = validation.problems
    else:
        routine = next((p for p in validation.problems if p.family != "IIIILLLL"), None)
        challenge = next((p for p in validation.problems if p.family == "IIIILLLL"), None)
        if routine is None or challenge is None:
            raise ValueError("validation fixture requires both strata")
        scoring_problems = (routine, challenge)
    if not scoring_problems:
        raise ValueError("fixture validation panel must be nonempty")
    bank = heldout_bank(validation.problems)
    if len(bank.selected) != 1024 or bank.selected_hash != result["bank"]["selected_hash"]:
        raise ValueError("reconstructed 1,024-state proper bank mismatch")
    baseline_path = owner / "score-0.json"
    baseline = _read(baseline_path)
    old_rows = baseline.get("proper", {}).get("rows", [])
    rebuilt_rows = [{"canonical": c.canonical.hex(), "map_id": c.map_id,
                     "family": c.family, "goal": c.goal, "current": c.current,
                     "q": list(c.q)} for c in bank.selected]
    if [_identity(row) for row in old_rows] != [_identity(row) for row in rebuilt_rows]:
        raise ValueError("validation bank ordering/q differs from retained baseline")
    training = load_training()
    if training_bank(training.states).selected_hash != ids["training_selected_hash"]:
        raise ValueError("training support source differs from original frozen training identity")
    support = frozenset(training.support)
    score_bank = bank
    if _fixture is not None:
        from dataclasses import replace
        proper_per_stratum = max(1, int(_fixture.get("proper_per_stratum", 2)))
        selected_rows = []
        for family_test in (False, True):
            selected_rows.extend([c for c in bank.selected
                if (c.family == "IIIILLLL") == family_test][:proper_per_stratum])
        if not any(c.family == "IIIILLLL" for c in selected_rows) or not any(c.family != "IIIILLLL" for c in selected_rows):
            raise ValueError("tiny proper fixture requires both strata")
        score_bank = replace(bank, selected=tuple(selected_rows))
    bank_rows = [{"canonical": c.canonical.hex(), "map_id": c.map_id, "family": c.family,
                  "goal": c.goal, "current": c.current, "q": list(c.q)} for c in score_bank.selected]
    legal_masks = [legal_mask(RouteState(bytes.fromhex(row["canonical"]), row["map_id"], row["family"],
                    row["current"], row["goal"], tuple(row["q"]))) for row in bank_rows]
    state_metadata = statewise_metadata(bank_rows, [list(map(bool, mask.tolist())) for mask in legal_masks])
    candidates = accepted.validation_probe_candidates(bank)
    if len(candidates) != 128:
        raise ValueError("accepted deterministic probe panel must contain 128 rows")
    if _fixture is not None:
        probe_count = max(2, int(_fixture.get("probe_count", 8)))
        selected_candidates = []
        for challenge in (False, True):
            selected_candidates.extend([c for c in candidates
                if (c.family == "IIIILLLL") == challenge][:probe_count // 2])
        if not any(c.family == "IIIILLLL" for c in selected_candidates) or not any(c.family != "IIIILLLL" for c in selected_candidates):
            raise ValueError("tiny probe fixture requires both strata")
        candidates = selected_candidates
    candidate_ids = [serialize_candidate(candidate).hex() for candidate in candidates]
    candidate_hash = hashlib.sha256("".join(candidate_ids).encode()).hexdigest()

    original_global = (dict(accepted.STAGES), accepted.GLOBAL_CAP, accepted.CARRY)
    try:
        accepted.STAGES.clear()
        accepted.STAGES.update({"A": 120.0, "B": 1440.0, "C": 0.0, "D": 240.0})
        accepted.GLOBAL_CAP, accepted.CARRY = 1800.0, 0.0
        output_name = f"early-{seed}-{mode}-0-to-3000"
        with accepted.OwnedAttempt.begin(ATTEMPTS, LEDGER, "B", output_name) as attempt:
            # Keep immutable lineage verification inside the owned timer.
            paired_stream_hashes = _audit_paired_stream(inventory)
            _durable(attempt.output / "lineage.json", {
                "original_owner": str(owner.resolve()),
                "original_result_sha256": entry["files"]["result.json"],
                "original_manifest_sha256": entry["files"]["output-manifest.json"],
                "source_identity": entry["identity"],
                "inventory_sha256": sha256(INVENTORY),
                "checkpoint_grid": list(UPDATES),
                "validation_problems": len(validation.problems),
                "proper_rows": len(bank.selected),
                "statewise_rows": state_metadata,
                "probe_candidates_sha256": candidate_hash,
                "probe_candidate_ids": candidate_ids})
            model = RoutePolicy(mode)
            points, details = [], []
            selected_updates = UPDATES if _fixture is None else tuple(_fixture["updates"])
            if selected_updates != UPDATES and (not selected_updates or any(u not in UPDATES for u in selected_updates)):
                raise ValueError("private fixture grid must be a subset of the frozen grid")
            checkpoint_identities, checkpoint_paths = _audit_checkpoints(entry, result, model, torch,
                accepted, None if _fixture is None else selected_updates)
            for update in selected_updates:
                checkpoint_path = checkpoint_paths[update]
                checkpoint_sha = entry["checkpoints"][update // 100][1]
                if sha256(checkpoint_path) != checkpoint_sha:
                    raise ValueError("checkpoint changed after original lineage audit")
                payload = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
                if payload.get("identity") != checkpoint_identities[update]["identity"]:
                    raise ValueError("checkpoint identity changed after original lineage audit")
                model.load_state_dict(payload["model"])
                model.eval()
                identity = f"early-learning:{seed}:{mode}:{update}:{checkpoint_sha}"
                before_hash = accepted.state_hash(model)
                cache = {}
                started = time.monotonic()
                if update in REUSED:
                    evidence = _read(owner / f"score-{update}.json")
                    expected_reused = next((item for item in entry["reused_scores"] if item[0] == update), None)
                    if expected_reused is None or sha256(owner / f"score-{update}.json") != expected_reused[1]:
                        raise ValueError("reused score hash differs from immutable inventory")
                    if evidence.get("checkpoint_sha256") != checkpoint_sha or evidence.get("checkpoint_identity") != payload.get("identity"):
                        raise ValueError("reused score does not identify exact target checkpoint")
                    if set(evidence.get("metrics", {})) != {"brier", "challenge_q", "kl", "policy_entropy", "q", "teacher_entropy"}:
                        raise ValueError("reused score metric schema mismatch")
                    proper, rollout = evidence["proper"], evidence["rollout"]
                    if len(proper.get("arrays", {}).get("ce", [])) != 1024 or len(rollout.get("problems", [])) != 512:
                        raise ValueError("reused raw proper/rollout evidence incomplete")
                    rebuilt = {"q": rollout["mixture"]["Q"],
                        "challenge_q": rollout["strata"]["challenge"]["Q"],
                        "kl": proper["weighted"]["kl"], "brier": proper["weighted"]["brier"],
                        "teacher_entropy": proper["weighted"]["entropy_q"],
                        "policy_entropy": proper["weighted"]["entropy_p"]}
                    old_metrics = evidence["metrics"]
                    if any(not _finite(old_metrics.get(key)) or abs(old_metrics[key] - value) > 1e-8
                           for key, value in rebuilt.items()):
                        raise ValueError("reused summaries disagree with retained raw evidence")
                    metric = {**evidence["metrics"]}
                    metric["nonoptimal_mass"] = proper["weighted"]["nonoptimal_mass"]
                else:
                    with torch.inference_mode():
                        proper = evaluate_proper(model, score_bank, identity=identity, cache=cache)
                        rollout = evaluate_rollouts(model, scoring_problems, identity=identity,
                            seed=seed, splitcode=1, replicate=0, support=support,
                            k=32, temperature=1.0, cache=cache)
                    metric = {"q": rollout["mixture"]["Q"], "challenge_q": rollout["strata"]["challenge"]["Q"],
                        "kl": proper["weighted"]["kl"], "brier": proper["weighted"]["brier"],
                        "teacher_entropy": proper["weighted"]["entropy_q"],
                        "policy_entropy": proper["weighted"]["entropy_p"],
                        "nonoptimal_mass": proper["weighted"]["nonoptimal_mass"]}
                cache.clear()
                with torch.inference_mode():
                    greedy = evaluate_rollouts(model, scoring_problems, identity=identity + ":greedy",
                        seed=seed, splitcode=1, replicate=0, support=support,
                        k=1, temperature=1.0, greedy=True)
                    metric["greedy_q"] = greedy["mixture"]["Q"]
                    metric["greedy_challenge_q"] = greedy["strata"]["challenge"]["Q"]
                    effective = None
                    if mode == "schrodinger":
                        effective = [{"layer": layer,
                            "dt": (0.5 * torch.sigmoid(attn.raw_dt)).detach().cpu().tolist(),
                            "gamma": (math.pi * torch.tanh(attn.raw_gamma)).detach().cpu().tolist()}
                            for layer, attn in enumerate(model.attn)]
                    probe = None
                    if mode == "schrodinger" and update in PROBE_UPDATES:
                        probe_before = accepted.state_hash(model)
                        probe = mechanism_probe(model, candidates)
                        if accepted.state_hash(model) != probe_before:
                            raise RuntimeError("mechanism probe mutated model state")
                if accepted.state_hash(model) != before_hash:
                    raise RuntimeError("inference changed model state")
                statewise = statewise_scores(proper["rows"],
                    {key: (value.tolist() if hasattr(value, "tolist") else value)
                     for key, value in proper["arrays"].items()}, state_metadata)
                if abs(statewise["weighted_nonoptimal_mass"] - proper["weighted"]["nonoptimal_mass"]) > 1e-10:
                    raise ValueError("statewise nonoptimal mass disagrees with saved weighted aggregate")
                if abs(statewise["weighted_kl_from_states"] - proper["weighted"]["kl"]) > 1e-10:
                    raise ValueError("statewise weighted KL disagrees with saved weighted aggregate")
                metric["nonoptimal_mass"] = statewise["weighted_nonoptimal_mass"]
                point = {"update": update, "checkpoint_sha256": checkpoint_sha,
                         "metrics": metric, "effective_dt_gamma": effective,
                         "lineage": {"owner": str(owner.resolve()), "checkpoint_path": str(checkpoint_path.resolve()),
                                     "checkpoint_identity": payload["identity"],
                                     "reused_score_sha256": next((pair[1] for pair in entry["reused_scores"] if pair[0] == update), None)},
                         "timing_seconds": time.monotonic() - started}
                detail = {"point": point,
                    "proper": evidence["proper"] if update in REUSED else accepted._serializable({k: v for k, v in proper.items() if k != "cache"}),
                    "rollout": evidence["rollout"] if update in REUSED else accepted._serializable({k: v for k, v in rollout.items() if k != "cache"}),
                    "greedy": accepted._serializable({k: v for k, v in greedy.items() if k != "cache"}),
                    "statewise": statewise,
                    "probe": accepted._serializable(probe)}
                _durable(attempt.output / f"score-{update:04d}.json", detail)
                if probe is not None:
                    _durable(attempt.output / f"probe-{update:04d}.json", {
                        "candidate_ids": candidate_ids, "candidate_hash": candidate_hash,
                        "probe": accepted._serializable(probe), "before_state_hash": before_hash,
                        "after_state_hash": accepted.state_hash(model)})
                points.append(point)
                details.append(detail)
                del payload
            result_owner = {"status": "COMPLETE", "seed": seed, "mode": mode,
                "updates": 3000, "input_ids": ids, "config_hash": result["config_hash"],
                "shared_initial_digest": result["shared_initial_digest"],
                "source_hashes": result["source_hashes"], "bank": result["bank"],
                "reviewed_source_hashes": decision["source_hashes"],
                "inventory_sha256": sha256(INVENTORY), "attempt_entry_id": attempt.entry_id,
                "runtime": {"python": sys.version, "torch": torch.__version__},
                "training_support_sha256": training.support_hash,
                "paired_batch_stream_sha256": paired_stream_hashes[seed],
                "probe_updates": list(PROBE_UPDATES if mode == "schrodinger" else ()), "points": points,
                "details": [f"score-{point['update']:04d}.json" for point in points]}
            _durable(attempt.output / "result.json", result_owner)
            _durable(attempt.output / "index.json", {"status": "COMPLETE",
                "result_sha256": sha256(attempt.output / "result.json"),
                "points": [{"update": point["update"], "path": f"score-{point['update']:04d}.json",
                            "sha256": sha256(attempt.output / f"score-{point['update']:04d}.json")} for point in points]})
            return result_owner
    finally:
        accepted.STAGES.clear()
        accepted.STAGES.update(original_global[0])
        accepted.GLOBAL_CAP, accepted.CARRY = original_global[1], original_global[2]


def main(argv=None) -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", type=Path, required=True)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--nonce", required=True)
    args = parser.parse_args(argv)
    argv_bound = [sys.executable, "-m", "execution.early_learning.study",
        "--decision", str(args.decision.resolve()), "--session", str(args.session.resolve()),
        "--nonce", args.nonce]
    result = run(decision_path=args.decision, session_path=args.session,
                 nonce=args.nonce, argv=argv_bound)
    print(json.dumps({"status": result["status"], "seed": result["seed"],
                      "mode": result["mode"]}, sort_keys=True))


if __name__ == "__main__":
    main()
