"""Pure, fail-closed summaries for the one-seed paired behavior analysis.

This module deliberately does not load checkpoints, run inference, create an
attempt, or reconstruct a cohort.  The gated job supplies already saved rows
and uses these functions to reject identity/order mismatches before it reports
the descriptive comparison.
"""
from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np


class AlignmentError(ValueError):
    """Saved records cannot safely be paired."""


def _get(row: object, name: str) -> Any:
    return row[name] if isinstance(row, Mapping) else getattr(row, name)


def state_key(row: object) -> tuple[bytes, int, str, int, int]:
    canonical = _get(row, "canonical")
    if isinstance(canonical, str):
        canonical = bytes.fromhex(canonical)
    return canonical, int(_get(row, "map_id")), str(_get(row, "family")), int(_get(row, "goal")), int(_get(row, "current"))


def problem_key(row: object) -> tuple[bytes, int, str, int, int]:
    canonical = _get(row, "canonical")
    if isinstance(canonical, str):
        canonical = bytes.fromhex(canonical)
    return canonical, int(_get(row, "map_id")), str(_get(row, "family")), int(_get(row, "start")), int(_get(row, "goal"))


def require_exact_order(left: Sequence[object], right: Sequence[object], key: Callable[[object], object]) -> None:
    """Reject reorder, duplicates, omissions and additions; never pair by zip alone."""
    lk, rk = [key(x) for x in left], [key(x) for x in right]
    if len(lk) != len(set(lk)) or len(rk) != len(set(rk)):
        raise AlignmentError("duplicate saved record identity")
    if lk != rk:
        raise AlignmentError("saved record identity/order mismatch")


def paired_states(sm: Sequence[object], sa: Sequence[object]) -> list[dict[str, Any]]:
    require_exact_order(sm, sa, state_key)
    rows = []
    for a, b in zip(sm, sa):
        p_sm, p_sa, q = (np.asarray(_get(x, name), float) for x, name in ((a, "p"), (b, "p"), (a, "q")))
        if p_sm.shape != (4,) or p_sa.shape != (4,) or q.shape != (4,) or not np.isclose(q.sum(), 1):
            raise AlignmentError("malformed aligned policy/q row")
        sm_action, sa_action = int(np.argmax(p_sm)), int(np.argmax(p_sa))  # N/E/S/W tie order
        sm_optimal, sa_optimal = bool(q[sm_action] > 0), bool(q[sa_action] > 0)
        optimality = "both_q_optimal" if sm_optimal and sa_optimal else "sm_only_optimal" if sm_optimal else "sa_only_optimal" if sa_optimal else "neither_optimal"
        entropy_p = lambda p: float(-np.sum(p[p > 0] * np.log(p[p > 0])))
        entropy_q = entropy_p(q)
        if not np.array_equal(q,np.asarray(_get(b,"q"),float)) or any(not np.isfinite(p).all() or (p<0).any() or not np.isclose(p.sum(),1) for p in (p_sm,p_sa)):
            raise AlignmentError("paired q/probability mismatch")
        scores={}
        for label,p in (("sm",p_sm),("sa",p_sa)):
            with np.errstate(divide="ignore"):
                ce=float(-np.sum(q[q>0]*np.log(p[q>0])))
            scores.update({label+"_ce":ce,label+"_kl":ce-entropy_q,label+"_brier":float(((p-q)**2).sum()),label+"_nonoptimal_mass":float(p[q==0].sum())})
        rows.append({"key": state_key(a), "map_id": int(_get(a, "map_id")), "family": str(_get(a, "family")),
                     "p_sm": p_sm.tolist(), "p_sa": p_sa.tolist(), "q": q.tolist(), "tv": float(.5 * np.abs(p_sa-p_sm).sum()),
                     "sm_argmax": sm_action, "sa_argmax": sa_action, "argmax_disagreement": sm_action != sa_action,
                     "optimality": optimality, "entropy_q": entropy_q, "entropy_sm": entropy_p(p_sm), "entropy_sa": entropy_p(p_sa),
                     "entropy_sm_minus_q": entropy_p(p_sm)-entropy_q, "entropy_sa_minus_q": entropy_p(p_sa)-entropy_q,
                     "entropy_sm_abs_minus_q":abs(entropy_p(p_sm)-entropy_q), "entropy_sa_abs_minus_q":abs(entropy_p(p_sa)-entropy_q),**scores})
    return rows


def _summary(values: Iterable[float]) -> dict[str, float | int | None]:
    a = np.asarray(list(values), float)
    return {"count": int(a.size), "mean": None if not a.size else float(a.mean()), "p50": None if not a.size else float(np.percentile(a, 50)), "p95": None if not a.size else float(np.percentile(a, 95))}


def state_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows: groups[("challenge" if row["family"] == "IIIILLLL" else "routine", row["map_id"])].append(row)
    per_map = {f"{s}:{m}": {"tv": _summary(x["tv"] for x in group), "argmax_disagreement": _summary(float(x["argmax_disagreement"]) for x in group)} for (s, m), group in groups.items()}
    disagreement=[x for x in rows if x["argmax_disagreement"]]
    aggregate=equal_map_summary(rows,("tv","argmax_disagreement","entropy_sm_minus_q","entropy_sa_minus_q","entropy_sm_abs_minus_q","entropy_sa_abs_minus_q")+tuple(a+"_"+m for a in ("sm","sa") for m in ("ce","kl","brier","nonoptimal_mass")))
    return {"raw": list(rows), "overall": {"tv": _summary(x["tv"] for x in rows), "argmax_disagreement": _summary(float(x["argmax_disagreement"]) for x in rows)},
            "optimality_counts_among_disagreements": {name: sum(x["optimality"] == name for x in disagreement) for name in ("both_q_optimal", "sm_only_optimal", "sa_only_optimal", "neither_optimal")}, "per_map": per_map,
            "equal_map":aggregate}


def equal_map_summary(rows: Sequence[Mapping[str, Any]], metrics: Sequence[str]) -> dict[str, Any]:
    """Retain problem rows, then average problem metrics equally within each map.

    The frozen report's routine/challenge mixture is exactly .8/.2 and is NA
    for a metric if either required stratum has no finite map value.
    """
    grouped: dict[tuple[str, int], list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[("challenge" if row["family"] == "IIIILLLL" else "routine", int(row["map_id"]))].append(row)
    maps=[]
    for (stratum, map_id), members in sorted(grouped.items()):
        values={}
        for metric in metrics:
            x=[float(r[metric]) for r in members if r.get(metric) is not None]
            values[metric]=None if not x else float(np.mean(x))
        maps.append({"stratum":stratum,"map_id":map_id,"metrics":values,"rows":list(members)})
    strata={}
    for stratum in ("routine","challenge"):
        selected=[x for x in maps if x["stratum"] == stratum]
        strata[stratum]={metric:(None if not (v:=[x["metrics"][metric] for x in selected if x["metrics"][metric] is not None]) else float(np.mean(v))) for metric in metrics}
    mixture={metric:(None if strata["routine"][metric] is None or strata["challenge"][metric] is None else .8*strata["routine"][metric]+.2*strata["challenge"][metric]) for metric in metrics}
    return {"rows":list(rows),"maps":maps,"strata":strata,"mixture":mixture}


def paired_greedy(sm: Sequence[object], sa: Sequence[object]) -> list[dict[str, Any]]:
    require_exact_order(sm, sa, problem_key)
    out=[]
    for a,b in zip(sm,sa):
        av,bv=bool(_get(a,"valid")),bool(_get(b,"valid"))
        outcome="both_solve" if av and bv else "sm_only" if av else "sa_only" if bv else "neither"
        out.append({"key":problem_key(a),"map_id":int(_get(a,"map_id")),"family":str(_get(a,"family")),"outcome":outcome,"sm_valid":av,"sa_valid":bv})
    return out


def valid_route_sets(sm_attempts: Sequence[Mapping[str, Any]], sa_attempts: Sequence[Mapping[str, Any]], support: frozenset[bytes], signature: Callable[[bytes], bytes]) -> dict[str, Any]:
    """Compare only valid routes; both-empty Jaccard is explicitly NA."""
    valid = lambda xs: {bytes(x["route"]) for x in xs if bool(x["valid"])}
    sm, sa = valid(sm_attempts), valid(sa_attempts)
    sm_sig, sa_sig = {signature(x) for x in sm}, {signature(x) for x in sa}
    union = sm | sa
    raw={"sm":sorted(sm),"sa":sorted(sa),"intersection":sorted(sm&sa),"sm_only":sorted(sm-sa),"sa_only":sorted(sa-sm),"sm_novel":sorted(x for x in sm if signature(x) not in support),"sa_novel":sorted(x for x in sa if signature(x) not in support),"sm_signatures":sorted(sm_sig),"sa_signatures":sorted(sa_sig)}
    normalized={}
    for label,xs,valids in (("sm",sm_attempts,sm),("sa",sa_attempts,sa)):
        if not xs:
            normalized.update({label+"_"+m:None for m in ("Q","pass_at_k","U_valid","U_novel","V_novel")})
            continue
        normalized.update({label+"_Q":sum(bool(x["valid"]) for x in xs)/len(xs),label+"_pass_at_k":float(bool(valids)),label+"_U_valid":len(valids)/len(xs),label+"_U_novel":len(raw[label+"_novel"])/len(xs),label+"_V_novel":sum(bool(x["valid"]) and signature(bytes(x["route"])) not in support for x in xs)/len(xs)})
    return {"raw_sets":raw,**normalized,"sm_valid_routes": len(sm), "sa_valid_routes": len(sa), "sm_only_valid_routes": len(sm-sa), "sa_only_valid_routes": len(sa-sm),
            "jaccard": None if not union else len(sm & sa)/len(union), "jaccard_denominator": len(union),
            "sm_valid_signatures": len(sm_sig), "sa_valid_signatures": len(sa_sig), "sm_only_valid_signatures": len(sm_sig-sa_sig), "sa_only_valid_signatures": len(sa_sig-sm_sig),
            "sm_novel_signatures": len(sm_sig-support), "sa_novel_signatures": len(sa_sig-support)}


def load_matched_support(path: str | Path) -> dict[str, Any]:
    """Bind analysis to the existing frozen 24-triplet support, without rebuilding it."""
    raw=Path(path).read_bytes(); data=json.loads(raw)
    if hashlib.sha256(raw).hexdigest()!="2bcde9c3823a41cc0a0ac7c4383ef1323658ca47b5b7a53336f4f4e2adf9babc":
        raise AlignmentError("frozen matched support hash mismatch")
    if data.get("status") != "MATCHED_SUPPORT_SUFFICIENT" or len(data.get("triplets", ())) != 24:
        raise AlignmentError("frozen matched support is absent or incomplete")
    retained=[x for x in data["triplets"] if not x.get("excluded")]
    if len(retained) != 24 or any(len(x.get("routes", ())) != 3 or len(x.get("states", ())) != 3 for x in retained):
        raise AlignmentError("frozen matched support triplet layout mismatch")
    return {"data":data,"sha256":hashlib.sha256(raw).hexdigest(),"retained":retained}
