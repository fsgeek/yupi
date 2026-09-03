"""Prediction checker — flatten committed artifacts into cells; evaluate
pre-stated predictions against every matching cell.

Owed since Aug 22 (promised twice); required by the D8 attribution prereg
§8 before any prediction is scored. Purpose: make "does something already
committed know the answer?" a command rather than a recollection — the
week's four reversals were generalizations that a lookup would have caught.

Firewall: this module reads JSON only. It imports no world, filter, or
enumerator code and computes no posterior.

Cell schema (one flat dict per number):
    artifact, family, tag (raw|corrected|heldout|None), superseded (bool),
    T_ep, L, B, eps (str fraction or None), rung, discipline, W, T (endpoint
    or None), quantity (dotted path), value (number), plus family extras
    (r_obs, r_pred, target).
Selectors: scalar (equality), list (membership), dict with le/lt/ge/gt,
    the string "T_ep" for L (full context), and superseded="any" to include
    superseded cells (default: excluded).
Outcomes: PASS (all matched cells satisfy), FAIL (some do not), NO_CHECK
    (no committed cell matches — reported, never treated as a pass).
"""
import glob
import json
import os
import re
from typing import Any, Dict, List, Tuple

Cell = Dict[str, Any]

# Recognized non-measurement files (meta, cost pricing, derived scores and
# comparisons of other artifacts): skipped on purpose and by name, and
# reported by the CLI as "recognized, not flattened" — distinct from unknown.
NON_MEASUREMENT_PREFIXES = (
    "artifact-status", "held-out-selection-e-draw", "d4-pricing", "c1-budget",
    "c1-heldout-tier1-score", "c1-sweep-rerun-comparison",
    "d8-attribution-benchmark", "d8-attribution-grid-freeze", "d8-attribution-predictions",
    "d8-bucket-census",   # structural census of order-sensitive bucket kinds (no result quantity)
)

# The direct-handoff kernel erratum was fixed 2026-08-20 (commit d69fa87);
# every number produced before that date is buggy-kernel (tick >= 11 affected).
KERNEL_FIX_DATE = "2026-08-20"

_TAG_RE = re.compile(r"-(raw|corrected|heldout|F[0-9][^-]*-heldout)(?=-|$)")
_DATE_RE = re.compile(r"-(20\d\d-\d\d-\d\d)(-[A-Za-z0-9.]+)*\.json$")


def _tag(name: str):
    m = _TAG_RE.search(name)
    if not m:
        return None
    t = m.group(1)
    return "heldout" if t.endswith("heldout") else t


def _date(name: str):
    m = _DATE_RE.search(name)
    return m.group(1) if m else None


def _stem(name: str) -> str:
    """Filename with date, variant suffix, and tag removed."""
    stem = _DATE_RE.sub("", name) if _DATE_RE.search(name) else name[:-5]
    return _TAG_RE.sub("", stem)


def _family(name: str) -> str:
    stem = _stem(name)
    stem = re.sub(r"-W\d+$", "", stem)
    stem = re.sub(r"(-\d+)+$", "", stem)          # strip law numbers
    stem = re.sub(r"-h\d+$", "", stem)            # c1-multiwaiter-census-h14
    stem = re.sub(r"-v\d+$", "", stem)            # d10-lineage-search-v2
    stem = re.sub(r"-v\d+(?:\.\d+)+$", "", stem)   # d8-attribution-c1-v0.3 (grid-rule version; a distinct artifact, not a sibling)
    stem = re.sub(r"-(c0a|c0b|c0c|c1)$", "", stem)  # d8-attribution-c0b
    return stem


def _law_key(name: str) -> str:
    """Identity of an artifact modulo tag/date/variant — raw and corrected
    siblings share it."""
    return _stem(name)


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _flat(prefix: str, obj: Any, out: Dict[str, float]):
    if isinstance(obj, dict):
        for k, v in obj.items():
            _flat(f"{prefix}.{k}" if prefix else str(k), v, out)
    elif _num(obj):
        out[prefix] = obj


def _base(name, family, law, **kw) -> Cell:
    d = _date(name)
    c = dict(artifact=name, family=family, tag=_tag(name), superseded=False,
             kernel=("buggy" if d and d < KERNEL_FIX_DATE else "fixed"),
             T_ep=law.get("T_ep"), L=law.get("L"), B=law.get("B"),
             eps=None, rung=None, discipline=None, W=None, T=None)
    c.update(kw)
    return c


def _rows_family(name, family, d, skip=(), row_extra=lambda r: {}):
    law = d.get("law", {})
    cells = []
    for r in d["rows"]:
        meta = dict(eps=r.get("eps"), rung=r.get("rung"), W=d.get("W"))
        meta.update(row_extra(r))
        for k, v in r.items():
            if k in ("eps", "rung") or k in skip:
                continue
            if k == "by_endpoint":
                for T, sub in v.items():
                    flat = {}
                    _flat("", sub, flat)
                    for q, val in flat.items():
                        if q == "U":
                            continue
                        cells.append(_base(name, family, law, T=int(T),
                                           quantity=f"by_endpoint.{q}", value=val, **meta))
                continue
            flat = {}
            _flat("" if k == "queries" else k, v, flat)
            for q, val in flat.items():
                cells.append(_base(name, family, law, quantity=q, value=val, **meta))
    return cells


def _eps_pair_tree(name, family, d, top):
    """{eps: {pair: {...numbers or {query: {...}}}}} → cells with eps, pair."""
    cells = []
    for eps, pairs in d[top].items():
        for pair, block in pairs.items():
            flat = {}
            _flat("", block, flat)
            for q, val in flat.items():
                cells.append(_base(name, family, d["law"], eps=eps, pair=pair, quantity=q, value=val))
    return cells


def _delta_sweep(name, family, d):
    cells = []
    for lawblock in d["laws"]:
        for c in lawblock["cells"]:
            for k, v in c.items():
                if _num(v):
                    cells.append(_base(name, family, lawblock["law"], eps=c["eps"], pair=c["pair"],
                                       W=c.get("W"), quantity=k, value=v))
    return cells


def _multiwaiter(name, family, d):
    cells = []
    for eps, block in d["results"].items():
        flat = {}
        _flat("", block, flat)
        for q, val in flat.items():
            cells.append(_base(name, family, dict(T_ep=d["horizon"]), eps=eps, quantity=q, value=val))
    return cells


def _sync_sweep(name, family, d):
    cells = []
    for c in d["curves"]:
        for q, series in c["curves"].items():
            for L, val in zip(d["Ls"], series):
                if val is None:
                    continue
                cells.append(_base(name, family, dict(T_ep=d["T_ep"], L=L, B=d["B"]),
                                   eps=c["eps"], rung=c["rung"], quantity=q, value=val))
    return cells


def _d10(name, family, d):
    cells = []
    for law in d["laws"]:
        lk = dict(T_ep=law["T_ep"], L=law["L"], B=d["B"])
        for k, v in law.items():
            if _num(v) and k not in ("T_ep", "L"):
                cells.append(_base(name, family, lk, quantity=k, value=v))
        for disc, block in law["disciplines"].items():
            flat = {}
            _flat("", block, flat)
            for q, val in flat.items():
                cells.append(_base(name, family, lk, discipline=disc, quantity=q, value=val))
    return cells


ADAPTERS = {
    "c1-query-ceilings": lambda n, f, d: _rows_family(n, f, d),
    "c1-q4-ceilings": lambda n, f, d: _rows_family(n, f, d),
    "c1-predictive-targets": lambda n, f, d: _rows_family(n, f, d),
    "c1-offset-vs-state": lambda n, f, d: _rows_family(n, f, d),
    "c1-divergent-grid": lambda n, f, d: _rows_family(
        n, f, d, skip=("r_obs", "r_pred"), row_extra=lambda r: dict(r_obs=r["r_obs"], r_pred=r["r_pred"])),
    "c1-tv-sweep": lambda n, f, d: _rows_family(
        n, f, d, skip=("cdf_tv_pnext", "cdf_tv_tau_max", "joint_bins", "surface", "surface_by_tau")),
    "c1-divergent-resolution": lambda n, f, d: _rows_family(n, f, d),
    "c1-support": lambda n, f, d: _rows_family(n, f, d),
    "c1-support-exact": lambda n, f, d: _rows_family(n, f, d),
    "c1-rung-gaps": lambda n, f, d: _eps_pair_tree(n, f, d, "gaps"),
    "c1-query-gap-decomposition": lambda n, f, d: _eps_pair_tree(n, f, d, "decomposition"),
    "c1-delta-sweep": _delta_sweep,
    "c1-multiwaiter-census": _multiwaiter,
    "c1-sync-sweep": _sync_sweep,
    "d10-lineage-search": _d10,
    "d8-attribution": lambda n, f, d: _d8(n, f, d),
    # witness-11 search (2026-09-03): one row per (eps, adjacent pair); scalar
    # counts/masses/max-TV become quantities, the per-candidate dumps are not
    # quantities. W is a [primary, secondary] list on this family, so it is
    # not a selector here.
    "w11-predictive-rung-search": lambda n, f, d: _rows_family(
        n, f, d, skip=("pair", "candidates"), row_extra=lambda r: dict(pair=r["pair"], W=None)),
    # residual-ambiguity census (2026-09-03): per-ε scalars only; the
    # per-signature table is not a quantity.
    "c1-residual-ambiguity-census": lambda n, f, d: _rows_family(n, f, d, skip=("signatures",)),
    # r0 (kind-only) ladder census (2026-09-03, exploratory, enumerator side,
    # ungated): per-(ε, rung) scalars; the r0 residual/pricing block is not a
    # quantity.
    "r0-ladder-census": lambda n, f, d: _rows_family(n, f, d, skip=("support_hist",)),
}


_D8_META = {"world", "discipline", "eps", "T_ep", "L", "B", "rung", "gates", "cost", "wall_s",
            "prereg", "prevalence_exact"}


def _d8(name, family, d):
    """d8-attribution-<world>-<date>.json: {prereg, freeze, cells: [...]}. Every
    numeric field of a cell becomes a quantity; per_endpoint_* fan out on T;
    gate-failed cells contribute only gates.all_passed = 0."""
    cells = []
    for c in d["cells"]:
        law = dict(T_ep=c["T_ep"], L=c["L"], B=c["B"])
        meta = dict(discipline=c["discipline"], eps=c["eps"], rung=c["rung"], world=c["world"])
        cells.append(_base(name, family, law, quantity="gates.all_passed",
                           value=int(bool(c["gates"].get("all_passed"))), **meta))
        if not c["gates"].get("all_passed"):
            continue
        for k, v in c.items():
            if k in _D8_META:
                continue
            if isinstance(v, bool):
                v = int(v)                              # collapsed_* flags as 0/1 quantities
            if k.startswith("per_endpoint_"):
                for T, val in v.items():
                    cells.append(_base(name, family, law, T=int(T), quantity=k, value=val, **meta))
                continue
            flat = {}
            _flat(k, v, flat)
            for q, val in flat.items():
                cells.append(_base(name, family, law, quantity=q, value=val, **meta))
    return cells


def load_artifacts(docs_dir: str) -> Tuple[List[Cell], List[str]]:
    """All cells from every *.json in docs_dir, plus the list of files whose
    family has no adapter (reported by the CLI; never silently skipped).
    Recognized non-measurement files are skipped by name (see
    NON_MEASUREMENT_PREFIXES); a raw/untagged artifact with a corrected
    sibling (same law key) is flagged superseded."""
    cells: List[Cell] = []
    unknown: List[str] = []
    names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(docs_dir, "*.json")))
    corrected_keys = {_law_key(n) for n in names if _tag(n) == "corrected"}
    for n in names:
        if n.startswith(NON_MEASUREMENT_PREFIXES):
            continue
        fam = _family(n)
        if fam not in ADAPTERS:
            unknown.append(n)
            continue
        with open(os.path.join(docs_dir, n)) as fh:
            d = json.load(fh)
        new = ADAPTERS[fam](n, fam, d)
        if _tag(n) in (None, "raw") and _law_key(n) in corrected_keys:
            for c in new:
                c["superseded"] = True
        cells.extend(new)
    return cells, unknown


def _sel_ok(cell: Cell, key: str, want) -> bool:
    have = cell.get(key)
    if key == "L" and want == "T_ep":
        return have is not None and have == cell.get("T_ep")
    if isinstance(want, dict):
        if have is None:
            return False
        return all((op == "le" and have <= v) or (op == "lt" and have < v)
                   or (op == "ge" and have >= v) or (op == "gt" and have > v)
                   for op, v in want.items())
    if isinstance(want, list):
        return have in want
    return have == want


def match(cells: List[Cell], select: Dict[str, Any]) -> List[Cell]:
    sup = select.get("superseded", False)
    out = []
    for c in cells:
        if sup != "any" and c["superseded"] != sup:
            continue
        if all(_sel_ok(c, k, v) for k, v in select.items() if k != "superseded"):
            out.append(c)
    return out


_REL = {
    "==": lambda a, b, t: abs(a - b) <= t,
    "!=": lambda a, b, t: abs(a - b) > t,
    ">": lambda a, b, t: a > b + t,
    "<": lambda a, b, t: a < b - t,
    ">=": lambda a, b, t: a >= b - t,
    "<=": lambda a, b, t: a <= b + t,
}


def evaluate(pred: Dict[str, Any], cells: List[Cell]) -> Dict[str, Any]:
    """quantifier "all" (default): every matched cell must satisfy the
    relation — the form of a per-cell prediction. "any": at least one matched
    cell must — the form of an existence prediction (a witness class is
    non-empty somewhere in the selection); its failures list is then the
    whole selection, since no cell served as the witness."""
    hits = match(cells, pred["select"])
    rel, val, tol = _REL[pred["relation"]], pred["value"], pred.get("tol", 0)
    quant = pred.get("quantifier", "all")
    if quant not in ("all", "any"):
        raise ValueError(f"quantifier must be all|any, got {quant!r}")
    fails = [c for c in hits if not rel(c["value"], val, tol)]
    if quant == "any":
        fails = [] if len(fails) < len(hits) else hits
    status = "NO_CHECK" if not hits else ("FAIL" if fails else "PASS")
    return dict(id=pred["id"], status=status, quantifier=quant, n_matched=len(hits),
                n_fail=len(fails), failures=fails, relation=pred["relation"], value=val)
