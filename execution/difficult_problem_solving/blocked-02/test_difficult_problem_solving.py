import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

MODULE=Path(__file__).parents[1]/"execution"/"difficult_problem_solving"/"analyze.py"
spec=importlib.util.spec_from_file_location("d0",MODULE); d0=importlib.util.module_from_spec(spec); spec.loader.exec_module(d0)
def attempts(valid): return [{"valid":x,"route":bytes([i%3])} for i,x in enumerate(valid)]
def test_bags_prefixes_duplicates_and_impossible_terms():
 assert d0.choose(2,3)==0 and d0.bag(0,{},1)["pass"]==0 and d0.bag(32,{b"a":32},32)["pass"]==1
 x=d0.metric(attempts([True,True,False]+[False]*29),4)
 assert x["bag"]["1"]["pass"]==2/32 and x["bag"]["32"]["pass"]==1
 assert x["duplicate_concentration"]==.5 and x["prefix"]["2"]["pass"]==1 and x["prefix"]["2"]["Q"]==1
 z=d0.metric(attempts([False]*32),4); assert z["u_if_solved"] is None and z["duplicate_concentration"] is None
def test_equal_maps_geometry_and_empty_support():
 assert d0.equal([{"map_id":1,"value":1},{"map_id":1,"value":1},{"map_id":2,"value":0}])==.5 and d0.equal([]) is None
 assert d0.geom(SimpleNamespace(start=0,goal=26,length=4,M=1))=={"length":"4","detour":"0","multiplicity":"1-8"}
 assert d0.geom(SimpleNamespace(start=0,goal=26,length=6,M=65))["detour"]=="2+"
 with pytest.raises(d0.core.IdentityError): d0.geom(SimpleNamespace(start=0,goal=26,length=5,M=1))
def test_gate_same_map_deletions_zero_and_concentrated_failure():
 maps={s:{m:{"sm":0.,"sa":.1 if m==0 else 0.} for m in range(8)} for s in d0.SEEDS}; g=d0.gate(maps)
 assert not g["pass"] and g["leave_one_map_out"][0]==0
 maps={s:{m:{"sm":0.,"sa":.1} for m in range(8)} for s in d0.SEEDS}; assert d0.gate(maps)["pass"]
 with pytest.raises(d0.core.IdentityError): d0.gate({1702:{m:{"sm":0.,"sa":1.}for m in range(8)}})
def test_composed_metric_is_json_safe_and_summary_retains_support():
 x=d0.metric(attempts([True,False]*16),9); json.dumps(x)
 bag0={str(k):{"pass":0.,"u_per_M":0.}for k in d0.KS}; bag1={str(k):{"pass":1.,"u_per_M":1/9}for k in d0.KS}
 rows=[{"map_id":1,"family":"IIIILLLL","mode":"sm","c":0,"c_per_32":0.,"u":0,"length":"14","detour":"0","multiplicity":"1-8","bag":bag0},{"map_id":1,"family":"IIIILLLL","mode":"sa","c":1,"c_per_32":1/32,"u":1,"length":"14","detour":"0","multiplicity":"1-8","bag":bag1}]
 s=d0.summaries(rows); assert s["strata"]["challenge"]["sm"]["solved_support"]==0 and s["strata"]["challenge"]["sa"]["maps"]==1
def test_shared_assembly_four_seed_exact_panel_paired_bins_and_gate():
 problems=[]
 for m in range(32):
  family="IIIILLLL" if m<8 else "IIIIIIII" if m<20 else "LLLLLLLL"
  for i in range(16):
   length=14+(i%3); problems.append(SimpleNamespace(canonical=bytes([m,i]),map_id=m,family=family,start=0,goal=136 if length==15 else 135,length=length if length<16 else 16,M=(1,9,65)[i%3]))
 bags={}
 for seed in d0.SEEDS:
  for mode in("sm","sa"):
   supplied=[]
   for p in problems:
    good=mode=="sa" and p.family=="IIIILLLL"
    supplied.append((p,attempts([good]+[False]*31),{"event_sha256":"e","result_sha256":"r"}))
   bags[seed,mode]=supplied
 out=d0.assemble(problems,bags); json.dumps(out)
 assert out["gate"]["pass"] and len(out["paired_k32"]["1702"])==32
 assert set(out["geometry"]["length"])==set(d0.LENGTH_BINS)
 assert out["summary"]["1702"]["challenge"]["sa"]["problems"]==128
 assert out["summary"]["1702"]["challenge"]["sa_minus_sm"][32]>0
 assert out["summary"]["1702"]["routine"]["sm"]["prefix_sensitivity"]["1"]["Q"]==0
 assert out["geometry"]["length"]["14"]["challenge"]["1702"]["sa"]["problems"]>0
 assert out["paired_k32"]["1702"]["8"]["outcomes"]["neither"]==16
 broken=dict(bags); broken[1702,"sm"]=broken[1702,"sm"][:-1]
 with pytest.raises(d0.core.IdentityError): d0.assemble(problems,broken)
def test_real_retained_event_interface_without_inference_or_test_loader(monkeypatch):
 assert "load_final_test" not in MODULE.read_text() and "torch.load" not in MODULE.read_text()
 root=Path("execution/model_training_comparison"); _,ids=d0.core._prepared_ids(root/"prepare-001"/"prepared.json")
 own=d0.owners(root,ids); assert len(own)==8 and all(x[3]["decision_sha256"] for x in own.values())
 record=own[1702,"softmax"][1]; ev=next(x for x in record["result"]["events"] if x["update"]==1000); bound={**ev,"_binding":{"event_sha256":d0._event_digest(ev)}}; problems=d0.load_validation().problems; routes,_=d0._storedroutes(bound,"t1_k32",problems); assert len(routes)==16384
 bad={**bound,"routes":{**bound["routes"],"t1_k32":{**bound["routes"]["t1_k32"],"problems":list(reversed(bound["routes"]["t1_k32"]["problems"]))}}}
 with pytest.raises(d0.core.IdentityError): d0._storedroutes(bad,"t1_k32",problems)
def test_owned_d0_seam_fixed_stage_alarm_and_failure_never_succeeds(monkeypatch):
 seen={}
 class Attempt:
  output=Path("/tmp/d0-failed")
  def __enter__(self): return self
  def __exit__(self,*args): seen["failed"]=args[0] is not None; return False
 monkeypatch.setattr(d0.wrapper,"install_replication_resource_limits",lambda:None)
 monkeypatch.setattr(d0.core,"configure_runtime",lambda:None)
 monkeypatch.setattr(d0.core.OwnedAttempt,"begin",lambda root,ledger,stage,name:(seen.update(root=root,ledger=ledger,stage=stage,name=name) or Attempt()))
 monkeypatch.setattr(d0.signal,"setitimer",lambda *args:seen.setdefault("alarm",args))
 monkeypatch.setattr(d0.core,"_prepared_ids",lambda *_:(_ for _ in ()).throw(RuntimeError("durable failure")))
 monkeypatch.setattr(d0,"load_validation",lambda:(_ for _ in ()).throw(AssertionError("no loader after failure")))
 with pytest.raises(RuntimeError,match="durable failure"): d0.run()
 assert seen["stage"]=="D" and seen["name"]=="difficult-d0-001" and seen["alarm"][1]<=56 and seen["failed"]
