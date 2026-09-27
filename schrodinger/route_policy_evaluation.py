"""A2b2a pure batched route evaluation; no CLI, files, or release policy."""
from __future__ import annotations
import time
import math
from collections import defaultdict
import numpy as np
import torch
from .route_policy_data import RouteState, features, legal_mask, ACTIONS
from .route_policy_metrics import ScoreCandidate, proper_scores, weighted_proper, rollout_uniforms, choose_action, greedy_action, verify_route, route_metrics
from .route_feasibility import signature
from .attention import attention_from_scores

def _state(canonical,map_id,family,current,goal): return RouteState(canonical,map_id,family,current,goal,(0.,0.,0.,0.))
def _legal(canonical,current,goal,map_id=0,family=""):
    return legal_mask(_state(canonical,map_id,family,current,goal))
def _prob(logits, legal, temperature):
    z=np.asarray(logits,float)/temperature; z[~legal]=-np.inf; z-=np.max(z); p=np.exp(z); return p/p.sum()
def _logits(model, states, *, dt0=False):
    x=torch.tensor(np.stack([features(s) for s in states]))
    with torch.inference_mode(): out=model(x,dt_override=0. if dt0 and model.mode=="schrodinger" else None)
    return out.detach().cpu().numpy()

def evaluate_rollouts(model, problems, *, identity, seed, splitcode, support=frozenset(), k=32, temperature=1., greedy=False, dt0=False, cache=None, replicate=0, uniform_legal=False):
    """Advance all active routes together; every missing (map,goal,current) is one batch."""
    started=time.perf_counter(); cache={} if cache is None else cache; inference=rollout_time=verify_time=0.; attempts=[[] for _ in problems]
    active=[]
    uniforms={}
    for pi,p in enumerate(problems):
        for sample in range(1 if greedy else k):
            uniforms[pi,sample]=rollout_uniforms(seed,splitcode,p.map_id,p.start,p.goal,replicate,sample)
            active.append([pi,sample,p.start,bytearray()])
    for step in range(16):
        missing={}
        for pi,sample,current,route in active:
            p=problems[pi]
            if current!=p.goal: missing.setdefault((p.map_id,p.goal,current),_state(p.canonical,p.map_id,p.family,current,p.goal))
        todo=[(key,state) for key,state in missing.items() if (identity,dt0,*key) not in cache]
        if todo:
            then=time.perf_counter(); values=_logits(model,[s for _,s in todo],dt0=dt0); inference+=time.perf_counter()-then
            for (key,_),value in zip(todo,values): cache[(identity,dt0,*key)]=value.copy()
        nxt=[]; then=time.perf_counter()
        for pi,sample,current,route in active:
            p=problems[pi]
            if current==p.goal:
                nxt.append([pi,sample,current,route]); continue
            legal=_legal(p.canonical,current,p.goal,p.map_id,p.family); logits=cache[(identity,dt0,p.map_id,p.goal,current)]
            probs=np.where(legal,1/legal.sum(),0.) if uniform_legal else _prob(logits,legal,temperature); uniform=uniforms[pi,sample][step]
            action=greedy_action(probs,legal) if greedy else choose_action(probs,legal,uniform); route.append(action)
            row,col=divmod(current,12); dr,dc=ACTIONS[action]; nxt.append([pi,sample,(row+dr)*12+col+dc,route])
        rollout_time+=time.perf_counter()-then; active=nxt
    then=time.perf_counter()
    for pi,_,_,route in active:
        p=problems[pi]; raw=bytes(route); valid=verify_route(raw,p.canonical,p.start,p.goal); attempts[pi].append({"route":raw,"valid":valid,"novel":valid and signature(raw) not in support})
    verify_time+=time.perf_counter()-then
    per=[]; by_map=defaultdict(list); by_stratum=defaultdict(list)
    for p,rows in zip(problems,attempts):
        m=route_metrics([type("A",(),r)() for r in rows],p.M,p.Mnovel); m["known_valid_mass"]=sum(r["valid"] and not r["novel"] for r in rows)/len(rows); m["weighted_known_valid_ratio"]=None if not any(r["valid"] for r in rows) else sum(r["valid"] and not r["novel"] for r in rows)/sum(r["valid"] for r in rows)
        per.append({"map_id":p.map_id,"family":p.family,"attempts":rows,"metrics":m}); by_map[(p.family,p.map_id)].append(m)
    maps,strata,mixture=aggregate_rollout_metrics(per)
    return {"problems":per,"maps":maps,"strata":strata,"mixture":mixture,"cache":cache,"timing":{"cache_inference_seconds":inference,"categorical_rollout_seconds":rollout_time,"verifier_uniqueness_seconds":verify_time,"proper_seconds":0.,"mechanism_seconds":0.,"end_to_end_seconds":time.perf_counter()-started}}

def aggregate_rollout_metrics(per):
    """Frozen problem→equal-map→stratum→mixture aggregation, independently testable."""
    by_map=defaultdict(list)
    for item in per: by_map[(item["family"],item["map_id"])].append(item["metrics"])
    keys=("Q","U_valid","U_novel","V_novel","pass_at_k","coverage","valid_headroom","duplicate_rate","invalid_rate","duplicate_concentration","known_valid_mass")
    map_metrics={}; strata_maps=defaultdict(list)
    for (family,map_id), rows in by_map.items():
        values={key:([r[key] for r in rows if r[key] is not None]) for key in keys}; metrics={key:(None if not value else float(np.mean(value))) for key,value in values.items()}
        valid=sum(1-r["invalid_rate"] for r in rows); known=sum(r["known_valid_mass"] for r in rows); metrics["weighted_known_valid_ratio"]=None if valid==0 else known/valid
        item={"map_id":map_id,"family":family,"metrics":metrics}; map_metrics[map_id]=item; strata_maps["challenge" if family=="IIIILLLL" else "routine"].append(item)
    strata={}
    for stratum,maps in strata_maps.items():
        values={key:[m["metrics"][key] for m in maps if m["metrics"][key] is not None] for key in keys}; out={key:(None if not value else float(np.mean(value))) for key,value in values.items()}
        valid=sum(m["metrics"]["Q"] for m in maps); known=sum(m["metrics"]["known_valid_mass"] for m in maps); out["weighted_known_valid_ratio"]=None if valid==0 else known/valid; strata[stratum]=out
    mixture={key:(None if any(strata.get(s,{}).get(key) is None for s in ("routine","challenge")) else .8*strata["routine"][key]+.2*strata["challenge"][key]) for key in keys}
    mixture["weighted_known_valid_ratio"]=weighted_known_valid_ratio(strata.get("routine",{}).get("known_valid_mass",0.),strata.get("routine",{}).get("Q",0.),strata.get("challenge",{}).get("known_valid_mass",0.),strata.get("challenge",{}).get("Q",0.))
    return map_metrics,strata,mixture

def evaluate_proper(model, bank, *, identity, cache=None, dt0=False):
    started=time.perf_counter(); cache={} if cache is None else cache; missing=[]; logits=[]
    for c in bank.selected:
        key=(identity,dt0,c.map_id,c.goal,c.current)
        if key not in cache: missing.append((key,_state(c.canonical,c.map_id,c.family,c.current,c.goal)))
    if missing:
        values=_logits(model,[s for _,s in missing],dt0=dt0)
        for (key,_),value in zip(missing,values): cache[key]=value.copy()
    for c in bank.selected: logits.append(cache[(identity,dt0,c.map_id,c.goal,c.current)])
    legal=np.stack([_legal(c.canonical,c.current,c.goal,c.map_id,c.family) for c in bank.selected]); q=np.asarray([c.q for c in bank.selected])
    scores=proper_scores(np.asarray(logits),legal,q)
    return {"rows":bank.selected,"arrays":scores,"weighted":weighted_proper(bank.selected,scores),"cache":cache,"timing":{"proper_seconds":time.perf_counter()-started}}

def _summary(values):
    values=[v for v in values if v is not None]; a=np.asarray(values,float); return {"mean":float(a.mean()),"p50":float(np.percentile(a,50)),"p95":float(np.percentile(a,95)),"max":float(a.max()),"count":len(values)} if len(a) else {"mean":None,"p50":None,"p95":None,"max":None,"count":0}
def weighted_known_valid_ratio(routine_known, routine_valid, challenge_known, challenge_valid):
    denominator=.8*routine_valid+.2*challenge_valid
    return None if denominator==0 else (.8*routine_known+.2*challenge_known)/denominator
def _split(x):
    b,l,_=x.shape; return x.reshape(b,l,2,32).transpose(1,2)
def local_mechanism_probe(model, candidates):
    """Explicit detached reconstruction on normal-SA hidden inputs; no hooks persist."""
    if model.mode!="schrodinger": raise ValueError("local SA probe requires schrodinger model")
    started=time.perf_counter(); states=[_state(c.canonical,c.map_id,c.family,c.current,c.goal) for c in candidates]
    before={k:v.detach().clone() for k,v in model.state_dict().items()}; x=torch.tensor(np.stack([features(s) for s in states])); z=model.row(x)+model.pos; z=torch.cat((model.cls.expand(x.shape[0],-1,-1),z),1)
    raw={"all_rows_tv":[],"cls_tv":[],"av_abs_rms":[],"av_relative_rms":[],"projected_abs_rms":[],"projected_relative_rms":[],"dt_h_spectral_norm":[],"phase_dispersion":[]}; records=[]; herm=unit=rowerr=0.
    with torch.inference_mode():
        for layer,(norm,attn,norm2,ff) in enumerate(zip(model.norm1,model.attn,model.norm2,model.ff)):
            hidden=norm(z); q,k,v=(_split(part(hidden)) for part in (attn.q,attn.k,attn.v)); scores=q@k.transpose(-2,-1)/math.sqrt(32)
            dt=.5*torch.sigmoid(attn.raw_dt)[None,:,None,None]; gamma=math.pi*torch.tanh(attn.raw_gamma)[None,:,None,None]
            evolved,a,diag=attention_from_scores(scores,v,gamma*scores,dt,"schrodinger",return_diagnostics=True); base,base_a=attention_from_scores(scores,v)
            zero,zero_a=attention_from_scores(scores,v,gamma*scores,0.,"schrodinger")
            tv=.5*(a-base_a).abs().sum(-1); zero_tv=.5*(zero_a-base_a).abs().sum(-1)
            if float(zero_tv.max())>2e-6: raise FloatingPointError("dt0 local fidelity")
            av=evolved-base; proj=attn.o(evolved.transpose(1,2).reshape(x.shape[0],13,64))-attn.o(base.transpose(1,2).reshape(x.shape[0],13,64))
            h=.5*(scores+scores.transpose(-2,-1))/math.sqrt(13); phase=gamma*scores; wrapped=torch.atan2(torch.sin(phase-phase[..., :1]),torch.cos(phase-phase[..., :1]))
            av_rms=torch.sqrt((av*av).mean((-1,-2))); base_rms=torch.sqrt((base*base).mean((-1,-2)))
            raw["all_rows_tv"].extend(tv.flatten().tolist()); raw["cls_tv"].extend(tv[...,0].flatten().tolist()); raw["av_abs_rms"].extend(av_rms.flatten().tolist()); raw["av_relative_rms"].extend([None if float(d)==0 else float(n/d) for n,d in zip(av_rms.flatten(),base_rms.flatten())]); raw["dt_h_spectral_norm"].extend(torch.linalg.matrix_norm(dt*h,ord=2).flatten().tolist()); raw["phase_dispersion"].extend(torch.sqrt((wrapped*wrapped).mean(-1)).flatten().tolist())
            for bi,candidate in enumerate(candidates):
                for head in range(2):
                    w=attn.o.weight[:,head*32:(head+1)*32]; hp=evolved[bi,head]@w.T; hb=base[bi,head]@w.T; delta=hp-hb; nr=torch.sqrt((delta*delta).mean()); dr=torch.sqrt((hb*hb).mean())
                    raw["projected_abs_rms"].append(float(nr)); raw["projected_relative_rms"].append(None if float(dr)==0 else float(nr/dr))
                    for row in range(13): records.append({"candidate":bi,"canonical":candidate.canonical.hex(),"map_id":candidate.map_id,"family":candidate.family,"stratum":"challenge" if candidate.family=="IIIILLLL" else "routine","goal":candidate.goal,"current":candidate.current,"layer":layer,"head":head,"row":row,"cls":row==0,"all_rows_tv":float(tv[bi,head,row]),"cls_tv":float(tv[bi,head,0]),"av_abs_rms":float(av_rms[bi,head]),"av_relative_rms":None if float(base_rms[bi,head])==0 else float(av_rms[bi,head]/base_rms[bi,head]),"projected_abs_rms":float(nr),"projected_relative_rms":None if float(dr)==0 else float(nr/dr),"dt_h_spectral_norm":float(torch.linalg.matrix_norm((dt*h)[bi,head],ord=2)),"phase_dispersion":float(torch.sqrt((wrapped[bi,head,row]*wrapped[bi,head,row]).mean()))})
            herm=max(herm,diag.max_hermiticity_error); unit=max(unit,diag.max_unitarity_error); rowerr=max(rowerr,diag.max_probability_row_error)
            y=attn.o(evolved.transpose(1,2).reshape(x.shape[0],13,64)); z=z+y; z=z+ff(norm2(z))
        normal=model.head(model.final(z)[:,0]); ordinary=model(x); dtzero=model(x,dt_override=0.)
    if not torch.allclose(normal,ordinary,atol=2e-6,rtol=2e-5): raise FloatingPointError("manual normal reconstruction mismatch")
    legal=np.stack([legal_mask(s) for s in states]); q=np.asarray([c.q for c in candidates]); normal_np=normal.numpy(); zero_np=dtzero.numpy(); pn=proper_scores(normal_np,legal,q); p0=proper_scores(zero_np,legal,q)
    full_tv=[.5*np.abs(_prob(a,m,1)-_prob(b,m,1)).sum() for a,b,m in zip(normal_np,zero_np,legal)]; disagreement=[float(greedy_action(_prob(a,m,1),m)!=greedy_action(_prob(b,m,1),m)) for a,b,m in zip(normal_np,zero_np,legal)]
    numerical={"hermiticity_max":herm,"unitary_max":unit,"row_error_max":rowerr}
    if herm>1e-6 or unit>2e-3 or rowerr>2e-3: raise FloatingPointError("probe numerical abort")
    assert all(torch.equal(before[k],v) for k,v in model.state_dict().items())
    raw.update({"full_path_dt0_tv":full_tv,"greedy_disagreement":disagreement,"ce_delta":(p0["ce"]-pn["ce"]).tolist(),"kl_delta":(p0["kl"]-pn["kl"]).tolist(),"brier_delta":(p0["brier"]-pn["brier"]).tolist()})
    per_head={}
    for metric in ("all_rows_tv","cls_tv","av_abs_rms","av_relative_rms","projected_abs_rms","projected_relative_rms","dt_h_spectral_norm","phase_dispersion"):
        for layer in range(2):
            for head in range(2): per_head[f"layer{layer}_head{head}_{metric}"]=_summary([r[metric] for r in records if r["layer"]==layer and r["head"]==head])
    fullpath_records=[{"candidate":i,"canonical":c.canonical.hex(),"map_id":c.map_id,"family":c.family,"stratum":"challenge" if c.family=="IIIILLLL" else "routine","goal":c.goal,"current":c.current,"policy_tv":full_tv[i],"ce_delta":float(p0["ce"][i]-pn["ce"][i]),"kl_delta":float(p0["kl"][i]-pn["kl"][i]),"brier_delta":float(p0["brier"][i]-pn["brier"][i]),"greedy_disagreement":disagreement[i]} for i,c in enumerate(candidates)]
    per_stratum={}
    for stratum in ("routine","challenge"):
        for metric in ("all_rows_tv","cls_tv","av_abs_rms","av_relative_rms","projected_abs_rms","projected_relative_rms","dt_h_spectral_norm","phase_dispersion"):
            per_stratum[f"{stratum}_{metric}"]=_summary([r[metric] for r in records if r["stratum"]==stratum])
    for stratum in ("routine","challenge"):
        for metric in ("policy_tv","ce_delta","kl_delta","brier_delta","greedy_disagreement"): per_stratum[f"{stratum}_fullpath_{metric}"]=_summary([r[metric] for r in fullpath_records if r["stratum"]==stratum])
    return {"applicable":True,"raw":raw,"records":records,"fullpath_records":fullpath_records,"summary":{k:_summary(v) for k,v in raw.items()},"per_head":per_head,"per_stratum":per_stratum,"numerical":numerical,"timing":{"mechanism_seconds":time.perf_counter()-started}}
def mechanism_probe(model, candidates):
    """Read-only bounded numerical/local probe. Hooks are deliberately unnecessary."""
    if model.mode=="schrodinger": return local_mechanism_probe(model,candidates)
    started=time.perf_counter(); states=[_state(c.canonical,c.map_id,c.family,c.current,c.goal) for c in candidates]
    before={k:v.detach().clone() for k,v in model.state_dict().items()}; normal=_logits(model,states); dt0=_logits(model,states,dt0=True)
    legal=np.stack([legal_mask(s) for s in states]); tv=[]
    for a,b,m in zip(normal,dt0,legal): tv.append(.5*np.abs(_prob(a,m,1)-_prob(b,m,1)).sum())
    assert all(torch.equal(before[k],v) for k,v in model.state_dict().items())
    return {"applicable":False,"raw":{"full_path_dt0_tv":tv},"summary":{"full_path_dt0_tv":_summary(tv)},"numerical":None,"timing":{"mechanism_seconds":time.perf_counter()-started}}
