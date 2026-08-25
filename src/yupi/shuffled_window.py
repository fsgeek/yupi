"""Statutory posterior semantics for shuffled windows (Part II §2 + §4),
using RESET and TIME_CLASS-equivalent conditioning.

Scope note: this is the exact posterior machinery — NOT the schema/emitter
implementation. Physical RESET/TIME_CLASS records and the corpus emitter
do not exist yet; RESET enters as the flag (as in the ordered machinery)
and the anchored condition as component selection on U, which is what
unmasked absolute bucket indices reveal under a fixed law.

Composes the within-bucket permutation channel with the statutory window
mixture: an observed window is a sequence of delivered buckets (size B,
bucket-boundary delivery); the posterior over (U, S_T) conditions on window
length and RESET via `WindowLaw.compatible_endpoints` (RESET is the flag,
exactly as in the ordered machinery), then per-component filtering carries
the channel likelihood m/B! per bucket. TIME_CLASS: the base condition
masks it, so it does not appear here; the anchored condition is
conditioning on U (component selection), which unmasked absolute bucket
indices reveal under a fixed law.

Firewall: this module implements only the RECURSIVE side
(`shuffled_window_filter`) plus an algorithmically independent
path-summation side (`shuffled_window_by_paths`) that never touches the
recursion — shared consumption is the world definition and the channel
likelihood, whose own independence gate (literal permutation count) lives
in tests/test_shuffled_channel.py.
"""
from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.filter import Belief
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.shuffled import channel_likelihood
from yupi.state import State
from yupi.window import WindowLaw, WindowPosterior
from yupi.window_filter import ZeroProbabilityWindow, state_marginal_at


def _bucket_step_unnorm(belief: Belief, visible: List[Record], rung: str,
                        cfg: WorldConfig, programs) -> Tuple[Belief, Fraction]:
    """One shuffled-bucket update, unnormalized: returns (new belief summing
    to the evidence likelihood of the bucket, that likelihood)."""
    B = len(visible)
    frontier = [(s, m, []) for s, m in belief.items() if m]
    for _ in range(B):
        nxt = []
        for s, m, recs in frontier:
            for t, p in enabled(s, cfg, programs):
                nxt.append((t.next_state, m * p,
                            recs + [project(record_of(t), rung)]))
        frontier = nxt
    unnorm: Belief = {}
    for s, m, recs in frontier:
        lik = channel_likelihood(recs, visible)
        if lik:
            unnorm[s] = unnorm.get(s, Fraction(0)) + m * lik
    total = sum(unnorm.values(), Fraction(0))
    return unnorm, total


def shuffled_window_filter(cfg: WorldConfig, programs, law: WindowLaw,
                           buckets: List[List[Record]], rung: str,
                           reset_observed: bool) -> WindowPosterior:
    """Exact posterior over (U, S_T) for a shuffled-mode window."""
    return shuffled_window_filter_with_evidence(
        cfg, programs, law, buckets, rung, reset_observed)[0]


def shuffled_window_filter_with_evidence(cfg: WorldConfig, programs, law: WindowLaw,
                                         buckets: List[List[Record]], rung: str,
                                         reset_observed: bool) -> Tuple[WindowPosterior, Fraction]:
    """The posterior AND the law mass of the shuffled observation:
    P(v) = Σ_u P(T = u + n) · P(v | U = u), uniform endpoint prior
    (D8 attribution prereg §5 gate 2: mass on both sides)."""
    from yupi.window import endpoint_prior
    for b in buckets:
        if len(b) != law.B:
            raise ValueError(f"bucket of size {len(b)} under B={law.B}")
    n_obs = law.B * len(buckets)
    compatible = law.compatible_endpoints(n_obs, reset_observed)
    if not compatible:
        raise ZeroProbabilityWindow(
            f"no endpoint on the grid yields a window of {n_obs} records")
    components: Dict[int, Tuple[Fraction, Belief]] = {}
    for _, u in compatible:
        belief = state_marginal_at(cfg, programs, u)
        weight = Fraction(1)
        dead = False
        for vis in buckets:
            unnorm, lik = _bucket_step_unnorm(belief, vis, rung, cfg, programs)
            if lik == 0:
                dead = True
                break
            weight *= lik
            belief = {s: m / lik for s, m in unnorm.items()}
        if not dead:
            components[u] = (weight, belief)
    grand = sum((w for w, _ in components.values()), Fraction(0))
    if grand == 0:
        raise ZeroProbabilityWindow("window has probability zero at every endpoint")
    post = WindowPosterior(components={
        u: (w / grand, belief) for u, (w, belief) in components.items()})
    return post, grand * endpoint_prior(law)


def shuffled_window_by_paths(cfg: WorldConfig, programs, law: WindowLaw,
                             buckets: List[List[Record]], rung: str,
                             reset_observed: bool) -> WindowPosterior:
    """Independent path-summation side: enumerate full episode paths per
    compatible endpoint; weight = path probability × Π bucket channel
    likelihoods of the path's projected latent buckets."""
    B = law.B
    n_obs = B * len(buckets)
    raw: Dict[int, Belief] = {}
    for T, u in law.compatible_endpoints(n_obs, reset_observed):
        totals: Belief = {}
        for recs, prob, final in paths(cfg, programs, T):
            w = prob
            for k, vis in enumerate(buckets):
                latent = [project(r, rung) for r in recs[u + k * B:u + (k + 1) * B]]
                w *= channel_likelihood(latent, vis)
                if w == 0:
                    break
            if w:
                totals[final] = totals.get(final, Fraction(0)) + w
        if totals:
            raw[u] = totals
    grand = sum((m for t in raw.values() for m in t.values()), Fraction(0))
    if grand == 0:
        raise ZeroProbabilityWindow("window has probability zero at every endpoint")
    components: Dict[int, Tuple[Fraction, Belief]] = {}
    for u, totals in raw.items():
        mass = sum(totals.values(), Fraction(0))
        components[u] = (mass / grand, {s: m / mass for s, m in totals.items()})
    return WindowPosterior(components=components)
