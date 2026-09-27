from types import SimpleNamespace
from collections import Counter
from math import comb
import pytest
from execution.model_training_comparison.threeway_diagnosis_job import PREFIX,_dag,_joint,_startq,_support_status,b_candidates,match_triplet,validate_overlap
from schrodinger.route_policy_metrics import ScoreCandidate
from schrodinger.route_policy_data import Problem
from schrodinger.route_policy_metrics import _bfs

def test_literal_prefix_and_open_grid_bfs_goal_exclusion_and_overlap():
    assert PREFIX==b"goaldiag-route-v1\\0"
    canonical=bytes(144)
    base=Problem(canonical,1,"IIIIIIII",0,25,3,3,None)
    assert _startq(base,{}) == pytest.approx((0.,1/3,2/3,0.))
    saved=tuple(SimpleNamespace(canonical=s.canonical,current=s.current,goal=s.goal) for s in _dag(base))
    candidates=b_candidates(base,saved)
    assert all(p.goal!=25 and p.length in (14,15,16) and p.M==_bfs(canonical,p.goal)[1][p.start] for p in candidates)
    other=(SimpleNamespace(canonical=bytes([0])*143+b"\x01",current=0,goal=25),)
    assert any(p.goal==25 for p in b_candidates(base,other))
    validate_overlap((base,),(),saved)
    with pytest.raises(Exception): validate_overlap((),(base,),saved)

def test_joint_quota_is_deterministic_and_excludes_unsupported_triplet():
    canonical=bytes(144)
    # These synthetic rows exercise joint supply; BFS-specific coverage is above.
    rows=[[Problem(canonical,1,"IIIIIIII",i,20+i,14,1,None) for i in range(n)] for n in (3,2,4)]
    matched,meta=match_triplet(*rows)
    assert matched is None and meta["reason"] in {"route_support","state_support"}

def test_joint_round_robin_unequal_supply_keeps_exact_equal_quotas():
    canonical=bytes(144)
    def row(goal,current): return ScoreCandidate(canonical,1,"IIIIIIII",goal,current,(0.,1.,0.,0.))
    # Two shared bins, deliberately unequal supply; each quota is min(2, supplies).
    groups=tuple(tuple(row(10,i) for i in cells) for cells in ((1,2,3,20),(4,5,21),(6,7,8,22,23)))
    out,meta=_joint(groups,lambda x:(x.current>=20,1),lambda x:(x.current,x.goal),2,6)
    again,again_meta=_joint(groups,lambda x:(x.current>=20,1),lambda x:(x.current,x.goal),2,6)
    assert out==again and meta==again_meta and [len(x) for x in out]==[3,3,3]
    assert sorted(meta["quotas"].values())==[1,2]

def test_actual_quotas_after_cap_and_conditional_support_status():
    rows=tuple(ScoreCandidate(bytes(144),1,"IIIIIIII",100,i,(0.,1.,0.,0.)) for i in range(16))
    selected,meta=_joint((rows,rows,rows),lambda x:x.current//2,lambda x:x.current,2,6)
    assert sum(meta["capacities"].values())==16
    assert sum(meta["quotas"].values())==6
    assert meta["quotas"]=={str(i):int(i<6) for i in range(8)}
    for group in selected:
        assert Counter(x.current//2 for x in group)==Counter({i:1 for i in range(6)})
    assert _support_status({"IIIIIIII":8,"LLLLLLLL":8})=="MATCHED_SUPPORT_SUFFICIENT"
    assert _support_status({"IIIIIIII":12,"LLLLLLLL":7})=="MATCHED_SUPPORT_INSUFFICIENT"

def test_real_successful_route_dag_matching_and_exact_bank():
    canonical=bytes(144)
    cohorts=[]
    for map_id in (1,2,3):
        rows=[]
        for goal in (47,59,71):
            dist,count=_bfs(canonical,goal)
            length=dist[0]
            assert length in (14,15,16)
            assert count[0]==comb(length,11)
            p=Problem(canonical,map_id,"IIIIIIII",0,goal,length,count[0],None)
            assert _startq(p,{})==pytest.approx((0.,11/length,(length-11)/length,0.))
            rows.append(p)
        cohorts.append(tuple(rows))
    matched,meta=match_triplet(*cohorts)
    assert matched is not None
    assert [len(x) for x in matched["routes"]]==[3,3,3]
    assert meta["route"]["quotas"]=={str((length,2)):1 for length in (14,15,16)}
    counts=[]
    for states,bank in zip(matched["states"],matched["banks"]):
        assert 8<=len(states)<=32
        assert bank.selected==bank.candidates==states
        count=Counter()
        for s in states:
            dist,_=_bfs(s.canonical,s.goal)
            count[str((dist[s.current],sum(q>0 for q in s.q)))]+=1
            assert sum(s.q)==pytest.approx(1.)
        assert dict(count)=={k:v for k,v in meta["state"]["quotas"].items() if v}
        counts.append(count)
    assert counts[0]==counts[1]==counts[2]
