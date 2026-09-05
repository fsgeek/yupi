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


# Exact cross-call cache of the forward marginals (2026-09-04): μ_t is a pure
# function of (cfg, programs, t) and the filter recomputed it from reset for
# every compatible offset of every window — 14.7 of 17 s per window at
# (40,4,2) on the looping C1′ (profile in the commit). The cache stores the
# whole prefix μ_0 … μ_T per (cfg, programs) and extends it incrementally;
# a lookup below the reached T costs nothing. Arithmetic unchanged, exact
# rationals, copies returned (tests/test_marginal_cache.py).
_MARGINALS: Dict[Tuple[WorldConfig, object], List[Belief]] = {}


def marginal_cache_clear() -> None:
    _MARGINALS.clear()


# Second exact memo (2026-09-04): the first Bayes step of a component runs
# the kernel over the whole marginal μ_u and depends only on
# (cfg, programs, rung, u, first record). Unnormalized belief and likelihood
# are stored; every later step is unchanged (tests/test_first_step_cache.py).
_FIRST_STEP: Dict[Tuple, Tuple[Belief, Fraction]] = {}


def first_step_cache_clear() -> None:
    _FIRST_STEP.clear()


def state_marginal_at(cfg: WorldConfig, programs, t: int) -> Belief:
    """μ_t: the exact unconditional state distribution after t ticks,
    by forward belief propagation from the known reset state (cached
    across calls per (cfg, programs); see `_MARGINALS`)."""
    key = (cfg, programs)
    seq = _MARGINALS.get(key)
    if seq is None:
        seq = [{initial_state(cfg): Fraction(1)}]
        _MARGINALS[key] = seq
    while len(seq) <= t:
        belief = seq[-1]
        nxt: Belief = {}
        for s, mass in belief.items():
            for tr, p in enabled(s, cfg, programs):
                nxt[tr.next_state] = nxt.get(tr.next_state, Fraction(0)) + mass * p
        seq.append(nxt)
    return dict(seq[t])


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


def _components_unnorm(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    obs_seq: List[Record],
    rung: str,
    reset_observed: bool,
    stats: dict = None,
) -> Dict[int, Tuple[Fraction, Belief]]:
    """Per-offset (unnormalized evidence weight P(window | U = u), normalized
    belief) for every surviving compatible component — offset-unanchored.

    Length and RESET conditioning first (the compatible-endpoint rule),
    then per-step mixture filtering: each component's belief updates by
    Bayes, its weight accumulates the evidence likelihood; weights
    normalize across surviving components at the end (equivalent to
    per-step renormalization, exact either way). `reset_observed` is
    required, not defaulted: the caller must say whether the window
    reached episode start, because the statute makes that observable.
    """
    compatible = law.compatible_endpoints(len(obs_seq), reset_observed)
    if not compatible:
        raise ZeroProbabilityWindow(
            f"no endpoint on the grid yields a window of {len(obs_seq)} records"
        )

    # endpoint prior is uniform on the grid, so after conditioning on
    # length every compatible component starts with equal unnormalized
    # weight; the constant cancels in the final normalization.
    components: Dict[int, Tuple[Fraction, Belief]] = {}
    for _, u in compatible:
        weight = Fraction(1)
        belief = None          # μ_u is only materialized if the first step is not memoized
        dead = False
        for k, obs in enumerate(obs_seq):
            if k == 0:
                key = (cfg, programs, rung, u, obs)
                hit = _FIRST_STEP.get(key)
                if hit is None:
                    prior_belief = state_marginal_at(cfg, programs, u)
                    if stats is not None:
                        stats["max_support"] = max(stats.get("max_support", 0), len(prior_belief))
                    hit = _step_unnorm(prior_belief, obs, rung, cfg, programs)
                    _FIRST_STEP[key] = hit
                belief, lik = hit
            else:
                if stats is not None:
                    stats["max_support"] = max(stats.get("max_support", 0), len(belief))
                belief, lik = _step_unnorm(belief, obs, rung, cfg, programs)
            if lik == 0:
                dead = True
                break
            weight *= lik
            belief = {s: m / lik for s, m in belief.items()}
        if not dead:
            components[u] = (weight, belief)

    return components


def filter_window(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    obs_seq: List[Record],
    rung: str,
    reset_observed: bool,
) -> WindowPosterior:
    """Exact posterior over (U, S_T) for an observed window, offset-unanchored
    (mixture semantics documented on `_components_unnorm`)."""
    return filter_window_with_evidence(cfg, programs, law, obs_seq, rung, reset_observed)[0]


def filter_window_with_evidence(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    obs_seq: List[Record],
    rung: str,
    reset_observed: bool,
    stats: dict = None,
) -> Tuple[WindowPosterior, Fraction]:
    """The posterior AND the law mass of the observation:
    P(window) = Σ_u P(T = u + n) · P(window | U = u), uniform endpoint prior
    (D8 attribution prereg §5 gate 2: mass on both sides)."""
    from yupi.window import endpoint_prior
    components = _components_unnorm(cfg, programs, law, obs_seq, rung, reset_observed, stats)
    total = sum((w for w, _ in components.values()), Fraction(0))
    if total == 0:
        raise ZeroProbabilityWindow(
            "window has probability zero under every compatible offset"
        )
    post = WindowPosterior(
        components={u: (w / total, b) for u, (w, b) in components.items()}
    )
    return post, total * endpoint_prior(law)
