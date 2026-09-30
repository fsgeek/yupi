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


def implicit_info(table, m: int, threshold: float = 0.01, keep_laws: bool = False, target=None,
                  keep_mix: bool = False) -> dict:
    """{per_class: {key: ι_m}, H_star, H_bar, H_m, mean_iota_kl, mean_iota_ent,
    identity_diff, n_classes, n_groups, mass, mass_frac_iota_gt}; means are
    law-mass means normalized by the table's total mass. `target`, if given,
    maps each (suffix-keyed) next record to the quantity predicted — e.g.
    `lambda r: r.kind` for the naming-free common target; H_star is then the
    full-prefix entropy of that target. `keep_mix` adds suffix_of {key: s}
    and mixtures {s: exact P*_m(· | s)} (relay design v0.1 §4: an exact
    Δι = 0 between two tables is decided on the mixtures, not on floats)."""
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
    mixtures = {}
    for s, keys in groups.items():
        gm = sum((table[k][0] for k in keys), Fraction(0))
        mix: Dict[Record, Fraction] = {}
        for k in keys:
            w = table[k][0] / gm
            for r, p in laws[k].items():
                mix[r] = mix.get(r, Fraction(0)) + w * p
        h_m += float(gm) * _h(mix)
        if keep_mix:
            mixtures[s] = mix
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
    if keep_mix:
        out["mixtures"] = mixtures
        out["suffix_of"] = {k: s for s, keys in groups.items() for k in keys}
    return out


def kind_actor(r: Record) -> tuple:
    """The (KIND, ACTOR) target of docs/actor-long-lag-design-prereg-v0.1.md. Applied, like
    every target, to the next record already pushed through the suffix binding, so the actor
    is in suffix-coarsened pattern names (an actor seen only before the suffix reads fresh)."""
    return (r.kind, r.actor)


def _kind_marginal(law: Dict[tuple, Fraction]) -> Dict[str, Fraction]:
    out: Dict[str, Fraction] = {}
    for (k, _), p in law.items():
        out[k] = out.get(k, Fraction(0)) + p
    return out


def iota_actor_given_kind(q: Dict[tuple, Fraction], p: Dict[tuple, Fraction]) -> float:
    """Σ_k q(k) KL(q(A | k) ‖ p(A | k)) in bits, for laws over (kind, actor): the per-class
    chain-rule term ι_{(K,A)} − ι_K computed directly. Each log ratio
    q(a | k) / p(a | k) = q(k, a) p(k) / (q(k) p(k, a)) is formed exactly (Fractions)."""
    qk, pk = _kind_marginal(q), _kind_marginal(p)
    return sum(float(a) * log2(float(a * pk[ka[0]] / (qk[ka[0]] * p[ka])))
               for ka, a in q.items() if a > 0)


def h_actor_given_kind(star: Dict[Record, Fraction]) -> float:
    """The class's exact H(ACTOR | KIND) in bits under P*(· | c) in the class's own pattern
    names (the analogue of H_kind): Σ p(k, a) log2(p(k) / p(k, a)), ratios exact."""
    joint: Dict[tuple, Fraction] = {}
    for r, p in star.items():
        joint[(r.kind, r.actor)] = joint.get((r.kind, r.actor), Fraction(0)) + p
    pk = _kind_marginal(joint)
    return sum(float(p) * log2(float(pk[ka[0]] / p)) for ka, p in joint.items() if p > 0)


def weighted_quantiles(pairs, qs):
    """Law-mass quantiles of (value, mass) pairs: for each q, the smallest value
    v whose cumulative mass (values ascending) reaches q × total. Exact in the
    masses (Fractions); q is compared against the exact cumulative share."""
    items = sorted(pairs, key=lambda vm: vm[0])
    total = sum((m for _, m in items), Fraction(0))
    order = sorted(range(len(qs)), key=lambda i: qs[i])
    out = [items[-1][0]] * len(qs)
    cum, j = Fraction(0), 0
    for v, m in items:
        cum += m
        while j < len(order) and cum >= Fraction(qs[order[j]]) * total:
            out[order[j]] = v
            j += 1
        if j == len(order):
            break
    return out
