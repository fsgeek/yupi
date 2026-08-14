"""Windowed exact inference by RECURSIVE MIXTURE FILTERING (Part II §2b).

The base observer's joint (U, S_U) belief, carried forward one observation
at a time: one anchored component per length-compatible offset, each
holding a normalized state belief, each accumulating its evidence
likelihood; mixture weights are posterior weights (statute §2b — never
frozen at their sampling-prior values).

Component priors are DERIVED (statute §2a): the state marginal μ_U under
the world's own forward law, computed by recursive belief propagation. No
enumeration of trajectories anywhere in this module: this path exists to
be compared bit-for-bit against the independent prefix-marginalized path
summation in `window_enumerator`, which is never imported here. Shared
consumption is the world definition (`kernel.enabled`, `records`,
`interfaces`, `state`) and the law/result structures in `window` — no
posterior-computation logic crosses the firewall.

The per-step update here is deliberately UNNORMALIZED (then renormalized),
unlike `filter.step`: the mixture weights need the per-component evidence
likelihood that normalization discards (precedent: the clock experiment's
`step_unnorm`, with the same documented reason).
"""

from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.state import initial_state
from yupi.window import Belief, WindowLaw, WindowPosterior


class ZeroProbabilityWindow(Exception):
    """Raised when a window has probability zero under the law."""


def state_marginal_at(cfg: WorldConfig, programs, t: int) -> Belief:
    """μ_t: the exact unconditional state distribution after t ticks,
    by forward belief propagation from the known reset state."""
    belief: Belief = {initial_state(cfg): Fraction(1)}
    for _ in range(t):
        nxt: Belief = {}
        for s, mass in belief.items():
            for tr, p in enabled(s, cfg, programs):
                nxt[tr.next_state] = nxt.get(tr.next_state, Fraction(0)) + mass * p
        belief = nxt
    return belief


def _step_unnorm(
    belief: Belief, obs: Record, rung: str, cfg: WorldConfig, programs
) -> Tuple[Belief, Fraction]:
    """One Bayes update without normalization; returns (belief', likelihood)."""
    out: Belief = {}
    for s, mass in belief.items():
        if mass == 0:
            continue
        for tr, p in enabled(s, cfg, programs):
            if project(record_of(tr), rung) != obs:
                continue
            out[tr.next_state] = out.get(tr.next_state, Fraction(0)) + mass * p
    total = sum(out.values(), Fraction(0))
    return out, total


def filter_window(
    cfg: WorldConfig, programs, law: WindowLaw, obs_seq: List[Record], rung: str
) -> WindowPosterior:
    """Exact posterior over (U, S_T) for an observed window, offset-unanchored.

    Length conditioning first (the compatible-endpoint rule), then per-step
    mixture filtering: each component's belief updates by Bayes, its weight
    accumulates the evidence likelihood; weights normalize across surviving
    components at the end (equivalent to per-step renormalization, exact
    either way).
    """
    compatible = law.compatible_endpoints(len(obs_seq))
    if not compatible:
        raise ZeroProbabilityWindow(
            f"no endpoint on the grid yields a window of {len(obs_seq)} records"
        )

    # endpoint prior is uniform on the grid, so after conditioning on
    # length every compatible component starts with equal unnormalized
    # weight; the constant cancels in the final normalization.
    components: Dict[int, Tuple[Fraction, Belief]] = {}
    for _, u in compatible:
        prior_belief = state_marginal_at(cfg, programs, u)
        weight = Fraction(1)
        belief = prior_belief
        dead = False
        for obs in obs_seq:
            belief, lik = _step_unnorm(belief, obs, rung, cfg, programs)
            if lik == 0:
                dead = True
                break
            weight *= lik
            belief = {s: m / lik for s, m in belief.items()}
        if not dead:
            components[u] = (weight, belief)

    total = sum((w for w, _ in components.values()), Fraction(0))
    if total == 0:
        raise ZeroProbabilityWindow(
            "window has probability zero under every compatible offset"
        )
    return WindowPosterior(
        components={u: (w / total, b) for u, (w, b) in components.items()}
    )
