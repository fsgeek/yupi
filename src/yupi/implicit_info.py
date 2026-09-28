"""Implicit information ι_m and the exact order-m ceiling over a pattern table
(docs/implicit-information-design-v0.1.md).

For a prefix class c with law mass m_c and exact next-record law P*(· | c), the
suffix view re-keys the last m records by Π_all; the next record is pushed
through the suffix binding (an entity bound only before the suffix becomes
fresh, as an m-record observer sees it), Q_c = φ_c # P*(· | c). The order-m
ceiling P*_m(· | s) is the law-mass mixture of Q_c over classes sharing the
suffix s, and ι_m(c) = KL(Q_c ‖ P*_m(· | s(c))) in bits — a function of the
prefix only. Mixtures are exact (Fractions); logarithms are float.
"""
from __future__ import annotations

from fractions import Fraction
from math import log2
from typing import Dict, Tuple

from yupi.naming import extend_binding
from yupi.records import Record


def suffix_view(pw: tuple, m: int) -> Tuple[tuple, tuple]:
    """(the last m records re-keyed by Π_all, the suffix binding)."""
    binding = ((), (), (), ())
    out = []
    for r in pw[-m:] if m else ():
        pr, binding = extend_binding(binding, r)
        out.append(pr)
    return tuple(out), binding


def _h(law: Dict[Record, Fraction]) -> float:
    return -sum(float(p) * log2(float(p)) for p in law.values() if p > 0)


def _kl(q: Dict[Record, Fraction], p: Dict[Record, Fraction]) -> float:
    return sum(float(a) * (log2(float(a)) - log2(float(p[r]))) for r, a in q.items() if a > 0)


def implicit_info(table, m: int, threshold: float = 0.01, keep_laws: bool = False, target=None) -> dict:
    """{per_class: {key: ι_m}, H_star, H_bar, H_m, mean_iota_kl, mean_iota_ent,
    identity_diff, n_classes, n_groups, mass, mass_frac_iota_gt}; means are
    law-mass means normalized by the table's total mass. `target`, if given,
    maps each (suffix-keyed) next record to the quantity predicted — e.g.
    `lambda r: r.kind` for the naming-free common target; H_star is then the
    full-prefix entropy of that target."""
    groups: Dict[tuple, list] = {}
    laws: Dict[tuple, Dict[Record, Fraction]] = {}
    total = Fraction(0)
    h_star = 0.0
    for key, (mass, star) in table.items():
        _, pw = key
        s, beta = suffix_view(pw, m)
        q: Dict[Record, Fraction] = {}
        full: Dict = {}
        for rho, p in star.items():
            r, _ = extend_binding(beta, rho)
            if target is not None:
                full[target(rho)] = full.get(target(rho), Fraction(0)) + p
                r = target(r)
            q[r] = q.get(r, Fraction(0)) + p
        laws[key] = q
        groups.setdefault(s, []).append(key)
        total += mass
        h_star += float(mass) * _h(full if target is not None else star)
    per_class: Dict[tuple, float] = {}
    h_bar = h_m = mean_kl = gt = 0.0
    for s, keys in groups.items():
        gm = sum((table[k][0] for k in keys), Fraction(0))
        mix: Dict[Record, Fraction] = {}
        for k in keys:
            w = table[k][0] / gm
            for r, p in laws[k].items():
                mix[r] = mix.get(r, Fraction(0)) + w * p
        h_m += float(gm) * _h(mix)
        for k in keys:
            mk = float(table[k][0])
            iota = _kl(laws[k], mix)
            per_class[k] = iota
            mean_kl += mk * iota
            h_bar += mk * _h(laws[k])
            if iota > threshold:
                gt += mk
    t = float(total)
    out = {"per_class": per_class, "n_classes": len(table), "n_groups": len(groups), "mass": t,
           "H_star": h_star / t, "H_bar": h_bar / t, "H_m": h_m / t,
           "mean_iota_kl": mean_kl / t, "mean_iota_ent": (h_m - h_bar) / t,
           "mass_frac_iota_gt": gt / t, "threshold": threshold}
    out["identity_diff"] = out["mean_iota_kl"] - out["mean_iota_ent"]
    if keep_laws:
        out["laws"] = laws
    return out
