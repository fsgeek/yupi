"""Window law and shared result structure (Part II §2, the decided statute).

This module holds the OBSERVATION-PROCESS DEFINITION shared by the two
independent windowed-posterior paths (`window_filter`, `window_enumerator`):
the endpoint grid, the offset map, the endpoint prior, and the
length-compatibility rule. It contains no posterior computation — sharing
it is sharing the world, like `kernel`/`records`, not sharing an algorithm.

Statute anchors (Part II §2(a)/(b), v0.2; window-prior note v0.3):
- Endpoint T ~ Uniform{B, 2B, ..., T_ep}; offset U = max(0, T - L).
- The truncation prior is DERIVED: the marginal induced by this joint law.
- The base observer is offset-UNANCHORED: a joint belief over (U, S_U)
  whose mixture weights are posterior-updated by evidence. Window length
  is evidence (the length-compatibility rule below is its exact form).

RESET is modeled as an observation-level FLAG (`reset_observed`), not yet
as a schema record: the statute includes the RESET record O_0 exactly when
U = 0, so its presence pins U = 0 and its absence excludes U = 0 a priori.
The flag carries precisely that information. *(Correction, v0.2 — the v0.1
docstring claimed RESET would be "redundant, not a semantic change"; that
was false: without it, U = 0 wrongly competes with U > 0 at full window
length, and reset-visible windows wrongly fail to collapse to the point
masses injectivity guarantees. Self-caught on day five, before external
review.)* TIME_CLASS still awaits the schema extension.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Tuple

from yupi.state import State

Belief = Dict[State, Fraction]


@dataclass(frozen=True)
class WindowLaw:
    """The joint episode/endpoint/window law.

    T_ep: fixed episode horizon in transition records (multiple of B).
    L: context horizon in transition records (multiple of B).
    B: delivered-bucket size; the endpoint grid is {B, 2B, ..., T_ep}.
    """

    T_ep: int
    L: int
    B: int = 1

    def __post_init__(self):
        if self.T_ep % self.B != 0:
            raise ValueError("T_ep must be a multiple of B")
        if self.L % self.B != 0:
            raise ValueError("L must be a multiple of B")

    def endpoints(self) -> range:
        return range(self.B, self.T_ep + 1, self.B)

    def offset(self, T: int) -> int:
        return max(0, T - self.L)

    def compatible_endpoints(
        self, n_obs: int, reset_observed: bool
    ) -> List[Tuple[int, int]]:
        """(T, U) pairs the law permits for an observed window of n_obs
        transition records — the exact form of 'window length and RESET are
        evidence'. RESET is present iff U = 0 (statute §2a), so the flag
        partitions the offsets: with RESET only U = 0 is possible; without
        it only U > 0. Offsets are distinct across pairs (T = U + n_obs).
        """
        return [
            (T, self.offset(T))
            for T in self.endpoints()
            if T - self.offset(T) == n_obs
            and (self.offset(T) == 0) == reset_observed
        ]


def endpoint_prior(law: WindowLaw) -> Fraction:
    """P(T = t) for each t on the grid — uniform by the statute."""
    return Fraction(1, len(law.endpoints()))


@dataclass(frozen=True)
class WindowPosterior:
    """Joint posterior over (U, S_T): per-offset mixture weight and
    normalized within-component state belief. Zero-weight components are
    absent (both paths drop them identically, so equality is bit-for-bit).
    """

    components: Dict[int, Tuple[Fraction, Belief]] = field(default_factory=dict)

    def offset_marginal(self) -> Dict[int, Fraction]:
        return {u: w for u, (w, _) in self.components.items()}

    def state_marginal(self) -> Belief:
        out: Belief = {}
        for _, (w, belief) in self.components.items():
            for s, m in belief.items():
                out[s] = out.get(s, Fraction(0)) + w * m
        return out
