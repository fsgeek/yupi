"""The window census: from per-window excesses (the evaluator's `on_window`
rows) to the distribution the aggregate mean hides — quantiles, the share of
the total carried by the top fraction of windows, per-class aggregates, and
the worst windows. Pure arithmetic; imports nothing from the exact side.

A row is {i, key, structural, naming, by_field}; `key` is any hashable
class label (the evaluator's ceiling-table key). Per-window values are
realized-record estimates and may be negative; a class mean over its windows
is an unbiased estimate of that class's KL, a single window is not.
"""
from __future__ import annotations

import math
from typing import Dict, List, Sequence

import numpy as np

FIELDS = ("kind", "actor", "obj", "related", "lineage")
TAIL = (0.01, 0.05, 0.10)
QUANTILES = (0.5, 0.9, 0.99, 0.999)


def summarize(rows: Sequence[dict], top: int = 20) -> dict:
    n = len(rows)
    xs = np.array([r["structural"] for r in rows], dtype=np.float64)
    total = float(xs.sum())
    order = np.argsort(-xs, kind="stable")
    out: Dict = dict(n=n, mean=float(xs.mean()), sd=float(xs.std(ddof=1)) if n > 1 else 0.0,
                     total=total, max=float(xs.max()), min=float(xs.min()),
                     negative_share=float(np.mean(xs < 0)),
                     quantiles={str(q): float(np.quantile(xs, q)) for q in QUANTILES},
                     tail_share={str(p): float(xs[order[:max(1, math.ceil(p * n))]].sum() / total) if total else None
                                 for p in TAIL})
    by_class: Dict = {}
    for r, x in zip(rows, xs):
        c = by_class.setdefault(r["key"], dict(key=r["key"], xs=[], fields={f: 0.0 for f in FIELDS}))
        c["xs"].append(float(x))
        for f in FIELDS:
            c["fields"][f] += float(r["by_field"][f])
    classes = []
    for c in by_class.values():
        a = np.array(c["xs"])
        m = len(a)
        classes.append(dict(key=c["key"], n=m, mean=float(a.mean()),
                            se=float(a.std(ddof=1) / math.sqrt(m)) if m > 1 else 0.0,
                            sum=float(a.sum()), share=float(a.sum() / total) if total else None,
                            by_field={f: c["fields"][f] / m for f in FIELDS}))
    classes.sort(key=lambda c: -c["sum"])
    out["n_classes"] = len(classes)
    out["classes"] = classes[:top]
    out["worst"] = [dict(rows[j], structural=float(xs[j])) for j in order[:top]]
    return out


def variance_split(rows: Sequence[dict]) -> dict:
    """One-way random-effects split of the per-window variance into a class
    component and a within-class component (unequal class sizes; singleton
    classes count toward the between sum and contribute no within degrees of
    freedom). within = MS_within; between = max(0, (MS_between − MS_within) / n0)
    with n0 = (n − Σ n_c² / n) / (C − 1); between_share = between / (between + within).
    Within-class spread is the realized-record sampling variance (plus any
    dependence on the surface names inside a class); between is what the
    class explains."""
    xs = np.array([r["structural"] for r in rows], dtype=np.float64)
    n = len(xs)
    by: Dict = {}
    for r, x in zip(rows, xs):
        by.setdefault(r["key"], []).append(float(x))
    C = len(by)
    mean = float(xs.mean())
    ss_within = sum(float(np.sum((np.array(v) - np.mean(v)) ** 2)) for v in by.values())
    ss_between = sum(len(v) * (float(np.mean(v)) - mean) ** 2 for v in by.values())
    ms_within = ss_within / (n - C) if n > C else float("nan")
    ms_between = ss_between / (C - 1) if C > 1 else float("nan")
    n0 = (n - sum(len(v) ** 2 for v in by.values()) / n) / (C - 1) if C > 1 else float("nan")
    between = max(0.0, (ms_between - ms_within) / n0) if C > 1 and n > C else float("nan")
    return dict(n=n, n_classes=C, n_classes_multi=sum(1 for v in by.values() if len(v) >= 2),
                total=float(xs.var(ddof=1)), within=ms_within, between=between,
                between_share=between / (between + ms_within) if (between + ms_within) > 0 else None)


def attribute(rows: Sequence[dict], features: Sequence[dict]) -> dict:
    """Per feature name and value (stringified): n, mean, se, share of the
    total, by_field means. A signed decomposition of the estimator's sum by
    outcome categories: shares over a feature sum to 1, but a value's mean
    is not a KL and may be negative (it conditions on the realized record)."""
    xs = np.array([r["structural"] for r in rows], dtype=np.float64)
    total = float(xs.sum())
    acc: Dict = {}
    for r, x, f in zip(rows, xs, features):
        for name, val in f.items():
            c = acc.setdefault(name, {}).setdefault(str(val), dict(xs=[], fields={}))
            c["xs"].append(float(x))
            for fld, v in r["by_field"].items():
                c["fields"][fld] = c["fields"].get(fld, 0.0) + float(v)
    out: Dict = {}
    for name, vals in acc.items():
        out[name] = {}
        for val, c in vals.items():
            a = np.array(c["xs"])
            m = len(a)
            out[name][val] = dict(n=m, frac=m / len(rows), mean=float(a.mean()),
                                  se=float(a.std(ddof=1) / math.sqrt(m)) if m > 1 else 0.0,
                                  share=float(a.sum() / total) if total else None,
                                  by_field={fld: s / m for fld, s in c["fields"].items()})
    return out


def record_features(prefix, nxt) -> dict:
    """Outcome features of the predicted record given the k seen: its kind,
    whether its actor already acted in the prefix ("bound") or not ("fresh"),
    the number of distinct actors in the prefix, and the joint label."""
    seen = {r.actor for r in prefix if r.actor not in (None, "MASKED")}
    actor = "bound" if nxt.actor in seen else "fresh"
    return dict(kind=nxt.kind, actor=actor, nthreads=len(seen), kind_actor=f"{nxt.kind}/{actor}")


def contrast(cells: Sequence[dict], high: Sequence[int], low: Sequence[int]) -> dict:
    """Seed-group contrast within one cell: per predicted kind, frac × (pooled
    mean over `high` seeds − pooled mean over `low` seeds); the contributions
    sum to the gap between the groups' mean totals. `cells` are the cuts
    script's per-seed entries (seed, mean, attribution.kind)."""
    hi = [c for c in cells if c["seed"] in set(high)]
    lo = [c for c in cells if c["seed"] in set(low)]
    if not hi or not lo:
        raise ValueError("both seed groups must be non-empty")
    kinds = sorted({k for c in hi + lo for k in c["attribution"]["kind"]})
    def pooled(group, k, key):
        vals = [c["attribution"]["kind"][k][key] for c in group if k in c["attribution"]["kind"]]
        return sum(vals) / len(vals) if vals else None
    by_kind = {}
    for k in kinds:
        fh, fl = pooled(hi, k, "frac"), pooled(lo, k, "frac")
        mh, ml = pooled(hi, k, "mean"), pooled(lo, k, "mean")
        if None in (fh, fl, mh, ml):
            continue
        by_kind[k] = fh * mh - fl * ml
    gap = sum(c["mean"] for c in hi) / len(hi) - sum(c["mean"] for c in lo) / len(lo)
    return dict(high=list(high), low=list(low), gap=gap, high_mean=sum(c["mean"] for c in hi) / len(hi),
                low_mean=sum(c["mean"] for c in lo) / len(lo), by_kind=by_kind)
