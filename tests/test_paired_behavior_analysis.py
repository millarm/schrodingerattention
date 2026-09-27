import importlib.util
from pathlib import Path
import sys
import pytest
import numpy as np

_spec=importlib.util.spec_from_file_location("paired_behavior_analysis",Path(__file__).parents[1]/"execution/paired_behavior/analysis.py")
_module=importlib.util.module_from_spec(_spec); assert _spec.loader is not None; _spec.loader.exec_module(_module)
AlignmentError=_module.AlignmentError; equal_map_summary=_module.equal_map_summary; paired_greedy=_module.paired_greedy; paired_states=_module.paired_states; valid_route_sets=_module.valid_route_sets
sys.path.insert(0,str(Path(__file__).parents[1])); from execution.paired_behavior.job import _event, _storedproper, _storedroutes
from schrodinger.route_policy_data import load_validation
from schrodinger.route_policy_metrics import heldout_bank


def _state(p, q=(1,0,0,0), **extra):
    return {"canonical":"00"*144,"map_id":1,"family":"IIIIIIII","goal":2,"current":1,"p":p,"q":q,**extra}


def test_state_pairing_is_ordered_and_uses_nesw_ties():
    sm=[_state([.5,.5,0,0]), _state([0,1,0,0], current=3)]
    sa=[_state([0,.5,.5,0]), _state([0,1,0,0], current=3)]
    rows=paired_states(sm,sa)
    assert rows[0]["sm_argmax"] == 0 and rows[0]["sa_argmax"] == 1
    assert rows[0]["optimality"] == "sm_only_optimal" and rows[0]["argmax_disagreement"]
    with pytest.raises(AlignmentError): paired_states(sm, list(reversed(sa)))


def test_greedy_four_way_pairing_rejects_blind_zip():
    base={"canonical":"00"*144,"map_id":1,"family":"IIIIIIII","start":0,"goal":1}
    sm=[{**base,"valid":True},{**base,"goal":2,"valid":False}]
    sa=[{**base,"valid":False},{**base,"goal":2,"valid":False}]
    assert [x["outcome"] for x in paired_greedy(sm,sa)] == ["sm_only","neither"]
    with pytest.raises(AlignmentError): paired_greedy(sm, list(reversed(sa)))


def test_valid_route_sets_exclude_invalid_and_mark_both_empty_na():
    sig=lambda x:x
    empty=valid_route_sets([{"route":b"x","valid":False}], [], frozenset(), sig)
    assert empty["jaccard"] is None and empty["jaccard_denominator"] == 0
    result=valid_route_sets([{"route":b"a","valid":True},{"route":b"bad","valid":False}], [{"route":b"b","valid":True}], frozenset({b"a"}), sig)
    assert result["sm_only_valid_routes"] == result["sa_only_valid_routes"] == 1
    assert result["sm_novel_signatures"] == 0 and result["sa_novel_signatures"] == 1


def test_equal_map_summary_retains_rows_and_uses_fixed_mixture():
    rows=[{"family":"IIIIIIII","map_id":1,"q":.2},{"family":"IIIIIIII","map_id":1,"q":.6},
          {"family":"IIIIIIII","map_id":2,"q":1.0},{"family":"IIIILLLL","map_id":3,"q":.5}]
    result=equal_map_summary(rows, ["q"])
    assert result["strata"]["routine"]["q"] == .7  # average of map means .4 and 1.0
    assert result["mixture"]["q"] == pytest.approx(.8*.7+.2*.5)
    assert next(x for x in result["maps"] if x["map_id"] == 1)["rows"] == rows[:2]


def test_serialized_event_adapters_bind_real_retained_direct_hex_and_dataset_order():
    root=Path(__file__).parents[1]/"execution/model_training_comparison"; event=_event(root,"pilot-1701-softmax-1000",1000)
    problems=load_validation().problems; bank=heldout_bank(problems)
    rows,_=_storedproper(event,bank); attempts,_=_storedroutes(event,"greedy",problems)
    assert rows[0]["canonical"] == bank.selected[0].canonical and isinstance(event["proper"]["rows"][0]["canonical"],str)
    assert attempts[0]["canonical"] == problems[0].canonical and isinstance(event["routes"]["greedy"]["problems"][0]["attempts"][0]["route"],str)

def test_real_same_map_permutation_breaks_immutable_event_binding():
    from copy import deepcopy
    from schrodinger.route_policy_experiment import IdentityError
    root=Path(__file__).parents[1]/"execution/model_training_comparison"
    event=_event(root,"pilot-1701-softmax-1000",1000)
    changed=deepcopy(event); groups=changed["routes"]["greedy"]["problems"]
    assert groups[0]["map_id"]==groups[1]["map_id"]
    groups[0],groups[1]=groups[1],groups[0]
    with pytest.raises(IdentityError,match="mutation/order"):
        _storedroutes(changed,"greedy",load_validation().problems)

def test_raw_normalized_routes_and_ambiguity_aware_scores():
    from execution.paired_behavior.analysis import state_summary
    attempts=[{"route":b"a","valid":True},{"route":b"a","valid":True},{"route":b"b","valid":True},{"route":b"x","valid":False}]
    result=valid_route_sets(attempts,attempts,frozenset({b"a"}),lambda x:x)
    assert result["sm_Q"]==.75 and result["sm_pass_at_k"]==1
    assert result["sm_U_valid"]==.5 and result["sm_U_novel"]==result["sm_V_novel"]==.25
    assert result["raw_sets"]["sm"]==[b"a",b"b"] and result["raw_sets"]["sm_novel"]==[b"b"]
    row={"canonical":"00"*144,"map_id":1,"family":"IIIIIIII","goal":1,"current":0,"q":[.5,.5,0,0],"p":[.25,.5,.25,0]}
    paired=paired_states([row],[row]); summary=state_summary(paired)
    assert paired[0]["sm_brier"]==pytest.approx(.125)
    assert paired[0]["sm_nonoptimal_mass"]==pytest.approx(.25)
    assert paired[0]["sm_kl"]==pytest.approx(.5*np.log(2))
    assert summary["equal_map"]["strata"]["routine"]["sa_kl"]==paired[0]["sm_kl"]

def test_literal_frozen_abc_comparison_binds_saved_rows_without_inference():
    import json
    from execution.paired_behavior.analysis import load_matched_support
    from execution.paired_behavior.job import _frozen_abc,_load_sm_abc,_abc_compare
    root=Path(__file__).parents[1]/"execution/model_training_comparison"
    frozen=load_matched_support(root/"threeway-diagnosis-001/matched_support.json")
    result,digest=_load_sm_abc(root,frozen);banks,problems=_frozen_abc(frozen)
    assert [len(b.selected) for b in banks]==[768]*3 and [len(p) for p in problems]==[144]*3
    for i,name in enumerate("ABC"):
        sm=result["scores"]["8000"][name]
        # Identity comparator fixture only: exact saved SM probabilities, no SA claim.
        same={"proper":{"rows":banks[i].selected,"arrays":sm["proper"]["arrays"]},"greedy":sm["greedy"],"t1_k32":sm["t1_k32"]}
        paired=_abc_compare(sm,same,banks[i])
        assert paired["summary"]["greedy"]["sa_minus_sm"]==0
        assert paired["summary"]["t1_k32"]["sa_minus_sm"]==0
        assert paired["summary"]["kl"]["sa_minus_sm"]==pytest.approx(0,abs=1e-12)
        assert paired["paired_state"]["equal_map"]["strata"]["routine"]["tv"]==0
