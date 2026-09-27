from __future__ import annotations

from math import comb
from fractions import Fraction
import json
from pathlib import Path

import numpy as np
import pytest

from schrodinger import productive_diversity_v3_data as data
from schrodinger.route_feasibility import q_target, transform, triominoes


def _recovery_b_records() -> list[dict[str, object]]:
    root=Path(__file__).resolve().parents[1]/"execution/next_level_v3/fixtures"; out=[]; mid=0
    for filename,family in (("recovery_b_i8.json","IIIIIIII"),("recovery_b_l8.json","LLLLLLLL"),("recovery_b_mixed.json","IIIILLLL")):
        payload=json.loads((root/filename).read_text())
        variants=(("base",payload["base_walls"]),("validation",payload["validation_walls"]),("test",payload["test_walls"])) if family!="IIIILLLL" else (("base",payload["base_walls"]),("variant",payload["variant_walls"]))
        for _,raw in variants:
            walls=frozenset(raw); pairs=[]
            for item in payload["pairs"]:
                s,g=item[:2]; dist,count=data.bfs_counts(walls,g,12); pairs.append((s,g,dist[s],count[s]))
            out.append({"n":12,"map_id":mid,"family":family,"canonical":data.canonical_map(walls,12),"walls":walls,"shortlists":{p[2]:{"retained":(p,)} for p in pairs}});mid+=1
    return out


def test_recovery_b_unmocked_eight_record_composition() -> None:
    records=_recovery_b_records(); data.validate_inventory_records(records)
    assert len(records)==8 and len({r["canonical"] for r in records})==8
    expected={"IIIIIIII":{12:21,13:28,14:28},"LLLLLLLL":{12:28,13:75,14:122},"IIIILLLL":{12:148,13:84,14:140}}
    assert all(pair[3]==expected[row["family"]][pair[2]] for row in records for payload in row["shortlists"].values() for pair in payload["retained"])
    ranking={"retained":({"window_start":12,"window":(12,13,14),"quota":(1,1,1)},)}
    out=data.run_ranked_proposals(ranking,records,config=data.SelectionConfig((12,13,14),(1,1,1),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    assert out["outcome"]=="FIRST_FULL_DATASET_PASS"
    stages=out["stages"]; train=stages["training"]["selected"]
    groups=[train]+[[row for family in stages[name] for row in family["result"]["selected"]] for name in ("validation_routine","validation_mixed","test_routine","test_mixed")]
    assert all(len({row["map_id"] for row in group})==len(group)//3 for group in groups)
    identities=[{row["canonical"] for row in group} for group in groups]
    assert all(a.isdisjoint(b) for i,a in enumerate(identities) for b in identities[i+1:])
    assert all({row["length"] for row in group}=={12,13,14} for group in groups)
    mixed=groups[2]+groups[4]; assert [row["Mnovel"] for row in sorted(mixed,key=lambda r:r["length"])]==[89,89,35,35,60,60]
    assert all(row["Mnovel"]==0 for group in (groups[1],groups[3]) for row in group)
    rebuilt={data.signature(route[i:]) for row in train for route in data.enumerate_routes(row["start"],row["goal"],next(r["walls"] for r in records if r["canonical"]==row["canonical"]),12) for i in range(len(route))}
    assert tuple(sorted(rebuilt))==stages["training"]["support"]
    walls_by_key={r["canonical"]:r["walls"] for r in records}
    assert any(data.bfs_counts(walls_by_key[key],goal,12)[0][node]==1 for key,node,goal in stages["training"]["states"])
    for (key,node,goal),q in stages["training"]["states"].items():
        assert q==q_target(node,walls_by_key[key],goal,12) and abs(sum(q.values())-1)<1e-12
    for family in data.FAMILIES:
        family_records=[r for r in records if r["family"]==family]; base=family_records[0]
        pairs=[p for payload in base["shortlists"].values() for p in payload["retained"]]
        for variant in family_records[1:]:
            for start,goal,_,_ in pairs:
                assert set(data.enumerate_routes(start,goal,base["walls"],12))==set(data.enumerate_routes(start,goal,variant["walls"],12))


@pytest.mark.parametrize("index",[2,3])
def test_real_on_use_bfs_distance_or_count_mismatch_is_technical(index) -> None:
    records=_recovery_b_records()
    for row in [r for r in records if r["family"]=="IIIIIIII"]:
        pair=list(row["shortlists"][12]["retained"][0]); pair[index]+=1
        row["shortlists"][12]={"retained":(tuple(pair),)}
    with pytest.raises(data.SelectionTechnicalError): data.build_training_support(records,window_start=12,config=data.SelectionConfig((12,13,14),(1,1,1),1))


def test_real_on_use_bfs_distance_mismatch_after_valid_metadata() -> None:
    base=next(r for r in _recovery_b_records() if r["family"]=="IIIIIIII")
    record={**base,"shortlists":{12:{"retained":((3,23,12,28),)}}}
    data.validate_inventory_records((record,))
    assert data.bfs_counts(record["walls"],23,12)[0][3]==13
    with pytest.raises(data.SelectionTechnicalError,match="held-out inventory/oracle mismatch"):
        data.lazy_select_heldout((record,),family="IIIIIIII",split="test",window_start=12,config=data.SelectionConfig((12,),(1,),1),support=(),mode="routine",required_maps=1,excluded_identities=set())


def test_excluded_map_never_calls_oracle_or_commits(monkeypatch) -> None:
    record={"map_id":1,"family":"IIIIIIII","canonical":b"x","walls":frozenset(),"shortlists":{12:{"retained":((1,2,12,16),)}}}
    cache=data.ProposalOracleCache(); monkeypatch.setattr(cache,"routes",lambda *a:(_ for _ in ()).throw(AssertionError("oracle")))
    out=data.lazy_select_heldout((record,),family="IIIIIIII",split="test",window_start=12,config=data.SelectionConfig((12,),(1,),1),support=(),mode="routine",required_maps=1,excluded_identities={b"x"},cache=cache)
    assert out["outcome"]=="SCIENTIFIC_HELDOUT_SUPPLY_FAILED" and out["evidence"]==[{"map_id":1,"status":"EXCLUDED"}]


def test_direct_placements_match_small_exhaustive_and_n12_counts() -> None:
    for n in (3, 4, 5):
        expected = {kind: {tuple(sorted(part)) for part, old_kind in triominoes(n).items() if old_kind == kind} for kind in ("I", "L")}
        actual = {kind: set(data.direct_shape_placements(n)[kind]) for kind in ("I", "L")}
        assert actual == expected
    placements = data.direct_shape_placements(12)
    assert len(placements["I"]) == 240
    assert len(placements["L"]) == 484
    assert any(cell > 63 for part in placements["L"] for cell in part)
    assert data.direct_shape_placements(12) is placements


def _i8_components() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(r * 12 + c + delta for delta in range(3)) for r in (0, 2, 4, 6) for c in (0, 5))


def _l8_components() -> tuple[tuple[int, ...], ...]:
    return tuple((r * 12 + c, r * 12 + c + 1, (r + 1) * 12 + c) for r in (0, 3, 6, 9) for c in (0, 5))


def _mixed_components() -> tuple[tuple[int, ...], ...]:
    return _i8_components()[:4] + _l8_components()[4:]


def _canonical(parts: tuple[tuple[int, ...], ...]) -> bytes:
    return data.canonical_map(frozenset(cell for part in parts for cell in part), 12)


def test_pool_branch_order_and_independent_pcg64_draw_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    base = _i8_components()
    rotated = tuple(tuple(sorted(transform(cell, 1, 12) for cell in part)) for part in base)
    # Row 0 overlaps; row 1 has no overlaps but has orthogonal touching; row 2
    # is retained; row 3 is its distinct D4 representation and is a duplicate.
    touching = list(base)
    touching[1] = (12, 13, 14)
    placements = {"I": base + rotated, "L": ()}
    monkeypatch.setattr(data, "direct_shape_placements", lambda n: placements)
    # The branch fixture's placements are deliberately indexed rather than a
    # complete table; geometry validation itself is exercised by the assembler.
    monkeypatch.setattr(data, "validate_family_components", lambda walls, family, n: None)
    expected_rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([93000, 0])))
    expected = tuple(int(expected_rng.integers(len(placements["I"]))) for _ in range(8))
    stream = data.pool_family("IIIIIIII", n=12, limit=9, max_trials=1)
    assert stream.draw_prefix == (expected,)
    result = data.pool_family(
        "IIIIIIII", n=12, limit=2, max_trials=4,
        injected_draw_rows=((0, 0, 2, 3, 4, 5, 6, 7), tuple(range(8)), tuple(range(8)), tuple(range(8, 16))),
    )
    # Make the second draw non-overlapping but touching without changing the
    # separate accepted/rotated-D4 rows.
    assert result.trials == 4
    assert result.rejected_overlap == 1 and result.rejected_touching == 0 and result.rejected_duplicate == 2
    assert len(result.maps) == 1 and result.maps[0] == _canonical(base)
    # Explicitly drive the touching branch with a dedicated direct table.
    monkeypatch.setattr(data, "direct_shape_placements", lambda n: {"I": tuple(touching), "L": ()})
    touching_result = data.pool_family("IIIIIIII", n=12, limit=2, max_trials=1, injected_draw_rows=(tuple(range(8)),))
    assert touching_result.rejected_overlap == 0 and touching_result.rejected_touching == 1 and touching_result.rejected_duplicate == 0


def test_pool_draw_audit_prefix_is_capped_without_changing_trials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(data, "direct_shape_placements", lambda n: {"I": ((0, 1, 2),), "L": ()})
    rows = tuple((0,) * 8 for _ in range(17))
    result = data.pool_family("IIIIIIII", n=12, limit=1, max_trials=17, injected_draw_rows=rows)
    assert result.trials == 17 and result.rejected_overlap == 17
    assert result.draw_prefix == rows[:16]
    assert sum(len(row) for row in result.draw_prefix) == 128


def test_explicit_n12_bfs_candidate_bounds_order_and_q_oracle() -> None:
    walls = frozenset()
    target = 143
    q = q_target(130, walls, target, 12)
    assert sum(q.values()) == pytest.approx(1.0)
    assert q[1] > 0 and q[2] > 0
    candidates = data.inventory_candidates(walls, n=12)
    retained = (98, 143, 12, comb(12, 3))
    assert retained in candidates and retained[0] > 63
    assert candidates == tuple(sorted(set(candidates)))
    assert all(12 <= d <= 20 and 16 <= m <= 256 for _, _, d, m in candidates)


def test_shortlists_have_one_seeded_permutation_per_map_length() -> None:
    candidates = tuple((i, 143 - i, 12, 16 + i) for i in range(70)) + ((1, 2, 13, 20),)
    first = data.shortlist_by_length(candidates, map_id=17)
    assert len(first[12]["permutation"]) == 70
    assert len(first[12]["retained"]) == 64
    assert first[13]["retained"] == ((1, 2, 13, 20),)
    assert tuple(sorted(first[12]["retained"])) != first[12]["retained"]
    complete = tuple(item for item in candidates if item[2] == 12)
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([93001, 17, 12])))
    expected_order = tuple(int(value) for value in rng.permutation(len(complete)))
    assert first[12]["permutation"] == expected_order
    assert first[12]["retained"] == tuple(complete[index] for index in expected_order[:64])


def test_global_assembler_sorts_ids_rejects_cross_family_and_passes_n(monkeypatch: pytest.MonkeyPatch) -> None:
    maps = {
        "IIIIIIII": data.PoolResult("IIIIIIII", (_canonical(_i8_components()),), 0, 0, 0, 0),
        "LLLLLLLL": data.PoolResult("LLLLLLLL", (_canonical(_l8_components()),), 0, 0, 0, 0),
        "IIIILLLL": data.PoolResult("IIIILLLL", (_canonical(_mixed_components()),), 0, 0, 0, 0),
    }
    oracle_n: list[int] = []
    def candidates(walls: frozenset[int], *, n: int) -> tuple[tuple[int, int, int, int], ...]:
        oracle_n.append(n)
        return ((70, 143, 12, 16),)
    records = data.assemble_global_inventory(maps, candidate_oracle=candidates)
    assert oracle_n == [12, 12, 12]
    assert [record["map_id"] for record in records] == [0, 1, 2]
    assert [record["canonical"] for record in records] == sorted(pool.maps[0] for pool in maps.values())
    collided = dict(maps)
    collided["LLLLLLLL"] = data.PoolResult("LLLLLLLL", (maps["IIIIIIII"].maps[0],), 0, 0, 0, 0)
    with pytest.raises(data.GeometryError, match="canonical identity collision"):
        data.assemble_global_inventory(collided, candidate_oracle=candidates)


def _record(map_id: int, family: str, count: int = 6, m: int = 16) -> dict[str, object]:
    return {
        "map_id": map_id,
        "family": family,
        "shortlists": {
            length: {"retained": tuple((map_id, length, length, m) for _ in range(count))}
            for length in data.LENGTHS
        },
    }


def test_ranking_raw_capacity_failure_exact_ratio_and_no_route_enumeration(monkeypatch: pytest.MonkeyPatch) -> None:
    records = [_record(i, "IIIIIIII") for i in range(91)]
    records += [_record(100 + i, "LLLLLLLL") for i in range(92)]
    records += [_record(200 + i, "IIIILLLL") for i in range(40)]
    monkeypatch.setattr(data, "enumerate_routes", lambda *args: (_ for _ in ()).throw(AssertionError("ranking must not enumerate routes")), raising=False)
    ranked = data.rank_proposals(records)
    assert ranked["status"] == "RAW_JOINT_CAPACITY_FAILED"
    proposal = ranked["proposals"][0]
    assert proposal["score"] == {"numerator": 91, "denominator": 92}
    assert proposal["feasible"] is False
    assert proposal["infeasibility_reasons"] == ["IIIIIIII:91<92"]


def _window_records(offset: int, window: tuple[int, int, int], counts: dict[str, int], m: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    next_id = offset
    for family in data.FAMILIES:
        for _ in range(counts[family]):
            row = _record(next_id, family, count=0, m=m)
            for length in window:
                row["shortlists"][length] = {"retained": tuple((next_id, length, length, m) for _ in range(6))}
            rows.append(row)
            next_id += 1
    return rows


def test_ranking_precedence_score_cost_window_quota_and_top_three() -> None:
    full = {"IIIIIIII": 92, "LLLLLLLL": 92, "IIIILLLL": 40}
    double = {family: count * 2 for family, count in full.items()}
    records = _window_records(0, (12, 13, 14), double, 50)
    records += _window_records(1_000, (14, 15, 16), full, 20)
    records += _window_records(2_000, (16, 17, 18), full, 10)
    records += _window_records(3_000, (18, 19, 20), full, 10)
    ranked = data.rank_proposals(records)
    assert ranked["status"] == "OK"
    assert len(ranked["proposals"]) == 12
    assert len(ranked["window_winners"]) == 4
    assert [item["quota"] for item in ranked["window_winners"]] == [data.QUOTAS[0]] * 4
    # Score two at cost 50 outranks the cheaper score-one proposal; equal full
    # scores next use exact mean-M, then lower window start.
    assert [item["window_start"] for item in ranked["retained"]] == [12, 16, 18]
    by_start = {proposal["window_start"]: proposal for proposal in ranked["window_winners"]}
    assert by_start[14]["score"] == {"numerator": 1, "denominator": 1}
    assert by_start[12]["mean_m"] == {"numerator": 50, "denominator": 1}


def test_heldout_support_key_cache_and_challenge_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    key = bytes(144); record = {"map_id": 77, "family": "IIIILLLL", "canonical": key, "walls": frozenset(),
        "shortlists": {12: {"retained": ((1, 2, 12, 16),)}}}
    config = data.SelectionConfig((12,), (1,), train_maps_per_family=1)
    cache = data.ProposalOracleCache(); routes = tuple(bytes([i]) for i in range(16))
    monkeypatch.setattr(cache, "routes", lambda *args: routes)
    monkeypatch.setattr(cache, "bfs_counts", lambda *args: ({1: 12, 2: 0}, {1: 16}))
    monkeypatch.setattr(cache, "canonical_signature", lambda route: route)
    # Exactly 1/4 novel (four routes not in support) is eligible.
    support = routes[4:]
    one = data.lazy_select_heldout((record,), family="IIIILLLL", split="test", window_start=12, config=config,
                                   support=support, mode="challenge", required_maps=1, excluded_identities=set(), cache=cache)
    assert one["outcome"] == "OK" and one["selected"][0]["Mnovel"] == 4
    two = data.lazy_select_heldout((record,), family="IIIILLLL", split="test", window_start=12, config=config,
                                   support=support, mode="challenge", required_maps=1, excluded_identities=set(), cache=cache)
    assert two["outcome"] == "OK" and cache.profile()["stats"]["eligibility_hits"] >= 1
    changed = data.lazy_select_heldout((record,), family="IIIILLLL", split="test", window_start=12, config=config,
                                       support=routes[12:], mode="challenge", required_maps=1, excluded_identities=set(), cache=cache)
    assert changed["outcome"] == "OK" and changed["selected"][0]["Mnovel"] == 12
    assert cache.profile()["stats"]["eligibility_misses"] == 2 and cache.profile()["eligibility_entries"] == 2
    for support in (routes[3:], routes[:3]):
        # 3/16 is below four; 13/16 is outside 3/4.
        probe = data.lazy_select_heldout((record,), family="IIIILLLL", split="test", window_start=12, config=config,
            support=support, mode="challenge", required_maps=1, excluded_identities=set(), cache=cache)
        assert probe["outcome"] == "SCIENTIFIC_HELDOUT_SUPPLY_FAILED"
    record20=dict(record); record20["shortlists"]={12:{"retained":((1,2,12,20),)}}
    cache20=data.ProposalOracleCache(); routes20=tuple(bytes([i]) for i in range(20))
    monkeypatch.setattr(cache20,"routes",lambda *args: routes20); monkeypatch.setattr(cache20,"bfs_counts",lambda *args: ({1:12,2:0},{1:20})); monkeypatch.setattr(cache20,"canonical_signature",lambda r:r)
    assert data.lazy_select_heldout((record20,),family="IIIILLLL",split="test",window_start=12,config=config,support=routes20[4:],mode="challenge",required_maps=1,excluded_identities=set(),cache=cache20)["outcome"]=="SCIENTIFIC_HELDOUT_SUPPLY_FAILED"


def test_rejected_map_preserves_prior_accepted_rows_and_noncommit(monkeypatch) -> None:
    record={"map_id":9,"family":"IIIIIIII","canonical":bytes(144),"walls":frozenset(),"shortlists":{12:{"retained":((1,2,12,16),)},13:{"retained":((3,4,13,16),)},14:{"retained":((5,6,14,16),)}}}
    cache=data.ProposalOracleCache(); monkeypatch.setattr(cache,"bfs_counts",lambda walls,goal,n: ({1:12,2:0,3:13,4:0},{1:16,3:16}))
    def routes(walls,start,goal,n):
        if start==1: return tuple(bytes([i]) for i in range(16))
        if start==3: return tuple(bytes([100+i]) for i in range(16))
        raise AssertionError("third length must not be visited")
    monkeypatch.setattr(cache,"routes",routes)
    monkeypatch.setattr(cache,"canonical_signature",lambda route: route)
    excluded=set(); result=data.lazy_select_heldout((record,),family="IIIIIIII",split="test",window_start=12,config=data.SelectionConfig((12,13,14),(1,1,1),1),support=tuple(bytes([i]) for i in range(4)),mode="challenge",required_maps=1,excluded_identities=excluded,cache=cache)
    assert result["outcome"]=="SCIENTIFIC_HELDOUT_SUPPLY_FAILED" and not excluded
    first=next(item for item in result["evidence"] if item.get("length")==12)
    assert first["accepted_rows"][0]["start"]==1
    assert not any(item.get("length")==14 for item in result["evidence"])


def test_orchestrator_stage_order_and_scientific_advance_isolated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolated orchestration unit test; it is deliberately not composition evidence."""
    calls=[]; callbacks=[]; validation_calls=[]
    original_validate=data.validate_inventory_records
    def spy_validate(records): validation_calls.append(1); return original_validate(records)
    monkeypatch.setattr(data,"validate_inventory_records",spy_validate)
    def training(records, *, window_start, config, cache, **kwargs):
        return {"outcome":"SCIENTIFIC_TRAINING_SUPPLY_FAILED"} if window_start == 12 else {"outcome":"OK","selected":[{"canonical":b"train"}],"support":()}
    def held(records, *, family, split, window_start, config, support, mode, required_maps, excluded_identities, cache):
        calls.append((split,family,mode,frozenset(excluded_identities)))
        key=(split+family).encode(); return {"outcome":"OK","selected":[{"canonical":key}],"evidence":[]}
    monkeypatch.setattr(data,"build_training_support",training); monkeypatch.setattr(data,"lazy_select_heldout",held)
    ranked={"retained":({"window_start":12,"window":(12,),"quota":(1,)},{"window_start":14,"window":(12,),"quota":(1,)})}
    out=data.run_ranked_proposals(ranked,(),config=data.SelectionConfig((12,), (1,),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1},on_stage=lambda name,value: callbacks.append(name))
    assert out["outcome"]=="FIRST_FULL_DATASET_PASS"
    assert [(x[0],x[1]) for x in calls]==[("validation","IIIIIIII"),("validation","LLLLLLLL"),("validation","IIIILLLL"),("test","IIIIIIII"),("test","LLLLLLLL"),("test","IIIILLLL")]
    assert callbacks==["training","validation_routine","validation_mixed","test_routine","test_mixed","training","validation_routine","validation_mixed","test_routine","test_mixed"]
    assert len(validation_calls)==1
    expected={b"train"}
    for split,family,mode,excluded in calls:
        assert excluded==frozenset(expected)
        expected.add((split+family).encode())


@pytest.mark.parametrize("training_outcome,heldout_outcome,raises", [("SCIENTIFIC_TRAINING_SUPPLY_FAILED",None,False),("OK","SCIENTIFIC_HELDOUT_SUPPLY_FAILED",False),("OK","TECHNICAL_BAD",True)])
def test_orchestrator_short_circuits_training_and_first_family(monkeypatch, training_outcome, heldout_outcome, raises) -> None:
    calls=[]
    monkeypatch.setattr(data,"build_training_support",lambda *a,**k:{"outcome":training_outcome,"selected":[],"support":()})
    def held(*a,**k): calls.append(k["family"]); return {"outcome":heldout_outcome,"selected":[],"evidence":[]}
    monkeypatch.setattr(data,"lazy_select_heldout",held)
    ranked={"retained":({"window_start":12,"window":(12,),"quota":(1,)},)}
    if raises:
        with pytest.raises(data.SelectionTechnicalError): data.run_ranked_proposals(ranked,(),config=data.SelectionConfig((12,),(1,),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    else:
        out=data.run_ranked_proposals(ranked,(),config=data.SelectionConfig((12,),(1,),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
        assert out["outcome"]=="DATASET_CONSTRUCTION_FAILED"
        if training_outcome=="OK" and heldout_outcome=="SCIENTIFIC_HELDOUT_SUPPLY_FAILED":
            stages=out["evidence"][0]["stages"]
            assert stages["validation_routine"]==[{"family":"IIIIIIII","result":{"outcome":"SCIENTIFIC_HELDOUT_SUPPLY_FAILED","selected":[],"evidence":[]}}, {"family":"LLLLLLLL","result":{"outcome":"NOT_EVALUATED"}}]
            assert all(stages[name]=={"outcome":"NOT_EVALUATED"} for name in ("validation_mixed","test_routine","test_mixed"))
            assert calls==["IIIIIIII"]
    assert calls in ([],["IIIIIIII"])


def test_unknown_training_outcome_aborts_before_heldout(monkeypatch) -> None:
    monkeypatch.setattr(data,"build_training_support",lambda *a,**k:{"outcome":"TECHNICAL_BAD","selected":[],"support":()})
    calls=[]; monkeypatch.setattr(data,"lazy_select_heldout",lambda *a,**k:calls.append(1))
    with pytest.raises(data.SelectionTechnicalError): data.run_ranked_proposals({"retained":({"window_start":12,"window":(12,),"quota":(1,)},)},(),config=data.SelectionConfig((12,),(1,),1))
    assert not calls


def test_three_proposals_scientific_then_pass_stops_and_preserves_evidence(monkeypatch) -> None:
    seen=[]
    def training(records,*,window_start,**kwargs):
        seen.append(window_start)
        if window_start==12:return {"outcome":"SCIENTIFIC_TRAINING_SUPPLY_FAILED","selected":[],"support":()}
        if window_start==14:return {"outcome":"OK","selected":[{"canonical":b"t"}],"support":()}
        raise AssertionError("third proposal must not run")
    monkeypatch.setattr(data,"build_training_support",training)
    monkeypatch.setattr(data,"lazy_select_heldout",lambda *a,**k:{"outcome":"OK","selected":[],"evidence":[]})
    rank={"retained":tuple({"window_start":w,"window":(12,),"quota":(1,)} for w in (12,14,16))}
    out=data.run_ranked_proposals(rank,(),config=data.SelectionConfig((12,),(1,),1),counts={"val_routine":1,"val_mixed":1,"test_routine":1,"test_mixed":1})
    assert out["outcome"]=="FIRST_FULL_DATASET_PASS" and out["proposal"]["window_start"]==14 and seen==[12,14]
    assert out["evidence"][0]["training"]["outcome"]=="SCIENTIFIC_TRAINING_SUPPLY_FAILED"


def test_technical_first_training_never_advances(monkeypatch) -> None:
    seen=[]; monkeypatch.setattr(data,"build_training_support",lambda records,*,window_start,**kwargs:(seen.append(window_start) or {"outcome":"TECHNICAL_BAD","selected":[],"support":()}))
    monkeypatch.setattr(data,"lazy_select_heldout",lambda *a,**k:(_ for _ in ()).throw(AssertionError("heldout")))
    rank={"retained":tuple({"window_start":w,"window":(12,),"quota":(1,)} for w in (12,14))}
    with pytest.raises(data.SelectionTechnicalError): data.run_ranked_proposals(rank,(),config=data.SelectionConfig((12,),(1,),1))
    assert seen==[12]


@pytest.mark.parametrize("field,value",[("n",8),("family","bad"),("map_id",1),("canonical",bytes(144)),("shortlists",{13:{"retained":((98,143,12,16),)}}),("shortlists",{12:{"retained":((-1,143,12,16),)}}),("shortlists",{12:{"retained":((144,143,12,16),)}}),("shortlists",{12:{"retained":((0,143,12,16),)}}),("shortlists",{12:{"retained":((98,143,12,15),)}}),("shortlists",{12:{"retained":((98,143,12,257),)}})])
def test_validate_inventory_bad_n_endpoints_family_identity_M_length(field, value) -> None:
    walls=frozenset(x for part in _i8_components() for x in part)
    good={"n":12,"map_id":1,"family":"IIIIIIII","canonical":data.canonical_map(walls,12),"walls":walls,"shortlists":{12:{"retained":((98,143,12,16),)}}}
    bad=dict(good); bad[field]=value
    if field=="map_id":
        with pytest.raises(data.SelectionTechnicalError): data.validate_inventory_records((good,bad))
    else:
        with pytest.raises(data.SelectionTechnicalError): data.validate_inventory_records((bad,))


def _real_selection_record(parts: tuple[tuple[int, ...], ...], family: str, map_id: int) -> dict[str, object]:
    walls = frozenset(cell for part in parts for cell in part)
    candidates = data.inventory_candidates(walls, n=12)
    retained = {}
    for length in (12, 13, 14):
        retained[length] = {"retained": (next(row for row in candidates if row[2] == length),)}
    return {"n":12, "map_id": map_id, "family": family, "canonical": data.canonical_map(walls, 12), "walls": walls, "shortlists": retained}


def test_orientation_deficient_n12_training_truthfully_rejects() -> None:
    records = [_real_selection_record(_i8_components(), "IIIIIIII", 1),
               _real_selection_record(_l8_components(), "LLLLLLLL", 2),
               _real_selection_record(_mixed_components(), "IIIILLLL", 3)]
    # Frozen deterministic bounded-search results: each is genuinely partial
    # novel against the homogeneous support built below.
    records[2]["shortlists"] = {12: {"retained": ((3, 70, 12, 150),)},
                                13: {"retained": ((4, 83, 13, 166),)},
                                14: {"retained": ((17, 119, 14, 165),)}}
    config = data.SelectionConfig((12, 13, 14), (1, 1, 1), train_maps_per_family=1)
    built = data.build_training_support(records, window_start=12, config=config)
    assert built["outcome"] == "SCIENTIFIC_TRAINING_ORIENTATION_SHORTAGE"
