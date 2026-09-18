"""Window-law aggregation by FORWARD RECURSION OVER (STATE, LAST-L WINDOW).

The third exact path in the instrument, built 2026-09-03 so that the window
law can be evaluated at horizons where path enumeration is impossible
(`c1-prime-pilot-note-v0.1.md`): the ceilings producers aggregate every
full path by (reset observed, projected in-window suffix) → law mass over
final states; this module produces the identical dictionary by carrying
the joint law of (S_t, last-L projected records) forward one tick at a
time, applying the endpoint prior at each grid point. Memory is the number
of distinct (state, window) pairs at a tick — bounded by reachable states
× distinct windows, independent of the horizon — instead of the number of
paths, which is exponential in it.

Firewall: this module imports neither `window_filter` (recursive mixture
filtering per observed window) nor `window_enumerator` / `enumerator`
(brute-force path summation). Sharing is the world definition
(`kernel.enabled`, `records`, `interfaces`, `state`) and the law structure
in `window`. Its gate is exact equality with the path aggregation at
horizons where both exist (`tests/test_window_process.py`), the same
relation `filter` bears to `enumerator`.

Exact rationals throughout.

Memory and time (2026-09-12): the arithmetic is unchanged from 2026-09-03,
but the objects are shared. The kernel is memoized per canonical state
inside one recursion (a few thousand states; the 2026-09-04 recursion
called `enabled` once per frontier pair per tick), projected records are
interned (a rung has a few dozen distinct projected records), states are
canonical (one object per reachable state), and a window reached from
several states within a tick is one tuple. The dictionaries returned are
equal (==) to the 2026-09-04 recursion's, with the same key order; only
object identity and the call count changed. Gate: the (32,8,2) and
(40,8,2) old-vs-new equality runs recorded in
`docs/window-process-interning-note-v0.1.md`, plus this module's tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from math import gcd
from typing import Dict, Iterable, Optional, Tuple

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.records import Record, record_of
from yupi.state import State, initial_state
from yupi.window import WindowLaw, endpoint_prior

WindowKey = Tuple[bool, Tuple[Record, ...]]
Aggregate = Dict[WindowKey, Dict[State, Fraction]]


class MassT(Mapping):
    """Per-window law mass by endpoint — `mass_T[key][T]` is the law mass
    generated at endpoint T for the window `key` — stored compactly and
    decoded to `{T: Fraction}` on access (2026-09-12).

    Storage: one bytearray per window = an 8-byte little-endian endpoint
    mask (bit i set iff endpoint i of the law's grid contributed) followed
    by the numerators, in increasing T, each `width[T]` bytes little-endian,
    over the per-endpoint common denominator `D[T]` (the lcm of the
    denominators of every window's mass at T; every numerator is ≤ D[T]
    because the masses at T sum to the endpoint prior < 1). Exact: the
    decoded Fraction is the value the 2026-09-04 dict-of-Fractions held.
    The 2026-09-04 form cost ~2 KB per window at (40,8,2) (one dict and
    one Fraction per (window, T)); this form costs the bytes.

    Coarser rungs share D and width with the fine rung (a coarse numerator
    is a sum of fine numerators over the same denominator)."""

    __slots__ = ("_rows", "_endpoints", "_D", "_width")

    def __init__(self, endpoints: Iterable[int], D: Optional[Dict[int, int]] = None,
                 width: Optional[Dict[int, int]] = None):
        self._endpoints = tuple(endpoints)
        if len(self._endpoints) > 64 or len(set(self._endpoints)) != len(self._endpoints):
            raise ValueError(f"MassT: the endpoint mask is 8 bytes — at most 64 distinct endpoints; got {len(self._endpoints)}")
        self._rows: Dict[WindowKey, bytearray] = {}
        self._D: Dict[int, int] = {} if D is None else D
        self._width: Dict[int, int] = {} if width is None else width

    # -- building ---------------------------------------------------------
    def add_endpoint(self, T: int, masses: Dict[WindowKey, Fraction]) -> None:
        """Record every window's mass at endpoint T (called once per T, in
        increasing T; `masses` iterates in first-seen window order so the
        row order equals the 2026-09-04 dict's)."""
        if T not in self._endpoints or (self._D and T <= max(self._D)):
            raise ValueError(f"MassT.add_endpoint: endpoints must be added once each in increasing order; got T={T} after {sorted(self._D)}")
        D = 1
        for m in masses.values():
            D = D * m.denominator // gcd(D, m.denominator)
        width = (D.bit_length() + 7) // 8
        self._D[T] = D
        self._width[T] = width
        bit = 1 << self._endpoints.index(T)
        rows = self._rows
        for key, m in masses.items():
            n = m.numerator * (D // m.denominator)
            row = rows.get(key)
            if row is None:
                row = bytearray(8)
                rows[key] = row
            row[:8] = (int.from_bytes(row[:8], "little") | bit).to_bytes(8, "little")
            row += n.to_bytes(width, "little")

    def _ints(self, key: WindowKey) -> Dict[int, int]:
        blob = self._rows[key]
        mask = int.from_bytes(blob[:8], "little")
        pos, out = 8, {}
        for i, T in enumerate(self._endpoints):
            if mask >> i & 1:
                w = self._width[T]
                out[T] = int.from_bytes(blob[pos:pos + w], "little")
                pos += w
        return out

    def projected(self, keymap) -> "MassT":
        """The coarser rung's MassT: `keymap(fine_key) -> coarse_key`; rows
        in order of the first fine key mapping to each coarse key."""
        acc: Dict[WindowKey, Dict[int, int]] = {}
        for key in self._rows:
            d = acc.setdefault(keymap(key), {})
            for T, n in self._ints(key).items():
                d[T] = d.get(T, 0) + n
        out = MassT(self._endpoints, self._D, self._width)
        rows = out._rows
        for ckey, d in acc.items():
            mask = 0
            row = bytearray(8)
            for i, T in enumerate(self._endpoints):
                n = d.get(T)
                if n is not None:
                    mask |= 1 << i
                    row += n.to_bytes(self._width[T], "little")
            row[:8] = mask.to_bytes(8, "little")
            rows[ckey] = row
        return out

    # -- Mapping ----------------------------------------------------------
    def __getitem__(self, key: WindowKey) -> Dict[int, Fraction]:
        D = self._D
        return {T: Fraction(n, D[T]) for T, n in self._ints(key).items()}

    def __iter__(self):
        return iter(self._rows)

    def __len__(self) -> int:
        return len(self._rows)

    def __contains__(self, key) -> bool:
        return key in self._rows

    def __eq__(self, other) -> bool:
        if not isinstance(other, Mapping) or len(self) != len(other):
            return False
        return all(k in other and self[k] == other[k] for k in self._rows)

    __hash__ = None


def window_law_aggregate(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    rung: str,
    stats: Optional[dict] = None,
) -> Aggregate:
    """Law mass over final states per (reset_observed, projected window),
    for every endpoint on the law's grid — the dictionary the ceilings
    producers build from `paths`, without the paths.

    reset_observed is True iff the endpoint T ≤ L (offset U = 0), in which
    case the window is the whole trace (length T); otherwise the window is
    the last L records and the reset is not in view. Windows of different
    lengths never share a key, so the endpoint mixture happens exactly as
    in the path aggregation.
    """
    L = law.L
    w_T = endpoint_prior(law)
    endpoints = set(law.endpoints())
    # Shared objects (2026-09-12): one State object per reachable state, one
    # Record object per distinct projected record, and the kernel's moves
    # memoized per state for this recursion — same values, same order.
    states: Dict[State, State] = {}
    records: Dict[Record, Record] = {}
    moves: Dict[State, list] = {}

    def canon_state(s: State) -> State:
        return states.setdefault(s, s)

    def moves_of(s: State) -> list:
        m = moves.get(s)
        if m is None:
            m = []
            for tr, p in enabled(s, cfg, programs):
                r = project(record_of(tr), rung)
                m.append((canon_state(tr.next_state), records.setdefault(r, r), p))
            moves[s] = m
        return m

    dist: Dict[Tuple[State, Tuple[Record, ...]], Fraction] = {
        (canon_state(initial_state(cfg)), ()): Fraction(1)
    }
    agg: Aggregate = {}
    if stats is not None:
        stats["pairs_per_tick"] = []
        stats["states_per_tick"] = []   # reachable states at each tick (2026-09-04)
        stats["mass_T"] = MassT(law.endpoints())   # mass_T[key][T] = law mass generated at endpoint T (2026-09-04; compact 2026-09-12)
    for t in range(1, law.T_ep + 1):
        nxt: Dict[Tuple[State, Tuple[Record, ...]], Fraction] = {}
        windows: Dict[Tuple[Record, ...], Tuple[Record, ...]] = {}   # per tick: one tuple per window
        for (s, buf), mass in dist.items():
            for ns, r, p in moves_of(s):
                nb = buf + (r,)
                if len(nb) > L:
                    nb = nb[-L:]
                key = (ns, windows.setdefault(nb, nb))
                nxt[key] = nxt.get(key, Fraction(0)) + mass * p
        dist = nxt
        del windows
        if stats is not None:
            stats["pairs_per_tick"].append(len(dist))
            stats["states_per_tick"].append(len({s for s, _ in dist}))
        if t in endpoints:
            reset = t <= L
            at_T: Optional[Dict[WindowKey, Fraction]] = {} if stats is not None else None
            for (s, buf), mass in dist.items():
                d = agg.setdefault((reset, buf), {})
                d[s] = d.get(s, Fraction(0)) + w_T * mass
                if at_T is not None:
                    at_T[(reset, buf)] = at_T.get((reset, buf), Fraction(0)) + w_T * mass
            if at_T is not None:
                stats["mass_T"].add_endpoint(t, at_T)
                del at_T
    if stats is not None:
        stats["max_pairs"] = max(stats["pairs_per_tick"])
        stats["max_states"] = max(stats["states_per_tick"])
        stats["n_windows"] = len(agg)
    return agg


def prefix_law_aggregate(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    k: int,
    rung: str,
    stats: Optional[dict] = None,
) -> Aggregate:
    """Prefix-length variant (learner contract v0.1.2, 2026-09-18): for
    every window whose law window runs at least k records (T − U ≥ k), the
    first k records U+1..U+k and the state S_{U+k}, keyed like the full
    aggregate by (reset_observed, records). Non-RESET offsets emit at
    t = U + k, one endpoint each; the RESET prefix emits once at t = k with
    weight |{T on the grid : U(T) = 0, T ≥ k}| — the observer at a prefix
    knows the window has at least k records, not where it ends. Same
    recursion as `window_law_aggregate` with a k-record buffer; gated
    against path summation in tests/test_prefix_aggregate.py.
    """
    if not 1 <= k <= law.L:
        raise ValueError("prefix length must lie in 1..L")
    w_T = endpoint_prior(law)
    emit: Dict[int, Tuple[bool, int]] = {}           # tick -> (reset_observed, multiplicity)
    for T in law.endpoints():
        u = law.offset(T)
        if T - u < k:
            continue
        reset, mult = emit.get(u + k, (u == 0, 0))
        assert reset == (u == 0)
        emit[u + k] = (reset, mult + 1)
    states: Dict[State, State] = {}
    records: Dict[Record, Record] = {}
    moves: Dict[State, list] = {}

    def canon_state(s: State) -> State:
        return states.setdefault(s, s)

    def moves_of(s: State) -> list:
        m = moves.get(s)
        if m is None:
            m = []
            for tr, p in enabled(s, cfg, programs):
                r = project(record_of(tr), rung)
                m.append((canon_state(tr.next_state), records.setdefault(r, r), p))
            moves[s] = m
        return m

    dist: Dict[Tuple[State, Tuple[Record, ...]], Fraction] = {
        (canon_state(initial_state(cfg)), ()): Fraction(1)
    }
    agg: Aggregate = {}
    if stats is not None:
        stats["pairs_per_tick"] = []
    for t in range(1, max(emit) + 1):
        nxt: Dict[Tuple[State, Tuple[Record, ...]], Fraction] = {}
        windows: Dict[Tuple[Record, ...], Tuple[Record, ...]] = {}
        for (s, buf), mass in dist.items():
            for ns, r, p in moves_of(s):
                nb = buf + (r,)
                if len(nb) > k:
                    nb = nb[-k:]
                key = (ns, windows.setdefault(nb, nb))
                nxt[key] = nxt.get(key, Fraction(0)) + mass * p
        dist = nxt
        del windows
        if stats is not None:
            stats["pairs_per_tick"].append(len(dist))
        if t in emit:
            reset, mult = emit[t]
            for (s, buf), mass in dist.items():
                d = agg.setdefault((reset, buf), {})
                d[s] = d.get(s, Fraction(0)) + w_T * mult * mass
    if stats is not None:
        stats["max_pairs"] = max(stats["pairs_per_tick"])
        stats["n_windows"] = len(agg)
    return agg


def prefix_law_aggregates(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    k: int,
    rungs=("r0", "r1", "r2", "r3", "r4"),
    stats: Optional[dict] = None,
) -> Dict[str, Aggregate]:
    """The prefix aggregate for every requested rung from ONE recursion at r4
    (each rung only masks fields; keys re-projected, masses merged)."""
    fine = prefix_law_aggregate(cfg, programs, law, k, "r4", stats)
    out: Dict[str, Aggregate] = {}
    for r in rungs:
        if r == "r4":
            out[r] = fine
            continue
        coarse: Aggregate = {}
        records: Dict[Record, Record] = {}
        for (reset, win), joint in fine.items():
            key = (reset, tuple(records.setdefault(x, x) for x in (project(y, r) for y in win)))
            d = coarse.setdefault(key, {})
            for s, m in joint.items():
                d[s] = d.get(s, Fraction(0)) + m
        out[r] = coarse
    return out


def window_law_aggregates(
    cfg: WorldConfig,
    programs,
    law: WindowLaw,
    rungs=("r0", "r1", "r2", "r3", "r4"),
    stats: Optional[dict] = None,
) -> Dict[str, Aggregate]:
    """The aggregate for every requested rung from ONE recursion at r4.

    r4 refines every other rung (each rung only masks fields), so a coarser
    rung's aggregate is the r4 aggregate with keys re-projected and masses
    merged. Same output as calling `window_law_aggregate` per rung, at the
    cost of a single r4 recursion (gate: tests/test_window_process.py).
    """
    fine = window_law_aggregate(cfg, programs, law, "r4", stats)
    fine_mT = stats.get("mass_T") if stats is not None else None
    out: Dict[str, Aggregate] = {}
    mT_by_rung: Dict[str, MassT] = {}
    for r in rungs:
        if r == "r4":
            out[r] = fine
            if fine_mT is not None:
                mT_by_rung[r] = fine_mT
            continue
        coarse: Aggregate = {}
        records: Dict[Record, Record] = {}       # interned projected records (2026-09-12)
        keymap: Dict[WindowKey, WindowKey] = {}  # fine key -> coarse key, one tuple per coarse window
        for (reset, win), joint in fine.items():
            key = (reset, tuple(records.setdefault(x, x) for x in (project(y, r) for y in win)))
            d = coarse.setdefault(key, {})
            for s, m in joint.items():
                d[s] = d.get(s, Fraction(0)) + m
            keymap[(reset, win)] = key
        out[r] = coarse
        if fine_mT is not None:                  # per-endpoint mass projects the same way (2026-09-04)
            mT_by_rung[r] = fine_mT.projected(keymap.__getitem__)
        del keymap
    if stats is not None:
        stats["mass_T_by_rung"] = mT_by_rung
    return out
