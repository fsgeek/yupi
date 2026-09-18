"""The pattern observer's exact filter — RECURSIVE MIXTURE FILTERING over
(U, S, β) (learner contract v0.1 §2.1–2.2, 2026-09-18).

The trained model sees surface names drawn per episode (v0.2.9 Clause 4),
so the observer it instantiates sees the equality pattern Πw over all four
entity types (`yupi.naming.pattern_all`). Its exact posterior is over the
offset U, the structural state S, and the partial binding β from pattern
indices to structural entities. Because σ is uniform and independent of
the dynamics, P(S, β | Πw) is the sum of the structural masses of the
canonical windows in the class (the lemma of tests/test_naming_bridge*.py)
— so the filter needs no σ factor: a pattern record ρ is consistent with a
transition from (S, β) iff extend_binding(β, project(record)) yields ρ,
and the binding grows through fresh entities.

This module is the RECURSIVE side. It never imports an enumerator; its
validator is `yupi.pattern_enumerator` (path summation), gated
bit-for-bit in tests/test_pattern_filter.py, with the re-keyed canonical
aggregate (the corpus-track producer's construction) as a third path.
Shared consumption: the world definition (kernel, records, interfaces,
state), the law (`window`), Π (`naming`), the exact forward marginal
μ_u (`window_filter.state_marginal_at`, cached) and `predict.p_next`.

Prefix mode (contract §2.2): a prefix of k records is compatible with every
(T, U) whose window runs at least k records — T − U ≥ k — rather than
exactly k. RESET fixes U = 0 and leaves every T ≥ k open, so the U = 0
component's prior weight is the number of open endpoints.
"""
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.naming import ENTITY_ORDER, extend_binding
from yupi.records import Record, record_of
from yupi.state import State
from yupi.window import WindowLaw, endpoint_prior
from yupi.window_filter import ZeroProbabilityWindow, state_marginal_at

Binding = Tuple[tuple, tuple, tuple, tuple]
EMPTY_BINDING: Binding = ((), (), (), ())
JointBelief = Dict[Tuple[State, Binding], Fraction]


@dataclass(frozen=True)
class PatternPosterior:
    """Per-offset (mixture weight, normalized belief over (S, β))."""

    components: Dict[int, Tuple[Fraction, JointBelief]] = field(default_factory=dict)

    def offset_marginal(self) -> Dict[int, Fraction]:
        return {u: w for u, (w, _) in self.components.items()}

    def joint_marginal(self) -> JointBelief:
        out: JointBelief = {}
        for _, (w, belief) in self.components.items():
            for k, m in belief.items():
                out[k] = out.get(k, Fraction(0)) + w * m
        return out

    def state_marginal(self) -> Dict[State, Fraction]:
        out: Dict[State, Fraction] = {}
        for (s, _), m in self.joint_marginal().items():
            out[s] = out.get(s, Fraction(0)) + m
        return out


def compatible_offsets(law: WindowLaw, n_obs: int, reset_observed: bool, prefix: bool) -> Dict[int, int]:
    """{U: number of compatible endpoints T} — full-window mode requires
    T − U = n_obs (the statute's length rule, one T per U); prefix mode
    requires T − U ≥ n_obs. RESET partitions U = 0 from U > 0 either way."""
    out: Dict[int, int] = {}
    for T in law.endpoints():
        u = law.offset(T)
        if (u == 0) != reset_observed:
            continue
        if (T - u >= n_obs) if prefix else (T - u == n_obs):
            out[u] = out.get(u, 0) + 1
    return out


_FIRST_STEP: Dict[Tuple, Tuple[JointBelief, Fraction]] = {}


def first_step_cache_clear() -> None:
    _FIRST_STEP.clear()


def _step_unnorm(belief: JointBelief, rho: Record, rung: str, cfg: WorldConfig, programs, types) -> Tuple[JointBelief, Fraction]:
    out: JointBelief = {}
    for (s, b), mass in belief.items():
        if mass == 0:
            continue
        for tr, p in enabled(s, cfg, programs):
            pr, b2 = extend_binding(b, project(record_of(tr), rung), types)
            if pr != rho:
                continue
            key = (tr.next_state, b2)
            out[key] = out.get(key, Fraction(0)) + mass * p
    return out, sum(out.values(), Fraction(0))


def filter_pattern_window(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    pattern_seq: List[Record],
    rung: str,
    reset_observed: bool,
    prefix: bool = False,
    types=ENTITY_ORDER,
) -> Tuple[PatternPosterior, Fraction]:
    """Exact (posterior over (U, S, β), law mass) for a pattern window (or a
    prefix of one). Law mass = Σ_{compatible (T,U)} P(T) · P(pattern | U)."""
    compat = compatible_offsets(law, len(pattern_seq), reset_observed, prefix)
    if not compat:
        raise ZeroProbabilityWindow(f"no endpoint on the grid yields a window of {len(pattern_seq)} records")
    components: Dict[int, Tuple[Fraction, JointBelief]] = {}
    for u, n_T in compat.items():
        weight = Fraction(n_T)
        belief: JointBelief = {(s, EMPTY_BINDING): m for s, m in state_marginal_at(cfg, programs, u).items()}
        dead = False
        for k, rho in enumerate(pattern_seq):
            if k == 0:
                key = (cfg, programs, rung, u, rho, types)
                hit = _FIRST_STEP.get(key)
                if hit is None:
                    hit = _step_unnorm(belief, rho, rung, cfg, programs, types)
                    _FIRST_STEP[key] = hit
                belief, lik = hit
            else:
                belief, lik = _step_unnorm(belief, rho, rung, cfg, programs, types)
            if lik == 0:
                dead = True
                break
            weight *= lik
            belief = {kk: m / lik for kk, m in belief.items()}
        if not dead:
            components[u] = (weight, belief)
    total = sum((w for w, _ in components.values()), Fraction(0))
    if total == 0:
        raise ZeroProbabilityWindow("pattern window has probability zero under every compatible offset")
    post = PatternPosterior(components={u: (w / total, b) for u, (w, b) in components.items()})
    return post, total * endpoint_prior(law)


def next_pattern_dist(post: PatternPosterior, cfg: WorldConfig, programs, rung: str, types=ENTITY_ORDER) -> Dict[Record, Fraction]:
    """P*(Πr_next | Πw): one kernel step per support (S, β), the record
    projected to the rung and re-keyed through β by extend_binding (fresh
    entities take the next pattern indices). The model's ceiling for the
    next record (contract §2.1)."""
    out: Dict[Record, Fraction] = {}
    for (s, b), m in post.joint_marginal().items():
        for tr, p in enabled(s, cfg, programs):
            pr, _ = extend_binding(b, project(record_of(tr), rung), types)
            out[pr] = out.get(pr, Fraction(0)) + m * p
    return out


def pattern_end_probability(law: WindowLaw, k: int, reset_observed: bool) -> Fraction:
    """P(the window ends after record k | k records seen, RESET flag) — the
    exact end-of-window term of the token loss (contract §1 item 3). T is
    independent of the dynamics, so no record content enters: non-RESET
    windows have exactly L records; a RESET window ends at k iff T = k,
    with T uniform over the open endpoints {T on the grid : U(T) = 0, T ≥ k}."""
    if not reset_observed:
        return Fraction(1) if k == law.L else Fraction(0)
    open_T = [T for T in law.endpoints() if law.offset(T) == 0 and T >= k]
    if not open_T:
        raise ZeroProbabilityWindow(f"a RESET window cannot reach {k} records under this law")
    return Fraction(1, len(open_T)) if k in open_T else Fraction(0)
