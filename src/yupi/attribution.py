"""D8 order-mode attribution — path-side aggregated tables and exact
information functionals. Preregistration: docs/d8-attribution-prereg-v0.1.md
(commit a39f555, stamped before any of this existed).

Firewall placement: ENUMERATOR SIDE. Tables are built by exhaustive path
enumeration (`enumerator.paths`) aggregated by projected latent window, and
the permutation channel is applied by a LITERAL permutation count (the
statute's definition), independent of `shuffled.channel_likelihood`. This
module imports no filter. The recursive side (`window_filter`,
`shuffled_window`) is compared against these tables by the measurement's
gate 2 — every distinct observation, posterior and law mass, uncapped.

Quantities (prereg §1–§3): for a coordinate subset A of the six
{U, κ, WQ, DQ, REQ, ρ} (a bijection with (U, S_T), gate F),
    F(A) = E[H(A | O_shuf)] − E[H(A | O_ord)]      (shuffle loss on A)
Δ_un = F(all); offset term = F({U}); Δ_an = F(all) − F({U}); a chain term
for coordinate k after prefix P is F(P ∪ k) − F(P); Shapley and the
min/max envelope range over the same 2^n subset values. Entropies are
floats of exact rational distributions; every F is a difference of two such
expectations, so identities that hold as partitions hold bit-for-bit.
"""
from fractions import Fraction
from itertools import permutations, product
from math import factorial, fsum, log2
from typing import Dict, FrozenSet, Hashable, Iterable, List, Tuple

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.records import Record
from yupi.state import State
from yupi.window import WindowLaw, endpoint_prior

Joint = Dict[Tuple[int, State], Fraction]              # (u, final) -> law mass
LatentKey = Tuple[bool, Tuple[Record, ...]]
VisibleKey = Tuple[bool, Tuple[Tuple[Record, ...], ...]]

COORDS = ("U", "kappa", "WQ", "DQ", "REQ", "rho")
SEMANTIC_ORDER = COORDS                                # prereg §3 item 1


# ---------------------------------------------------------------- tables

def latent_table(cfg: WorldConfig, programs, law: WindowLaw, rung: str
                 ) -> Dict[LatentKey, Joint]:
    """(reset, ordered projected window) -> joint law mass over (U, S_T)."""
    w_T = endpoint_prior(law)
    table: Dict[LatentKey, Joint] = {}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, prob, final in paths(cfg, programs, T):
            key = (u == 0, tuple(project(r, rung) for r in recs[u:]))
            j = table.setdefault(key, {})
            j[(u, final)] = j.get((u, final), Fraction(0)) + w_T * prob
    return table


def literal_likelihood(latent: Tuple[Record, ...], visible: Tuple[Record, ...]) -> Fraction:
    """m / B! by literal permutation count — the statute's definition."""
    n = len(latent)
    m = sum(1 for perm in permutations(range(n))
            if tuple(latent[i] for i in perm) == tuple(visible))
    return Fraction(m, factorial(n))


def distinct_orders(bucket: Tuple[Record, ...]) -> List[Tuple[Record, ...]]:
    return sorted({tuple(p) for p in permutations(bucket)}, key=repr)


def visible_table(latent: Dict[LatentKey, Joint], B: int
                  ) -> Tuple[Dict[VisibleKey, Joint], Dict[VisibleKey, Dict[LatentKey, Fraction]]]:
    """Push the latent table through the within-bucket permutation channel.
    Returns (table: visible observation -> joint law mass over (U, S_T),
             sources: visible -> {latent window: law mass routed to it})."""
    table: Dict[VisibleKey, Joint] = {}
    sources: Dict[VisibleKey, Dict[LatentKey, Fraction]] = {}
    for (reset, win), joint in latent.items():
        mass_w = sum(joint.values(), Fraction(0))
        buckets = [win[k * B:(k + 1) * B] for k in range(len(win) // B)]
        for vis in product(*(distinct_orders(b) for b in buckets)):
            lik = Fraction(1)
            for b, v in zip(buckets, vis):
                lik *= literal_likelihood(b, v)
            key = (reset, tuple(vis))
            j = table.setdefault(key, {})
            for k, m in joint.items():
                j[k] = j.get(k, Fraction(0)) + m * lik
            src = sources.setdefault(key, {})
            src[(reset, win)] = src.get((reset, win), Fraction(0)) + mass_w * lik
    return table, sources


def mass(joint: Joint) -> Fraction:
    return sum(joint.values(), Fraction(0))


def normalized(joint: Joint) -> Joint:
    z = mass(joint)
    return {k: m / z for k, m in joint.items()}


# ----------------------------------------------------------- coordinates

def coords(u: int, s: State) -> Dict[str, Hashable]:
    """The prereg §2 factorization of (U, S_T)."""
    wq_rank = tuple(tuple(sorted(q).index(t) for t in q) for q in s.lock_wq)
    dq_rank = tuple(tuple(sorted(t for t, _ in q).index(t) for t, _ in q) for q in s.dev_q)
    req = tuple(tuple(sorted(q)) for q in s.dev_q)
    rho = (s.pc,
           tuple(("IO_BLOCKED",) if st[0] == "IO_BLOCKED" else st for st in s.status),
           s.running, s.lock_owner,
           tuple(frozenset(q) for q in s.lock_wq),
           tuple(tuple(sorted(t for t, _ in q)) for q in s.dev_q))
    return dict(U=u, kappa=s.rr_cursor, WQ=wq_rank, DQ=dq_rank, REQ=req, rho=rho)


def reconstruct(c: Dict[str, Hashable]) -> Tuple[int, State]:
    """Inverse of `coords` (gate F: bijection on every reachable state)."""
    pc, status_stripped, running, lock_owner, wq_sets, dq_sorted = c["rho"]
    lock_wq = tuple(tuple(sorted(sset)[i] for i in ranks)
                    for sset, ranks in zip(wq_sets, c["WQ"]))
    dev_q = []
    req_of: Dict[int, int] = {}
    for threads, ranks, pairs in zip(dq_sorted, c["DQ"], c["REQ"]):
        rmap = dict(pairs)
        req_of.update(rmap)
        dev_q.append(tuple((threads[i], rmap[threads[i]]) for i in ranks))
    status = tuple(("IO_BLOCKED", req_of[i]) if st == ("IO_BLOCKED",) else st
                   for i, st in enumerate(status_stripped))
    return c["U"], State(pc=pc, status=status, running=running, lock_owner=lock_owner,
                         lock_wq=lock_wq, dev_q=tuple(dev_q), rr_cursor=c["kappa"])


def check_bijection(*tables: Dict[Hashable, Joint]) -> int:
    """Gate F over every (u, s) in the given tables; returns the count checked."""
    seen = set()
    for t in tables:
        for joint in t.values():
            for (u, s) in joint:
                if (u, s) in seen:
                    continue
                seen.add((u, s))
                if reconstruct(coords(u, s)) != (u, s):
                    raise AssertionError(f"coordinate bijection fails at {(u, s)}")
    return len(seen)


# ----------------------------------------------------------- functionals

def entropy_bits(masses: Iterable[Fraction]) -> float:
    """Shannon entropy in bits of an exact-rational mass list. Terms are
    combined with math.fsum (correctly rounded, order-independent) so that
    two computations over the same partition (the same multiset of masses)
    produce the same float bit-for-bit — the exact-equality gates
    (full-coordinate identity, Z1, Z2) rely on this."""
    ms = sorted(m for m in masses if m > 0)
    z = sum(ms, Fraction(0))
    return -fsum(float(m / z) * log2(float(m / z)) for m in ms)


class CoordCache:
    def __init__(self):
        self._c: Dict[Tuple[int, State], Dict[str, Hashable]] = {}

    def get(self, k: Tuple[int, State]) -> Dict[str, Hashable]:
        c = self._c.get(k)
        if c is None:
            c = self._c[k] = coords(*k)
        return c


def subset_entropy(table: Dict[Hashable, Joint], subset: Tuple[str, ...],
                   cache: CoordCache) -> float:
    """E_obs[ H(coordinates in `subset` | obs) ], law-mass weighted."""
    terms = []
    for joint in table.values():
        groups: Dict[Hashable, Fraction] = {}
        for k, m in joint.items():
            key = tuple(cache.get(k)[c] for c in subset)
            groups[key] = groups.get(key, Fraction(0)) + m
        terms.append(float(mass(joint)) * entropy_bits(groups.values()))
    return fsum(terms)


def joint_entropy(table: Dict[Hashable, Joint]) -> float:
    """E_obs[ H(U, S_T | obs) ] directly on the joint (gate: equals the
    all-coordinates subset entropy bit-for-bit, since the partition is the same)."""
    return fsum(float(mass(j)) * entropy_bits(j.values()) for j in table.values())


def losses(latent: Dict[LatentKey, Joint], visible: Dict[VisibleKey, Joint],
           players: Tuple[str, ...] = COORDS) -> Dict[FrozenSet[str], float]:
    """F(A) for every subset A of `players` (2^n values)."""
    cache = CoordCache()
    out: Dict[FrozenSet[str], float] = {}
    n = len(players)
    for bits in range(1 << n):
        A = tuple(p for i, p in enumerate(players) if bits >> i & 1)
        out[frozenset(A)] = (subset_entropy(visible, A, cache) - subset_entropy(latent, A, cache)
                             if A else 0.0)
    return out


def value_fn(F: Dict[FrozenSet[str], float], cond: FrozenSet[str] = frozenset()):
    """v(A) = F(A ∪ cond) − F(cond): the unanchored game (cond = ∅) or the
    anchored game (cond = {U})."""
    base = F[cond]
    return lambda A: F[frozenset(A) | cond] - base


def chain_terms(v, order: Tuple[str, ...]) -> Dict[str, float]:
    out, prefix = {}, []
    for k in order:
        out[k] = v(prefix + [k]) - v(prefix)
        prefix.append(k)
    return out


def shapley(v, players: Tuple[str, ...]) -> Dict[str, float]:
    n = len(players)
    others = lambda k: [p for p in players if p != k]
    out = {}
    for k in players:
        acc = 0.0
        rest = others(k)
        for bits in range(1 << (n - 1)):
            P = [p for i, p in enumerate(rest) if bits >> i & 1]
            w = factorial(len(P)) * factorial(n - len(P) - 1) / factorial(n)
            acc += w * (v(P + [k]) - v(P))
        out[k] = acc
    return out


def envelope(v, players: Tuple[str, ...]) -> Dict[str, Tuple[float, float]]:
    """(min, max) of coordinate k's chain term over all orders = over all
    prefixes P ⊆ players \\ {k}."""
    n = len(players)
    out = {}
    for k in players:
        rest = [p for p in players if p != k]
        vals = []
        for bits in range(1 << (n - 1)):
            P = [p for i, p in enumerate(rest) if bits >> i & 1]
            vals.append(v(P + [k]) - v(P))
        out[k] = (min(vals), max(vals))
    return out


# ---------------------------------------------------- per-observation view

def per_observation(latent: Dict[LatentKey, Joint], visible: Dict[VisibleKey, Joint],
                    sources: Dict[VisibleKey, Dict[LatentKey, Fraction]]):
    """For every visible v: (law mass, g(v) in bits, informative-exactly flag).
    g(v) = H(U,S | v) − Σ_w P(w | v) H(U,S | w); informative iff some source
    w has a normalized joint different from v's (exact rational test — the
    conditional MI is zero iff (U,S) ⟂ O_ord given O_shuf = v)."""
    Hlat = {w: entropy_bits(j.values()) for w, j in latent.items()}
    norm_lat = {w: normalized(j) for w, j in latent.items()}
    rows = []
    for v, joint in visible.items():
        mv = mass(joint)
        hv = entropy_bits(joint.values())
        mix = fsum(float(m / mv) * Hlat[w] for w, m in sources[v].items())
        nv = normalized(joint)
        informative = any(norm_lat[w] != nv for w in sources[v])
        rows.append((v, mv, hv - mix, informative))
    return rows


def per_offset_anchored(latent: Dict[LatentKey, Joint], visible: Dict[VisibleKey, Joint],
                        sources: Dict[VisibleKey, Dict[LatentKey, Fraction]],
                        law: WindowLaw) -> Dict[int, float]:
    """Anchored gain restricted to windows generated at each endpoint (per U):
    E[H(S | O_shuf, U=u)] − E[H(S | O_ord, U=u)] over that endpoint's law mass."""
    out = {}
    for T in law.endpoints():
        u = law.offset(T)
        pu = Fraction(0)
        hs = ho = 0.0
        for v, joint in visible.items():
            comp = {s: m for (uu, s), m in joint.items() if uu == u}
            if not comp:
                continue
            mvu = mass(comp)
            pu += mvu
            hs += float(mvu) * entropy_bits(comp.values())
        for w, joint in latent.items():
            comp = {s: m for (uu, s), m in joint.items() if uu == u}
            if comp:
                ho += float(mass(comp)) * entropy_bits(comp.values())
        out[T] = (hs - ho) / float(pu) if pu else 0.0
    return out
