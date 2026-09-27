"""Literal unit coverage for the additive update-count estimator.

The composed accepted-trainer fixture is intentionally dispatched only after
static review; these tests contain no import-time production work.
"""
import errno, json, math, os, signal, sys, time
from pathlib import Path
import pytest
from execution.update_efficiency import study

def points(q, *, kl=.1, brier=.1, teacher_entropy=.1, policy_entropy=.2, challenge_q=.1):
 return [{"update":u,"metrics":{"q":value,"kl":kl,"brier":brier,"teacher_entropy":teacher_entropy,"policy_entropy":policy_entropy,"challenge_q":challenge_q}} for u,value in zip(study.GRID,q)]

def test_v3_grid_finite_and_q_plateau_known_values_and_rebound():
 flat=points([.2]*13);result=study.q_plateau(flat)
 assert result["status"]=="SUSTAINED" and result["first_low_window"]==8000 and result["confirmation_update"]==10000 and result["windows"][0]["update"]==8000 and result["windows"][0]["mean_q"]==pytest.approx(.2) and result["windows"][0]["gain"]==pytest.approx(0.)
 rising=points([u/100000 for u in study.GRID]);assert study.q_plateau(rising)["status"]=="RIGHT_CENSORED"
 rebound=points([.2,.2,.2,.2,.2,.2,.2,.2,.2,.2,.3,.3,.3]);temporary=study.q_plateau(rebound)["temporary_plateaus"]
 assert temporary and study.q_plateau(points([.2,.19,.18,.17,.16,.15,.14,.13,.12,.11,.10,.09,.08]))["deterioration_updates"]
 exact=[0.,0.,0.,0.,.0,.0,.0,.0,.005,.005,.005,.005,.005]
 assert study.q_plateau(points(exact))["qualifying"][:2]==[True,True]
 bad=flat[:-1]
 with pytest.raises(ValueError):study.q_plateau(bad)
 duplicate=points([.2]*13);duplicate[1]["update"]=0
 with pytest.raises(ValueError):study.q_plateau(duplicate)
 bad=points([.2]*13);bad[3]["metrics"]["teacher_entropy"]=math.nan
 with pytest.raises(ValueError):study.q_plateau(bad)
 bad=points([.2]*13);del bad[3]["metrics"]["teacher_entropy"]
 with pytest.raises(ValueError):study.q_plateau(bad)
 bad=points([.2]*13);bad[3]["metrics"]["challenge_q"]=math.nan
 with pytest.raises(ValueError):study.q_plateau(bad)
 bad=points([.2]*13);del bad[3]["metrics"]["challenge_q"]
 with pytest.raises(ValueError):study.q_plateau(bad)

def test_ce_blocks_windows_denominators_and_suffixes_are_literal():
 curve=[{"update":u,"ce":2.} for u in range(1,16001)];result=study.ce_plateau(curve)
 assert result["blocks"][0]=={"end_update":100,"mean_ce":2.} and result["two_k_means"][2000]==2. and result["status"]=="SUSTAINED"
 bad=[{"update":u,"ce":0. if u<=6000 else 1.} for u in range(1,16001)]
 with pytest.raises(ValueError):study.ce_plateau(bad)
 curve[-1]["update"]=15999
 with pytest.raises(ValueError):study.ce_plateau(curve)
 rising=[{"update":u,"ce":2.-u/16000} for u in range(1,16001)];assert study.ce_plateau(rising)["status"]=="RIGHT_CENSORED"
 falling=[{"update":u,"ce":1.+u/16000} for u in range(1,16001)];assert study.ce_plateau(falling)["deterioration_updates"]
 rebound=[{"update":u,"ce":2. if u<=10000 else 1.} for u in range(1,16001)];assert study.ce_plateau(rebound)["temporary_plateaus"]

def test_milestones_thresholds_irregular_lag_and_censoring():
 q=[.0,.0,.0,.0,.0,.0,.0,.0,.29,.29,.37198,.37198,.38198];result=study.milestones(points(q))
 assert result["tolerant_30"]["update"]==8000 and result["tolerant_30"]["confirmation_lag"]==2000
 assert result["tolerant_38198"]["update"]==12000 and result["exact_30"]["update"]==12000 and result["exact_38198"]["status"]=="FINAL_UNCONFIRMED"
 isolated=points([.0,.3,.0]+[.0]*10);assert study.quality_milestone(isolated,.29)["status"]=="RIGHT_CENSORED"
 outside=points([.289]*13);assert study.quality_milestone(outside,.29)["status"]=="RIGHT_CENSORED"
 fragile=points([.3]*13,kl=.1);fragile[4]["metrics"]["challenge_q"]=.07;fragile[5]["metrics"]["kl"]=.41
 assert study.quality_milestone(fragile,.29)["status"]=="ACQUIRED" and study.fragility_flags(fragile)==[3600,4000]
 observed=study.milestone_comparison(result["tolerant_30"],result["tolerant_38198"]);assert observed["sa_minus_sm_updates"]==4000 and observed["sa_over_sm_grid_ratio"]==1.5
 assert study.milestone_comparison(result["tolerant_30"],result["exact_38198"])["status"]=="CENSORED"
 anomalous={**result["tolerant_30"],"initial_pass_anomaly":True};assert study.milestone_comparison(anomalous,result["tolerant_38198"])["status"]=="CENSORED"
 zero={**result["tolerant_30"],"interval":[0,1200]};assert study.milestone_comparison(zero,result["tolerant_38198"])["upper_unbounded"]

def _owner(seed,mode):
 return {"seed":seed,"mode":mode,"shared_initial_digest":"s"*64,"batch_digests":["x"*64]*16000,"config_hash":"c"*64,"input_ids":{"prepared_sha256":"i"*64,"training_selected_hash":"j"*64,"validation_selected_hash":"k"*64,"test_selected_hash":"l"*64,"manifest_sha256":"m"*64,"frozen_source_hash":"n"*64},"source_hashes":{"study":"h"*64},"bank":{"selected_hash":"a"*64,"candidate_hash":"b"*64,"q_hash":"d"*64,"record_hash":"e"*64,"rows":2},"summary":{"training_support_hash":"p"*64},"points":[{"update":u,"score_path":f"score-{u}.json","score_sha256":"z"*64} for u in study.GRID]}

def _pair(seed,sm_scores,sa_scores):
 sm_scores=json.loads(json.dumps(sm_scores));sa_scores=json.loads(json.dumps(sa_scores));sm_owner,sa_owner=_owner(seed,"softmax"),_owner(seed,"schrodinger")
 for owner,scores in ((sm_owner,sm_scores),(sa_owner,sa_scores)):
  for point,score in zip(owner["points"],scores): point["score_sha256"]=study.hashlib.sha256(study.canonical(score)).hexdigest()
 return {"seed":seed,"softmax":{"owner":sm_owner,"scores":sm_scores},"schrodinger":{"owner":sa_owner,"scores":sa_scores}}

def _refresh_pair_hashes(pairs):
 for pair in pairs:
  for bundle in (pair["softmax"],pair["schrodinger"]):
   for point,score in zip(bundle["owner"]["points"],bundle["scores"]): point["score_sha256"]=study.hashlib.sha256(study.canonical(score)).hexdigest()

def test_fixed_contrast_pair_identity_and_full_two_seed_aggregation():
 sm=points([.1]*13);sa=points([.1]*13);sa[4]["metrics"]["q"]=.13;sa[7]["metrics"]["q"]=.11
 assert study.early_contrast(sm,sa)==pytest.approx(2.5)
 affine=points([.1]*13);affine_sa=points([.1+.001*u for u in study.GRID]);assert study.early_contrast(affine,affine_sa)==pytest.approx(0.)
 left,right=_owner(2201,"softmax"),_owner(2201,"schrodinger");study.validate_pair_identity(2201,left,right)
 for key,value in (("seed",2202),("mode","softmax"),("shared_initial_digest","z"*64),("config_hash","q"*64),("input_ids",{**right["input_ids"],"prepared_sha256":"q"*64}),("source_hashes",{"study":"q"*64}),("bank",{**right["bank"],"q_hash":"q"*64})):
  right=_owner(2201,"schrodinger");right[key]=value
  with pytest.raises(ValueError):study.validate_pair_identity(2201,left,right)
 right=_owner(2201,"schrodinger");right["input_ids"]={}
 with pytest.raises(ValueError):study.validate_pair_identity(2201,left,right)
 for key,value in (("selected_hash","q"*64),("candidate_hash","q"*64),("q_hash","q"*64),("record_hash","q"*64),("rows",3)):
  right=_owner(2201,"schrodinger");right["bank"][key]=value
  with pytest.raises(ValueError):study.validate_pair_identity(2201,left,right)
 right=_owner(2201,"schrodinger");right["summary"]["training_support_hash"]="q"*64
 with pytest.raises(ValueError):study.validate_pair_identity(2201,left,right)
 right=_owner(2201,"schrodinger");right["batch_digests"][2]="bad"
 with pytest.raises(ValueError):study.validate_pair_identity(2201,left,right)
 sm1=points([.0]*8+[.30,.30,.30,.30,.38198]);sa1=points([.0]*10+[.30,.30,.30]);sa1[4]["metrics"]["q"]=.03
 sm2=points([.30]+[.0]*12);sa2=points([.0]*12+[.38198]);sa2[4]["metrics"]["q"]=.03
 for scores in (sa1,sa2):
  scores[4]["metrics"]["kl"]=.13;scores[4]["metrics"]["challenge_q"]=.07
 summary=study.aggregate_all([_pair(2201,sm1,sa1),_pair(2202,sm2,sa2)])
 assert summary["contrast_pp"]["values"]==[pytest.approx(3.),pytest.approx(3.)] and summary["contrast_pp"]["material"] and summary["contrast_pp"]["same_sign"] and summary["contrast_pp"]["screen"]
 stage=next(row for row in summary["stagewise"] if row["update"]==3600);assert len(summary["stagewise"])==13 and all(len(row["per_seed"])==2 for row in summary["stagewise"]) and stage["mean_q_gap"]>0 and stage["mean_kl_gap"]>.02 and stage["mixed"]
 assert all(len(rows)==2 for rows in summary["milestone_comparisons"].values()) and summary["milestone_comparisons"]["tolerant_30"][0]["status"]=="OBSERVED" and summary["per_seed"][1]["milestones"]["schrodinger"]["exact_38198"]["status"]=="FINAL_UNCONFIRMED" and summary["per_seed"][1]["milestones"]["softmax"]["tolerant_30"]["initial_pass_anomaly"]

def test_two_seed_guard_boundaries_and_curvature_signs_are_literal():
 base=points([.0]*13);plus=points([.0]*13);plus[4]["metrics"]["q"]=.01
 pairs=[_pair(2201,base,plus),_pair(2202,base,plus)];summary=study.aggregate_all(pairs)
 stage=next(row for row in summary["stagewise"] if row["update"]==3600);assert stage["mean_q_gap"]==pytest.approx(.01) and not stage["mixed"] and summary["contrast_pp"]["material"] and summary["contrast_pp"]["same_sign"] and summary["contrast_pp"]["screen"]
 for pair in pairs:
  pair["schrodinger"]["scores"][4]["metrics"]["kl"]=.12;pair["schrodinger"]["scores"][4]["metrics"]["challenge_q"]=.08
 _refresh_pair_hashes(pairs)
 boundary=next(row for row in study.aggregate_all(pairs)["stagewise"] if row["update"]==3600);assert boundary["mean_kl_gap"]==pytest.approx(.02) and boundary["mean_challenge_q_gap"]==pytest.approx(-.02) and not boundary["mixed"]
 for pair in pairs:
  pair["schrodinger"]["scores"][4]["metrics"]["kl"]=.1200001
 _refresh_pair_hashes(pairs)
 assert next(row for row in study.aggregate_all(pairs)["stagewise"] if row["update"]==3600)["mixed"]
 for pair in pairs:
  pair["schrodinger"]["scores"][4]["metrics"]["kl"]=.12;pair["schrodinger"]["scores"][4]["metrics"]["challenge_q"]=.079999
 _refresh_pair_hashes(pairs)
 assert next(row for row in study.aggregate_all(pairs)["stagewise"] if row["update"]==3600)["mixed"]
 pairs[0]["schrodinger"]["scores"][4]["metrics"]["q"]=.03;pairs[1]["schrodinger"]["scores"][4]["metrics"]["q"]=-.01
 _refresh_pair_hashes(pairs)
 opposite=study.aggregate_all(pairs);assert opposite["contrast_pp"]["material"] and not opposite["contrast_pp"]["same_sign"] and not opposite["contrast_pp"]["screen"]
 for pair in pairs:
  pair["schrodinger"]["scores"][4]["metrics"].update({"q":-.01,"kl":.2,"challenge_q":0.})
 _refresh_pair_hashes(pairs)
 assert not next(row for row in study.aggregate_all(pairs)["stagewise"] if row["update"]==3600)["mixed"]

def _s2_actual_fixture(tmp_path,monkeypatch):
 """Safe boundaries surround a real accepted owner/train/restore/evaluate seam."""
 from schrodinger import route_policy_experiment as accepted
 from schrodinger import route_policy_data
 from schrodinger.route_policy_data import RouteState, Problem
 from schrodinger.route_policy_metrics import heldout_bank, q_array_hash, record_hash
 state=RouteState(bytes(144),1,"IIIIIIII",0,1,(0.,1.,0.,0.));routine=Problem(bytes(144),1,"IIIIIIII",0,1,1,1,None);challenge=Problem(bytes(144),2,"IIIILLLL",0,1,1,1,None);bank=heldout_bank((routine,challenge))
 ids={"prepared_sha256":"a"*64,"training_selected_hash":"b"*64,"validation_selected_hash":"c"*64,"test_selected_hash":"d"*64,"manifest_sha256":"e"*64,"frozen_source_hash":"f"*64};ledger=tmp_path/"ledger.jsonl";accepted.initialize_ledger(ledger)
 monkeypatch.setattr(study,"LEDGER",ledger);monkeypatch.setattr(study,"ATTEMPTS",tmp_path/"attempts");monkeypatch.setattr(study,"ROOT",tmp_path/"root");study.ATTEMPTS.mkdir();study.ROOT.mkdir();accepted.configure_runtime();monkeypatch.setattr(accepted,"configure_runtime",lambda:None)
 identity={"selected_hash":bank.selected_hash,"candidate_hash":bank.candidate_hash,"q_hash":q_array_hash(bank.selected),"record_hash":record_hash(bank.selected),"rows":len(bank.selected)}
 forbidden=[]
 def no_final_test(*args,**kwargs): forbidden.append("final_test");raise AssertionError("S2 must not load final test")
 monkeypatch.setattr(route_policy_data,"load_final_test",no_final_test);monkeypatch.setattr(accepted,"load_final_test",no_final_test)
 source={"study":"s"*64}
 monkeypatch.setattr(study,"manifest_bound_ids",lambda:ids);monkeypatch.setattr(study,"source_hashes",lambda:source);monkeypatch.setattr(study,"validation_bank",lambda validation,actual:(bank,identity));monkeypatch.setattr(study,"load_training",lambda:type("Train",(),{"states":(state,),"support":frozenset(),"support_hash":"p"*64})());monkeypatch.setattr(study,"load_validation",lambda:type("Validation",(),{"problems":(routine,challenge)})());monkeypatch.setattr(accepted,"CHECKPOINT_INTERVAL",1)
 def decision(mode): return {"approved":True,"hashes":source,"seed":2201,"mode":mode,"updates":2,"plan_sha256":study.sha256(study.PLAN),"spec_sha256":study.sha256(study.SPEC),"input_ids":ids,"config_hash":accepted.config_hash()}
 return accepted,ledger,identity,decision,forbidden

def _owner_charges(ledger):
 return [json.loads(line) for line in ledger.read_text().splitlines() if json.loads(line).get("kind")=="attempt_charge"]

def test_s2_actual_short_owner_training_restores_both_modes_and_exact_endpoints(tmp_path,monkeypatch):
 """Two actual modes train two updates, restore initial/final checkpoints, and score routine+challenge."""
 _,ledger,identity,decision,forbidden=_s2_actual_fixture(tmp_path,monkeypatch)
 for mode in study.MODES:
  result=study.run(seed=2201,mode=mode,decision=decision(mode),_test_schedule=(2,(0,2)))
  assert result["status"]=="COMPLETE" and result["bank"]==identity and result["source_hashes"]=={"study":"s"*64} and result["summary"]["training_support_hash"]=="p"*64 and [p["update"]for p in result["points"]]==[0,2] and len(result["batch_digests"])==2
  assert result["training"]["initial_checkpoint_hash"] and result["training"]["final_checkpoint_hash"]
  owner=study.ATTEMPTS/f"update-efficiency-2201-{mode}-2";assert (owner/"score-0.json").is_file() and (owner/"score-2.json").is_file() and (owner/"result.json").is_file() and (owner/"index.json").is_file() and len(list(owner.glob("score-*.json")))==2
  import torch
  initial=study.sha256(owner/"checkpoints"/"initial.pt");first=owner/"checkpoints"/"update-1.pt";second=owner/"checkpoints"/"update-2.pt"
  assert torch.load(first,weights_only=False)["identity"]["parent_hash"]==initial and torch.load(second,weights_only=False)["identity"]["parent_hash"]==study.sha256(first)
  scores=json.loads((owner/"index.json").read_text())["scores"];manifest=json.loads((owner/"output-manifest.json").read_text());raw=[json.loads((owner/p["score_path"]).read_text()) for p in scores]
  assert json.loads((owner/"index.json").read_text())["result_sha256"]==study.sha256(owner/"result.json") and [study.sha256(owner/p["score_path"]) for p in scores]==[p["score_sha256"] for p in scores] and [row["checkpoint_identity"]["update"] for row in raw]==[0,2] and all("proper" in row and "rollout" in row and row["metrics"]["teacher_entropy"]==pytest.approx(row["proper"]["weighted"]["entropy_q"]) for row in raw) and manifest["result.json"]["sha256"]==study.sha256(owner/"result.json")
 assert len(_owner_charges(ledger))==2 and not forbidden

def test_s2_endpoint_write_failure_has_one_charge_and_durable_failed_owner(tmp_path,monkeypatch):
 _,ledger,_,decision,_=_s2_actual_fixture(tmp_path,monkeypatch);original=study._atomic
 def endpoint(path,value):
  if Path(path).name=="score-2.json": raise OSError("endpoint write")
  original(path,value)
 monkeypatch.setattr(study,"_atomic",endpoint)
 with pytest.raises(OSError):study.run(seed=2201,mode="softmax",decision=decision("softmax"),_test_schedule=(2,(0,2)))
 owner=study.ATTEMPTS/"update-efficiency-2201-softmax-2";attempt=json.loads((owner/"attempt.json").read_text())
 assert len(_owner_charges(ledger))==1 and attempt["status"]=="FAILED" and (owner/"score-0.json").is_file() and not (owner/"score-2.json").exists()

def test_s2_final_manifest_failure_has_one_charge_and_durable_failure_evidence(tmp_path,monkeypatch):
 accepted,ledger,_,decision,_=_s2_actual_fixture(tmp_path,monkeypatch)
 monkeypatch.setattr(accepted,"file_manifest",lambda directory:(_ for _ in ()).throw(OSError("manifest fsync")))
 with pytest.raises(accepted.ArtifactError):study.run(seed=2201,mode="schrodinger",decision=decision("schrodinger"),_test_schedule=(2,(0,2)))
 owner=study.ATTEMPTS/"update-efficiency-2201-schrodinger-2";attempt=json.loads((owner/"attempt.json").read_text())
 assert len(_owner_charges(ledger))==1 and attempt["status"]=="FAILED_ARTIFACT" and (owner/"finalization_error.json").is_file() and not (owner/"output-manifest.json").exists()

def test_s2_checkpoint_identity_mutation_is_refused_inside_one_failed_owner(tmp_path,monkeypatch):
 accepted,ledger,_,decision,_=_s2_actual_fixture(tmp_path,monkeypatch);original=study._checkpoint;changed=[]
 def mutation(path,**kwargs):
  if kwargs["update"]==2 and not changed:
   import torch
   payload=torch.load(path,weights_only=False);payload["identity"]["parent_hash"]="0"*64;torch.save(payload,path);changed.append(True)
  return original(path,**kwargs)
 monkeypatch.setattr(study,"_checkpoint",mutation)
 with pytest.raises(accepted.IdentityError):study.run(seed=2201,mode="softmax",decision=decision("softmax"),_test_schedule=(2,(0,2)))
 owner=study.ATTEMPTS/"update-efficiency-2201-softmax-2";assert changed and len(_owner_charges(ledger))==1 and json.loads((owner/"attempt.json").read_text())["status"]=="FAILED"

def test_driver_literal_v3_shapes_and_authority_inventory():
 from execution.update_efficiency import command
 assert command.KINDS=={"smoke":("A",10.),"suite":("A",30.),"production":("B",None)}
 hashes=command.authority_hashes()
 assert {"driver","watchdog","tests","plan","spec","decisions"}.issubset(hashes)
 assert all(len(value)==64 for value in hashes.values())

def test_driver_reservation_rejects_unknown_or_overallocation_without_runtime(tmp_path,monkeypatch):
 from execution.update_efficiency import command
 monkeypatch.setattr(command,"HERE",tmp_path)
 monkeypatch.setattr(command,"ATTEMPTS",tmp_path/"attempts")
 monkeypatch.setattr(command,"ROOT",tmp_path/"root")
 monkeypatch.setattr(command,"ledger_rows",lambda:([{ "entry_id":"x","charged_seconds":101.,"study":"update_efficiency_v3","stage":"A"}],{"A":900.,"B":0.,"C":0.,"D":0.}))
 with pytest.raises(RuntimeError):command.reserve({"ledger_sha256":"fixture"},"A",10.)

# Driver-only synthetic orchestration: no study/data/model fixture is used below.
def _driver_fixture(tmp_path,monkeypatch,kind="smoke",mode="softmax"):
 from execution.update_efficiency import command
 tmp_path=tmp_path/f"case-{len(list(tmp_path.iterdir()))}";tmp_path.mkdir()
 rows=[];lock=tmp_path/"driver.lock";attempts=tmp_path/"attempts";attempts.mkdir();decision_path=tmp_path/"decision.json"
 monkeypatch.setattr(command,"HERE",tmp_path);monkeypatch.setattr(command,"ROOT",tmp_path/"root");monkeypatch.setattr(command,"ATTEMPTS",attempts);monkeypatch.setattr(command,"LEDGER",tmp_path/"ledger.jsonl")
 monkeypatch.setattr(command,"authority_hashes",lambda:{"fixture":"a"*64});monkeypatch.setattr(command,"review_ok",lambda *args:None)
 (tmp_path/"ledger.jsonl").write_text("");(tmp_path/"plan-v3-saturation.md").write_text("plan");(tmp_path/"spec-03-saturation.md").write_text("spec");(tmp_path/"driver-accounting-clarification.md").write_text("clarification")
 monkeypatch.setattr(command,"ledger_rows",lambda path=None:(list(rows),{"A":0.,"B":0.,"C":0.,"D":0.}))
 def append(row):
  if any(x["entry_id"]==row["entry_id"]for x in rows):raise RuntimeError("duplicate")
  rows.append(row)
 monkeypatch.setattr(command,"append_once",append)
 def reserve(*args):lock.write_text("reserved");return lock
 monkeypatch.setattr(command,"acquire_reservation",reserve)
 seconds=command.KINDS[kind][1]if kind!="production"else({"softmax":350.,"schrodinger":550.}[mode])
 expected=[sys.executable,"-m","pytest","-q",command.SMOKE if kind=="smoke"else"tests/test_update_efficiency.py"]if kind!="production"else[sys.executable,"-m","execution.update_efficiency.study","--decision",str(decision_path.resolve())]
 decision={"kind":kind,"approved":True,"hashes":{"fixture":"a"*64},"seed":2201,"mode":mode,"argv":expected,"cwd":str(command.WORKSPACE)}
 if kind=="production":decision.update({"updates":16000,"plan_sha256":command.sha256(tmp_path/"plan-v3-saturation.md"),"spec_sha256":command.sha256(tmp_path/"spec-03-saturation.md"),"driver_accounting_clarification_sha256":command.sha256(tmp_path/"driver-accounting-clarification.md")})
 decision_path.write_text(json.dumps(decision));return command,rows,lock,attempts,decision_path,seconds

def test_driver_main_a_success_failed_and_exception_charge_once(tmp_path,monkeypatch):
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch)
 monkeypatch.setattr(command,"supervise",lambda *args:{"exit_code":0,"timed_out":False,"cleanup_verified":True})
 command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["status"]=="COMPLETE" and rows[0]["charged_seconds"]>=1 and not lock.exists()
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch)
 monkeypatch.setattr(command,"supervise",lambda *args:{"exit_code":1,"timed_out":False,"cleanup_verified":True})
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["status"]=="FAILED" and not lock.exists()
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch)
 monkeypatch.setattr(command,"supervise",lambda *args:(_ for _ in ()).throw(RuntimeError("watchdog boom")))
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["status"]=="FAILED" and lock.exists()

def test_driver_main_timeout_descendant_and_accounting(tmp_path,monkeypatch):
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch)
 monkeypatch.setattr(command,"supervise",lambda *args:{"exit_code":-15,"timed_out":True,"cleanup_verified":True,"descendants_reaped":True})
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert rows[0]["status"]=="FAILED" and rows[0]["finalization_allowance_seconds"]==1 and not lock.exists()

def test_driver_watchdog_descendant_fixture(tmp_path):
 """A real parent reaps its SIGTERM'd group child before the watchdog verifies absence."""
 from execution.update_efficiency import command
 proof=tmp_path/"proof";proof.mkdir();logs=tmp_path/"watchdog";logs.mkdir()
 child="""import json,os,sys,time
from pathlib import Path
root=Path(sys.argv[1])
def durable(name,value):
 path=root/name
 with path.open('w') as handle: json.dump(value,handle,sort_keys=True);handle.flush();os.fsync(handle.fileno())
durable('child-ready.json',{'pid':os.getpid(),'pgid':os.getpgrp(),'parent_pid':os.getppid()})
until=time.monotonic()+4.
while time.monotonic()<until: time.sleep(.02)
"""
 parent=f"""import json,os,signal,subprocess,sys,time
from pathlib import Path
root=Path(sys.argv[1])
def durable(name,value):
 path=root/name
 with path.open('w') as handle: json.dump(value,handle,sort_keys=True);handle.flush();os.fsync(handle.fileno())
terminated=[False]
def on_term(signum,frame): terminated[0]=True
signal.signal(signal.SIGTERM,on_term)
child=subprocess.Popen([sys.executable,'-c',{child!r},str(root)])
durable('parent-start.json',{{'pid':os.getpid(),'pgid':os.getpgrp(),'child_pid':child.pid}})
until=time.monotonic()+.75
while not (root/'child-ready.json').is_file() and time.monotonic()<until: time.sleep(.01)
if not (root/'child-ready.json').is_file(): durable('parent-error.json',{{'pid':os.getpid(),'reason':'child readiness timeout'}});sys.exit(2)
durable('parent-ready.json',{{'pid':os.getpid(),'pgid':os.getpgrp(),'child_pid':child.pid}})
until=time.monotonic()+4.
while time.monotonic()<until and not terminated[0]: time.sleep(.01)
if not terminated[0]:
 child.terminate();child.wait(timeout=.5);durable('reaped.json',{{'pid':child.pid,'returncode':child.returncode,'reason':'defensive lifetime'}});sys.exit(3)
child.wait(timeout=.5)
durable('reaped.json',{{'pid':child.pid,'returncode':child.returncode,'reason':'SIGTERM handler'}})
sys.exit(0)
"""
 result=command.supervise([sys.executable,"-c",parent,str(proof)],2.,logs)
 parent_start=json.loads((proof/"parent-start.json").read_text());parent_ready=json.loads((proof/"parent-ready.json").read_text());child_ready=json.loads((proof/"child-ready.json").read_text());reaped=json.loads((proof/"reaped.json").read_text())
 assert result["timed_out"] and result["cleanup_verified"] and result["exit_code"]==0 and parent_start==parent_ready and parent_ready["pid"]==result["child_pid"] and parent_ready["pid"]!=child_ready["pid"] and parent_ready["pgid"]==parent_ready["pid"] and child_ready["pgid"]==parent_ready["pid"] and child_ready["parent_pid"]==parent_ready["pid"] and reaped=={"pid":child_ready["pid"],"returncode":-15,"reason":"SIGTERM handler"} and command.reviewed_watchdog.group_gone(parent_ready["pgid"])

def _complete_owner(command,attempts,rows,mode="softmax",status="COMPLETE",with_manifest=True):
 owner=command.owner_path(2201,mode);owner.mkdir();ident="owner-uuid";attempt={"entry_id":ident,"status":status};(owner/"attempt.json").write_text(json.dumps(attempt));(owner/"attempt.pending.json").write_text(json.dumps({"entry_id":ident}))
 if status=="COMPLETE":
  points=[]
  for update in command.GRID:
   cp=owner/"checkpoints"/("initial.pt"if update==0 else f"update-{update}.pt");cp.parent.mkdir(exist_ok=True);cp.write_text(str(update));score=owner/f"score-{update}.json";score.write_text(json.dumps({"checkpoint_sha256":command.sha256(cp)}));points.append({"update":update,"score_path":score.name,"score_sha256":command.sha256(score)})
  result={"seed":2201,"mode":mode,"points":points};(owner/"result.json").write_text(json.dumps(result));(owner/"index.json").write_text(json.dumps({"status":"COMPLETE","result_sha256":command.sha256(owner/"result.json"),"scores":points}))
 if with_manifest:
  manifest={str(p.relative_to(owner)):{"sha256":command.sha256(p)}for p in owner.rglob("*")if p.is_file()and p.name!="output-manifest.json"};(owner/"output-manifest.json").write_text(json.dumps(manifest))
 rows.append({"entry_id":ident,"kind":"attempt_charge","stage":"B","status":"FINALIZATION_UNCERTAIN","charged_seconds":2.,"output":str(owner)})
 return owner

def test_driver_main_b_complete_failed_and_missing_charge_reconciliation(tmp_path,monkeypatch):
 command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production")
 monkeypatch.setattr(command,"supervise",lambda *args:(_complete_owner(command,attempts,rows),{"exit_code":0,"timed_out":False,"cleanup_verified":True})[1])
 command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and not lock.exists()
 command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production")
 monkeypatch.setattr(command,"supervise",lambda *args:(_complete_owner(command,attempts,rows,status="FAILED",with_manifest=False),{"exit_code":1,"timed_out":False,"cleanup_verified":True})[1])
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["kind"]=="attempt_charge" and not lock.exists()
 command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production")
 monkeypatch.setattr(command,"supervise",lambda *args:{"exit_code":1,"timed_out":False,"cleanup_verified":True})
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["kind"]=="watchdog_uncertain_fallback" and rows[0]["charged_seconds"]>=1 and not lock.exists()
 command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production")
 monkeypatch.setattr(command,"supervise",lambda *args:(_complete_owner(command,attempts,rows,status="FAILED",with_manifest=False),rows.__setitem__(0,{**rows[0],"charged_seconds":351.}),{"exit_code":0,"timed_out":False,"cleanup_verified":True})[2])
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["kind"]=="attempt_charge" and not lock.exists()

def test_driver_b_fallback_nonpromotion_and_artifact_negatives(tmp_path,monkeypatch):
 command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production")
 owner=command.owner_path(2201,"softmax");rows.append({"entry_id":"fallback","kind":"watchdog_uncertain_fallback","stage":"B","charged_seconds":1.,"output":str(owner)})
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert lock.exists() # historic fallback is not recharged or promoted.
 owner.mkdir();owner.joinpath("attempt.json").write_text("{")
 with pytest.raises(Exception):command.reconcile_owner(owner,tmp_path,0.)
 owner.joinpath("attempt.json").write_text(json.dumps({"entry_id":"x"}));owner.joinpath("attempt.pending.json").write_text(json.dumps({"entry_id":"y"}))
 with pytest.raises(RuntimeError):command.reconcile_owner(owner,tmp_path,0.)
 escaped=tmp_path/"outside";escaped.write_text("x")
 with pytest.raises(RuntimeError):command._safe_file(owner,str(escaped))

def test_driver_ledger_prefix_carry_uuid_and_review_authority_negatives(tmp_path,monkeypatch):
 from execution.update_efficiency import command
 ledger=tmp_path/"ledger.jsonl";carry={"entry_id":"carry","kind":"inherited_budget","charged_seconds":0,"carried_budget_debit_seconds":command.CARRY}
 ledger.write_text(json.dumps(carry)+"\n");monkeypatch.setattr(command,"PREFIX_LINES",1);monkeypatch.setattr(command,"PREFIX_SHA",command.sha256(ledger))
 assert command.ledger_rows(ledger)[0]==[carry]
 ledger.write_text(json.dumps(carry)+"\n"+json.dumps(carry)+"\n")
 with pytest.raises(RuntimeError):command.ledger_rows(ledger)
 historical=command.HERE/"reviews"/"03-driver-closure.md";decision={"review":{"path":str(historical),"phase":"static-safety","sha256":command.sha256(historical)}}
 with pytest.raises(RuntimeError):command.review_ok(decision,{"fixture":"a"*64},"smoke")
 driver_only=tmp_path/"05-driver-final.md";driver_only.write_text("DRIVER_REVIEW_VERDICT: PASS\n"+"a"*64);decision["review"]={"path":str(driver_only),"phase":"static-safety","sha256":command.sha256(driver_only)}
 with pytest.raises(RuntimeError):command.review_ok(decision,{"fixture":"a"*64},"smoke")
 review=tmp_path/"review.md";review.write_text("DRIVER_REVIEW_VERDICT: PASS\n"+"a"*64);monkeypatch.setattr(command,"DRIVER_REVIEW",review)
 decision={"review":{"path":str(review),"phase":"static-safety","sha256":command.sha256(review)}}
 command.review_ok(decision,{"fixture":"a"*64},"smoke")
 with pytest.raises(RuntimeError):command.review_ok(decision,{"fixture":"a"*64},"production")

def test_driver_complete_real_hash_positive_and_literal_mutations(tmp_path,monkeypatch):
 command,rows,_,attempts,_,_=_driver_fixture(tmp_path,monkeypatch,"production");owner=_complete_owner(command,attempts,rows)
 command.validate_complete(owner,rows[0],2201,"softmax")
 def refresh():
  result=json.loads((owner/"result.json").read_text());index=json.loads((owner/"index.json").read_text());index["result_sha256"]=command.sha256(owner/"result.json");(owner/"index.json").write_text(json.dumps(index));manifest={str(p.relative_to(owner)):{"sha256":command.sha256(p)}for p in owner.rglob("*")if p.is_file()and p.name!="output-manifest.json"};(owner/"output-manifest.json").write_text(json.dumps(manifest));return result,index
 (owner/"score-1200.json").write_text("mutated")
 with pytest.raises(RuntimeError):command.validate_complete(owner,rows[0],2201,"softmax")
 (owner/"score-1200.json").write_text(json.dumps({"checkpoint_sha256":command.sha256(owner/"checkpoints"/"update-1200.pt")}));refresh();(owner/"checkpoints"/"update-1200.pt").write_text("mutated")
 with pytest.raises(RuntimeError):command.validate_complete(owner,rows[0],2201,"softmax")
 (owner/"checkpoints"/"update-1200.pt").write_text("1200");result,index=refresh();result["points"][-1]["update"]=15999;(owner/"result.json").write_text(json.dumps(result));index["scores"]=result["points"];(owner/"index.json").write_text(json.dumps(index));refresh()
 with pytest.raises(RuntimeError):command.validate_complete(owner,rows[0],2201,"softmax")
 result["points"][-1]["update"]=16000;result["outside_path"]="../../outside";result["outside_sha256"]="0"*64;(owner/"result.json").write_text(json.dumps(result));index["scores"]=result["points"];(owner/"index.json").write_text(json.dumps(index));refresh()
 with pytest.raises(RuntimeError):command.validate_complete(owner,rows[0],2201,"softmax")

def test_driver_owner_charge_ambiguity_never_appends_fallback(tmp_path,monkeypatch):
 command,rows,_,attempts,_,_=_driver_fixture(tmp_path,monkeypatch,"production");owner=command.owner_path(2201,"softmax");owner.mkdir();(owner/"attempt.json").write_text(json.dumps({"entry_id":"actual"}))
 rows.append({"entry_id":"other","kind":"attempt_charge","stage":"B","charged_seconds":1.,"output":str(owner)})
 with pytest.raises(RuntimeError):command.reconcile_owner(owner,tmp_path,0.)
 assert len(rows)==1
 rows[:] = [rows[0],{**rows[0],"entry_id":"second"}]
 with pytest.raises(RuntimeError):command.reconcile_owner(owner,tmp_path,0.)
 assert len(rows)==2

def test_driver_overhead_is_only_uncovered_difference_and_never_owner(tmp_path,monkeypatch):
 command,rows,_,attempts,_,_=_driver_fixture(tmp_path,monkeypatch,"production");owner=command.owner_path(2201,"softmax");owner.mkdir();(owner/"attempt.json").write_text(json.dumps({"entry_id":"owner"}));owned={"entry_id":"owner","kind":"attempt_charge","stage":"B","charged_seconds":5.,"output":str(owner)};rows.append(owned)
 monkeypatch.setattr(command,"charge",lambda start:3.)
 assert command.settle_owner(owner,owned,tmp_path,0.)==5. and len(rows)==1
 monkeypatch.setattr(command,"charge",lambda start:8.)
 assert command.settle_owner(owner,owned,tmp_path,0.)==8. and len(rows)==2 and rows[1]["kind"]=="driver_overhead" and rows[1]["charged_seconds"]==3.
 assert command.settle_owner(owner,owned,tmp_path,0.)==8. and len(rows)==2
 assert command.reconcile_owner(owner,tmp_path,0.)==owned

def test_driver_reservation_uses_one_locked_snapshot(tmp_path,monkeypatch):
 from execution.update_efficiency import command
 monkeypatch.setattr(command,"HERE",tmp_path);monkeypatch.setattr(command,"ROOT",tmp_path/"root");monkeypatch.setattr(command,"ATTEMPTS",tmp_path/"attempts");(tmp_path/"attempts").mkdir();rows=[];totals={"A":0.,"B":0.,"C":0.,"D":0.}
 monkeypatch.setattr(command,"locked_ledger_snapshot",lambda:("bound",(rows,totals)));monkeypatch.setattr(command,"ledger_rows",lambda *args:(_ for _ in ()).throw(AssertionError("second snapshot")))
 lock=command.acquire_reservation({"ledger_sha256":"bound"},"A",10.);assert lock.exists();lock.unlink()
 monkeypatch.setattr(command,"locked_ledger_snapshot",lambda:("mutated",(rows,totals)))
 with pytest.raises(RuntimeError):command.acquire_reservation({"ledger_sha256":"bound"},"A",10.)

def test_driver_append_uses_actual_single_descriptor_snapshot(tmp_path,monkeypatch):
 from execution.update_efficiency import command
 ledger=tmp_path/"ledger.jsonl";carry={"entry_id":"carry","kind":"inherited_budget","charged_seconds":0,"carried_budget_debit_seconds":command.CARRY};ledger.write_text(json.dumps(carry)+"\n")
 monkeypatch.setattr(command,"LEDGER",ledger);monkeypatch.setattr(command,"PREFIX_LINES",1);monkeypatch.setattr(command,"PREFIX_SHA",command.sha256(ledger))
 command.append_once({"entry_id":"row","kind":"attempt_charge","stage":"A","charged_seconds":1.})
 rows,_=command.ledger_rows(ledger);assert [r["entry_id"]for r in rows]==["carry","row"]

def test_driver_post_child_overrun_charges_full_failed_terminal(tmp_path,monkeypatch):
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch);clock={"now":0.};calls=[];monkeypatch.setattr(command.time,"monotonic",lambda:clock["now"])
 def child(argv,remaining,session):calls.append(remaining);clock["now"]=20.;return {"exit_code":0,"timed_out":False,"cleanup_verified":True}
 monkeypatch.setattr(command,"supervise",child)
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert calls and calls[0]>0 and len(rows)==1 and rows[0]["status"]=="FAILED" and rows[0]["charged_seconds"]==21. and rows[0]["resource_overrun"] and not lock.exists()

def test_driver_setup_exhaustion_never_supervises_and_records_overrun(tmp_path,monkeypatch):
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch);clock={"now":0.,"reads":0}
 def monotonic():
  clock["reads"]+=1
  if clock["reads"]==2:clock["now"]=20.
  return clock["now"]
 monkeypatch.setattr(command.time,"monotonic",monotonic)
 def child(*args):raise AssertionError("setup exhaustion must not supervise")
 monkeypatch.setattr(command,"supervise",child)
 with pytest.raises(TimeoutError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert len(rows)==1 and rows[0]["status"]=="FAILED" and rows[0]["charged_seconds"]==21. and rows[0]["resource_overrun"] and not lock.exists()

def test_driver_b_watchdog_exception_retains_lock(tmp_path,monkeypatch):
 command,rows,lock,_,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production");monkeypatch.setattr(command,"supervise",lambda *args:(_ for _ in ()).throw(RuntimeError("watchdog")))
 with pytest.raises(RuntimeError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
 assert rows and rows[0]["kind"]=="watchdog_uncertain_fallback" and lock.exists()

def test_driver_b_overhead_append_uncertainty_retains_without_retry(tmp_path,monkeypatch):
 for write_then_raise in (False,True):
  command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,"production");original=command.append_once;monkeypatch.setattr(command,"charge",lambda start:5.)
  monkeypatch.setattr(command,"supervise",lambda *args:(_complete_owner(command,attempts,rows),{"exit_code":0,"timed_out":False,"cleanup_verified":True})[1])
  def append(row,write_then_raise=write_then_raise):
   if row.get("kind")=="driver_overhead":
    if write_then_raise:original(row)
    raise OSError("fsync uncertainty")
   original(row)
  monkeypatch.setattr(command,"append_once",append)
  with pytest.raises(OSError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
  assert lock.exists() and len(rows)==(2 if write_then_raise else 1) and all(r["kind"]!="watchdog_uncertain_fallback"for r in rows)

def test_driver_final_terminal_failure_retains_a_and_b_reservations(tmp_path,monkeypatch):
 from execution.update_efficiency import command as imported_command
 base_durable=imported_command.durable
 for kind in ("smoke","production"):
  command,rows,lock,attempts,decision,seconds=_driver_fixture(tmp_path,monkeypatch,kind)
  if kind=="production":
   monkeypatch.setattr(command,"charge",lambda start:2.)
   monkeypatch.setattr(command,"supervise",lambda *args:(_complete_owner(command,attempts,rows),{"exit_code":0,"timed_out":False,"cleanup_verified":True})[1])
  else:monkeypatch.setattr(command,"supervise",lambda *args:{"exit_code":0,"timed_out":False,"cleanup_verified":True})
  def durable(path,value,original=base_durable):
   if Path(path).name=="terminal.json"and value.get("status")=="COMPLETE":raise OSError("terminal fsync")
   return original(path,value)
  monkeypatch.setattr(command,"durable",durable)
  with pytest.raises(OSError):command.main(["--decision",str(decision),"--seconds",str(seconds),"--seed","2201","--mode","softmax"])
  assert lock.exists() and rows and all(r.get("kind")!="watchdog_uncertain_fallback"for r in rows)

# Study-local watchdog fallback unit seams. These are static fixtures here; the
# reviewed runtime gate controls when the suite may be executed.
def _watchdog_ps(monkeypatch, output=b"1 1\n", error=b"", status=0, timeout=False):
 from execution.update_efficiency import watchdog
 class Helper:
  def __init__(self,*args,**kwargs):self.returncode=None;self.killed=False;self.reaped=False;self.calls=0;helper_state["helpers"].append(self)
  def communicate(self,timeout=None):
   self.calls+=1
   if self._timeout and self.calls==1:
    raise __import__("subprocess").TimeoutExpired("ps",timeout)
   self.returncode=self._status;self.reaped=True;return self._output,self._error
  def poll(self):return self.returncode
  def kill(self):self.killed=True
 monkeypatch.setattr(watchdog.subprocess,"Popen",Helper)
 helper_state={"output":output,"error":error,"status":status,"timeout":timeout,"helpers":[]}
 original=Helper.__init__
 def init(self,*args,**kwargs):
  original(self,*args,**kwargs);self._output=helper_state["output"];self._error=helper_state["error"];self._status=helper_state["status"];self._timeout=helper_state["timeout"]
 Helper.__init__=init
 return watchdog,helper_state

def test_watchdog_darwin_eperm_empty_valid_table_is_proven_and_recorded(tmp_path,monkeypatch):
 from execution.update_efficiency import watchdog
 own=os.getpid();own_group=os.getpgrp();_watchdog_ps(monkeypatch,f"{own} {own_group}\n".encode())
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 def probe(pgid,sig):raise PermissionError(errno.EPERM,"denied")
 monkeypatch.setattr(watchdog.os,"killpg",probe)
 gone,evidence=watchdog._group_probe(own_group+100000,time.monotonic()+2)
 assert gone and evidence["method"]=="darwin_ps" and evidence["member_pids"]==[]

@pytest.mark.parametrize("table,reason",[
 (lambda own,group:f"{own} {group}\n{own+1} 777777\n{own+1} 777778\n","duplicate PID"),
 (lambda own,group:"1 x\n","malformed"),
 (lambda own,group:"","empty"),
 (lambda own,group: f"{own+1} {group}\n","missing self"),
 (lambda own,group:f"{own} {group}","truncated row"),
])
def test_watchdog_darwin_invalid_or_unrelated_snapshot_never_matches(tmp_path,monkeypatch,table,reason):
 from execution.update_efficiency import watchdog
 own=os.getpid();group=os.getpgrp();_watchdog_ps(monkeypatch,table(own,group).encode())
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 with pytest.raises(RuntimeError):watchdog._group_probe(group+100000,time.monotonic()+2)

@pytest.mark.parametrize("status,error",[(1,b""),(0,b"warning")])
def test_watchdog_darwin_process_table_command_error_fails_closed(monkeypatch,status,error):
 from execution.update_efficiency import watchdog
 _watchdog_ps(monkeypatch,b"1 1\n",error,status)
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 with pytest.raises(RuntimeError):watchdog._group_probe(900000,time.monotonic()+2)

def test_watchdog_darwin_probe_timeout_kills_and_reaps_helper(monkeypatch):
 from execution.update_efficiency import watchdog
 watchdog,state=_watchdog_ps(monkeypatch,timeout=True)
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 with pytest.raises(TimeoutError):watchdog._group_probe(900000,time.monotonic()+1)
 assert state["timeout"] and state["helpers"][0].reaped and state["helpers"][0].killed

def test_watchdog_darwin_valid_unrelated_group_is_proven_absent(monkeypatch):
 from execution.update_efficiency import watchdog
 own=os.getpid();group=os.getpgrp();_watchdog_ps(monkeypatch,f"{own} {group}\n{own+1} 777777\n".encode())
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 gone,evidence=watchdog._group_probe(888888,time.monotonic()+2)
 assert gone and evidence["member_pids"]==[] and evidence["row_count"]==2

def test_watchdog_darwin_live_matching_member_is_present(monkeypatch):
 from execution.update_efficiency import watchdog
 own=os.getpid();group=os.getpgrp();_watchdog_ps(monkeypatch,f"{own} {group}\n42 888888\n".encode())
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 gone,evidence=watchdog._group_probe(888888,time.monotonic()+2)
 assert not gone and evidence["member_pids"]==[42]

def test_watchdog_non_darwin_eperm_and_expired_deadline_fail_closed(monkeypatch):
 from execution.update_efficiency import watchdog
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Linux")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 with pytest.raises(RuntimeError):watchdog._group_probe(42,time.monotonic()+1)
 with pytest.raises(TimeoutError):watchdog._group_probe(42,time.monotonic()-1)

def test_watchdog_normal_esrch_proves_absence(monkeypatch):
 from execution.update_efficiency import watchdog
 def gone(*args):raise ProcessLookupError(errno.ESRCH,"gone")
 monkeypatch.setattr(watchdog.os,"killpg",gone)
 assert watchdog._group_probe(42,time.monotonic()+1)==(True,{"method":"killpg_zero_esrch","pgid":42,"present":False})

@pytest.mark.parametrize("sig",[signal.SIGTERM,signal.SIGKILL])
def test_watchdog_signal_eperm_with_live_member_is_capability_failure(monkeypatch,sig):
 from execution.update_efficiency import watchdog
 own=os.getpid();group=os.getpgrp();_watchdog_ps(monkeypatch,f"{own} {group}\n42 900000\n".encode())
 monkeypatch.setattr(watchdog.platform,"system",lambda:"Darwin")
 monkeypatch.setattr(watchdog.os,"killpg",lambda *args:(_ for _ in ()).throw(PermissionError(errno.EPERM,"denied")))
 with pytest.raises(RuntimeError,match="signaling a live"):
  watchdog._signal_group(900000,sig,time.monotonic()+2)
