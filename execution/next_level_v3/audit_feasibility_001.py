"""Read-only bounded audit of the frozen feasibility-001 artifacts."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import time
import uuid

from schrodinger import productive_diversity_v3_data as data
from schrodinger.productive_diversity_v3_runner import _append_ledger, _json
from schrodinger.route_feasibility import q_target

START = time.perf_counter()
ROOT = Path(__file__).resolve().parents[2]
ATTEMPT = ROOT / "execution/next_level_v3/attempts/feasibility-001"
OUT = ROOT / "execution/next_level_v3/audits/feasibility-001-audit.json"
LEDGER = ROOT / "execution/next_level_v3/ledger.jsonl"
STAGES = ("training", "validation_routine", "validation_mixed", "test_routine", "test_mixed")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(value):
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    if isinstance(value, dict):
        return tuple(sorted((key, freeze(item)) for key, item in value.items()))
    return value


def decode(value):
    if isinstance(value, dict):
        if set(value) == {"bytes_hex"}:
            return bytes.fromhex(value["bytes_hex"])
        return {key: decode(item) for key, item in value.items()}
    if isinstance(value, list):
        if value and all(isinstance(item, dict) and set(item) == {"key", "value"} for item in value):
            return {freeze(decode(item["key"])): decode(item["value"]) for item in value}
        return [decode(item) for item in value]
    return value


def load(name: str):
    return decode(json.loads((ATTEMPT / name).read_text()))


manifest_raw = json.loads((ATTEMPT / "manifest.json").read_text())
manifest = decode(manifest_raw)
summary = load("summary.json")
attempt = load("attempt.json")
inventory = tuple(load("inventory.json"))
ranking = load("ranking.json")

checks: dict[str, object] = {}
errors: list[str] = []

# Provenance and immutable byte bindings.
checks["manifest_sha256"] = sha(ATTEMPT / "manifest.json")
checks["attempt_manifest_binding"] = attempt["manifest_sha256"] == checks["manifest_sha256"]
checks["manifest_expected_sha256"] = checks["manifest_sha256"] == "26ddf4277f1c8e3ab63505cd93c7a643c4b76bf9eaf1cf4c9705f3d629e82464"
bad_outputs = {name: {"expected": digest, "actual": sha(ATTEMPT / name)}
               for name, digest in manifest["outputs"].items() if sha(ATTEMPT / name) != digest}
bad_sources = {name: {"expected": digest, "actual": sha(ROOT / name)}
               for name, digest in manifest["sources"].items() if sha(ROOT / name) != digest}
checks["output_hash_mismatches"] = bad_outputs
checks["source_hash_mismatches"] = bad_sources
checks["attempt_complete_no_error"] = attempt["status"] == "COMPLETE" and attempt["error"] is None
checks["summary_outcome"] = summary["outcome"]
if bad_outputs or bad_sources or not checks["attempt_manifest_binding"]:
    errors.append("provenance/hash binding mismatch")

# Inventory metadata and exact re-ranking from saved inventory only.
data.validate_inventory_records(inventory)
family_counts = Counter(row["family"] for row in inventory)
checks["inventory"] = {"records": len(inventory), "family_counts": dict(family_counts),
                       "unique_ids": len({row["map_id"] for row in inventory}),
                       "unique_canonical": len({row["canonical"] for row in inventory})}
recomputed_ranking = data.rank_proposals(inventory)
checks["ranking_exact_reproduction"] = _json(recomputed_ranking) == _json(ranking)
checks["ranking_retained"] = [{"window_start": row["window_start"], "window": row["window"],
                                "quota": row["quota"], "raw_family_counts": row["raw_family_counts"],
                                "score": row["score"], "mean_m": row["mean_m"]}
                               for row in ranking["retained"]]
if not checks["ranking_exact_reproduction"]:
    errors.append("saved ranking does not reproduce from saved inventory")

by_canonical = {row["canonical"]: row for row in inventory}
proposal_reports: dict[str, object] = {}
sample_groups: dict[tuple, list[dict]] = defaultdict(list)

for proposal in (12, 14, 16):
    pkey = str(proposal)
    stage_files = {stage: load(f"proposal-{proposal}-{stage}.json") for stage in STAGES}
    training = stage_files["training"]["result"]
    support = tuple(training["support"])
    encoded = b"".join(len(item).to_bytes(2, "big") + item for item in support)
    support_ok = hashlib.sha256(encoded).hexdigest() == training["support_hash"]
    metadata_errors: list[str] = []
    stage_counts: dict[str, object] = {}
    identity_sets: dict[str, set[bytes]] = {}

    def validate_rows(rows: list[dict], stage: str) -> None:
        for row in rows:
            source = by_canonical.get(row["canonical"])
            if source is None or row["map_id"] != source["map_id"] or row["family"] != source["family"] or row["n"] != 12:
                metadata_errors.append(f"{stage}: identity linkage")
                continue
            pair = (row["start"], row["goal"], row["length"], row["M"])
            if row["length"] not in source["shortlists"] or pair not in (
                tuple(candidate) for candidate in source["shortlists"][row["length"]]["retained"]
            ):
                metadata_errors.append(f"{stage}: pair linkage")
            sample_groups[(proposal, stage, row["family"], row["length"])].append(row)

    train_rows = list(training["selected"])
    validate_rows(train_rows, "training")
    identity_sets["training"] = {row["canonical"] for row in train_rows}
    stage_counts["training"] = {"rows": len(train_rows), "maps": len(identity_sets["training"]),
                                "family_rows": dict(Counter(row["family"] for row in train_rows))}

    failure_details = None
    for stage in STAGES[1:]:
        payload = stage_files[stage]
        results = payload.get("results", [])
        rows = [row for group in results for row in group["result"].get("selected", [])]
        validate_rows(rows, stage)
        ids = {row["canonical"] for row in rows}
        identity_sets[stage] = ids
        stage_counts[stage] = {"rows": len(rows), "maps": len(ids),
                               "families": {group["family"]: {"outcome": group["result"]["outcome"],
                                  "rows": len(group["result"].get("selected", [])),
                                  "maps": len({row["canonical"] for row in group["result"].get("selected", [])})}
                                  for group in results}}
        for group in results:
            result = group["result"]
            if result["outcome"] == "SCIENTIFIC_HELDOUT_SUPPLY_FAILED":
                evidence = result["evidence"]
                reason_counts = Counter(item.get("reason", item.get("status", "COMMITTED" if item.get("committed") else "SCANNED"))
                                        for item in evidence)
                rejected_maps = {item["map_id"] for item in evidence if item.get("reason")}
                committed_maps = {item["map_id"] for item in evidence if item.get("committed") is True}
                last_failed = next((item for item in reversed(evidence) if item.get("reason")), None)
                failure_details = {"stage": stage, "family": group["family"],
                    "selected_rows": len(result.get("selected", [])),
                    "selected_maps": len({row["canonical"] for row in result.get("selected", [])}),
                    "evidence_rows": len(evidence), "reason_counts": dict(reason_counts),
                    "rejected_maps": len(rejected_maps), "committed_maps": len(committed_maps),
                    "last_failed_prefix": last_failed, "profile": result.get("profile")}
                if last_failed:
                    for row in last_failed.get("accepted_rows", []):
                        sample_groups[(proposal, stage + "_failed_prefix", group["family"], row["length"])].append(row)

    disjoint = True
    seen: set[bytes] = set()
    for stage in STAGES:
        if seen & identity_sets.get(stage, set()):
            disjoint = False
        seen |= identity_sets.get(stage, set())
    proposal_reports[pkey] = {"window": next(row["window"] for row in ranking["retained"] if row["window_start"] == proposal),
        "quota": next(row["quota"] for row in ranking["retained"] if row["window_start"] == proposal),
        "summary_stages": summary["proposals"][pkey]["stages"], "support_entries": len(support),
        "support_hash_ok": support_ok, "metadata_errors": metadata_errors,
        "cross_stage_identities_disjoint": disjoint, "stage_counts": stage_counts,
        "failure": failure_details, "training_profile": training.get("profile")}
    if not support_ok or metadata_errors or not disjoint:
        errors.append(f"proposal {proposal} scientific artifact invariant failed")

# Deterministic stratified sample, at most 60 distinct selected/failure-prefix rows.
sample_rows: list[tuple[tuple, dict]] = []
for key in sorted(sample_groups, key=repr):
    rows = sorted(sample_groups[key], key=lambda row: (row["map_id"], row["start"], row["goal"]))
    for row in (rows[0], rows[-1]) if len(rows) > 1 else (rows[0],):
        identity = (key, row["canonical"], row["start"], row["goal"])
        if not any(old[0] == identity for old in sample_rows):
            sample_rows.append((identity, row))
sample_rows = sample_rows[:60]

oracle_results = []
for identity, row in sample_rows:
    proposal = identity[0][0]
    training = load(f"proposal-{proposal}-training.json")["result"]
    support_set = frozenset(training["support"])
    source = by_canonical[row["canonical"]]
    distance, counts = data.bfs_counts(source["walls"], row["goal"], 12)
    routes = tuple(data.enumerate_routes(row["start"], row["goal"], source["walls"], 12))
    novel = sum(data.signature(route) not in support_set for route in routes)
    expected_novel = row.get("Mnovel")
    ok = distance.get(row["start"]) == row["length"] and counts.get(row["start"]) == row["M"] == len(routes)
    if expected_novel is not None:
        ok = ok and novel == expected_novel
    oracle_results.append({"proposal": proposal, "stage": identity[0][1], "family": row["family"],
        "map_id": row["map_id"], "length": row["length"], "M": row["M"],
        "Mnovel_saved": expected_novel, "Mnovel_recomputed": novel, "ok": ok})
    if not ok:
        errors.append(f"oracle sample mismatch proposal={proposal} map={row['map_id']}")

# Up to 32 deterministic q states spread over proposals.
q_results = []
for proposal in (12, 14, 16):
    training = load(f"proposal-{proposal}-training.json")["result"]
    states = sorted(training["states"].items(), key=lambda pair: repr(pair[0]))
    picks = states[::max(1, len(states)//11)][:11]
    for (canonical, node, goal), saved_q in picks:
        source = by_canonical[canonical]
        recomputed = q_target(node, source["walls"], goal, 12)
        ok = all(abs(saved_q.get(action, 0.0) - recomputed.get(action, 0.0)) <= 1e-12 for action in range(4))
        q_results.append({"proposal": proposal, "map_id": source["map_id"], "node": node, "goal": goal, "ok": ok})
        if not ok:
            errors.append(f"q sample mismatch proposal={proposal} map={source['map_id']}")
q_results = q_results[:32]

# Ledger uniqueness/arithmetic before adding this audit row.
ledger_rows = [json.loads(line) for line in LEDGER.read_text().splitlines() if line.strip()]
ids = [row.get("entry_id") for row in ledger_rows]
operational_before = sum(float(row.get("carried_budget_debit_seconds", 0.0)) +
                         float(row.get("charged_seconds", 0.0)) + float(row.get("budget_allowance_seconds", 0.0))
                         for row in ledger_rows)
checks["ledger"] = {"unique_entry_ids": len(ids) == len(set(ids)), "production_entry_count": ids.count(attempt["entry_id"]),
                    "operational_sum_before_audit": operational_before,
                    "production_charged_plus_allowance": attempt["charged_seconds"] + attempt["budget_allowance_seconds"]}

report = {"audit_version": 1, "attempt": str(ATTEMPT.relative_to(ROOT)),
          "outcome": summary["outcome"], "checks": checks, "proposals": proposal_reports,
          "oracle_sample": {"pairs_checked": len(oracle_results), "all_ok": all(row["ok"] for row in oracle_results),
                            "rows": oracle_results},
          "q_sample": {"states_checked": len(q_results), "all_ok": all(row["ok"] for row in q_results), "rows": q_results},
          "limitations": ["No pool, inventory, proposal, or selection was regenerated.",
                          "Oracle replay is limited to the deterministic saved-row sample shown (maximum 60 pairs) and 32 q states.",
                          "All saved selected rows were metadata-linked, but only sampled rows received independent BFS/route/novelty replay."],
          "errors": errors}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(_json(report), sort_keys=True, indent=2) + "\n", encoding="utf-8")

elapsed = time.perf_counter() - START
entry_id = str(uuid.uuid4())
ledger_record = {"entry_id": entry_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                 "kind": "independent_results_audit", "stage": "v3_feasibility_001",
                 "charged_seconds": elapsed, "budget_allowance_seconds": 3.0,
                 "exit_code": 0 if not errors else 2,
                 "command": ".venv/bin/python execution/next_level_v3/audit_feasibility_001.py",
                 "output_sha256": sha(OUT),
                 "note": "Full in-script elapsed plus 3s conservative allowance for interpreter startup and two prior read-only inspection commands; no regeneration."}
_append_ledger(ledger_record, LEDGER)
print(json.dumps({"output": str(OUT.relative_to(ROOT)), "sha256": sha(OUT), "entry_id": entry_id,
                  "elapsed_seconds": elapsed, "allowance_seconds": 3.0, "errors": errors,
                  "pairs_checked": len(oracle_results), "q_states_checked": len(q_results)}, sort_keys=True))
raise SystemExit(0 if not errors else 2)
