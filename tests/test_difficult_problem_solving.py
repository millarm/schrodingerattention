import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest

MODULE=Path(__file__).parents[1]/"execution"/"difficult_problem_solving"/"analyze.py"
spec=importlib.util.spec_from_file_location("d0",MODULE); d0=importlib.util.module_from_spec(spec); spec.loader.exec_module(d0)
def attempts(valid): return [{"valid":x,"route":bytes([i%3])} for i,x in enumerate(valid)]
def fixture_panel():
 problems=[]
 for m in range(32):
  family="IIIILLLL" if m<8 else "IIIIIIII" if m<20 else "LLLLLLLL"
  for i in range(16):
   length=14+(i%2) if m<8 else 14+(i%3); problems.append(SimpleNamespace(canonical=bytes([m,i]),map_id=m,family=family,start=0,goal=136 if length==15 else 135,length=length,M=(1,9,65)[i%3]))
 return problems
def fixture_bags(problems):
 bags={}; outcomes=(("both","sm_only","sa_only","neither"), ("both","both","sa_only","neither"), ("both","sm_only","sm_only","neither"), ("both","sa_only","sa_only","neither"))
 for si,seed in enumerate(d0.SEEDS):
  for mode in("sm","sa"):
   supplied=[]
   for p in problems:
    outcome=outcomes[si][p.canonical[1] % 4] if p.family=="IIIILLLL" else "neither"
    good=(outcome in ("both","sm_only") if mode=="sm" else outcome in ("both","sa_only"))
    supplied.append((p,attempts([good]+[False]*31),{"event_sha256":"e","result_sha256":"r"}))
   bags[seed,mode]=supplied
 return bags
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
 problems=fixture_panel(); bags=fixture_bags(problems)
 out=d0.assemble(problems,bags); json.dumps(out)
 assert len(out["paired_k32"]["1702"])==32
 assert set(out["geometry"]["length"])==set(d0.LENGTH_BINS)
 assert out["summary"]["1702"]["challenge"]["sa"]["problems"]==128
 assert out["summary"]["1702"]["challenge"]["sa_minus_sm"]["bag"]["32"]["pass"] is not None
 assert out["summary"]["1702"]["challenge"]["sa_minus_sm"]["empirical_Q"] is not None
 assert out["summary"]["1702"]["challenge"]["sa_minus_sm"]["prefix_sensitivity"]["1"]["Q"] is not None
 assert out["summary"]["1702"]["challenge"]["sm"]["solved_only"]["zeros"]["c"]>0
 assert out["summary"]["1702"]["challenge"]["sm"]["solved_only"]["valid_count_distribution"]["c"]
 assert out["summary"]["1702"]["routine"]["sm"]["prefix_sensitivity"]["1"]["Q"]==0
 assert out["geometry"]["length"]["14"]["challenge"]["1702"]["sa"]["problems"]>0
 assert set(out["paired_k32"]["1702"]["0"]["outcomes"])=={"both","sm_only","sa_only","neither"}
 assert len(set(out["gate"]["seed_deltas"].values()))>1
 empty=out["geometry"]["length"]["16"]["challenge"]["1702"]["sa"]
 assert empty["problems"]==0 and empty["all_problem"]["1"]["pass"] is None
 broken=dict(bags); broken[1702,"sm"]=broken[1702,"sm"][:-1]
 with pytest.raises(d0.core.IdentityError): d0.assemble(problems,broken)
 unknown=list(problems); unknown[0]=SimpleNamespace(**{**problems[0].__dict__,"family":"UNKNOWN"})
 with pytest.raises(d0.core.IdentityError): d0.assemble(unknown,bags)
def test_real_retained_event_interface_without_inference_or_test_loader(monkeypatch):
 assert "load_final_test" not in MODULE.read_text() and "torch.load" not in MODULE.read_text()
 root=Path("execution/model_training_comparison"); _,ids=d0.core._prepared_ids(root/"prepare-001"/"prepared.json")
 own=d0.owners(root,ids); assert len(own)==8 and all(x[3]["decision_sha256"] for x in own.values())
 record=own[1702,"softmax"][1]; ev=next(x for x in record["result"]["events"] if x["update"]==1000); bound={**ev,"_binding":{"event_sha256":d0._event_digest(ev)}}; problems=d0.load_validation().problems; routes,_=d0._storedroutes(bound,"t1_k32",problems); assert len(routes)==16384
 bad={**bound,"routes":{**bound["routes"],"t1_k32":{**bound["routes"]["t1_k32"],"problems":list(reversed(bound["routes"]["t1_k32"]["problems"]))}}}
 with pytest.raises(d0.core.IdentityError): d0._storedroutes(bad,"t1_k32",problems)
 order_bad={**bound,"routes":{**bound["routes"],"t1_k32":{**bound["routes"]["t1_k32"],"problems":list(reversed(bound["routes"]["t1_k32"]["problems"]))}}}
 order_bad["_binding"]={"event_sha256":d0._event_digest(order_bad)}
 with pytest.raises(d0.core.IdentityError,match="dataset order"): d0._storedroutes(order_bad,"t1_k32",problems)
def test_owned_d0_success_and_late_output_finalization_failures(tmp_path,monkeypatch):
 problems=fixture_panel(); bags=fixture_bags(problems); retained={u:bags for u in d0.UPDATES}; ids={"fixture":"retained-only"}
 monkeypatch.setattr(d0.wrapper,"install_replication_resource_limits",lambda:None)
 monkeypatch.setattr(d0.core,"configure_runtime",lambda:None)
 original_timer=d0.signal.setitimer; timers=[]
 def observed_timer(*args):
  timers.append(args); return original_timer(*args)
 monkeypatch.setattr(d0.signal,"setitimer",observed_timer)
 def invoke(root):
  d0.core.initialize_ledger(root/"ledger.jsonl")
  return d0.run(root,retained_bags=retained,validation=SimpleNamespace(problems=problems),input_ids=ids,owner_metadata={"fixture":"retained"})
 success=tmp_path/"success"; success.mkdir(); out=invoke(success)
 produced=success/"difficult-d0-001"
 assert out["status"]=="COMPLETE" and (produced/"d0.json").is_file() and (produced/"attempt.json").is_file() and (produced/"output-manifest.json").is_file()
 completed=json.loads((produced/"attempt.json").read_text())
 assert completed["status"]=="COMPLETE" and completed["stage"]=="D" and any(args[1]<=56 for args in timers if args[0]==d0.signal.ITIMER_REAL)
 original_write=d0.core._write_json
 monkeypatch.setattr(d0.core,"_write_json",lambda path,value: (_ for _ in ()).throw(OSError("injected d0 write")) if path.name=="d0.json" else original_write(path,value))
 failed_write=tmp_path/"write"; failed_write.mkdir()
 with pytest.raises(OSError,match="injected d0 write"): invoke(failed_write)
 assert json.loads((failed_write/"difficult-d0-001"/"attempt.json").read_text())["status"]=="FAILED"
 monkeypatch.setattr(d0.core,"_write_json",original_write)
 monkeypatch.setattr(d0.core,"file_manifest",lambda _path: (_ for _ in ()).throw(OSError("injected finalization")))
 failed_final=tmp_path/"final"; failed_final.mkdir()
 with pytest.raises(d0.core.ArtifactError,match="injected finalization"): invoke(failed_final)
 assert (failed_final/"difficult-d0-001"/"d0.json").is_file() and (failed_final/"difficult-d0-001"/"finalization_error.json").is_file()
