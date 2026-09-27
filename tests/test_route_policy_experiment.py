import hashlib, json, signal, time
from pathlib import Path
import pytest, torch
from schrodinger.route_policy_data import load_training, MapBalancedSampler
from schrodinger.route_policy_experiment import *
from schrodinger.route_policy_experiment import _read
import schrodinger.route_policy_experiment as core

def test_ledger_budget_and_attempt_lifecycle(tmp_path):
    ledger=tmp_path/"ledger.jsonl"; initialize_ledger(ledger)
    assert ledger_totals(_read(ledger))["global"]==CARRY and deadline_seconds(ledger,"A")>0
    with pytest.raises(BudgetError): append_once(ledger,{"entry_id":"x","kind":"attempt","stage":"A","charged_seconds":float("nan")})
    with OwnedAttempt.begin(tmp_path,ledger,"A","one") as attempt: assert attempt.output.exists()
    assert _read(ledger)[-1]["status"]=="FINALIZATION_UNCERTAIN" and json.loads((attempt.output/"attempt.json").read_text())["status"]=="COMPLETE" and signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0) and not (tmp_path/"experiment.lock").exists()
    with pytest.raises(FileExistsError): OwnedAttempt.begin(tmp_path,ledger,"A","one")
    held=tmp_path/"experiment.lock"; held.write_text("x")
    with pytest.raises(RuntimeError): OwnedAttempt.begin(tmp_path,ledger,"A","two")
    held.unlink()
    with pytest.raises(ValueError):
        with OwnedAttempt.begin(tmp_path,ledger,"A","three"): raise ValueError("boom")
    assert _read(ledger)[-1]["status"]=="FINALIZATION_UNCERTAIN" and json.loads((tmp_path/"three"/"attempt.json").read_text())["status"]=="FAILED" and not (tmp_path/"experiment.lock").exists()

def test_ledger_rejects_bad_carry_ids_and_exhaustion(tmp_path):
    with pytest.raises(BudgetError): ledger_totals([])
    bad=[{"entry_id":"a","kind":"inherited_budget","charged_seconds":0,"carried_budget_debit_seconds":CARRY},{"entry_id":"a","kind":"attempt","stage":"A","charged_seconds":0}]
    with pytest.raises(BudgetError): ledger_totals(bad)
    ledger=tmp_path/"overrun.jsonl"; initialize_ledger(ledger); append_once(ledger,{"entry_id":"b","kind":"attempt","stage":"A","charged_seconds":STAGES["A"]+1})
    assert ledger_totals(_read(ledger))["A"]==STAGES["A"]+1
    with pytest.raises(BudgetError): deadline_seconds(ledger,"A")

def test_prepare_payload_immutable_and_final_release_guard(tmp_path):
    from schrodinger.route_policy_data import load_training, load_validation, load_final_test
    payload=prepare_banks(load_training(),load_validation(),load_final_test()); path=tmp_path/"prepared.json"; digest=write_prepared(path,payload)
    assert digest and payload["config_hash"]==config_hash() and payload["test"]["selected"] and "id" in payload["test"]["selected"][0]
    with pytest.raises(FileExistsError): write_prepared(path,payload)
    identities=[{"seed":2101+i//2,"mode":("softmax","schrodinger")[i%2],"checkpoint_hash":f"{i:064x}","config_hash":config_hash(),"status":"COMPLETE"} for i in range(20)]
    decision={"approved":True,"config_hash":config_hash(),"test_bank_hash":payload["test"]["selected_hash"],"completed_main_identities":identities,"pilot_accepted":True,"power_accepted":True,"runtime_accepted":True}
    require_final_release(decision,config_digest=config_hash(),test_bank_hash=payload["test"]["selected_hash"])
    with pytest.raises(PermissionError): require_final_release({**decision,"completed_main_identities":identities[:-1]},config_digest=config_hash(),test_bank_hash=payload["test"]["selected_hash"])

def test_smoke_pair_real_steps_checkpoints_and_decision(tmp_path):
    from schrodinger.route_policy_data import load_training, load_validation
    from schrodinger.route_policy_metrics import heldout_bank
    states=load_training().states[:128]; bank=heldout_bank(load_validation().problems[:1])
    with pytest.raises(PermissionError): smoke_pair(states,bank,root=tmp_path/"bad",decision={})
    got=smoke_pair(states,bank,root=tmp_path/"smoke",decision={"approved":True,"kind":"smoke_or_profile"})
    assert got["shared_init"] and all(got[name]["final_checkpoint"] and (tmp_path/"smoke"/name/"initial.pt").exists() for name in ("softmax","schrodinger"))

def test_profile_forecast_uses_20_cells_and_conservative_missing_stratum():
    profile={"measured_step_seconds":[[1.]*20,[2.]*20],"stratum_seconds":[3.,5.]}
    got=forecast_profile(profile,remaining_updates=10,checkpoints=2,evaluations=4,serialization_seconds=1,audit_seconds=2)
    assert got["profile_seed"]==1699 and got["train_seconds"]==45 and got["conservative_cell_seconds"]==5 and got["evaluation_io_seconds"]==33
    with pytest.raises(ValueError): forecast_profile({"measured_step_seconds":[[1.]*19,[1.]*20]})

def test_full_forecast_counts_all_prescribed_work_and_profile_subset():
    profile={"measured_step_seconds":[[1.]*20,[2.]*20],"stratum_cells":{"routine":3.},"probe_seconds":3.,"setup_seconds":4.,"ledger_seconds":5.,"checkpoint_io_seconds":1.,"serialization_per_problem_seconds":.01,"trace_per_step_seconds":.01}
    got=full_work_forecast(profile,remaining_updates=10)
    assert got["checkpoint_count"]==11 and got["evaluation_updates"]==[0,500,1000] and got["per_stratum_problem_seconds"]=={"routine":3.,"challenge":3.} and got["future_temperature_work"]=="NOT_IMPLEMENTED_GATED_COSTED" and got["temperature_work_seconds"]>0 and got["total_seconds"]>got["train_seconds"]
    from schrodinger.route_policy_data import load_validation
    subset=profile_map_subset(load_validation())
    assert len({p.map_id for p in subset})==6 and len(subset)==96

def test_frozen_probe_selectors_have_literal_family_map_counts():
    from schrodinger.route_policy_data import load_training,load_validation
    train=training_probe_candidates(training_bank(load_training().states)); validation=validation_probe_candidates(heldout_bank(load_validation().problems))
    assert len(train)==64 and {c.family for c in train}=={"IIIIIIII","LLLLLLLL"}
    assert len(validation)==128 and {c.family for c in validation}=={"IIIIIIII","LLLLLLLL","IIIILLLL"}

def test_cli_prints_complete_only_after_successful_owned_finalization(tmp_path, monkeypatch, capsys):
    ledger=tmp_path/"ledger.jsonl"; initialize_ledger(ledger)
    monkeypatch.setattr(core,"command_prepare",lambda out:{"prepared":True})
    core._cli(["prepare","--root",str(tmp_path),"--ledger",str(ledger),"--name","ok"])
    assert json.loads(capsys.readouterr().out)["status"]=="COMPLETE"
    monkeypatch.setattr(core,"append_once",lambda *_args,**_kwargs: (_ for _ in ()).throw(OSError("forced ledger finalization")))
    with pytest.raises(OSError,match="forced ledger"): core._cli(["prepare","--root",str(tmp_path),"--ledger",str(ledger),"--name","bad"])
    assert "COMPLETE" not in capsys.readouterr().out and not (tmp_path/"experiment.lock").exists()

def test_scheduled_training_validated_resume_matches_continuation(tmp_path):
    from schrodinger.route_policy_data import load_training
    states=load_training().states[:128]; decision={"approved":True,"kind":"smoke_or_profile"}; config={"batch":64,"lr":.001}; ids={"training_bundle":"x","support":"y","paired_stream":"z"}
    full,_,_=paired_models(1701); full_run=scheduled_training(full,optimizer(full),MapBalancedSampler(states,1701),seed=1701,source="resume",config=config,input_ids=ids,checkpoint_dir=tmp_path/"full",updates=3,decision=decision)
    split,_,_=paired_models(1701); first=scheduled_training(split,optimizer(split),MapBalancedSampler(states,1701),seed=1701,source="resume",config=config,input_ids=ids,checkpoint_dir=tmp_path/"split",updates=2,decision=decision)
    payload=torch.load(tmp_path/"split"/"update-2.pt",weights_only=False); identity=payload["identity"]
    initial_hash=hashlib.sha256((tmp_path/"split"/"initial.pt").read_bytes()).hexdigest()
    bound={"seed":1701,"mode":"softmax","source":"resume","config":config,"input_ids":ids,"initial_hash":identity["initial_hash"],"update":2,"parent_hash":identity["parent_hash"],"checkpoint_hash":first["final_checkpoint"],"initial_checkpoint_hash":initial_hash}
    resume_decision={**decision,"resume_identity":bound}
    resumed,_,_=paired_models(1701); resumed_run=scheduled_training(resumed,optimizer(resumed),MapBalancedSampler(states,1701),seed=1701,source="resume",config=config,input_ids=ids,checkpoint_dir=tmp_path/"resume",updates=3,decision=resume_decision,resume={"path":tmp_path/"split"/"update-2.pt","hash":first["final_checkpoint"],"initial_path":tmp_path/"split"/"initial.pt"})
    assert all(torch.equal(a,b) for a,b in zip(full.parameters(),resumed.parameters())) and resumed_run["final_checkpoint"] and [row["batch_digest"] for row in full_run["curves"]][-1]==resumed_run["curves"][-1]["batch_digest"] and resumed_run["start_update"]==2 and not resumed_run["events"]
    bad,_,_=paired_models(1701)
    before=state_hash(bad)
    with pytest.raises(IdentityError): scheduled_training(bad,optimizer(bad),MapBalancedSampler(states,1701),seed=1701,source="wrong",config=config,input_ids=ids,checkpoint_dir=tmp_path/"badresume",updates=3,decision=decision,resume={"path":tmp_path/"split"/"update-2.pt","hash":first["final_checkpoint"]})
    assert state_hash(bad)==before
    with pytest.raises(IdentityError): scheduled_training(bad,optimizer(bad),MapBalancedSampler(states,1701),seed=1701,source="resume",config={"batch":1},input_ids=ids,checkpoint_dir=tmp_path/"badconfig",updates=3,decision=decision,resume={"path":tmp_path/"split"/"update-2.pt","hash":first["final_checkpoint"]})

def test_attempt_output_record_failure_still_charges_and_cleans(tmp_path,monkeypatch):
    ledger=tmp_path/"ledger.jsonl"; initialize_ledger(ledger); attempt=OwnedAttempt.begin(tmp_path,ledger,"A","broken")
    monkeypatch.setattr(Path,"write_text",lambda *_args,**_kwargs: (_ for _ in ()).throw(OSError("disk")))
    with pytest.raises(ArtifactError): attempt.finalize("COMPLETE")
    assert _read(ledger)[-1]["status"]=="FAILED_ARTIFACT" and _read(ledger)[-1]["entry_id"]==attempt.entry_id and not (tmp_path/"experiment.lock").exists()

def test_timer_and_postwrite_fsync_failure_cleanup(tmp_path,monkeypatch):
    ledger=tmp_path/"ledger.jsonl"; initialize_ledger(ledger); prior=signal.getsignal(signal.SIGALRM)
    attempt=OwnedAttempt.begin(tmp_path,ledger,"A","timer"); signal.setitimer(signal.ITIMER_REAL,.001)
    with pytest.raises(TimeoutError): time.sleep(.02)
    attempt.finalize("FAILED","timeout")
    assert signal.getsignal(signal.SIGALRM)==prior and signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0)
    broken=OwnedAttempt.begin(tmp_path,ledger,"A","fsync")
    monkeypatch.setattr(core.os,"fsync",lambda _fd: (_ for _ in ()).throw(OSError("fsync after write")))
    with pytest.raises(OSError,match="after write"): broken.finalize("COMPLETE")
    rows=[r for r in _read(ledger) if r.get("entry_id")==broken.entry_id]
    failure=json.loads((broken.output/"finalization_error.json").read_text())
    assert len(rows)==1 and rows[0]["kind"]=="attempt_charge" and rows[0]["status"]=="FINALIZATION_UNCERTAIN" and failure["status"]=="FAILED_LEDGER"
    assert json.loads((broken.output/"attempt.json").read_text())["status"]=="FAILED_LEDGER" and not (tmp_path/"experiment.lock").exists() and signal.getsignal(signal.SIGALRM)==prior
    arming=tmp_path/"arming"; original=core.signal.setitimer; calls=0
    def fail_arming(*args):
        nonlocal calls
        calls+=1
        if calls==2: raise OSError("arming")
        return original(*args)
    monkeypatch.setattr(core.signal,"setitimer",fail_arming)
    with pytest.raises(OSError,match="arming"): OwnedAttempt.begin(tmp_path,ledger,"A","arming")
    assert signal.getsignal(signal.SIGALRM)==prior and signal.getitimer(signal.ITIMER_REAL)==(0.0,0.0) and not (tmp_path/"experiment.lock").exists() and arming.exists()

def test_paired_core_checkpoint_resume_and_identity_chain(tmp_path):
    torch.set_num_threads(2); states=load_training().states[:128]; soft,sch,digest=paired_models(1701)
    assert digest and state_hash(soft)!=state_hash(sch)
    config={"batch":64,"lr":.001}; source="fixture"; ids={"training_bundle":"x","support":"y","paired_stream":"z"}
    initial=state_hash(soft); sa_initial=state_hash(sch); opt=optimizer(soft); sopt=optimizer(sch)
    with torch.no_grad():
        sch.attn[0].raw_dt.copy_(torch.tensor([-1.,1.])); sch.attn[0].raw_gamma.copy_(torch.tensor([-.2,.3])); soft.attn[0].alpha.copy_(torch.tensor([-.4,.6])); soft.attn[0].beta.copy_(torch.tensor([-.7,.8]))
    initial=state_hash(soft); sa_initial=state_hash(sch)
    sampler=MapBalancedSampler(states,1701); paired=MapBalancedSampler(states,1701)
    assert MapBalancedSampler.batch_hash(sampler.batch())==MapBalancedSampler.batch_hash(paired.batch())
    sampler=MapBalancedSampler(states,1701); assert opt is not sopt and opt.state is not sopt.state
    cp0=tmp_path/"soft-initial.pt"; initial_checkpoint=checkpoint(cp0,model=soft,opt=opt,sampler=sampler,seed=1701,mode="softmax",source=source,config=config,initial_hash=initial,update=0,training_seconds=0,parent=None,input_ids=ids)
    plain=train_step(soft,opt,sampler)
    original_clip=torch.nn.utils.clip_grad_norm_; captured={}
    def capture_clip(parameters,*args,**kwargs):
        captured.update({name:p.grad.detach().clone() for name,p in soft.named_parameters()})
        return original_clip(parameters,*args,**kwargs)
    torch.nn.utils.clip_grad_norm_=capture_clip
    try: first=train_step(soft,opt,sampler,summary=True)
    finally: torch.nn.utils.clip_grad_norm_=original_clip
    assert "summary" not in plain and first["training_core_seconds"]==first["materialize_seconds"]+first["neural_seconds"] and first["end_to_end_seconds"]>=first["training_core_seconds"]+first["summary"]["summary_seconds"]
    summary=first["summary"]; assert summary["update_weight_ratio"] is not None and set(summary["group_gradient_norms"])=={"embedding","attention","feedforward","normalization_head","controls"} and all(torch.isfinite(p).all() for p in soft.parameters())
    assert summary["scalar_values"]["attention.0.alpha"][0] != summary["scalar_values"]["attention.0.alpha"][1] and summary["scalar_values"]["attention.0.beta"][0] != summary["scalar_values"]["attention.0.beta"][1]
    manual={"embedding":[],"attention":[],"feedforward":[],"normalization_head":[],"controls":[]}
    for name,p in soft.named_parameters():
        group="controls" if name.endswith(("alpha","beta","raw_dt","raw_gamma")) else "embedding" if name in ("row.weight","row.bias","pos","cls") else "attention" if name.startswith("attn.") else "feedforward" if name.startswith("ff.") else "normalization_head"
        manual[group].append(captured[name].square().sum())
    assert summary["group_gradient_norms"]=={k:float(torch.sqrt(sum(v))) for k,v in manual.items()}
    cp1=tmp_path/"soft-update-2.pt"; update_checkpoint=checkpoint(cp1,model=soft,opt=opt,sampler=sampler,seed=1701,mode="softmax",source=source,config=config,initial_hash=initial,update=2,training_seconds=plain["training_core_seconds"]+first["training_core_seconds"],parent=initial_checkpoint,input_ids=ids)
    uninterrupted=train_step(soft,opt,sampler); expected=[p.detach().clone() for p in soft.parameters()]
    restored,_,_=paired_models(1701); ropt=optimizer(restored); rsampler=MapBalancedSampler(states,1701); before=state_hash(restored); rng=torch.get_rng_state().clone()
    for kwargs in ({"source":"wrong"},{"config":{"batch":32}},{"input_ids":{**ids,"support":"wrong"}},{"parent":"0"*64},{"mode":"schrodinger"}):
        args=dict(seed=1701,mode="softmax",source=source,config=config,initial_hash=initial,input_ids=ids,update=2,parent=initial_checkpoint); args.update(kwargs)
        with pytest.raises(IdentityError): restore(cp1,model=restored,opt=ropt,sampler=rsampler,**args)
        assert state_hash(restored)==before and not ropt.state and torch.equal(torch.get_rng_state(),rng)
    payload=restore(cp1,model=restored,opt=ropt,sampler=rsampler,seed=1701,mode="softmax",source=source,config=config,initial_hash=initial,input_ids=ids,update=2,parent=initial_checkpoint)
    replay=train_step(restored,ropt,rsampler)
    assert payload["identity"]["parent_hash"]==initial_checkpoint and payload["training_seconds"]==plain["training_core_seconds"]+first["training_core_seconds"] and replay["scalars"]==uninterrupted["scalars"] and all(torch.equal(a,b) for a,b in zip(expected,restored.parameters()))
    with pytest.raises(FileExistsError): checkpoint(cp1,model=soft,opt=opt,sampler=sampler,seed=1701,mode="softmax",source=source,config=config,initial_hash=initial,update=2,training_seconds=0,parent=initial_checkpoint,input_ids=ids)
    ssampler=MapBalancedSampler(states,1701); sacp=tmp_path/"sa-initial.pt"; checkpoint(sacp,model=sch,opt=sopt,sampler=ssampler,seed=1701,mode="schrodinger",source=source,config=config,initial_hash=sa_initial,update=0,training_seconds=0,parent=None,input_ids=ids)
    sa_expected=train_step(sch,sopt,ssampler); sa_parameters=[p.detach().clone() for p in sch.parameters()]
    _,restored_sa,_=paired_models(1701); rsaopt=optimizer(restored_sa); rsasampler=MapBalancedSampler(states,1701)
    restore(sacp,model=restored_sa,opt=rsaopt,sampler=rsasampler,seed=1701,mode="schrodinger",source=source,config=config,initial_hash=sa_initial,input_ids=ids,update=0,parent=None)
    replay_sa=train_step(restored_sa,rsaopt,rsasampler)
    assert replay_sa["scalars"]==sa_expected["scalars"] and all(torch.equal(a,b) for a,b in zip(sa_parameters,restored_sa.parameters()))
    controls=core._control_values(restored_sa); raw=restored_sa.attn[0]
    assert controls["attention.0.dt"]==pytest.approx((.5*torch.sigmoid(raw.raw_dt.detach())).tolist()) and controls["attention.0.gamma"]==pytest.approx((torch.pi*torch.tanh(raw.raw_gamma.detach())).tolist()) and controls["attention.0.dt"][0]!=controls["attention.0.dt"][1]
