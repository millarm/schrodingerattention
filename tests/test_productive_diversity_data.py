import math

import pytest

import schrodinger.productive_diversity_data as data
from schrodinger.route_feasibility import enumerate_routes, q_target, signature


def _row(map_id, family, candidates, walls=frozenset()):
    return {"map_id": map_id, "canonical": bytes([map_id]) * 64, "family": family,
            "walls": walls, "candidates": candidates}


def _pairs(map_id, lengths=(6, 7), each=8):
    return [(map_id * 100 + length * 10 + index, map_id * 100 + length * 10 + index + 1, length, 16)
            for length in lengths for index in range(each)]


def test_explicit_n8_pool_component_rejections_d4_and_replay(monkeypatch):
    placements = data.component_placements(8)
    assert max(max(component) for values in placements.values() for component in values) > 35
    assert all(tuple(sorted(component)) for values in placements.values() for component in values)
    spec = data.rung("A")
    first, first_audit = data.pool_family(spec, "III", limit=2, trials=200)
    second, second_audit = data.pool_family(spec, "III", limit=2, trials=200)
    assert first == second and first_audit == second_audit and all(len(key) == 64 for key in first)
    monkeypatch.setattr(data, "component_placements", lambda n: {"I": [frozenset({0, 1, 2})], "L": [frozenset({10, 11, 18})]})
    empty, audit = data.pool_family(spec, "III", limit=1, trials=3)
    assert empty == [] and audit["rejections"]["overlap"] == 3 and audit["rejections"]["touch"] == 0
    class FixedDraw:
        def integers(self, _): return next(self.values)
        values = iter((0, 1, 0))
    monkeypatch.setattr(data, "component_placements", lambda n: {"I": [frozenset({0, 1, 2}), frozenset({20, 21, 22})], "L": [frozenset({3, 11, 12})]})
    monkeypatch.setattr(data, "_rng", lambda *_: FixedDraw())
    empty, audit = data.pool_family(spec, "IIL", limit=1, trials=1)
    assert empty == [] and audit["rejections"]["overlap"] == 0 and audit["rejections"]["touch"] == 1
    assert data.canonical_map({0, 1, 2}, 8) == data.canonical_map({7, 15, 23}, 8)


def test_candidates_q_and_support_use_explicit_n8_and_independent_routes():
    spec = data.rung("A"); walls = frozenset(); candidates = data.candidates_for(walls, spec, n=8)
    assert all(6 <= distance <= 14 and 16 <= multiplicity <= 256 for _, _, distance, multiplicity in candidates)
    start, goal = 0, 27
    routes = enumerate_routes(start, goal, walls, 8)
    assert len(routes) == math.comb(6, 3) == 20
    row = {"map_id": 80, "walls": walls, "start": start, "goal": goal, "length": 6, "M": 20}
    states, support, _ = data.training_states_and_support([row], n=8)
    brute = {signature(route[index:]) for route in routes for index in range(len(route))}
    assert set(support) == brute and states
    for state in states:
        target = q_target(state["state"], walls, goal, 8)
        assert sum(state["q"]) == pytest.approx(1.0, abs=1e-12)
        assert tuple(target[action] for action in range(4)) == pytest.approx(state["q"], abs=1e-12)


def test_canonical_component_orientation_classification_and_family_validation():
    assert data.classify_component(frozenset({0, 1, 2}), n=8) == ("I", "H")
    assert data.classify_component(frozenset({0, 8, 16}), n=8) == ("I", "V")
    corners = {"TL": frozenset({1, 8, 9}), "TR": frozenset({0, 8, 9}), "BL": frozenset({0, 1, 9}), "BR": frozenset({0, 1, 8})}
    assert {data.classify_component(component, n=8)[1] for component in corners.values()} == set(corners)
    horizontal, vertical = frozenset({0, 1, 2}), frozenset({16, 24, 32}); base = 5 * 8 + 5
    rows = [_row(map_id, "IIL", [], horizontal | vertical | frozenset(base + cell for cell in component)) for map_id, component in enumerate(corners.values())]
    assert data.require_training_orientation_coverage(rows, n=8) == {"I": {"H", "V"}, "L": {"TL", "TR", "BL", "BR"}}
    with pytest.raises(data.OracleIntegrityError, match="family/component mismatch"):
        data.family_component_orientations(horizontal | vertical, "IIL", n=8)


def test_hamilton_nonuniform_reverse_flow_and_continuous_family_problem_streams():
    assert data.length_quotas((6, 7, 8), 17, {6: .2, 7: .3, 8: .5}) == {6: 3, 7: 5, 8: 9}
    # m0 initially blocks m1's only length-6 edge; reverse residual flow repairs it.
    rows = [_row(0, "III", _pairs(0, (6, 7), 1)), _row(1, "III", _pairs(1, (6,), 1))]
    pairs = {row["map_id"]: row["candidates"] for row in rows}
    flow, _ = data.allocate_by_length(rows, pairs, {6: 1, 7: 1}, map_capacity=1)
    assert flow == {(0, (7, 0)): 1, (1, (6, 0)): 1}
    spec = data.rung("A"); rows = [_row(0, "III", _pairs(0)), _row(1, "III", _pairs(1))]
    pairs = {row["map_id"]: row["candidates"] for row in rows}
    flow = {(0, (6, 0)): 2, (0, (7, 0)): 1, (1, (6, 0)): 2, (1, (7, 0)): 1}
    selected, audit = data.select_pairs(rows, spec, "train", flow, pairs)
    generator = data.problem_rng(spec, "train", "III"); expected = []
    for row in rows:
        for length in (6, 7):
            available = [pair for pair in pairs[row["map_id"]] if pair[2] == length]
            expected.extend((row["map_id"], available[index][0], available[index][1]) for index in generator.permutation(len(available))[:flow[(row["map_id"], (length, 0))]])
    assert [(row["map_id"], row["start"], row["goal"]) for row in selected] == sorted(expected)
    assert audit["0:6"]["order"] != audit["1:6"]["order"]


def test_split_exclusions_support_and_exact_novelty_ratio_endpoints():
    spec = data.rung("A")
    rows = [_row(index, "III" if index < 4 else "LLL", _pairs(index)) for index in range(8)]
    excluded = set(); train, _ = data.select_maps(rows, spec, "train", {"III": 1, "LLL": 1}, excluded)
    validation, _ = data.select_maps(rows, spec, "validation", {"III": 1, "LLL": 1}, excluded)
    assert {row["canonical"] for values in train.values() for row in values}.isdisjoint({row["canonical"] for values in validation.values() for row in values})
    walls = frozenset({1}); start, goal = 24, 3; routes = enumerate_routes(start, goal, walls, 8)
    row = _row(99, "IIL", [(start, goal, 6, 16)], walls)
    grouped = {}
    for route in routes: grouped.setdefault(signature(route), []).append(route)
    all_signatures = set(grouped)
    assert data.eligible_novelty_pairs(row, all_signatures, "routine", n=8) == [(start, goal, 6, 16)]
    support = all_signatures - {next(item for item, group in grouped.items() if len(group) == 4)}
    challenge = data.eligible_novelty_pairs(row, support, "challenge", n=8)
    novelty = data.novelty_for([{**row, "start": start, "goal": goal, "length": 6, "M": 16}], support, n=8)[0]
    assert challenge == [(start, goal, 6, 16)] and novelty["M_novel"] == 4 and novelty["M_novel"] / novelty["M"] == .25
    assert novelty["route_count"] == novelty["signature_count"] == novelty["M"]
    upper_support = {next(item for item, group in grouped.items() if len(group) == 4)}
    upper = data.novelty_for([{**row, "start": start, "goal": goal, "length": 6, "M": 16}], upper_support, n=8)[0]
    assert upper["M_novel"] == 12 and upper["M_novel"] / upper["M"] == .75
    assert data.eligible_novelty_pairs(row, set(), "challenge", n=8) == []


def test_candidate_multiplicity_mismatch_is_technical_before_novelty_classification():
    row = _row(7, "IIL", [(24, 3, 6, 17)], frozenset({1}))
    with pytest.raises(data.OracleIntegrityError, match="candidate M mismatch"):
        data.eligible_novelty_pairs(row, set(), "challenge", n=8)
    with pytest.raises(data.OracleIntegrityError, match="candidate M mismatch"):
        data.novelty_for([{**row, "start": 24, "goal": 3, "length": 6, "M": 17}], set(), n=8)
    calls = []
    def technical(item):
        calls.append(item.name); return data.eligible_novelty_pairs(row, set(), "challenge", n=8)
    with pytest.raises(data.OracleIntegrityError, match="candidate M mismatch"):
        data.first_passing_rung(technical)
    assert calls == ["A"]


def test_training_engine_global_flow_exact_counts_and_ladder_policy():
    spec = data.rung("A")
    rows = []
    candidates = data.candidates_for(frozenset(), spec, n=8)
    for map_id, family in enumerate(("III", "III", "LLL", "LLL")):
        rows.append(_row(map_id, family, candidates))
    with pytest.raises(data.ConstructionFailure, match="LENGTH_FLOW_FAILED"):
        data.allocate_by_length(rows, {row["map_id"]: row["candidates"] for row in rows}, data.length_quotas(spec.lengths, 64))
    calls = []
    def construction(item):
        calls.append(item.name)
        if item.name == "A": raise data.ConstructionFailure("SUPPLY", {"rung": "A"})
        return "pass"
    assert data.first_passing_rung(construction) == ("B", "pass") and calls == ["A", "B"]
    calls.clear(); assert data.first_passing_rung(lambda item: calls.append(item.name) or "pass") == ("A", "pass") and calls == ["A"]
    calls.clear()
    def technical(item):
        calls.append(item.name); raise RuntimeError("technical")
    with pytest.raises(RuntimeError): data.first_passing_rung(technical)
    assert calls == ["A"]
    def both_fail(item):
        raise data.ConstructionFailure("A_SUPPLY" if item.name == "A" else "B_FLOW", {"rung": item.name})
    with pytest.raises(data.ConstructionFailure, match="DATASET_LADDER_FAILED") as failure:
        data.first_passing_rung(both_fail)
    assert failure.value.evidence == {"A": {"outcome": "A_SUPPLY", "evidence": {"rung": "A"}}, "B": {"outcome": "B_FLOW", "evidence": {"rung": "B"}}}
    assert isinstance(failure.value.__cause__, data.ConstructionFailure) and failure.value.__cause__.outcome == "A_SUPPLY"
