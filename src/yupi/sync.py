"""Synchronization horizon: the truncation-conditional mean (Part II §6,
semantics v0.2.5; formula corrected by proposal v0.2.7.1 Clause 2 for a
rung that is not injective from reset).

    E[H | U > 0] = (H_law − H_{U=0}) / Pr(U > 0)

H_law is the law-mass mean of a posterior entropy over all windows; H_{U=0}
is the same sum restricted to windows generated at endpoints T ≤ L (the
reset is in view, U = 0); Pr(U > 0) is the law's mass on the other
endpoints. For r1–r4, H_{U=0} = 0 by full-context injectivity of the
reset-anchored trace, and the expression reduces to the v0.2.5 closed form
T_ep/(T_ep − L) · H_law used in `c1-sync-sweep-v0.1.md`. For r0 it does
not. Built 2026-09-04, test-first (`tests/test_sync_conditional.py`).
"""
from fractions import Fraction
from typing import Callable, Dict

from yupi.window import WindowLaw


def conditional_from_aggregate(agg, law: WindowLaw, entropy: Callable) -> Dict:
    """From a window-law aggregate {(reset, window): {state: mass}} and an
    entropy functional on a normalized belief. `reset` is True iff U = 0."""
    H_law = 0.0
    H_U0 = 0.0
    mass_U0 = Fraction(0)
    for (reset, _), joint in agg.items():
        mass = sum(joint.values(), Fraction(0))
        h = float(mass) * entropy({s: m / mass for s, m in joint.items()})
        H_law += h
        if reset:
            H_U0 += h
            mass_U0 += mass
    P_U_pos = 1 - mass_U0
    return dict(H_law=H_law, H_U0=H_U0, P_U_pos=P_U_pos,
                E_H_given_U_pos=(H_law - H_U0) / float(P_U_pos) if P_U_pos else None)


def conditional_from_by_endpoint(by_endpoint: Dict[str, Dict], law: WindowLaw, quantity: str) -> Dict:
    """From a ceilings artifact's `by_endpoint` block ({T: {U, mean_state_
    entropy_bits, queries: {q: mean}}}); the endpoint prior is uniform on
    the law's grid, so each endpoint's mean is weighted by 1/|endpoints|."""
    Ts = sorted(int(T) for T in by_endpoint)
    w = Fraction(1, len(Ts))
    H_law = 0.0
    H_U0 = 0.0
    mass_U0 = Fraction(0)
    for T in Ts:
        e = by_endpoint[str(T)]
        v = e[quantity] if quantity in e else e["queries"][quantity]
        h = float(w) * v
        H_law += h
        if e["U"] == 0:
            H_U0 += h
            mass_U0 += w
    P_U_pos = 1 - mass_U0
    return dict(H_law=H_law, H_U0=H_U0, P_U_pos=P_U_pos,
                E_H_given_U_pos=(H_law - H_U0) / float(P_U_pos) if P_U_pos else None)
