import importlib.util
from pathlib import Path
import sys
import pytest

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
