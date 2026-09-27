"""Frozen route-policy scoring banks, proper scores, and rollout metrics.

This module is deliberately pure: it does not load production data or train a
model.  A harness supplies immutable A1 rows, logits, and checkpoints later.
"""
from __future__ import annotations

import hashlib
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from math import log
from typing import Callable, Iterable, Sequence

import numpy as np

from .route_feasibility import ACTIONS, signature as canonical_signature

N = 12
SERIALIZATION_VERSION = "route-score-v1"

@dataclass(frozen=True)
class ScoreCandidate:
    canonical: bytes; map_id: int; family: str; goal: int; current: int; q: tuple[float, float, float, float]

@dataclass(frozen=True)
class ScoreBank:
    candidates: tuple[ScoreCandidate, ...]
    selected: tuple[ScoreCandidate, ...]
    candidate_hash: str; selected_hash: str; q_hash: str; map_counts: tuple[tuple[int, int], ...]

def serialize_candidate(candidate: ScoreCandidate) -> bytes:
    if len(candidate.canonical) != N * N or any(x not in (0, 1) for x in candidate.canonical): raise ValueError("invalid canonical map")
    if not all(isinstance(x, int) and 0 <= x < N * N for x in (candidate.goal, candidate.current)) or candidate.goal == candidate.current: raise ValueError("invalid candidate cells")
    return SERIALIZATION_VERSION.encode("utf-8") + b"\0" + bytes([N]) + candidate.canonical + candidate.goal.to_bytes(2, "big") + candidate.current.to_bytes(2, "big")

def record_hash(candidates: Iterable[ScoreCandidate]) -> str:
    return hashlib.sha256(b"".join(len(raw := serialize_candidate(c)).to_bytes(4, "big") + raw for c in candidates)).hexdigest()

def q_array_hash(candidates: Iterable[ScoreCandidate]) -> str:
    array = np.ascontiguousarray(np.asarray([c.q for c in candidates], dtype="<f8"))
    return hashlib.sha256(array.tobytes()).hexdigest()

def _walls(canonical: bytes) -> frozenset[int]: return frozenset(i for i, wall in enumerate(canonical) if wall)
def _neighbors(cell: int, walls: frozenset[int]) -> list[tuple[int, int]]:
    row, col = divmod(cell, N); out=[]
    for action, (dr, dc) in enumerate(ACTIONS):
        r, c = row + dr, col + dc
        if 0 <= r < N and 0 <= c < N and r * N + c not in walls: out.append((action, r * N + c))
    return out
def _bfs(canonical: bytes, goal: int) -> tuple[dict[int, int], dict[int, int]]:
    walls=_walls(canonical)
    if goal in walls: raise ValueError("blocked goal")
    dist={goal: 0}; todo=deque([goal])
    while todo:
        cell=todo.popleft()
        for _, nxt in _neighbors(cell, walls):
            if nxt not in dist: dist[nxt]=dist[cell]+1; todo.append(nxt)
    count={goal: 1}
    for cell, distance in sorted(dist.items(), key=lambda item: item[1]):
        if distance: count[cell]=sum(count.get(nxt, 0) for _, nxt in _neighbors(cell, walls) if dist.get(nxt) == distance - 1)
    return dist, count
def oracle_q(canonical: bytes, goal: int, current: int) -> tuple[float, float, float, float]:
    dist, count = _bfs(canonical, goal); walls=_walls(canonical)
    return _q_from_oracle(walls, goal, current, dist, count)
def _q_from_oracle(walls: frozenset[int], goal: int, current: int, dist: dict[int,int], count: dict[int,int]) -> tuple[float, float, float, float]:
    if current not in dist or current == goal: raise ValueError("nonterminal unreachable state")
    denom=count[current]; result=[]
    for action in range(4):
        nxt=dict(_neighbors(current, walls)).get(action)
        result.append(count.get(nxt, 0) / denom if nxt is not None and dist.get(nxt) == dist[current] - 1 else 0.0)
    return tuple(result)  # type: ignore[return-value]

def _bank(candidates: Iterable[ScoreCandidate]) -> ScoreBank:
    groups: dict[int, list[ScoreCandidate]] = defaultdict(list)
    for candidate in candidates: groups[candidate.map_id].append(candidate)
    if not groups or any(not rows for rows in groups.values()): raise ValueError("empty map bank")
    ordered=[]; selected=[]; counts=[]
    for map_id in sorted(groups):
        rows=groups[map_id]
        if len({(c.canonical, c.goal, c.current) for c in rows}) != len(rows): raise ValueError("duplicate bank candidate")
        ids=sorted(rows, key=lambda c: (c.goal, c.current)); ordered.extend(ids)
        chosen=sorted(ids, key=lambda c: (hashlib.sha256(serialize_candidate(c)).digest(), c.goal, c.current))[:32]
        selected.extend(chosen); counts.append((map_id, len(chosen)))
    return ScoreBank(tuple(ordered), tuple(selected), record_hash(ordered), record_hash(selected), q_array_hash(selected), tuple(counts))

def training_bank(states: Iterable[object]) -> ScoreBank:
    """Use A1's saved deduplicated state facts; never enumerate training support."""
    return _bank(ScoreCandidate(s.canonical, s.map_id, s.family, s.goal, s.current, tuple(float(x) for x in s.q)) for s in states)

def heldout_bank(problems: Iterable[object]) -> ScoreBank:
    maps: dict[tuple[bytes, int, str], set[int]] = defaultdict(set)
    for problem in problems: maps[(problem.canonical, problem.map_id, problem.family)].add(problem.goal)
    rows=[]
    for (canonical, map_id, family), goals in sorted(maps.items(), key=lambda item: item[0][1]):
        for goal in sorted(goals):
            dist, _ = _bfs(canonical, goal)
            walls=_walls(canonical)
            for current in sorted(cell for cell in dist if cell != goal): rows.append(ScoreCandidate(canonical, map_id, family, goal, current, _q_from_oracle(walls, goal, current, dist, _)))
    return _bank(rows)

def probe_bank(bank: ScoreBank, *, training: bool) -> tuple[ScoreCandidate, ...]:
    families=("IIIIIIII", "LLLLLLLL") if training else ("IIIIIIII", "LLLLLLLL", "IIIILLLL")
    per_family=4 if training else 4; limit=8
    selected=[]
    for family in families:
        map_ids=sorted({c.map_id for c in bank.selected if c.family == family})
        if family == "IIIILLLL" and not training: map_ids=map_ids[:8]
        else: map_ids=map_ids[:per_family]
        for map_id in map_ids: selected.extend([c for c in bank.selected if c.map_id == map_id][:limit])
    return tuple(selected)

def proper_scores(logits: np.ndarray, legal: np.ndarray, q: np.ndarray) -> dict[str, np.ndarray]:
    logits=np.asarray(logits, float); legal=np.asarray(legal, bool); q=np.asarray(q, float)
    if logits.shape != legal.shape or logits.shape != q.shape or logits.ndim != 2 or logits.shape[1] != 4: raise ValueError("bad proper-score shape")
    if np.any(~np.isfinite(logits)) or np.any(q < 0) or not np.allclose(q.sum(1), 1.0): raise ValueError("invalid logits/q")
    if np.any(q[~legal] != 0): raise ValueError("q assigns illegal action")
    if np.any(~legal.any(1)): raise ValueError("all actions masked")
    masked=np.where(legal, logits, -np.inf); maxes=np.max(masked, axis=1, keepdims=True); logp=masked-maxes-np.log(np.exp(masked-maxes).sum(1, keepdims=True))
    p=np.exp(logp); ce=np.array([-np.sum(row_q[row_q>0]*row_logp[row_q>0]) for row_q,row_logp in zip(q,logp)])
    hq=np.array([-np.sum(row_q[row_q>0]*np.log(row_q[row_q>0])) for row_q in q])
    hp=np.array([-np.sum(row_p[row_legal]*row_logp[row_legal]) for row_p,row_logp,row_legal in zip(p,logp,legal)])
    return {"ce":ce,"brier":((p-q)**2).sum(1),"kl":ce-hq,"entropy_p":hp,"entropy_q":hq,"nonoptimal_mass":(p*(q==0)).sum(1),"p":p}

def weighted_proper(rows: Sequence[ScoreCandidate], scores: dict[str, np.ndarray], *, routine_weight: float=.8) -> dict[str, float]:
    if len(rows) != len(scores["ce"]): raise ValueError("row/score mismatch")
    by_map: dict[tuple[str, int], list[int]] = defaultdict(list)
    for i, row in enumerate(rows): by_map[("challenge" if row.family == "IIIILLLL" else "routine", row.map_id)].append(i)
    strata={"routine": [], "challenge": []}
    for (stratum, _), indexes in by_map.items(): strata[stratum].append(indexes)
    result={}
    for key, values in scores.items():
        if key == "p": continue
        means={s: np.mean([np.mean(values[indexes]) for indexes in groups]) if groups else np.nan for s, groups in strata.items()}
        result[f"routine_{key}"]=float(means["routine"])
        result[f"challenge_{key}"]=float(means["challenge"])
        if np.isnan(means["routine"]): result[key]=float(means["challenge"])
        elif np.isnan(means["challenge"]): result[key]=float(means["routine"])
        else: result[key]=float(routine_weight*means["routine"]+(1-routine_weight)*means["challenge"])
    return result

def relative_improvement(initial: float, final: float) -> float | None: return None if initial == 0 else (initial-final)/initial
def rollout_uniforms(seed:int, splitcode:int, map_id:int, start:int, goal:int, replicate:int, sample:int) -> np.ndarray:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([95002,seed,splitcode,map_id,start,goal,replicate,sample]))).random(16)
def choose_action(probabilities: Sequence[float], legal: Sequence[bool], uniform: float) -> int:
    legal=np.asarray(legal, bool); probs=np.asarray(probabilities, float)
    if probs.shape != (4,) or not legal.any() or np.any(probs[~legal] != 0): raise ValueError("invalid action distribution")
    total=probs.sum()
    if not np.isclose(total,1): raise ValueError("probabilities must sum to one")
    running=0.; last=int(np.flatnonzero(legal)[-1])
    for action in np.flatnonzero(legal):
        running += probs[action]
        if uniform < running: return int(action)
    return last
def greedy_action(probabilities: Sequence[float], legal: Sequence[bool]) -> int:
    legal=np.asarray(legal, bool); probs=np.asarray(probabilities, float); return int(np.flatnonzero(legal)[np.argmax(probs[legal])])

@dataclass(frozen=True)
class RolloutAttempt:
    route: bytes; valid: bool; novel: bool
def verify_route(route: bytes, canonical: bytes, start: int, goal: int) -> bool:
    dist,_=_bfs(canonical, goal); walls=_walls(canonical); current=start
    for action in route:
        if current == goal or action > 3: return False
        current=dict(_neighbors(current, walls)).get(action, -1)
        if current < 0: return False
    return current == goal and len(route) == dist.get(start, -1)
def rollout(canonical: bytes, start: int, goal: int, probabilities: Callable[[int], Sequence[float]], uniforms: Sequence[float], *, greedy: bool=False, support: frozenset[bytes]=frozenset()) -> RolloutAttempt:
    """One un-repaired 16-step attempt; callback gets only the current cell."""
    walls=_walls(canonical); current=start; actions=[]
    for uniform in list(uniforms)[:16]:
        if current == goal: break
        legal=np.zeros(4, dtype=bool)
        for action, _ in _neighbors(current, walls): legal[action]=True
        if not legal.any(): break
        probs=np.asarray(probabilities(current), float)
        action=greedy_action(probs,legal) if greedy else choose_action(probs,legal,float(uniform))
        actions.append(action); current=dict(_neighbors(current,walls))[action]
    route=bytes(actions); valid=verify_route(route,canonical,start,goal)
    return RolloutAttempt(route,valid,valid and canonical_signature(route) not in support)
def route_metrics(attempts: Sequence[RolloutAttempt], M: int, Mnovel: int | None) -> dict[str, float | None]:
    k=len(attempts)
    if not k: raise ValueError("empty attempts")
    valid=[a for a in attempts if a.valid]; novel=[a for a in valid if a.novel]; unique_valid={a.route for a in valid}; unique_novel={a.route for a in novel}; counts=Counter(a.route for a in valid)
    return {"Q":len(valid)/k,"U_valid":len(unique_valid)/k,"U_novel":len(unique_novel)/k,"V_novel":len(novel)/k,"pass_at_k":float(bool(valid)),"coverage":None if Mnovel in (None,0) else len(unique_novel)/Mnovel,"valid_headroom":len(unique_valid)/M,"duplicate_rate":(len(valid)-len(unique_valid))/k,"invalid_rate":(k-len(valid))/k,"duplicate_concentration":None if not valid else sum((n/len(valid))**2 for n in counts.values())}

@dataclass(frozen=True)
class TemperatureResult:
    temperature: float; matched: bool; fallback: bool; evaluations: tuple[tuple[float,float], ...]; target: float; direction: str
def choose_temperature(evaluate: Callable[[float], float], target: float, *, direction: str="nonincreasing", tolerance: float=.005, bounds: tuple[float,float]=(.25,3.), grid: tuple[float,...]=(.5,.75,1.,1.25,1.5,2.)) -> TemperatureResult:
    if direction not in ("nonincreasing","nondecreasing"): raise ValueError("invalid temperature direction")
    seen: dict[float,float] = {}
    def ev(t:float)->float:
        if t not in seen: seen[t]=float(evaluate(t))
        return seen[t]
    def monotonic_bad() -> bool:
        values=[value for _,value in sorted(seen.items())]
        return any((right < left) if direction=="nondecreasing" else (right > left) for left,right in zip(values,values[1:]))
    lo,hi=bounds; vlo,vhi=ev(lo),ev(hi)
    bracket= min(vlo,vhi) <= target <= max(vlo,vhi)
    if monotonic_bad() or not bracket:
        for t in grid: ev(t)
        t=min(grid, key=lambda t:(abs(seen[t]-target),t)); return TemperatureResult(t, abs(seen[t]-target)<=tolerance, True, tuple(sorted(seen.items())),target,direction)
    for _ in range(8):
        mid=(lo+hi)/2; value=ev(mid)
        if monotonic_bad():
            for t in grid: ev(t)
            t=min(grid, key=lambda t:(abs(seen[t]-target),t)); return TemperatureResult(t, abs(seen[t]-target)<=tolerance, True, tuple(sorted(seen.items())),target,direction)
        if abs(value-target)<=tolerance: return TemperatureResult(mid, True, False, tuple(sorted(seen.items())),target,direction)
        if (value < target) == (direction=="nondecreasing"): lo=mid
        else: hi=mid
    t=min(seen, key=lambda t:(abs(seen[t]-target),t)); return TemperatureResult(t, abs(seen[t]-target)<=tolerance, False, tuple(sorted(seen.items())),target,direction)
def quality_temperature(evaluate: Callable[[float], float], target: float=.9) -> TemperatureResult:
    return choose_temperature(evaluate,target,direction="nonincreasing",tolerance=.005)
def entropy_temperature(evaluate: Callable[[float], float], target: float) -> TemperatureResult:
    return choose_temperature(evaluate,target,direction="nondecreasing",tolerance=.01)

class LogitCache:
    """Cache is explicitly scoped by immutable model/checkpoint/intervention identity."""
    def __init__(self): self._values: dict[tuple[object,int,int,int], np.ndarray]={}
    def get_or_compute(self, identity: object, candidate: ScoreCandidate, compute: Callable[[ScoreCandidate], np.ndarray]) -> np.ndarray:
        key=(identity,candidate.map_id,candidate.goal,candidate.current)
        if key not in self._values: self._values[key]=np.asarray(compute(candidate), dtype=float).copy()
        return self._values[key]
