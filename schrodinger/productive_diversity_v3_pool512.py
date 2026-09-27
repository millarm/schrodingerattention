"""Additive, frozen pool-512 dataset runner configuration."""
from __future__ import annotations
import argparse
import hashlib
import os
import platform
import sys
from pathlib import Path
from typing import Callable
from schrodinger import productive_diversity_v3_data as data
from schrodinger import productive_diversity_v3_runner as base

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "execution/next_level_v3_pool512/ledger.jsonl"
LOCK = ROOT / "execution/next_level_v3_pool512/runner.lock"
REJECTIONS = ROOT / "execution/next_level_v3_pool512/rejections"
POOL_LIMIT, POOL_TRIALS = 512, 200_000
Attempt, RunnerError, Deadline, ProposalStatuses = base.Attempt, base.RunnerError, base.Deadline, base.ProposalStatuses

def pool512(family: str) -> data.PoolResult:
    return data.pool_family(family, n=12, limit=POOL_LIMIT, max_trials=POOL_TRIALS)

def budget_priors() -> tuple[float, float]:
    return base._prior(LEDGER, require_carry=True)

def deadline_seconds() -> float:
    stage, global_total = budget_priors()
    return min(base.STAGE_CAP_SECONDS-stage, base.GLOBAL_CAP_SECONDS-global_total)-base.STARTUP_ALLOWANCE_SECONDS-base.FINALIZATION_RESERVE_SECONDS-base.AUDIT_RESERVE_SECONDS

def _source_hashes() -> dict[str, str]:
    """Only immutable provenance inputs; the live pool512 ledger is excluded."""
    paths = {ROOT / relative for relative in base._source_hashes()}
    paths |= {ROOT / "schrodinger/productive_diversity_v3_pool512.py", ROOT / "tests/test_productive_diversity_v3_pool512.py", ROOT / "productive_diversity_v3_pool512_plan.md", ROOT / "execution/next_level_v3/ledger.jsonl", ROOT / "execution/next_level_v3/attempts/feasibility-001/manifest.json"}
    paths |= set((ROOT / "execution/next_level_v3_pool512/specs").glob("*.md")) | set((ROOT / "execution/next_level_v3_pool512/reviews").glob("*.md"))
    missing = [str(path) for path in paths if not path.exists()]
    if missing: raise RunnerError("mandatory pool512 provenance input missing: " + ", ".join(sorted(missing)))
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}

def _save(attempt: Attempt, name: str, value: object) -> str:
    return base._save(attempt, name, value)

def _validate_pass(result, records, counts, train_maps_per_family, ranking) -> None:
    base._validate_pass(result, records, counts, train_maps_per_family, ranking)

def execute_pipeline(attempt: Attempt, *, pools_fn: Callable[[str], data.PoolResult] = pool512,
                     assemble_fn: Callable[..., tuple[dict[str, object], ...]] = data.assemble_global_inventory,
                     rank_fn: Callable[..., dict[str, object]] = data.rank_proposals,
                     config: data.SelectionConfig | None = None, counts: dict[str, int] | None = None) -> dict[str, object]:
    """Accepted orchestration copied locally; only pool configuration differs."""
    config = config or data.SelectionConfig((12, 13, 14), (6, 5, 5), 32)
    counts = counts or {"val_routine": 12, "val_mixed": 8, "test_routine": 48, "test_mixed": 32}
    pools = {}; records = (); ranking = {}; stage_hashes = {}; output_hashes = {}; reached = []; statuses = ProposalStatuses()
    def on_stage(name, payload):
        proposal = payload["proposal"]; filename = f"proposal-{proposal}-{name}.json"
        try:
            stage_hashes[filename] = _save(attempt, filename, payload); reached.append(filename)
            statuses.observe(proposal, name, payload, filename, stage_hashes[filename])
        except BaseException:
            statuses.failed_write(proposal, name); raise
    result = None; error = None
    try:
        for family in data.FAMILIES:
            pools[family] = pools_fn(family)
            name = f"pool-{family}.json"; output_hashes[name] = _save(attempt, name, pools[family]); reached.append(name)
        records = assemble_fn(pools); data.validate_inventory_records(records)
        output_hashes["inventory.json"] = _save(attempt, "inventory.json", records); reached.append("inventory.json")
        ranking = rank_fn(records)
        output_hashes["ranking.json"] = _save(attempt, "ranking.json", ranking); reached.append("ranking.json")
        statuses = ProposalStatuses(tuple(item["window_start"] for item in ranking.get("retained", ())[:3]))
        result = data.run_ranked_proposals(ranking, records, config=config, counts=counts, on_stage=on_stage)
        _validate_pass(result, records, counts, config.train_maps_per_family, ranking)
        output_hashes["result.json"] = _save(attempt, "result.json", result); reached.append("result.json")
    except BaseException as caught:
        error = caught
    finally:
        for path in sorted(attempt.output.glob("*.json")):
            if path.name not in {"manifest.json", "summary.json", "attempt.json"}: output_hashes.setdefault(path.name, hashlib.sha256(path.read_bytes()).hexdigest())
        selected = result.get("proposal") if result else None
        effective = {"n":12, "families":data.FAMILIES, "shape_components":8, "family_composition":{f:{"I":f.count("I"),"L":f.count("L")} for f in data.FAMILIES}, "seeds":{"pool":data.POOL_SEED,"shortlist":data.SHORTLIST_SEED,"split":data.SPLIT_SEED,"family_codes":data.FAMILY_CODE}, "selection":{"window":selected.get("window") if selected else None,"quota":selected.get("quota") if selected else None,"train_maps_per_family":config.train_maps_per_family,"counts":counts}, "pool":{"limit":POOL_LIMIT,"max_trials":POOL_TRIALS,"direct_placements":"cached n12 I/L"}, "shortlist_cap":64, "ranking_windows":data.WINDOWS,"ranking_quotas":data.QUOTAS,"support":"all nonempty canonical suffixes","novelty":"routine=0; challenge>=4 and 1/4..3/4", "budget":{"stage":base.STAGE_CAP_SECONDS,"global":base.GLOBAL_CAP_SECONDS,"startup":base.STARTUP_ALLOWANCE_SECONDS,"reserve":base.FINALIZATION_RESERVE_SECONDS,"audit_reserve":base.AUDIT_RESERVE_SECONDS,"stage_prior":attempt.stage_prior,"global_prior":attempt.global_prior}}
        outcome = result.get("outcome") if result is not None and error is None else ("DEADLINE_FAILED" if isinstance(error, Deadline) else "TECHNICAL_FAILED")
        manifest = {"effective_config":effective,"argv":list(getattr(sys,"orig_argv",sys.argv)),"executable":sys.executable,"runtime":{"python":sys.version,"numpy":__import__("numpy").__version__,"pid":os.getpid(),"platform":platform.platform(),"cpu":platform.processor() or platform.machine(),"threads":{key:os.environ.get(key) for key in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS")}},"sources":_source_hashes(),"outputs":{**output_hashes,**stage_hashes},"reached":reached,"outcome":outcome,"error":None if error is None else repr(error)}
        finalization_error = None
        try:
            attempt.manifest_sha256 = _save(attempt, "manifest.json", manifest)
            _save(attempt, "summary.json", {"outcome":manifest["outcome"],"manifest_sha256":attempt.manifest_sha256,"reached":reached,"proposals":statuses.finalize(error is not None),"error":manifest["error"]})
        except BaseException as caught: finalization_error = caught
        if finalization_error is not None:
            if error is not None: raise error from finalization_error
            raise finalization_error
    if error is not None: raise error
    assert result is not None
    return result

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", required=True); args = parser.parse_args(argv)
    budget_priors()
    with Attempt(Path(args.output), lock=LOCK, ledger=LEDGER, rejections=REJECTIONS) as attempt: result = execute_pipeline(attempt)
    print(base.json.dumps({"outcome":result["outcome"],"output":str(args.output),"manifest_sha256":attempt.manifest_sha256},sort_keys=True,separators=(",",":"),allow_nan=False))

if __name__ == "__main__": main()
