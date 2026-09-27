"""Frozen v3 Block-1 n=12 geometry, inventory and raw-capacity ranking.

This module deliberately stops before route enumeration, novelty, support, or
any runner/model work.  Its inputs are explicit and dimension-parametric so
the v3 n=12 construction cannot accidentally inherit a v2-sized helper.
"""
from __future__ import annotations

from collections import Counter, OrderedDict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
import hashlib
import time
from typing import Callable, Iterable, Mapping, Sequence

import numpy as np

from .route_feasibility import bfs_counts, canonical_map, enumerate_routes, neighbors, q_target, signature, verify

N = 12
FAMILIES = ("IIIIIIII", "LLLLLLLL", "IIIILLLL")
FAMILY_CODE = {family: index for index, family in enumerate(FAMILIES)}
LENGTHS = tuple(range(12, 21))
WINDOWS = ((12, 13, 14), (14, 15, 16), (16, 17, 18), (18, 19, 20))
QUOTAS = ((6, 5, 5), (5, 6, 5), (5, 5, 6))
RAW_REQUIRED = {"IIIIIIII": 92, "LLLLLLLL": 92, "IIIILLLL": 40}
POOL_SEED = 93000
SHORTLIST_SEED = 93001
SPLIT_SEED = {"train": 94001, "validation": 94002, "test": 94003}


class GeometryError(RuntimeError):
    """A malformed component/pool is a technical failure, never supply."""


@lru_cache(maxsize=None)
def direct_shape_placements(n: int) -> Mapping[str, tuple[tuple[int, ...], ...]]:
    """Return sorted immutable direct I/L triomino placements for ``n``."""
    if n < 3:
        return {"I": (), "L": ()}
    i_parts: list[tuple[int, ...]] = []
    l_parts: list[tuple[int, ...]] = []
    cell = lambda r, c: r * n + c
    for r in range(n):
        for c in range(n - 2):
            i_parts.append((cell(r, c), cell(r, c + 1), cell(r, c + 2)))
    for r in range(n - 2):
        for c in range(n):
            i_parts.append((cell(r, c), cell(r + 1, c), cell(r + 2, c)))
    for r in range(n - 1):
        for c in range(n - 1):
            square = (cell(r, c), cell(r, c + 1), cell(r + 1, c), cell(r + 1, c + 1))
            for missing in range(4):
                l_parts.append(tuple(x for index, x in enumerate(square) if index != missing))
    return {"I": tuple(sorted(i_parts)), "L": tuple(sorted(l_parts))}


def _touches(a: Iterable[int], b: Iterable[int], n: int) -> bool:
    right = frozenset(b)
    return any(y in right for x in a for _, y in neighbors(x, frozenset(), n))


def _component_kind(component: frozenset[int], n: int) -> str:
    placements = direct_shape_placements(n)
    as_tuple = tuple(sorted(component))
    for kind, values in placements.items():
        if as_tuple in values:
            return kind
    raise GeometryError("component is not a direct I or L triomino")


def validate_family_components(walls: Iterable[int], family: str, n: int = N) -> None:
    """Validate 8 separated triominoes and exact literal family composition."""
    if family not in FAMILY_CODE:
        raise GeometryError(f"unknown family {family!r}")
    wallset = frozenset(walls)
    if len(wallset) != 24:
        raise GeometryError("canonical wall set must contain exactly 24 cells")
    remaining = set(wallset)
    kinds: list[str] = []
    while remaining:
        root = min(remaining)
        component = {root}
        frontier = [root]
        remaining.remove(root)
        while frontier:
            node = frontier.pop()
            for _, nxt in neighbors(node, frozenset(), n):
                if nxt in remaining:
                    remaining.remove(nxt)
                    component.add(nxt)
                    frontier.append(nxt)
        kinds.append(_component_kind(frozenset(component), n))
    if len(kinds) != 8 or Counter(kinds) != Counter(family):
        raise GeometryError("wall components do not match declared literal family")


@dataclass(frozen=True)
class PoolResult:
    family: str
    maps: tuple[bytes, ...]
    trials: int
    rejected_overlap: int
    rejected_touching: int
    rejected_duplicate: int
    draw_prefix: tuple[tuple[int, ...], ...] = ()


def pool_family(
    family: str,
    *,
    n: int = N,
    limit: int = 256,
    max_trials: int = 200_000,
    injected_draw_rows: Iterable[Sequence[int]] | None = None,
) -> PoolResult:
    """Generate a bounded deterministic canonical pool; no refill is attempted."""
    if family not in FAMILY_CODE or len(family) != 8:
        raise GeometryError("family must be one frozen eight-letter literal")
    placements = direct_shape_placements(n)
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([POOL_SEED, FAMILY_CODE[family]])))
    found: set[bytes] = set()
    overlap = touching = duplicate = 0
    trials = 0
    injected = iter(injected_draw_rows) if injected_draw_rows is not None else None
    draws: list[tuple[int, ...]] = []
    for trials in range(1, max_trials + 1):
        indices = tuple(int(x) for x in (next(injected) if injected is not None else (rng.integers(len(placements[kind])) for kind in family)))
        if len(indices) != len(family) or any(index < 0 or index >= len(placements[kind]) for index, kind in zip(indices, family)):
            raise GeometryError("injected component draw is outside the direct placement table")
        # Audit only a bounded prefix; retaining every production trial would
        # otherwise keep up to 200,000 eight-index rows without affecting RNG.
        if len(draws) < 16:
            draws.append(indices)
        chosen = [placements[kind][index] for kind, index in zip(family, indices)]
        cells = [x for part in chosen for x in part]
        if len(set(cells)) != len(cells):
            overlap += 1
            continue
        if any(_touches(chosen[i], chosen[j], n) for i in range(8) for j in range(i + 1, 8)):
            touching += 1
            continue
        key = canonical_map(cells, n)
        if key in found:
            duplicate += 1
            continue
        validate_family_components((i for i, bit in enumerate(key) if bit), family, n)
        found.add(key)
        if len(found) == limit:
            break
    return PoolResult(family, tuple(sorted(found)), trials, overlap, touching, duplicate, tuple(draws))


def inventory_candidates(walls: frozenset[int], *, n: int = N) -> tuple[tuple[int, int, int, int], ...]:
    """Return complete n-explicit (start, goal, distance, shortest-route-count)."""
    candidates: list[tuple[int, int, int, int]] = []
    for goal in range(n * n):
        if goal in walls:
            continue
        distance, multiplicity = bfs_counts(walls, goal, n)
        for start in sorted(distance):
            d, m = distance[start], multiplicity[start]
            if 12 <= d <= 20 and 16 <= m <= 256:
                candidates.append((start, goal, d, m))
    return tuple(sorted(candidates))


def shortlist_by_length(
    candidates: Sequence[tuple[int, int, int, int]], *, map_id: int, shortlist_cap: int = 64
) -> dict[int, dict[str, object]]:
    """Permute each complete sorted map/length list exactly once using frozen RNG."""
    result: dict[int, dict[str, object]] = {}
    for length in LENGTHS:
        complete = tuple(item for item in candidates if item[2] == length)
        rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([SHORTLIST_SEED, map_id, length])))
        order = tuple(int(i) for i in rng.permutation(len(complete)))
        retained = tuple(complete[i] for i in order[:shortlist_cap])
        result[length] = {"raw_count": len(complete), "permutation": order, "retained": retained}
    return result


def assemble_global_inventory(
    pools: Mapping[str, PoolResult],
    *,
    n: int = N,
    candidate_oracle: Callable[..., tuple[tuple[int, int, int, int], ...]] = inventory_candidates,
    shortlist_oracle: Callable[..., dict[int, dict[str, object]]] = shortlist_by_length,
) -> tuple[dict[str, object], ...]:
    """Bind global canonical identity to the map IDs used by shortlist streams.

    The optional oracle seams are only for small injected tests.  Production
    callers use the explicit n=12 inventory and frozen shortlist functions.
    """
    seen: dict[bytes, str] = {}
    entries: list[tuple[bytes, str]] = []
    for family in FAMILIES:
        if family not in pools:
            raise GeometryError(f"missing frozen family pool {family}")
        for key in pools[family].maps:
            prior = seen.get(key)
            if prior is not None:
                raise GeometryError(f"canonical identity collision: {prior} and {family}")
            seen[key] = family
            entries.append((key, family))
    records: list[dict[str, object]] = []
    for map_id, (key, family) in enumerate(sorted(entries, key=lambda item: item[0])):
        walls = frozenset(index for index, bit in enumerate(key) if bit)
        if canonical_map(walls, n) != key:
            raise GeometryError("pool canonical bytes do not reconstruct at declared dimension")
        validate_family_components(walls, family, n)
        candidates = candidate_oracle(walls, n=n)
        if tuple(sorted(candidates)) != tuple(candidates):
            raise GeometryError("candidate oracle returned unsorted candidates")
        shortlists = shortlist_oracle(candidates, map_id=map_id)
        records.append({
            "n": n,
            "map_id": map_id,
            "family": family,
            "canonical": key,
            "walls": walls,
            "candidates": candidates,
            "shortlists": shortlists,
        })
    return tuple(records)


def _fraction_json(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def _fraction_from_json(value: Mapping[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _shortlist(record: Mapping[str, object], length: int) -> Sequence[tuple[int, int, int, int]]:
    return record["shortlists"][length]["retained"]  # type: ignore[index,return-value]


def rank_proposals(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    """Compute the frozen all-12 raw-capacity ranking without route enumeration."""
    proposals: list[dict[str, object]] = []
    for window in WINDOWS:
        for quota_index, quota in enumerate(QUOTAS):
            eligible: dict[str, list[Mapping[str, object]]] = {family: [] for family in FAMILIES}
            for record in records:
                family = record["family"]
                if family not in eligible:
                    raise GeometryError("record has an unknown family")
                if all(len(_shortlist(record, length)) >= need for length, need in zip(window, quota)):
                    eligible[family].append(record)
            counts = {family: len(eligible[family]) for family in FAMILIES}
            score = min(Fraction(counts[f], RAW_REQUIRED[f]) for f in FAMILIES)
            reasons = [f"{family}:{counts[family]}<{RAW_REQUIRED[family]}" for family in FAMILIES if counts[family] < RAW_REQUIRED[family]]
            ms = [item[3] for family in FAMILIES for record in eligible[family] for length in window for item in _shortlist(record, length)]
            cost = Fraction(sum(ms), len(ms)) if ms else None
            proposals.append({
                "window": window,
                "window_start": window[0],
                "quota": quota,
                "quota_index": quota_index,
                "raw_family_counts": counts,
                "score": _fraction_json(score),
                "mean_m": _fraction_json(cost) if cost is not None else None,
                "feasible": not reasons,
                "infeasibility_reasons": reasons,
            })
    winners: list[dict[str, object]] = []
    for window in WINDOWS:
        candidates = [p for p in proposals if p["window"] == window and p["feasible"]]
        if candidates:
            winners.append(min(candidates, key=lambda p: (-_fraction_from_json(p["score"]), _fraction_from_json(p["mean_m"]), p["quota_index"])))
    ordered = sorted(winners, key=lambda p: (-_fraction_from_json(p["score"]), _fraction_from_json(p["mean_m"]), p["window_start"], p["quota_index"]))
    return {"proposals": proposals, "window_winners": winners, "retained": ordered[:3], "status": "OK" if ordered else "RAW_JOINT_CAPACITY_FAILED"}


class SelectionTechnicalError(RuntimeError):
    """Oracle/count/identity defects must never be interpreted as supply."""


@dataclass(frozen=True)
class SelectionConfig:
    """Internal test seam; production defaults are the frozen contract values."""
    lengths: tuple[int, int, int]
    quota: tuple[int, int, int]
    train_maps_per_family: int = 32


class ProposalOracleCache:
    """Bounded proposal-local cache; eligibility keys include the support hash."""
    def __init__(self) -> None:
        self.bfs: OrderedDict[tuple[bytes, int], tuple[dict[int, int], dict[int, int]]] = OrderedDict()
        self.pairs: OrderedDict[tuple[bytes, int, int], tuple[bytes, ...]] = OrderedDict()
        self.signatures: OrderedDict[bytes, bytes] = OrderedDict()
        self.eligibility: OrderedDict[tuple[str, bytes, int, int], tuple[int, tuple[bytes, ...]]] = OrderedDict()
        self.stats = Counter()
        self.started = time.perf_counter()

    @staticmethod
    def _put(cache: OrderedDict, key: object, value: object, limit: int) -> object:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > limit:
            cache.popitem(last=False)
        return value

    def routes(self, walls: frozenset[int], start: int, goal: int, n: int) -> tuple[bytes, ...]:
        key = (bytes(int(i in walls) for i in range(n * n)), n, start, goal)
        if key in self.pairs:
            self.stats["pair_hits"] += 1
            self.pairs.move_to_end(key)
            return self.pairs[key]
        self.stats["pair_misses"] += 1
        routes = tuple(enumerate_routes(start, goal, walls, n))
        self.stats["routes"] += len(routes)
        return self._put(self.pairs, key, routes, 512)  # type: ignore[return-value]

    def bfs_counts(self, walls: frozenset[int], goal: int, n: int) -> tuple[dict[int, int], dict[int, int]]:
        key = (bytes(int(i in walls) for i in range(n * n)), n, goal)
        if key in self.bfs:
            self.stats["bfs_hits"] += 1; self.bfs.move_to_end(key); return self.bfs[key]
        self.stats["bfs_misses"] += 1
        return self._put(self.bfs, key, bfs_counts(walls, goal, n), 512)  # type: ignore[return-value]

    def canonical_signature(self, route: bytes) -> bytes:
        if route in self.signatures:
            self.stats["signature_hits"] += 1
            self.signatures.move_to_end(route)
            return self.signatures[route]
        self.stats["signature_misses"] += 1
        return self._put(self.signatures, route, signature(route), 65536)  # type: ignore[return-value]

    def profile(self) -> dict[str, object]:
        return {"stats": dict(self.stats), "elapsed_seconds": time.perf_counter() - self.started,
                "bfs_entries": len(self.bfs), "pair_entries": len(self.pairs), "signature_entries": len(self.signatures), "eligibility_entries": len(self.eligibility)}


def _eligible(record: Mapping[str, object], config: SelectionConfig) -> bool:
    return all(len(_shortlist(record, length)) >= quota for length, quota in zip(config.lengths, config.quota))


def training_orientation_coverage(records: Sequence[Mapping[str, object]]) -> dict[str, set[str]]:
    """Classify direct triomino orientations for the frozen homogeneous gate."""
    covered = {"IIIIIIII": set(), "LLLLLLLL": set()}
    for record in records:
        family = record["family"]
        if family not in covered: continue
        walls = set(record["walls"]); parts = []
        while walls:
            root = next(iter(walls)); todo=[root]; part={root}; walls.remove(root)
            while todo:
                x=todo.pop()
                for _,y in neighbors(x,frozenset(),N):
                    if y in walls: walls.remove(y);part.add(y);todo.append(y)
            parts.append(part)
        for part in parts:
            rows={x//N for x in part}; cols={x%N for x in part}
            if len(rows)==1: covered[family].add("I-H")
            elif len(cols)==1: covered[family].add("I-V")
            else:
                r=min(rows); c=min(cols); missing=next((rr,cc) for rr in (r,r+1) for cc in (c,c+1) if rr*N+cc not in part)
                covered[family].add(f"L-{missing[0]-r}{missing[1]-c}")
    return covered


def validate_inventory_records(records: Sequence[Mapping[str, object]]) -> None:
    """One technical metadata/linkage validation pass before proposal selection."""
    ids=set(); identities=set()
    for record in records:
        if record.get("map_id") in ids or record.get("canonical") in identities: raise SelectionTechnicalError("duplicate map identity")
        ids.add(record["map_id"]); identities.add(record["canonical"])
        if record.get("n") != N or record.get("family") not in FAMILY_CODE: raise SelectionTechnicalError("unknown n or record family")
        walls=record["walls"]; key=record["canonical"]
        if canonical_map(walls,N)!=key: raise SelectionTechnicalError("canonical/walls mismatch")
        validate_family_components(walls,record["family"],N)
        seen=set()
        for length, payload in record["shortlists"].items():
            for start,goal,d,m in payload["retained"]:
                if d!=length or (start,goal) in seen or not(16<=m<=256) or not(0<=start<N*N and 0<=goal<N*N) or start in walls or goal in walls: raise SelectionTechnicalError("malformed inventory row")
                seen.add((start,goal))


def frozen_map_order(records: Sequence[Mapping[str, object]], family: str, *, split: str, window_start: int) -> tuple[Mapping[str, object], ...]:
    if split not in SPLIT_SEED or family not in FAMILY_CODE:
        raise SelectionTechnicalError("unknown frozen split or family")
    rows = sorted((row for row in records if row["family"] == family), key=lambda row: row["map_id"])
    rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence([SPLIT_SEED[split], window_start, FAMILY_CODE[family], 0])))
    return tuple(rows[int(index)] for index in rng.permutation(len(rows)))


def build_training_support(records: Sequence[Mapping[str, object]], *, window_start: int, config: SelectionConfig,
                           cache: ProposalOracleCache | None = None, validate: bool = True) -> dict[str, object]:
    """Map frozen training prefixes to full shortest-DAG q and suffix support."""
    if validate: validate_inventory_records(records)
    cache = cache or ProposalOracleCache()
    selected: list[dict[str, object]] = []
    support: set[bytes] = set()
    states: dict[tuple[bytes, int, int], dict[int, float]] = {}
    for family in FAMILIES[:2]:
        maps = [row for row in frozen_map_order(records, family, split="train", window_start=window_start) if _eligible(row, config)]
        if len(maps) < config.train_maps_per_family:
            return {"outcome": "SCIENTIFIC_TRAINING_SUPPLY_FAILED", "family": family, "selected": selected, "profile": cache.profile()}
        coverage = training_orientation_coverage(maps[:config.train_maps_per_family])[family]
        required = {"I-H", "I-V"} if family == "IIIIIIII" else {"L-00", "L-01", "L-10", "L-11"}
        if not required <= coverage:
            return {"outcome": "SCIENTIFIC_TRAINING_ORIENTATION_SHORTAGE", "family": family, "coverage": sorted(coverage), "required": sorted(required), "selected": selected, "profile": cache.profile()}
        for record in maps[:config.train_maps_per_family]:
            walls, key = record["walls"], record["canonical"]
            for length, quota in zip(config.lengths, config.quota):
                for start, goal, d, m in _shortlist(record, length)[:quota]:
                    if d != length or not (16 <= m <= 256):
                        raise SelectionTechnicalError("inventory row violates frozen distance/M")
                    distance, counts = cache.bfs_counts(walls, goal, N)
                    routes = cache.routes(walls, start, goal, N)
                    if len(routes) != m or distance.get(start) != d or counts.get(start) != m:
                        raise SelectionTechnicalError("route oracle does not reproduce inventory multiplicity")
                    for route in routes:
                        for index in range(len(route)):
                            support.add(cache.canonical_signature(route[index:]))
                    for route in routes:
                        node = start
                        for action in route:
                            state_key = (key, node, goal)
                            if state_key not in states:
                                q = {a: (counts.get(nxt, 0) / counts[node] if distance.get(nxt) == distance[node] - 1 else 0.0)
                                     for a, nxt in neighbors(node, walls, N)}
                                q = {a: q.get(a, 0.0) for a in range(4)}
                                if abs(sum(q.values()) - 1.0) > 1e-12:
                                    raise SelectionTechnicalError("non-normalized shortest-DAG q")
                                states[state_key] = q
                            node = dict(neighbors(node, walls, N))[action]
                    selected.append({"n": N, "family": family, "map_id": record["map_id"], "canonical": key,
                                     "start": start, "goal": goal, "length": d, "M": m})
    encoded = b"".join(len(value).to_bytes(2, "big") + value for value in sorted(support))
    return {"outcome": "OK", "selected": selected, "states": states, "support": tuple(sorted(support)),
            "support_hash": hashlib.sha256(encoded).hexdigest(), "profile": cache.profile(), "cache": cache}


def lazy_select_heldout(records: Sequence[Mapping[str, object]], *, family: str, split: str, window_start: int,
                        config: SelectionConfig, support: Sequence[bytes], mode: str, required_maps: int,
                        excluded_identities: set[bytes], cache: ProposalOracleCache | None = None) -> dict[str, object]:
    """Scan frozen shortlists lazily and commit a map only after every length passes."""
    if mode not in ("routine", "challenge"):
        raise SelectionTechnicalError("unknown held-out mode")
    cache = cache or ProposalOracleCache(); support_set = frozenset(support)
    support_hash = hashlib.sha256(b"".join(len(x).to_bytes(2,"big")+x for x in sorted(support_set))).hexdigest()
    committed: list[dict[str, object]] = []; evidence: list[dict[str, object]] = []
    for record in frozen_map_order(records, family, split=split, window_start=window_start):
        if record["canonical"] in excluded_identities:
            evidence.append({"map_id":record["map_id"],"status":"EXCLUDED"}); continue
        if not _eligible(record, config):
            evidence.append({"map_id":record["map_id"],"status":"RAW_INELIGIBLE"}); continue
            continue
        pending: list[dict[str, object]] = []; failures: list[str] = []
        for length, quota in zip(config.lengths, config.quota):
            accepted = []; examined = 0
            for start, goal, d, m in _shortlist(record, length):
                examined += 1
                dist, counts = cache.bfs_counts(record["walls"], goal, N)
                routes = cache.routes(record["walls"], start, goal, N)
                if len(routes) != m or d != length or dist.get(start)!=d or counts.get(start)!=m:
                    raise SelectionTechnicalError("held-out inventory/oracle mismatch")
                eligibility_key=(support_hash, bytes(int(i in record["walls"]) for i in range(N*N)), N, start, goal)
                if eligibility_key in cache.eligibility:
                    cache.stats["eligibility_hits"]+=1; novel,_=cache.eligibility[eligibility_key]
                else:
                    cache.stats["eligibility_misses"]+=1; novel=sum(cache.canonical_signature(route) not in support_set for route in routes)
                    cache._put(cache.eligibility,eligibility_key,(novel,routes),512)
                ok = novel == 0 if mode == "routine" else novel >= 4 and Fraction(novel, m) >= Fraction(1, 4) and Fraction(novel, m) <= Fraction(3, 4)
                if ok:
                    accepted.append({"n": N, "family": family, "map_id": record["map_id"], "canonical": record["canonical"],
                                     "start": start, "goal": goal, "length": d, "M": m, "Mnovel": novel})
                    if len(accepted) == quota: break
            if len(accepted) != quota:
                failures.append(f"length_{length}_exhausted")
                evidence.append({"map_id": record["map_id"], "committed": False, "length": length, "examined": examined, "accepted_rows": accepted, "reason": failures[-1]})
                break
            pending.extend(accepted)
            evidence.append({"map_id": record["map_id"], "committed": False, "length": length, "examined": examined, "accepted_rows": accepted})
        if not failures:
            committed.extend(pending); excluded_identities.add(record["canonical"])
            evidence.append({"map_id": record["map_id"], "committed": True})
            if len({row["map_id"] for row in committed}) == required_maps: break
    visited={item["map_id"] for item in evidence}; evidence.extend({"map_id":r["map_id"],"status":"NOT_EVALUATED"} for r in records if r["family"]==family and r["map_id"] not in visited)
    return {"outcome": "OK" if len({row["map_id"] for row in committed}) == required_maps else "SCIENTIFIC_HELDOUT_SUPPLY_FAILED",
            "selected": committed, "evidence": evidence, "profile": cache.profile()}


def run_ranked_proposals(ranking: Mapping[str, object], records: Sequence[Mapping[str, object]], *, config: SelectionConfig,
                         on_stage: Callable[[str, Mapping[str, object]], None] | None = None,
                         counts: Mapping[str, int] | None = None) -> dict[str, object]:
    """Full frozen stage order; only declared scientific supply outcomes advance."""
    counts = counts or {"val_routine":12,"val_mixed":8,"test_routine":48,"test_mixed":32}; evidence = []
    proposals=tuple(ranking.get("retained", ())[:3])
    if not proposals: return {"outcome":"RAW_JOINT_CAPACITY_FAILED","evidence":[]}
    validate_inventory_records(records)
    starts=[p["window_start"] for p in proposals]
    if len(starts)!=len(set(starts)): raise SelectionTechnicalError("duplicate retained window")
    for proposal in proposals:
        proposal_config=SelectionConfig(tuple(proposal["window"]),tuple(proposal["quota"]),config.train_maps_per_family)
        cache = ProposalOracleCache()
        training = build_training_support(records, window_start=proposal["window_start"], config=proposal_config, cache=cache, validate=False)
        evidence.append({"proposal": proposal, "training": training})
        if on_stage: on_stage("training", {"proposal":proposal["window_start"],"result":training})
        if training["outcome"] != "OK":
            if training["outcome"] not in ("SCIENTIFIC_TRAINING_SUPPLY_FAILED","SCIENTIFIC_TRAINING_ORIENTATION_SHORTAGE"): raise SelectionTechnicalError("technical training outcome")
            evidence[-1]["stages"]={name:{"outcome":"NOT_EVALUATED"} for name in ("validation_routine","validation_mixed","test_routine","test_mixed")}
            if on_stage:
                for name in evidence[-1]["stages"]: on_stage(name,{"proposal":proposal["window_start"],"outcome":"NOT_EVALUATED"})
            continue
        excluded={row["canonical"] for row in training["selected"]}; stages={"training":training}; failed=False
        stage_plan=(("validation_routine","validation",FAMILIES[:2],"routine","val_routine"),("validation_mixed","validation",("IIIILLLL",),"challenge","val_mixed"),("test_routine","test",FAMILIES[:2],"routine","test_routine"),("test_mixed","test",("IIIILLLL",),"challenge","test_mixed"))
        for stage_index,(name,split,families,mode,count_key) in enumerate(stage_plan):
            rows=[]
            for family_index, family in enumerate(families):
                result=lazy_select_heldout(records,family=family,split=split,window_start=proposal["window_start"],config=proposal_config,support=training["support"],mode=mode,required_maps=counts[count_key],excluded_identities=excluded,cache=cache)
                rows.append({"family":family,"result":result}); excluded.update(r["canonical"] for r in result["selected"])
                if result["outcome"] not in ("OK","SCIENTIFIC_HELDOUT_SUPPLY_FAILED"): raise SelectionTechnicalError("technical held-out outcome")
                if result["outcome"] != "OK":
                    rows.extend({"family":future,"result":{"outcome":"NOT_EVALUATED"}} for future in families[family_index+1:])
                    break
            stages[name]=rows
            if on_stage: on_stage(name,{"proposal":proposal["window_start"],"results":rows})
            if any(r["result"]["outcome"]!="OK" for r in rows):
                failed=True
                for future,*_ in stage_plan[stage_index+1:]:
                    stages[future]={"outcome":"NOT_EVALUATED"}
                    if on_stage: on_stage(future,{"proposal":proposal["window_start"],"outcome":"NOT_EVALUATED"})
                break
        evidence[-1]["stages"]=stages
        if not failed: return {"outcome":"FIRST_FULL_DATASET_PASS","proposal":proposal,"stages":stages,"evidence":evidence}
    return {"outcome": "DATASET_CONSTRUCTION_FAILED", "evidence": evidence}
