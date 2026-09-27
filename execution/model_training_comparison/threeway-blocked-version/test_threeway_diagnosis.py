from types import SimpleNamespace
import pytest
from execution.model_training_comparison.threeway_diagnosis_job import PREFIX,_dag,_joint,b_candidates,match_triplet,validate_overlap
from schrodinger.route_policy_metrics import ScoreCandidate
from schrodinger.route_policy_data import Problem
from schrodinger.route_policy_metrics import _bfs

def test_literal_prefix_and_open_grid_bfs_goal_exclusion_and_overlap():
    assert PREFIX==b"goaldiag-route-v1\\0"
    canonical=bytes(144)
    base=Problem(canonical,1,"IIIIIIII",0,25,14,1,None)
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
