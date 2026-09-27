import numpy as np, pytest, torch
from types import SimpleNamespace
from schrodinger.route_policy import RoutePolicy
from schrodinger.route_policy_data import load_validation
from schrodinger.route_policy_metrics import heldout_bank
from schrodinger.route_policy_evaluation import evaluate_rollouts, evaluate_proper, mechanism_probe, local_mechanism_probe, weighted_known_valid_ratio, aggregate_rollout_metrics

class Counting(torch.nn.Module):
    def __init__(self, model): super().__init__(); self.model=model; self.mode=model.mode; self.calls=[]
    def forward(self,x,**kw): self.calls.append(len(x)); return self.model(x,**kw)

def test_cached_batched_rollouts_common_streams_and_metrics():
    torch.set_num_threads(2); problems=load_validation().problems[:2]; model=Counting(RoutePolicy("softmax")); cache={}
    first=evaluate_rollouts(model,problems,identity="checkpoint-a",seed=1701,splitcode=1,k=3,cache=cache)
    calls=len(model.calls); second=evaluate_rollouts(model,problems,identity="checkpoint-a",seed=1701,splitcode=1,k=3,cache=cache); cached_calls=len(model.calls)
    hotter=evaluate_rollouts(model,problems,identity="checkpoint-a",seed=1701,splitcode=1,k=3,temperature=2,cache=cache)
    other=evaluate_rollouts(model,problems,identity="checkpoint-b",seed=1701,splitcode=1,k=3,cache=cache)
    assert calls and max(model.calls)>1 and cached_calls==calls and first["problems"]==second["problems"]
    assert len(hotter["problems"])==len(first["problems"]) and len(model.calls)>calls and other["timing"]["cache_inference_seconds"]>=0
    assert set(first["timing"])=={"cache_inference_seconds","categorical_rollout_seconds","verifier_uniqueness_seconds","proper_seconds","mechanism_seconds","end_to_end_seconds"}
    assert {"Q","U_valid","U_novel","V_novel","coverage","duplicate_rate","invalid_rate"} <= set(first["problems"][0]["metrics"])
    rep=evaluate_rollouts(model,problems,identity="checkpoint-a",seed=1701,splitcode=1,k=3,cache=cache,replicate=1)
    uniform=evaluate_rollouts(model,problems,identity="uniform",seed=1701,splitcode=1,k=3,uniform_legal=True)
    assert rep["problems"][0]["attempts"] != first["problems"][0]["attempts"] or rep["problems"][1]["attempts"] != first["problems"][1]["attempts"]
    assert "weighted_known_valid_ratio" in uniform["mixture"] and set(uniform["maps"])=={p.map_id for p in problems}

def test_real_proper_cache_and_readonly_dt0_probe():
    problems=load_validation().problems[:2]; bank=heldout_bank(problems); model=Counting(RoutePolicy("schrodinger")); cache={}
    proper=evaluate_proper(model,bank,identity="c",cache=cache); calls=len(model.calls); repeat=evaluate_proper(model,bank,identity="c",cache=cache)
    assert len(proper["arrays"]["ce"])==len(bank.selected) and proper["weighted"]["ce"]==repeat["weighted"]["ce"] and len(model.calls)==calls
    before={k:v.detach().clone() for k,v in model.state_dict().items()}; probe=local_mechanism_probe(model.model,bank.selected[:4])
    assert set(probe["raw"]) >= {"all_rows_tv","cls_tv","av_abs_rms","projected_abs_rms","dt_h_spectral_norm","phase_dispersion","full_path_dt0_tv","ce_delta","kl_delta","brier_delta","greedy_disagreement"}
    assert len(probe["raw"]["all_rows_tv"])==4*2*2*13 and len(probe["raw"]["cls_tv"])==4*2*2 and probe["numerical"]["hermiticity_max"]<=1e-6 and probe["numerical"]["unitary_max"]<=2e-3
    assert probe["applicable"] and {"candidate","map_id","family","stratum","layer","head","row","cls"} <= set(probe["records"][0]) and len(probe["per_head"])==32
    assert {"canonical","goal","current","av_relative_rms","projected_relative_rms","dt_h_spectral_norm","phase_dispersion"} <= set(probe["records"][0]) and probe["per_stratum"]["routine_all_rows_tv"]["count"]>0
    assert {"canonical","map_id","family","stratum","goal","current","policy_tv","ce_delta","kl_delta","brier_delta","greedy_disagreement"} <= set(probe["fullpath_records"][0]) and probe["per_stratum"]["routine_fullpath_policy_tv"]["count"]>0
    assert probe["summary"]["all_rows_tv"]["max"]>1e-7 and probe["raw"]["all_rows_tv"] is not probe["raw"]["full_path_dt0_tv"] and len(probe["fullpath_records"])==4
    assert all(torch.equal(before[k],v) for k,v in model.state_dict().items())

def test_zero_dt0_same_score_and_na_denominators():
    problem=load_validation().problems[0]; model=RoutePolicy("softmax")
    normal=evaluate_rollouts(model,[problem],identity="same",seed=3,splitcode=1,k=2)
    zero=evaluate_rollouts(model,[problem],identity="same",seed=3,splitcode=1,k=2,dt0=True)
    assert normal["problems"]==zero["problems"]
    assert normal["problems"][0]["metrics"]["coverage"] is None or normal["problems"][0]["metrics"]["coverage"]>=0
    soft=mechanism_probe(model,heldout_bank([problem]).selected[:1]); assert not soft["applicable"] and soft["numerical"] is None and "all_rows_tv" not in soft["raw"]

def test_equal_map_weighting_with_unequal_problem_counts():
    free=bytes(144); a=SimpleNamespace(canonical=free,map_id=1,family="IIIIIIII",start=0,goal=1,M=1,Mnovel=0)
    b=SimpleNamespace(canonical=free,map_id=2,family="IIIIIIII",start=0,goal=1,M=1,Mnovel=0)
    model=RoutePolicy("softmax")
    got=evaluate_rollouts(model,[a,a,a,b],identity="weight",seed=1,splitcode=1,k=1,greedy=True)
    assert len(got["maps"])==2 and got["strata"]["routine"]["coverage"] is None and got["mixture"]["coverage"] is None
    assert weighted_known_valid_ratio(.4,.5,.1,.2)==pytest.approx(.34/.44) and weighted_known_valid_ratio(0,0,0,0) is None

def test_used_aggregation_equal_maps_and_mixture_ratio():
    def metric(q,known): return {k:(q if k in ("Q","known_valid_mass") else 0.) for k in ("Q","U_valid","U_novel","V_novel","pass_at_k","coverage","valid_headroom","duplicate_rate","invalid_rate","duplicate_concentration","known_valid_mass")}|{"Q":q,"known_valid_mass":known}
    per=[{"family":"IIIIIIII","map_id":1,"metrics":metric(.2,.1)}]*3+[{"family":"IIIIIIII","map_id":2,"metrics":metric(.8,.4)},{"family":"IIIILLLL","map_id":3,"metrics":metric(.2,.1)}]
    _,strata,mix=aggregate_rollout_metrics(per)
    assert strata["routine"]["Q"]==pytest.approx(.5) and mix["weighted_known_valid_ratio"]==pytest.approx((.8*.25+.2*.1)/(.8*.5+.2*.2))

def test_zero_reference_relative_probe_na():
    bank=heldout_bank(load_validation().problems[:1]); model=RoutePolicy("schrodinger")
    with torch.no_grad():
        for a in model.attn: a.v.weight.zero_(); a.v.bias.zero_(); a.o.weight.zero_(); a.o.bias.zero_()
    probe=local_mechanism_probe(model,bank.selected[:1])
    assert all(v is None for v in probe["raw"]["av_relative_rms"]) and all(v is None for v in probe["raw"]["projected_relative_rms"]) and probe["summary"]["av_relative_rms"]["count"]==0
