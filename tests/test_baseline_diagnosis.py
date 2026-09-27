import hashlib, json
from pathlib import Path
import pytest, torch
from types import SimpleNamespace
from execution.model_training_comparison.baseline_diagnosis_job import dag_aligned_bank, validate_checkpoint
from schrodinger.route_policy_data import legal_mask
from schrodinger.route_policy_experiment import FROZEN_CONFIG, IdentityError

def test_open_grid_dag_q_dedup_mask_and_hash_determinism():
    p=SimpleNamespace(canonical=bytes(144),map_id=7,family="IIIIIIII",start=0,goal=25)
    overlapping=SimpleNamespace(canonical=bytes(144),map_id=7,family="IIIIIIII",start=1,goal=25)
    a=dag_aligned_bank([p,p,overlapping]); b=dag_aligned_bank([p,overlapping])
    assert {c.current for c in a.candidates}=={0,1,12,13,24}
    assert next(c.q for c in a.candidates if c.current==0)==(0.,1/3,2/3,0.)
    assert len(a.candidates)==5 and all(c.current!=c.goal and sum(c.q)==pytest.approx(1) and not any(q and not legal for q,legal in zip(c.q,legal_mask(c))) for c in a.selected)
    assert a.selected_hash==b.selected_hash and a.q_hash==b.q_hash

def test_checkpoint_substitution_and_wrong_update_fail_before_inference(tmp_path):
    root=tmp_path; owner=root/"pilot-1701-softmax-1000"; cp=owner/"checkpoints"/"initial.pt"; cp.parent.mkdir(parents=True)
    identity={"seed":1701,"mode":"softmax","update":99,"parent_hash":None,"source":"s","config":FROZEN_CONFIG,"initial_hash":"i","input_ids":{"frozen_source_hash":"s"}}
    torch.save({"identity":identity,"model":{}},cp); good=hashlib.sha256(cp.read_bytes()).hexdigest(); (owner/"output-manifest.json").write_text(json.dumps({"checkpoints/initial.pt":{"sha256":good}}))
    import execution.model_training_comparison.baseline_diagnosis_job as job
    old=job.CHECKPOINTS; job.CHECKPOINTS={0:("pilot-1701-softmax-1000","checkpoints/initial.pt")}
    try:
        with pytest.raises(IdentityError,match="mode/seed/update"): validate_checkpoint(root,0)
        (owner/"output-manifest.json").write_text(json.dumps({"checkpoints/initial.pt":{"sha256":"0"*64}}))
        with pytest.raises(IdentityError,match="owner-manifest"): validate_checkpoint(root,0)
    finally: job.CHECKPOINTS=old
