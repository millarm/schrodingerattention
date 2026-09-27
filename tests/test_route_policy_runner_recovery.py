"""Real composed command tests. Temporary compressed schedules are NOT production runs."""
import dataclasses
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
import schrodinger.route_policy_experiment as core


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_manifest(out):
    manifest=read(out/"output-manifest.json")
    assert manifest==core.file_manifest(out)
    assert "attempt.json" in manifest and "result.json" in manifest
    assert read(out/"attempt.json")["status"]=="COMPLETE"


@pytest.fixture(scope="module")
def frozen_inputs():
    # Accepted immutable source data, no fabricated probabilities or route sets.
    return core.load_training(),core.load_validation(),core.load_final_test()


def test_real_cli_profile_full_work_and_artifacts(tmp_path, monkeypatch, capsys, frozen_inputs):
    train,val,test=frozen_inputs
    monkeypatch.setattr(core,"load_training",lambda:train)
    monkeypatch.setattr(core,"load_validation",lambda:val)
    monkeypatch.setattr(core,"load_final_test",lambda:test)
    ledger=tmp_path/"actual-ledger.jsonl"; core.initialize_ledger(ledger)
    common=["--root",str(tmp_path),"--ledger",str(ledger)]
    core._cli(["prepare",*common,"--name","prepare"])
    prepared=tmp_path/"prepare/prepared.json"
    decision=tmp_path/"decision.json"
    decision.write_text(json.dumps({"approved":True,"kind":"smoke_or_profile","config_hash":core.config_hash(),"prepared_sha256":sha(prepared),"manifest_sha256":core.MANIFEST_SHA256}))
    core._cli(["profile",*common,"--name","profile","--prepared",str(prepared),"--decision",str(decision)])
    out=tmp_path/"profile"; record=read(out/"result.json"); profile=record["profile"]
    assert profile["run_order"]==["softmax","schrodinger"]
    assert profile["problem_count"]==96 and len(profile["map_ids"])==6
    assert [len(rows) for rows in profile["measured_step_seconds"]]==[20,20]
    assert len(profile["operations"])==30
    assert {r["name"] for r in profile["operations"]}=={"greedy","t1_k32","own_initial","uniform_legal","proper"}
    assert all(r["problems"]==32 and r["seconds"]>0 and (out/r["artifact"]).is_file() for r in profile["operations"])
    assert all(a["end"]<=b["start"] for a,b in zip(profile["phases"],profile["phases"][1:]))
    assert profile["exclusive_phase_seconds"]==pytest.approx(sum(p["seconds"] for p in profile["phases"]))
    assert 0<profile["exclusive_phase_seconds"]<=profile["end_to_end_seconds"]
    assert profile["actual_ledger_path"]==str(ledger.resolve()) and profile["actual_ledger_append_seconds"]>0
    assert profile["ledger_seconds"]>=profile["actual_ledger_append_seconds"]
    assert not (tmp_path/"ledger.jsonl").exists()
    for mode in ("softmax","schrodinger"):
        info=profile["models"][mode]
        assert info["warmup_count"]==5 and info["measured_count"]==20
        assert info["initial_checkpoint_hash"]==sha(out/f"{mode}-initial.pt")
        assert info["final_checkpoint_hash"]==sha(out/f"{mode}-update-25.pt")
        checkpoint=torch.load(out/f"{mode}-update-25.pt",weights_only=False)
        assert checkpoint["identity"]["update"]==25 and checkpoint["training_seconds"]>0
        assert len((out/f"{mode}-step-trace.jsonl").read_text().splitlines())==25
    for origin,count in (("training",64),("validation",128)):
        probe=read(out/f"probe-{origin}.json")
        assert probe["origin"]==origin and probe["count"]==count and len(set(probe["candidate_ids"]))==count
        assert profile["probe_banks"][origin]["numerical"]==probe["result"]["numerical"]
    assert set(record["provenance"]["source_files"])==set(core.runtime_provenance()["source_files"])
    assert any("A2b3-resource.md" in p for p in record["provenance"]["governing_files"])
    assert record["forecast"]["total_seconds"]>record["forecast"]["train_seconds"]>0
    check_manifest(out); check_manifest(tmp_path/"prepare")
    assert len(core._read(ledger))==3 and not (tmp_path/"experiment.lock").exists()
    assert all(json.loads(line)["status"]=="COMPLETE" for line in capsys.readouterr().out.splitlines())


def test_real_cli_paired_compressed_training_resume_and_authorization(tmp_path, monkeypatch, capsys, frozen_inputs):
    train,val,test=frozen_inputs
    assert (core.INITIAL_TARGET,core.PILOT_TARGETS,core.CHECKPOINT_INTERVAL)==(1000,(1000,2000,4000,8000),100)
    # Explicit test-only compression, keeping real model, optimizer, losses,
    # sampler, evaluator, checkpoint serializer and command ownership unchanged.
    monkeypatch.setattr(core,"INITIAL_TARGET",2)
    monkeypatch.setattr(core,"PILOT_TARGETS",(2,3))
    monkeypatch.setattr(core,"EVALUATION_UPDATES",(1,2,3))
    monkeypatch.setattr(core,"CHECKPOINT_INTERVAL",1)
    tiny=dataclasses.replace(train,states=train.states[:128])
    monkeypatch.setattr(core,"load_training",lambda:tiny)
    monkeypatch.setattr(core,"load_validation",lambda:dataclasses.replace(val,problems=val.problems[:1]))
    monkeypatch.setattr(core,"load_final_test",lambda:dataclasses.replace(test,problems=test.problems[:1]))
    monkeypatch.setattr(core,"training_probe_candidates",lambda bank:bank.selected[:2])
    monkeypatch.setattr(core,"validation_probe_candidates",lambda bank:bank.selected[:2])
    ledger=tmp_path/"ledger.jsonl"; core.initialize_ledger(ledger)
    common=["--root",str(tmp_path),"--ledger",str(ledger)]
    core._cli(["prepare",*common,"--name","prepare"])
    prepared=tmp_path/"prepare/prepared.json"; _,ids=core._prepared_ids(prepared)
    base={"approved":True,"kind":"pilot","command":"train","seed":1701,"target_updates":2,"run_kind":"fresh","config_hash":core.config_hash(),"prepared_sha256":sha(prepared),"manifest_sha256":core.MANIFEST_SHA256}
    records={}
    for mode in ("softmax","schrodinger"):
        decision=tmp_path/f"{mode}-decision.json"; decision.write_text(json.dumps({**base,"mode":mode}))
        core._cli(["train",*common,"--name",mode,"--mode",mode,"--updates","2","--prepared",str(prepared),"--decision",str(decision)])
        out=tmp_path/mode; record=read(out/"result.json"); result=record["result"]; records[mode]=record
        assert result["initial_checkpoint_hash"]==sha(Path(result["initial_checkpoint_path"]))
        assert result["final_checkpoint"]==sha(Path(result["final_checkpoint_path"]))
        assert [e["update"] for e in result["events"]]==[0,1,2]
        assert all(set(e["probes"])=={"training","validation"} for e in result["events"])
        assert len((out/"checkpoints/curves.jsonl").read_text().splitlines())==2
        check_manifest(out)
    assert records["softmax"]["shared_initial_digest"]==records["schrodinger"]["shared_initial_digest"]
    assert records["softmax"]["parameter_count"]==records["schrodinger"]["parameter_count"]
    assert [r["batch_digest"] for r in records["softmax"]["result"]["curves"]]==[r["batch_digest"] for r in records["schrodinger"]["result"]["curves"]]
    for field,value in (("seed",1702),("mode","schrodinger"),("target_updates",3),("run_kind","resume")):
        with pytest.raises(PermissionError):
            core._require_run_binding({**base,"mode":"softmax",field:value},SimpleNamespace(seed=1701,mode="softmax",updates=2,resume=None))
    first=records["schrodinger"]["result"]; cp=Path(first["final_checkpoint_path"]); initial=Path(first["initial_checkpoint_path"])
    payload=torch.load(cp,weights_only=False)
    bound={**payload["identity"],"checkpoint_hash":sha(cp),"initial_checkpoint_hash":sha(initial)}
    decision=tmp_path/"resume-decision.json"; decision.write_text(json.dumps({**base,"mode":"schrodinger","target_updates":3,"run_kind":"resume","resume_identity":bound}))
    resume_args=["train",*common,"--name","resumed","--mode","schrodinger","--updates","3","--prepared",str(prepared),"--decision",str(decision),"--resume",str(cp),"--resume-hash",sha(cp),"--initial-checkpoint",str(initial)]
    core._cli(resume_args)
    result=read(tmp_path/"resumed/result.json")["result"]
    assert result["start_update"]==2 and [e["update"] for e in result["events"]]==[3]
    assert result["initial_checkpoint_hash"]==first["initial_checkpoint_hash"]
    assert result["events"][0]["routes"]["own_initial"]["problems"]==first["events"][0]["routes"]["own_initial"]["problems"]
    _,full,_=core.paired_models(1701); opt=core.optimizer(full); sampler=core.MapBalancedSampler(tiny.states,1701)
    for _ in range(3): step=core.train_step(full,opt,sampler)
    resumed=torch.load(Path(result["final_checkpoint_path"]),weights_only=False)
    assert core.state_hash(full)==core.state_hash_from_state(resumed["model"])
    assert step["batch_digest"]==result["curves"][-1]["batch_digest"]
    check_manifest(tmp_path/"resumed")
    # Same initial identity but substituted bytes/model must fail before restore.
    substitute=tmp_path/"substitute.pt"; bad=torch.load(initial,weights_only=False)
    bad["model"]["cls"]=bad["model"]["cls"]+1; torch.save(bad,substitute)
    badargs=resume_args.copy(); badargs[badargs.index("resumed")]="bad-initial"; badargs[-1]=str(substitute)
    with pytest.raises(core.IdentityError,match="initial checkpoint"):
        core._cli(badargs)
    assert read(tmp_path/"bad-initial/attempt.json")["status"]=="FAILED"
    assert not (tmp_path/"experiment.lock").exists()
    capsys.readouterr()
