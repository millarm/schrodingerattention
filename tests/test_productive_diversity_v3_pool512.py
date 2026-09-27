import hashlib
import json
from pathlib import Path
import pytest
from schrodinger import productive_diversity_v3_data as data
from schrodinger import productive_diversity_v3_pool512 as ext
from schrodinger import productive_diversity_v3_runner as base
from tests.test_productive_diversity_v3_runner import _eight_records

def _ledger(path, *rows): path.write_text("".join(json.dumps(row)+"\n" for row in rows))
def _attempt(tmp_path, **kwargs):
    options={"lock":tmp_path/"lock","ledger":tmp_path/"ledger.jsonl","rejections":tmp_path/"rejections"}; options.update(kwargs)
    return ext.Attempt(tmp_path/"out", **options)
def _fixture():
    records=_eight_records()
    pools={f:data.PoolResult(f,tuple(r["canonical"] for r in records if r["family"]==f),0,0,0,0) for f in data.FAMILIES}
    return records,pools,{"retained":({"window_start":12,"window":(12,13,14),"quota":(1,1,1)},)},data.SelectionConfig((12,13,14),(1,1,1),1),{"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1}

def test_real_small_pool_prefix_subset_and_default_512_arguments(monkeypatch):
    calls=[]
    real_pool_family=data.pool_family
    monkeypatch.setattr(ext.data,"pool_family",lambda family,**kwargs:calls.append((family,kwargs)) or data.PoolResult(family,(),0,0,0,0))
    ext.pool512("IIIIIIII")
    assert calls == [("IIIIIIII",{"n":12,"limit":512,"max_trials":200000})]
    for family in data.FAMILIES:
        two=real_pool_family(family,n=12,limit=2,max_trials=200000); four=real_pool_family(family,n=12,limit=4,max_trials=200000)
        assert len(two.maps)==2 and len(four.maps)==4 and set(two.maps)<=set(four.maps)
        common=min(len(two.draw_prefix),len(four.draw_prefix)); assert two.draw_prefix[:common]==four.draw_prefix[:common]

def test_genuine_eight_map_fixture_passes_primary_512_manifest_with_provenance(tmp_path):
    records,pools,ranking,config,counts=_fixture(); root=Path(__file__).resolve().parents[1]
    old_manifest=(root/"execution/next_level_v3/attempts/feasibility-001/manifest.json").read_bytes()
    old_inputs={relative:hashlib.sha256((root/relative).read_bytes()).hexdigest() for relative in ("schrodinger/productive_diversity_v3_data.py","schrodinger/productive_diversity_v3_runner.py","productive_diversity_v3_plan.md","agent_execution_protocol.md","execution/next_level_v3/ledger.jsonl")}
    with _attempt(tmp_path) as attempt: result=ext.execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,config=config,counts=counts)
    out=tmp_path/"out"; manifest=json.loads((out/"manifest.json").read_text()); summary=json.loads((out/"summary.json").read_text())
    assert result["outcome"]==summary["outcome"]=="FIRST_FULL_DATASET_PASS"
    assert manifest["effective_config"]["pool"]=={"limit":512,"max_trials":200000,"direct_placements":"cached n12 I/L"}
    expected=set(base._source_hashes())|{"schrodinger/productive_diversity_v3_pool512.py","tests/test_productive_diversity_v3_pool512.py","productive_diversity_v3_pool512_plan.md","execution/next_level_v3/ledger.jsonl","execution/next_level_v3/attempts/feasibility-001/manifest.json"}
    expected|={str(path.relative_to(root)) for directory in (root/"execution/next_level_v3_pool512/specs",root/"execution/next_level_v3_pool512/reviews") for path in directory.glob("*.md")}
    assert set(manifest["sources"])==expected and "execution/next_level_v3_pool512/ledger.jsonl" not in manifest["sources"]
    assert (root/"execution/next_level_v3/attempts/feasibility-001/manifest.json").read_bytes()==old_manifest
    assert {relative:hashlib.sha256((root/relative).read_bytes()).hexdigest() for relative in old_inputs}==old_inputs
    for relative,digest in manifest["sources"].items(): assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest
    assert {family:len(json.loads((out/f"pool-{family}.json").read_text())["maps"]) for family in data.FAMILIES}=={"IIIIIIII":3,"LLLLLLLL":3,"IIIILLLL":2}
    assert sum(len(json.loads((out/f"pool-{family}.json").read_text())["maps"]) for family in data.FAMILIES)==8 != manifest["effective_config"]["pool"]["limit"]
    assert set(summary["proposals"]["12"]["artifacts"])==set(base.STAGE_ORDER)

def test_ledger_carry_deadline_and_isolated_rejections(tmp_path,monkeypatch):
    carry={"entry_id":"carry","carried_budget_debit_seconds":443.384519002,"budget_allowance_seconds":301.747054625}; ledger=tmp_path/"ledger.jsonl"; _ledger(ledger,carry)
    assert base._prior(ledger,require_carry=True)==(301.747054625,745.131573627)
    monkeypatch.setattr(ext,"LEDGER",ledger)
    assert ext.deadline_seconds()==pytest.approx(1146.252945375)
    _ledger(ledger,{"entry_id":"missing"})
    with pytest.raises(ext.RunnerError,match="exactly one carried"): base._prior(ledger,require_carry=True)
    _ledger(ledger,carry,{**carry,"entry_id":"carry2"})
    with pytest.raises(ext.RunnerError,match="exactly one carried"): base._prior(ledger,require_carry=True)
    old=Path(__file__).resolve().parents[1]/"execution/next_level_v3/ledger.jsonl"; before=old.read_bytes(); busy=tmp_path/"busy"; busy.write_text("x")
    with pytest.raises(FileExistsError):
        with _attempt(tmp_path,ledger=tmp_path/"local.jsonl",rejections=tmp_path/"rejects",lock=busy): pass
    assert old.read_bytes()==before and (tmp_path/"local.jsonl").exists()

def test_scientific_failure_and_interruption_preserve_statuses(tmp_path,monkeypatch):
    records,pools,ranking,config,counts=_fixture(); counts["val_routine"]=3
    with _attempt(tmp_path/"scientific") as attempt: result=ext.execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,config=config,counts=counts)
    assert result["outcome"]=="DATASET_CONSTRUCTION_FAILED"
    states=json.loads((tmp_path/"scientific/out/summary.json").read_text())["proposals"]["12"]["stages"]
    assert states=={"training":"COMPLETE","validation_routine":"SCIENTIFIC_HELDOUT_SUPPLY_FAILED","validation_mixed":"NOT_EVALUATED","test_routine":"NOT_EVALUATED","test_mixed":"NOT_EVALUATED"}
    records,pools,ranking,config,counts=_fixture(); original=data.run_ranked_proposals
    def interrupted(*args,on_stage=None,**kwargs):
        def callback(name,payload):
            on_stage(name,payload)
            if name=="training": raise ext.Deadline("injected")
        return original(*args,on_stage=callback,**kwargs)
    monkeypatch.setattr(ext.data,"run_ranked_proposals",interrupted)
    with pytest.raises(ext.Deadline,match="injected"):
        with _attempt(tmp_path/"interrupt") as attempt: ext.execute_pipeline(attempt,pools_fn=lambda f:pools[f],assemble_fn=lambda _:records,rank_fn=lambda _:ranking,config=config,counts=counts)
    summary=json.loads((tmp_path/"interrupt/out/summary.json").read_text())
    assert summary["outcome"]=="DEADLINE_FAILED"
    assert summary["proposals"]["12"]["stages"]=={"training":"COMPLETE","validation_routine":"NOT_COMPLETED_UNKNOWN","validation_mixed":"NOT_EVALUATED","test_routine":"NOT_EVALUATED","test_mixed":"NOT_EVALUATED"}
