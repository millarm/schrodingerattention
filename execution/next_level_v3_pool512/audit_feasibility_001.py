"""Bounded read-only audit of the frozen pool512 feasibility attempt."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib, json, time, uuid
from pathlib import Path

from schrodinger import productive_diversity_v3_data as data
from schrodinger.productive_diversity_v3_runner import _append_ledger, _json
from schrodinger.route_feasibility import q_target

START = time.perf_counter()
ROOT = Path(__file__).resolve().parents[2]
ATTEMPT = ROOT / "execution/next_level_v3_pool512/attempts/feasibility-001"
OLD = ROOT / "execution/next_level_v3/attempts/feasibility-001"
OUT = ROOT / "execution/next_level_v3_pool512/audits/feasibility-001-audit.json"
LEDGER = ROOT / "execution/next_level_v3_pool512/ledger.jsonl"
STAGES = ("training", "validation_routine", "validation_mixed", "test_routine", "test_mixed")

def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def freeze(value):
    if isinstance(value, list): return tuple(freeze(x) for x in value)
    if isinstance(value, dict): return tuple(sorted((k, freeze(v)) for k, v in value.items()))
    return value
def decode(value):
    if isinstance(value, dict):
        if set(value) == {"bytes_hex"}: return bytes.fromhex(value["bytes_hex"])
        return {k: decode(v) for k, v in value.items()}
    if isinstance(value, list):
        if value and all(isinstance(x, dict) and set(x) == {"key", "value"} for x in value):
            return {freeze(decode(x["key"])): decode(x["value"]) for x in value}
        return [decode(x) for x in value]
    return value
def load(directory: Path, name: str): return decode(json.loads((directory / name).read_text()))

manifest = load(ATTEMPT, "manifest.json")
summary = load(ATTEMPT, "summary.json")
attempt = load(ATTEMPT, "attempt.json")
inventory = tuple(load(ATTEMPT, "inventory.json"))
ranking = load(ATTEMPT, "ranking.json")
errors: list[str] = []
checks: dict[str, object] = {}

# Provenance, execution, and exact byte bindings.
manifest_sha = sha(ATTEMPT / "manifest.json")
checks["manifest_sha256"] = manifest_sha
checks["manifest_expected"] = manifest_sha == "305a9dd782befa9209942a2f52ebc0ba31d9d7ca61c913ecfb69fa5cca466395"
checks["attempt_binding"] = attempt.get("manifest_sha256") == manifest_sha
checks["attempt_complete"] = attempt.get("status") == "COMPLETE" and attempt.get("error") is None
checks["summary"] = {"outcome": summary.get("outcome"), "error": summary.get("error")}
checks["effective_pool"] = manifest["effective_config"]["pool"]
bad_outputs = {p: {"saved": d, "actual": sha(ATTEMPT / p)} for p, d in manifest["outputs"].items() if sha(ATTEMPT / p) != d}
bad_sources = {p: {"saved": d, "actual": sha(ROOT / p)} for p, d in manifest["sources"].items() if sha(ROOT / p) != d}
checks["output_hash_mismatches"] = bad_outputs
checks["source_hash_mismatches"] = bad_sources
if not all((checks["manifest_expected"], checks["attempt_binding"], checks["attempt_complete"])) or bad_outputs or bad_sources:
    errors.append("execution/provenance binding mismatch")
if manifest["effective_config"]["pool"].get("limit") != 512 or summary.get("outcome") != "FIRST_FULL_DATASET_PASS":
    errors.append("pool512 config or PASS outcome mismatch")

# Exact old-pool inclusion and common bounded RNG draw-prefix equality.
pool_report = {}
for family in data.FAMILIES:
    new = load(ATTEMPT, f"pool-{family}.json"); old = load(OLD, f"pool-{family}.json")
    old_maps, new_maps = set(old["maps"]), set(new["maps"])
    common = min(len(old["draw_prefix"]), len(new["draw_prefix"]))
    row = {"old_maps": len(old_maps), "new_maps": len(new_maps), "old_subset": old_maps <= new_maps,
           "common_draw_prefix_rows": common, "draw_prefix_equal": old["draw_prefix"][:common] == new["draw_prefix"][:common],
           "new_trials": new["trials"], "new_rejections": {k: new[f"rejected_{k}"] for k in ("overlap", "touching", "duplicate")}}
    pool_report[family] = row
    if len(old_maps) != 256 or len(new_maps) != 512 or not row["old_subset"] or not row["draw_prefix_equal"]:
        errors.append(f"pool prefix/inclusion mismatch {family}")
checks["pool_expansion"] = pool_report

# Inventory validation and exact ranking replay from the saved inventory only.
data.validate_inventory_records(inventory)
families = Counter(row["family"] for row in inventory)
checks["inventory"] = {"rows": len(inventory), "families": dict(families),
                       "unique_ids": len({r["map_id"] for r in inventory}),
                       "unique_canonical": len({r["canonical"] for r in inventory})}
recomputed = data.rank_proposals(inventory)
checks["ranking_exact"] = _json(recomputed) == _json(ranking)
checks["retained_windows"] = [r["window_start"] for r in ranking["retained"]]
if families != Counter({f: 512 for f in data.FAMILIES}) or len(inventory) != 1536 or not checks["ranking_exact"]:
    errors.append("inventory/ranking mismatch")

by_canonical = {r["canonical"]: r for r in inventory}
sample_groups: dict[tuple, list[dict]] = defaultdict(list)
proposal_reports = {}
expected = {"training": (1024, 64), "validation_routine": (384, 24), "validation_mixed": (128, 8),
            "test_routine": (1536, 96), "test_mixed": (512, 32)}

for proposal in (12, 14):
    available = {stage: load(ATTEMPT, f"proposal-{proposal}-{stage}.json") for stage in STAGES}
    training = available["training"]["result"]
    support = tuple(training["support"])
    encoded = b"".join(len(x).to_bytes(2, "big") + x for x in support)
    support_ok = hashlib.sha256(encoded).hexdigest() == training["support_hash"]
    metadata_errors = []; ids_by_stage = {}; stage_counts = {}; per_map_errors = []
    proposal_row = next(r for r in ranking["retained"] if r["window_start"] == proposal)
    lengths, quota = tuple(proposal_row["window"]), tuple(proposal_row["quota"])

    def validate_rows(rows, stage):
        per_map = defaultdict(list)
        for row in rows:
            source = by_canonical.get(row["canonical"])
            if source is None or (row["map_id"], row["family"], row["n"]) != (source["map_id"], source["family"], 12):
                metadata_errors.append(f"{stage}:identity"); continue
            pair = (row["start"], row["goal"], row["length"], row["M"])
            retained = source["shortlists"].get(row["length"], {}).get("retained", ())
            if pair not in (tuple(x) for x in retained): metadata_errors.append(f"{stage}:pair")
            per_map[row["canonical"]].append(row)
            sample_groups[(proposal, stage, row["family"], row["length"])].append(row)
        for canonical, map_rows in per_map.items():
            if len(map_rows) != sum(quota) or any(sum(r["length"] == length for r in map_rows) != need for length, need in zip(lengths, quota)):
                per_map_errors.append(f"{stage}:{by_canonical[canonical]['map_id']}")

    train_rows = list(training["selected"]); validate_rows(train_rows, "training")
    ids_by_stage["training"] = {r["canonical"] for r in train_rows}
    stage_counts["training"] = {"rows": len(train_rows), "maps": len(ids_by_stage["training"]), "families": dict(Counter(r["family"] for r in train_rows))}
    failure = None
    for stage in STAGES[1:]:
        groups = available[stage].get("results", [])
        rows = [r for group in groups for r in group["result"].get("selected", [])]
        validate_rows(rows, stage); ids_by_stage[stage] = {r["canonical"] for r in rows}
        stage_counts[stage] = {"rows": len(rows), "maps": len(ids_by_stage[stage]),
            "families": {g["family"]: {"outcome": g["result"]["outcome"], "rows": len(g["result"].get("selected", [])),
                         "maps": len({r["canonical"] for r in g["result"].get("selected", [])})} for g in groups}}
        for group in groups:
            result = group["result"]
            if result["outcome"] == "SCIENTIFIC_HELDOUT_SUPPLY_FAILED":
                failed = next((x for x in reversed(result["evidence"]) if x.get("reason")), None)
                failure = {"stage": stage, "family": group["family"], "selected_rows": len(result.get("selected", [])),
                           "selected_maps": len({r["canonical"] for r in result.get("selected", [])}),
                           "last_failed_prefix": failed}
                for r in (failed or {}).get("accepted_rows", []): sample_groups[(proposal, stage+"_failed_prefix", r["family"], r["length"])].append(r)
    seen = set(); disjoint = True
    for stage in STAGES:
        disjoint &= not bool(seen & ids_by_stage.get(stage, set())); seen |= ids_by_stage.get(stage, set())
    statuses = summary["proposals"][str(proposal)]["stages"]
    proposal_reports[str(proposal)] = {"window": lengths, "quota": quota, "support_entries": len(support),
        "support_hash_ok": support_ok, "metadata_errors": metadata_errors, "per_map_quota_errors": per_map_errors,
        "cross_stage_disjoint": disjoint, "stage_counts": stage_counts, "statuses": statuses, "failure": failure}
    if not support_ok or metadata_errors or per_map_errors or not disjoint: errors.append(f"proposal{proposal} invariant mismatch")

# Selected proposal exact stage cardinalities and status semantics; proposal16 is intentionally artifact-free.
for stage, (rows, maps) in expected.items():
    got = proposal_reports["14"]["stage_counts"][stage]
    if (got["rows"], got["maps"]) != (rows, maps): errors.append(f"selected proposal count mismatch {stage}")
if any(v != "COMPLETE" for v in summary["proposals"]["14"]["stages"].values()): errors.append("selected proposal status mismatch")
if summary["proposals"]["12"]["stages"]["validation_mixed"] != "SCIENTIFIC_HELDOUT_SUPPLY_FAILED": errors.append("proposal12 failure status mismatch")
if summary["proposals"]["16"]["artifacts"] or any(v != "NOT_EVALUATED" for v in summary["proposals"]["16"]["stages"].values()): errors.append("proposal16 unattempted status mismatch")

# Deterministic stratified oracle sample, capped at 60, including p12 failed prefix and selected p14.
samples = []
for key in sorted(sample_groups, key=repr):
    rows = sorted(sample_groups[key], key=lambda r: (r["map_id"], r["start"], r["goal"]))
    for row in ((rows[0], rows[-1]) if len(rows) > 1 else (rows[0],)):
        ident = (key, row["canonical"], row["start"], row["goal"])
        if not any(x[0] == ident for x in samples): samples.append((ident, row))
samples = samples[:60]
oracle = []
for ident, row in samples:
    proposal, stage = ident[0][0], ident[0][1]
    support = frozenset(load(ATTEMPT, f"proposal-{proposal}-training.json")["result"]["support"])
    source = by_canonical[row["canonical"]]
    distance, counts = data.bfs_counts(source["walls"], row["goal"], 12)
    routes = tuple(data.enumerate_routes(row["start"], row["goal"], source["walls"], 12))
    novel = sum(data.signature(route) not in support for route in routes)
    ok = distance.get(row["start"]) == row["length"] and counts.get(row["start"]) == row["M"] == len(routes)
    if row.get("Mnovel") is not None: ok &= novel == row["Mnovel"]
    oracle.append({"proposal": proposal, "stage": stage, "family": row["family"], "map_id": row["map_id"],
                   "length": row["length"], "M": row["M"], "saved_novel": row.get("Mnovel"), "recomputed_novel": novel, "ok": bool(ok)})
    if not ok: errors.append(f"oracle mismatch p{proposal}/map{row['map_id']}")

# 32 selected-proposal q states; p12's support is sampled above via failed-prefix rows.
q_rows = []
states = sorted(load(ATTEMPT, "proposal-14-training.json")["result"]["states"].items(), key=lambda x: repr(x[0]))
for (canonical, node, goal), saved in states[::max(1, len(states)//32)][:32]:
    source = by_canonical[canonical]; recomputed = q_target(node, source["walls"], goal, 12)
    ok = all(abs(saved.get(a, 0.0) - recomputed.get(a, 0.0)) <= 1e-12 for a in range(4))
    q_rows.append({"map_id": source["map_id"], "node": node, "goal": goal, "ok": ok})
    if not ok: errors.append(f"q mismatch map{source['map_id']}")

ledger_rows = [json.loads(x) for x in LEDGER.read_text().splitlines() if x.strip()]
ids = [x.get("entry_id") for x in ledger_rows]
operational = sum(float(x.get("carried_budget_debit_seconds", 0)) + float(x.get("charged_seconds", 0)) + float(x.get("budget_allowance_seconds", 0)) for x in ledger_rows)
checks["ledger"] = {"unique_ids": len(ids) == len(set(ids)), "production_entry_count": ids.count(attempt["entry_id"]), "operational_before_audit": operational}
if not checks["ledger"]["unique_ids"] or checks["ledger"]["production_entry_count"] != 1: errors.append("ledger uniqueness/binding mismatch")

report = {"audit_version": 1, "attempt": str(ATTEMPT.relative_to(ROOT)), "outcome": summary["outcome"],
          "checks": checks, "proposals": proposal_reports,
          "oracle_sample": {"pairs_checked": len(oracle), "all_ok": all(x["ok"] for x in oracle), "rows": oracle},
          "q_sample": {"states_checked": len(q_rows), "all_ok": all(x["ok"] for x in q_rows), "rows": q_rows},
          "limitations": ["No pool, inventory, ranking, proposal, or selection was regenerated.",
                          "All selected rows were linked and quota-checked; independent route/novelty replay is limited to the displayed deterministic sample of at most 60 pairs.",
                          "Independent q replay is limited to 32 selected-proposal states."], "errors": errors}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(_json(report), sort_keys=True, indent=2) + "\n")
elapsed = time.perf_counter() - START
entry_id = str(uuid.uuid4())
record = {"entry_id": entry_id, "recorded_at_utc": datetime.now(timezone.utc).isoformat(), "kind": "independent_results_audit",
          "stage": "pool512_feasibility_001", "charged_seconds": elapsed, "budget_allowance_seconds": 3.0,
          "exit_code": 0 if not errors else 2, "command": "env PYTHONPATH=. .venv/bin/python execution/next_level_v3_pool512/audit_feasibility_001.py",
          "output_sha256": sha(OUT), "note": "Full in-script wall plus 3s startup/static-inspection allowance; saved artifacts only, no regeneration."}
_append_ledger(record, LEDGER)
print(json.dumps({"output": str(OUT.relative_to(ROOT)), "sha256": sha(OUT), "entry_id": entry_id,
                  "recorded_at_utc": record["recorded_at_utc"], "elapsed_seconds": elapsed, "allowance_seconds": 3.0,
                  "errors": errors, "pairs_checked": len(oracle), "q_states_checked": len(q_rows)}, sort_keys=True))
raise SystemExit(0 if not errors else 2)
