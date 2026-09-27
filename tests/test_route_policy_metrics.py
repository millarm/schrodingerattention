import numpy as np, pytest
from schrodinger.route_policy_data import load_validation
from schrodinger.route_policy_metrics import *

def candidate(current=1, goal=2, q=(0.,1.,0.,0.)):
    walls=bytearray(144); walls[0]=1
    return ScoreCandidate(bytes(walls),7,"IIIIIIII",goal,current,q)
def test_serialization_bank_qhash_and_probes():
    c=candidate(); assert serialize_candidate(c).hex()==("726f7574652d73636f72652d7631000c"+c.canonical.hex()+"00020001")
    bank=training_bank([candidate(1,2),candidate(13,2,(1.,0.,0.,0.))])
    assert bank.candidate_hash==record_hash(bank.candidates) and bank.selected_hash==record_hash(bank.selected) and bank.q_hash==q_array_hash(bank.selected)
    assert len(bank.selected)==2 and bank.map_counts==((7,2),) and probe_bank(bank,training=True)==bank.selected and training_bank(list(reversed(bank.candidates))).selected_hash==bank.selected_hash
    with pytest.raises(ValueError): training_bank([candidate(),candidate()])
def test_heldout_dedup_q_and_real_accepted_route():
    problem=next(p for p in load_validation().problems if p.family=="IIIIIIII")
    bank=heldout_bank([problem,problem]); assert len(bank.candidates)>0 and all(c.current!=c.goal for c in bank.candidates)
    c=bank.candidates[0]; assert np.isclose(sum(c.q),1) and verify_route(bytes(),c.canonical,c.current,c.goal) is False
    # A real frozen selected problem reaches its goal by its exact shortest oracle route.
    from schrodinger.route_feasibility import enumerate_routes
    route=enumerate_routes(problem.start,problem.goal,frozenset(i for i,x in enumerate(problem.canonical) if x),12)[0]
    assert verify_route(route,problem.canonical,problem.start,problem.goal)
    from types import SimpleNamespace
    tiny=SimpleNamespace(canonical=bytes(144),map_id=91,family="IIIIIIII",goal=14)
    exact=heldout_bank([tiny,tiny]); branch=next(c for c in exact.candidates if c.current==1 and c.goal==14)
    assert branch.q==(0.,.5,.5,0.) and len(exact.candidates)==143 and exact.q_hash=="54d38f25271b98f027a31aa0cd911dbeddd90c15f62103b0aaad57582cf9e30e"
def test_proper_weighting_and_na():
    logits=np.array([[0.,0.,99.,99.],[0.,0.,0.,99.]]) ; legal=np.array([[1,1,0,0],[1,1,1,0]],bool); q=np.array([[.5,.5,0,0],[1.,0,0,0]])
    s=proper_scores(logits,legal,q); assert np.allclose(s["ce"],[np.log(2),np.log(3)]) and np.allclose(s["kl"],[0,np.log(3)]) and np.all(s["p"][~legal]==0) and s["brier"][0]==0
    rows=[candidate(),ScoreCandidate(candidate().canonical,8,"IIIILLLL",2,1,(1.,0.,0.,0.))]; assert np.isclose(weighted_proper(rows,s)["ce"],.8*np.log(2)+.2*np.log(3)) and relative_improvement(0,1) is None
    with pytest.raises(ValueError): proper_scores(logits,legal,np.array([[.5,.5,0,0],[0,0,0,1.]]))
def test_streams_actions_routes_and_cache():
    a=rollout_uniforms(1701,1,7,1,2,0,3); assert np.array_equal(a,rollout_uniforms(1701,1,7,1,2,0,3)) and not np.array_equal(a,rollout_uniforms(1701,2,7,1,2,0,3))
    assert choose_action([.2,.8,0,0],[1,1,0,0],.999999)==1 and greedy_action([.5,.5,0,0],[1,1,0,0])==0
    free=bytes(144); good=rollout(free,0,13,lambda x: [0.,1.,0.,0.] if x==12 else [0.,0.,1.,0.], [.1,.1], support=frozenset({canonical_signature(b"\2\1")})); bad=rollout(free,0,13,lambda x: [1.,0.,0.,0.] if x==12 else [0.,0.,1.,0.], [.1]*16)
    assert good.valid and good.route==b"\2\1" and not good.novel and not bad.valid and len(bad.route)==16
    metrics=route_metrics([RolloutAttempt(b"\1",True,False),RolloutAttempt(b"\1",True,False),RolloutAttempt(b"\2",True,True),RolloutAttempt(b"\2",True,True),RolloutAttempt(b"",False,False)],4,4)
    assert metrics["Q"]==.8 and metrics["U_valid"]==.4 and metrics["U_novel"]==.2 and metrics["V_novel"]==.4 and metrics["duplicate_rate"]==.4 and metrics["invalid_rate"]==.2
    cache=LogitCache(); calls=[]; assert np.array_equal(cache.get_or_compute(("m",0,"none"),candidate(),lambda c:calls.append(c) or np.ones(4)),np.ones(4)); cache.get_or_compute(("m",0,"none"),candidate(),lambda c:np.zeros(4)); cache.get_or_compute(("m",1,"none"),candidate(),lambda c:calls.append(c) or np.ones(4)); assert len(calls)==2
def test_temperature_all_branches():
    hit=quality_temperature(lambda t:3-t,1.375); assert hit.matched and not hit.fallback and hit.direction=="nonincreasing" and hit.target==1.375
    grid=quality_temperature(lambda t:t,.9); assert grid.fallback and grid.temperature in (.5,.75,1.,1.25,1.5,2.)
    miss=quality_temperature(lambda t:3-t,9.); assert miss.fallback and not miss.matched
    entropy=entropy_temperature(lambda t:t,1.625); assert entropy.matched and not entropy.fallback and entropy.direction=="nondecreasing"
    calls=[]; cached=choose_temperature(lambda t:calls.append(t) or 3-t,9.,grid=(.25,.5,3.)); assert cached.fallback and len(calls)==len(set(calls))
    intermediate=quality_temperature(lambda t:5. if t==1.625 else 3-t,1.); assert intermediate.fallback
