"""Regenerate the pool-512 route data from the frozen pipeline and check it.

The large training and inventory files are excluded from git. This reruns the
repository's own deterministic pipeline (``productive_diversity_v3_data``) and
compares every output with the committed manifest. Pools, inventory and ranking
match byte-for-byte. Proposal files differ only in a wall-clock profiling
field (``elapsed_seconds``). The training content is then verified separately
with ``verify_training_bank.py``.

Usage: python execution/classical_leads/regenerate_route_data.py OUTPUT_DIR
"""
import hashlib, json, sys, time
from pathlib import Path
sys.path.insert(0, "/home/user/schrodingerattention")
from schrodinger import productive_diversity_v3_data as data
from schrodinger.productive_diversity_v3_runner import write_json
OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
ATT = Path("/home/user/schrodingerattention/execution/next_level_v3_pool512/attempts/feasibility-001")
expected = json.loads((ATT / "manifest.json").read_text())["outputs"]
t = time.time(); pools = {}
for family in data.FAMILIES:
    pools[family] = data.pool_family(family, n=12, limit=512, max_trials=200_000)
    h = write_json(OUT / f"pool-{family}.json", pools[family])
    print(family, "pool hash match:", h == expected[f"pool-{family}.json"], f"{time.time()-t:.0f}s", flush=True)
records = data.assemble_global_inventory(pools); data.validate_inventory_records(records)
print("inventory", write_json(OUT / "inventory.json", records) == expected.get("inventory.json"), f"{time.time()-t:.0f}s", flush=True)
ranking = data.rank_proposals(records)
print("ranking", write_json(OUT / "ranking.json", ranking) == expected["ranking.json"], flush=True)
def on_stage(name, payload):
    fn = f"proposal-{payload['proposal']}-{name}.json"
    h = write_json(OUT / fn, payload)
    print(fn, "match:", h == expected.get(fn), f"{time.time()-t:.0f}s", flush=True)
config = data.SelectionConfig((12, 13, 14), (6, 5, 5), 32)
counts = {"val_routine": 12, "val_mixed": 8, "test_routine": 48, "test_mixed": 32}
result = data.run_ranked_proposals(ranking, records, config=config, counts=counts, on_stage=on_stage)
print("outcome", result.get("outcome"), f"{time.time()-t:.0f}s")
