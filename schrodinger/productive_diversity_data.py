"""Pure, frozen v2 8x8 route-data construction; no runner or model code."""
from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

import numpy as np

from schrodinger.route_feasibility import (
    bfs_counts, canonical_map, deterministic_flow, enumerate_routes, hamilton,
    q_target, signature, triominoes,
)

N = 8
POOL_SEED = 80000
POOL_TRIALS = 100_000
POOL_LIMIT = 256


class ConstructionFailure(ValueError):
    """An ordinary frozen supply, allocation, support, or novelty gate failure."""

    def __init__(self, outcome: str, evidence: dict):
        super().__init__(outcome)
        self.outcome, self.evidence = outcome, evidence


class OracleIntegrityError(RuntimeError):
    """A malformed canonical map or oracle inconsistency; never a ladder rung failure."""


@dataclass(frozen=True)
class Rung:
    name: str
    index: int
    training_families: tuple[str, ...]
    challenge_families: tuple[str, ...]
    lengths: tuple[int, ...]
    split_seeds: dict[str, int]
    family_codes: dict[str, int]


RUNGS = (
    Rung("A", 0, ("III", "LLL"), ("IIL", "ILL"), tuple(range(6, 15)),
         {"train": 81001, "validation": 81002, "test": 81003},
         {"III": 0, "LLL": 1, "IIL": 2, "ILL": 3}),
    Rung("B", 1, ("IIII", "LLLL"), ("IILL",), tuple(range(8, 19)),
         {"train": 82001, "validation": 82002, "test": 82003},
         {"IIII": 0, "LLLL": 1, "IILL": 2}),
)


class OracleCache:
    """Small insertion-ordered cache of reusable BFS and signature facts, never routes."""
    def __init__(self, limit: int = 256):
        self.limit = limit
        self._bfs: dict[tuple, tuple[dict[int, int], dict[int, int]]] = {}
        self._signatures: dict[tuple, tuple[bytes, ...]] = {}

    def _put(self, values: dict, key, value):
        if key not in values and len(values) >= self.limit:
            values.pop(next(iter(values)))
        values[key] = value
        return value

    def bfs(self, walls: frozenset[int], goal: int, n: int) -> tuple[dict[int, int], dict[int, int]]:
        key = (walls, goal, n)
        return self._bfs.get(key) or self._put(self._bfs, key, bfs_counts(walls, goal, n))

    def signatures(self, walls: frozenset[int], start: int, goal: int, n: int) -> tuple[bytes, ...]:
        key = (walls, start, goal, n)
        return self._signatures.get(key) or self._put(self._signatures, key, tuple(signature(route) for route in enumerate_routes(start, goal, walls, n)))


def rung(name: str) -> Rung:
    return next(item for item in RUNGS if item.name == name)


def _rng(*parts: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence(parts)))


def _touches(left: frozenset[int], right: frozenset[int], n: int = N) -> bool:
    for cell in left:
        row, col = divmod(cell, n)
        for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
            nr, nc = row + dr, col + dc
            if 0 <= nr < n and 0 <= nc < n and nr * n + nc in right:
                return True
    return False


def wall_components(walls: frozenset[int], *, n: int = N) -> list[frozenset[int]]:
    """Orthogonally connected wall components in deterministic canonical-frame order."""
    remaining = set(walls); components = []
    while remaining:
        todo = [min(remaining)]; component = set()
        while todo:
            current = todo.pop()
            if current in component:
                continue
            component.add(current); remaining.remove(current)
            row, col = divmod(current, n)
            for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nr, nc = row + dr, col + dc
                neighbor = nr * n + nc
                if 0 <= nr < n and 0 <= nc < n and neighbor in remaining:
                    todo.append(neighbor)
        components.append(frozenset(component))
    return sorted(components, key=lambda component: tuple(sorted(component)))


def classify_component(component: frozenset[int], *, n: int = N) -> tuple[str, str]:
    """Classify one canonical-frame triomino as I-H/I-V or L-missing-{corner}."""
    if len(component) != 3:
        raise OracleIntegrityError(f"malformed component cardinality {len(component)}")
    rows = sorted({cell // n for cell in component}); cols = sorted({cell % n for cell in component})
    if len(rows) == 1 and len(cols) == 3:
        return "I", "H"
    if len(rows) == 3 and len(cols) == 1:
        return "I", "V"
    if len(rows) == len(cols) == 2:
        top, bottom = rows; left, right = cols
        square = {top * n + left, top * n + right, bottom * n + left, bottom * n + right}
        missing = square - set(component)
        if len(missing) == 1:
            labels = {top * n + left: "TL", top * n + right: "TR", bottom * n + left: "BL", bottom * n + right: "BR"}
            return "L", labels[next(iter(missing))]
    raise OracleIntegrityError(f"malformed non-triomino component {tuple(sorted(component))}")


def family_component_orientations(walls: frozenset[int], family: str, *, n: int = N) -> list[tuple[str, str]]:
    """Validate canonical component count/kinds against a family and expose orientations."""
    result = [classify_component(component, n=n) for component in wall_components(walls, n=n)]
    if len(result) != len(family) or sorted(kind for kind, _ in result) != sorted(family):
        raise OracleIntegrityError(f"family/component mismatch family={family} components={result}")
    return result


def orientation_coverage(rows: Iterable[dict], *, n: int = N) -> dict[str, set[str]]:
    coverage = {"I": set(), "L": set()}
    for row in rows:
        for kind, orientation in family_component_orientations(row["walls"], row["family"], n=n):
            coverage[kind].add(orientation)
    return coverage


def require_training_orientation_coverage(rows: Iterable[dict], *, n: int = N) -> dict[str, set[str]]:
    coverage = orientation_coverage(rows, n=n)
    missing = {"I": sorted({"H", "V"} - coverage["I"]), "L": sorted({"TL", "TR", "BL", "BR"} - coverage["L"])}
    if missing["I"] or missing["L"]:
        raise ConstructionFailure("TRAINING_ORIENTATION_COVERAGE_FAILED", {"coverage": {kind: sorted(values) for kind, values in coverage.items()}, "missing": missing})
    return coverage


def component_placements(n: int = N) -> dict[str, list[frozenset[int]]]:
    """The contract's deterministic, sorted individual I/L placement lists."""
    out: dict[str, list[frozenset[int]]] = {"I": [], "L": []}
    for cells, kind in triominoes(n).items():
        out[kind].append(cells)
    for values in out.values():
        values.sort(key=lambda value: tuple(sorted(value)))
    return out


def pool_family(spec: Rung, family: str, *, n: int = N,
                limit: int = POOL_LIMIT, trials: int = POOL_TRIALS) -> tuple[list[bytes], dict]:
    """Build one bounded family pool exactly in placement/rejection draw order."""
    placements = component_placements(n)
    generator = _rng(POOL_SEED, spec.index, spec.family_codes[family])
    retained: set[bytes] = set()
    rejected = {"overlap": 0, "touch": 0, "duplicate": 0}
    for trial in range(trials):
        components = [placements[letter][int(generator.integers(len(placements[letter])))] for letter in family]
        union: set[int] = set()
        overlap = False
        for component in components:
            if union & component:
                overlap = True
                break
            union.update(component)
        if overlap:
            rejected["overlap"] += 1
            continue
        if any(_touches(components[i], components[j], n) for i in range(len(components)) for j in range(i)):
            rejected["touch"] += 1
            continue
        key = canonical_map(union, n)
        if key in retained:
            rejected["duplicate"] += 1
            continue
        retained.add(key)
        if len(retained) == limit:
            return sorted(retained), {"family": family, "trials": trial + 1, "retained": limit, "rejections": rejected}
    return sorted(retained), {"family": family, "trials": trials, "retained": len(retained), "rejections": rejected}


def inventory(spec: Rung, *, n: int = N, limit: int = POOL_LIMIT,
              trials: int = POOL_TRIALS) -> tuple[list[dict], dict]:
    """Frozen pool and candidate inventory, with globally sorted canonical IDs."""
    by_key: dict[bytes, str] = {}
    audit: dict[str, dict] = {}
    for family in (*spec.training_families, *spec.challenge_families):
        values, audit[family] = pool_family(spec, family, n=n, limit=limit, trials=trials)
        for key in values:
            if key in by_key:
                raise OracleIntegrityError(f"pool family identity collision family={family} canonical={key.hex()}")
            by_key[key] = family
    rows = []
    for map_id, key in enumerate(sorted(by_key)):
        walls = frozenset(index for index, value in enumerate(key) if value)
        family_component_orientations(walls, by_key[key], n=n)
        rows.append({"map_id": map_id, "canonical": key, "family": by_key[key], "walls": walls,
                     "candidates": candidates_for(walls, spec, n=n)})
    return rows, audit


def candidates_for(walls: frozenset[int], spec: Rung, *, n: int = N, cache: OracleCache | None = None) -> list[tuple[int, int, int, int]]:
    result = []
    cache = cache or OracleCache()
    for goal in range(n * n):
        if goal in walls:
            continue
        distances, counts = cache.bfs(walls, goal, n)
        for start in sorted(distances):
            distance, multiplicity = distances[start], counts[start]
            if distance in spec.lengths and 16 <= multiplicity <= 256:
                result.append((start, goal, distance, multiplicity))
    return sorted(result)


def map_rng(spec: Rung, split: str, family: str) -> np.random.Generator:
    return _rng(spec.split_seeds[split], spec.family_codes[family], 0)


def problem_rng(spec: Rung, split: str, family: str) -> np.random.Generator:
    return _rng(spec.split_seeds[split], spec.family_codes[family], 1)


def select_maps(rows: Iterable[dict], spec: Rung, split: str, required: dict[str, int],
                excluded: set[bytes], eligible_pairs: dict[int, list[tuple[int, int, int, int]]] | None = None) -> tuple[dict[str, list[dict]], dict]:
    """One continuous family map stream, immutable earlier-split exclusions."""
    chosen: dict[str, list[dict]] = {}
    evidence: dict[str, dict] = {}
    for family in required:
        eligible = [row for row in sorted(rows, key=lambda value: value["map_id"])
                    if row["family"] == family and row["canonical"] not in excluded
                    and len((eligible_pairs or {}).get(row["map_id"], row["candidates"])) >= 16]
        permutation = map_rng(spec, split, family).permutation(len(eligible)).tolist()
        take = [eligible[index] for index in permutation[:required[family]]]
        evidence[family] = {"requested": required[family], "eligible": len(eligible),
                            "permutation": permutation, "selected_map_ids": [row["map_id"] for row in take]}
        if len(take) != required[family]:
            raise ConstructionFailure("MAP_SUPPLY_FAILED", {"split": split, "family": family, **evidence[family]})
        chosen[family] = take
        excluded.update(row["canonical"] for row in take)
    return chosen, evidence


def length_quotas(lengths: Iterable[int], total: int, proportions: dict[int, float] | None = None) -> dict[int, int]:
    keys = tuple(sorted(lengths))
    fractions = proportions or {length: 1.0 / len(keys) for length in keys}
    allocated = hamilton({(length, 0): fractions[length] for length in keys}, total)
    return {key[0]: value for key, value in allocated.items()}


def _capacity(rows: Iterable[dict], pairs: dict[int, list[tuple[int, int, int, int]]], lengths: Iterable[int]) -> dict[int, dict[tuple[int, int], int]]:
    return {row["map_id"]: {(length, 0): sum(pair[2] == length for pair in pairs[row["map_id"]]) for length in lengths} for row in rows}


def allocate_by_length(rows: Iterable[dict], pairs: dict[int, list[tuple[int, int, int, int]]], quotas: dict[int, int], *, map_capacity: int = 16) -> tuple[dict[tuple[int, int], int], dict]:
    rows = list(rows)
    capacities = _capacity(rows, pairs, quotas)
    requested = {(length, 0): quotas[length] for length in sorted(quotas)}
    flow = deterministic_flow(capacities, requested, map_capacity=map_capacity)
    if sum(flow.values()) != sum(quotas.values()) or any(sum(value for (map_id, key), value in flow.items() if key == (length, 0)) != quota for length, quota in quotas.items()):
        raise ConstructionFailure("LENGTH_FLOW_FAILED", {"quotas": quotas, "capacities": capacities, "flow": flow})
    return flow, {"quotas": quotas, "capacities": capacities, "flow": flow}


def select_pairs(rows: Iterable[dict], spec: Rung, split: str,
                 flow: dict[tuple[int, tuple[int, int]], int], pairs: dict[int, list[tuple[int, int, int, int]]]) -> tuple[list[dict], dict]:
    """Consume each family generator continuously in sorted map-ID/length order."""
    generators = {family: problem_rng(spec, split, family) for family in spec.family_codes}
    selected: list[dict] = []
    permutations: dict[str, dict[str, list[int]]] = {}
    for row in sorted(rows, key=lambda value: value["map_id"]):
        generator = generators[row["family"]]
        for length in sorted(spec.lengths):
            available = [pair for pair in pairs[row["map_id"]] if pair[2] == length]
            order = generator.permutation(len(available)).tolist()
            take = flow.get((row["map_id"], (length, 0)), 0)
            permutations[f"{row['map_id']}:{length}"] = {"order": order, "take": take}
            for index in order[:take]:
                start, goal, distance, multiplicity = available[index]
                selected.append({"map_id": row["map_id"], "family": row["family"], "walls": row["walls"],
                                 "start": start, "goal": goal, "length": distance, "M": multiplicity})
    return sorted(selected, key=lambda value: (value["map_id"], value["start"], value["goal"])), permutations


def training_states_and_support(rows: Iterable[dict], *, n: int = N, cache: OracleCache | None = None) -> tuple[list[dict], list[bytes], str]:
    """Exact deduplicated DAG supervision and all nonempty shortest suffix signatures."""
    states: dict[tuple[int, int, int], dict] = {}; cache = cache or OracleCache()
    support: set[bytes] = set()
    for row in rows:
        distances, _ = cache.bfs(row["walls"], row["goal"], n)
        from_start, _ = cache.bfs(row["walls"], row["start"], n)
        for state in distances:
            if state != row["goal"] and from_start.get(state, 10 ** 9) + distances[state] == distances[row["start"]]:
                target = q_target(state, row["walls"], row["goal"], n)
                states.setdefault((row["map_id"], state, row["goal"]), {"map_id": row["map_id"], "state": state,
                               "goal": row["goal"], "q": tuple(target[action] for action in range(4))})
        for route in enumerate_routes(row["start"], row["goal"], row["walls"], n):
            support.update(signature(route[index:]) for index in range(len(route)))
    ordered = sorted(support)
    digest = hashlib.sha256(b"".join(len(item).to_bytes(2, "big") + item for item in ordered)).hexdigest()
    return [states[key] for key in sorted(states)], ordered, digest


def novelty_for(rows: Iterable[dict], support: set[bytes], *, n: int = N, cache: OracleCache | None = None) -> list[dict]:
    result = []
    cache = cache or OracleCache()
    for row in rows:
        signatures = cache.signatures(row["walls"], row["start"], row["goal"], n)
        if len(signatures) != row["M"]:
            raise OracleIntegrityError(f"candidate M mismatch map={row['map_id']} start={row['start']} goal={row['goal']} candidate={row['M']} enumerated={len(signatures)}")
        result.append({**row, "M_novel": sum(item not in support for item in signatures),
                       "route_count": len(signatures), "signature_count": len(signatures)})
    return result


def eligible_novelty_pairs(row: dict, support: set[bytes], kind: str, *, n: int = N, cache: OracleCache | None = None) -> list[tuple[int, int, int, int]]:
    accepted = []
    cache = cache or OracleCache()
    for start, goal, length, multiplicity in row["candidates"]:
        signatures = cache.signatures(row["walls"], start, goal, n)
        if len(signatures) != multiplicity:
            raise OracleIntegrityError(f"candidate M mismatch map={row['map_id']} start={start} goal={goal} candidate={multiplicity} enumerated={len(signatures)}")
        novel = sum(signature not in support for signature in signatures)
        if (kind == "routine" and novel == 0) or (kind == "challenge" and novel >= 4 and .25 <= novel / multiplicity <= .75):
            accepted.append((start, goal, length, multiplicity))
    return accepted


def stratum(rows: Iterable[dict], spec: Rung, split: str, required: dict[str, int], excluded: set[bytes],
            support: set[bytes], kind: str, proportions: dict[int, float], cache: OracleCache | None = None) -> tuple[list[dict], dict]:
    """Select an oracle-only routine/challenge held-out stratum and length-match it."""
    scoped = [row for row in rows if row["family"] in required and row["canonical"] not in excluded]
    cache = cache or OracleCache()
    eligible = {row["map_id"]: eligible_novelty_pairs(row, support, kind, n=N, cache=cache) for row in scoped}
    selected_by_family, map_audit = select_maps(scoped, spec, split, required, excluded, eligible)
    selected = [row for values in selected_by_family.values() for row in values]
    total = sum(required.values()) * 16
    quotas = length_quotas(spec.lengths, total, proportions)
    flow, flow_audit = allocate_by_length(selected, eligible, quotas)
    pairs, permutations = select_pairs(selected, spec, split, flow, eligible)
    records = novelty_for(pairs, support, n=N, cache=cache)
    if len(records) != total:
        raise OracleIntegrityError(f"stratum count mismatch kind={kind} expected={total} actual={len(records)}")
    return records, {"kind": kind, "map_selection": map_audit, "eligibility_counts": {key: len(value) for key, value in eligible.items()},
                     "flow": flow_audit, "permutations": permutations, "quotas": quotas}


def training_dataset(rows: Iterable[dict], spec: Rung, excluded: set[bytes], *,
                     maps_per_family: int = 32, problems: int = 1024) -> tuple[list[dict], list[dict], list[bytes], str, dict]:
    """Select the homogeneous training data, length-balance, then build exact support."""
    required = {family: maps_per_family for family in spec.training_families}
    selected_by_family, map_audit = select_maps(rows, spec, "train", required, excluded)
    selected_maps = [row for family in spec.training_families for row in selected_by_family[family]]
    coverage = require_training_orientation_coverage(selected_maps, n=N)
    pairs = {row["map_id"]: row["candidates"] for row in selected_maps}
    quotas = length_quotas(spec.lengths, problems)
    flow, flow_audit = allocate_by_length(selected_maps, pairs, quotas)
    selected, permutations = select_pairs(selected_maps, spec, "train", flow, pairs)
    observed = {length: sum(row["length"] == length for row in selected) for length in spec.lengths}
    if observed != quotas or any(value < 16 for value in observed.values()):
        raise OracleIntegrityError(f"training length/count mismatch observed={observed} quotas={quotas}")
    states, support, digest = training_states_and_support(selected, n=N)
    return selected, states, support, digest, {"map_selection": map_audit, "flow": flow_audit, "permutations": permutations, "length_quotas": quotas, "orientation_coverage": {kind: sorted(values) for kind, values in coverage.items()}}


def first_passing_rung(construct):
    """Pure ladder policy: only an ordinary construction failure permits B."""
    try:
        return "A", construct(rung("A"))
    except ConstructionFailure as first_error:
        first = {"outcome": first_error.outcome, "evidence": first_error.evidence}
        try:
            return "B", construct(rung("B"))
        except ConstructionFailure as second_error:
            second = {"outcome": second_error.outcome, "evidence": second_error.evidence}
            raise ConstructionFailure("DATASET_LADDER_FAILED", {"A": first, "B": second}) from first_error
