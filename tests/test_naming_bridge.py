"""Executable naming-bridge lemma (proposal: Part II v0.2.9, the naming bridge —
docs/part2-amendment-proposal-v0.2.9.md, 2026-09-12).

Clause 2′ (v0.2.6) says no canonical-track number is a random-naming
ceiling until a bridge exists: (a) naming-aware exact inference, or (b) a
per-metric equivariance proof validated on a small naming orbit. This file
is the bridge in its cleanest form, checked exhaustively at a small law:

  The corpus process draws a per-episode injection σ from structural
  threads into a token pool. An observer sees the surface window (actor and
  related fields renamed by σ). Because σ is uniform and independent of the
  dynamics, the observer's posterior over the structural state, and its
  answer distribution for a query about *the thread named x*, are functions
  of the window's EQUALITY PATTERN alone (first-appearance relabeling of
  thread fields within the window), and equal the pattern-window aggregate
  over (structural state, binding) — a re-keying of the rung aggregate the
  instrument already computes. Nothing about the world or the kernel
  changes; the bridge is a relabeling before the filter sees the window,
  and queries take pattern-indexed arguments.

Checked here, Fraction for Fraction, over every injection into a pool of
n_threads + 1 tokens, at C1 (8, 4, 2), rungs r1 and r3, both statutory ε:
  1. P(S_T | surface window) == P(S_T | pattern window), and the surface
     window's law mass is the pattern class's mass split uniformly over the
     token assignments of its k distinct threads;
  2. for every token x in a surface window, the exact answer distribution
     of Q2 "status of the thread named x" equals the pattern-side pushforward
     of status[binding[k]] where k is x's pattern index;
  3. the pattern partition at r3 refines the one at r1 (rung monotonicity
     survives the relabeling).
"""
import itertools
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import MASKED, project
from yupi.programs import c1_programs
from yupi.queries import q2_status
from yupi.records import Record
from yupi.window import WindowLaw, endpoint_prior

LAW = WindowLaw(T_ep=8, L=4, B=2)


def _is_thread_field(v):
    return v is not None and v != MASKED


def rename(rec: Record, sigma) -> Record:
    """Surface record: thread fields through the episode's injection σ."""
    return Record(kind=rec.kind,
                  actor=sigma[rec.actor] if _is_thread_field(rec.actor) else rec.actor,
                  obj=rec.obj,
                  related=sigma[rec.related] if _is_thread_field(rec.related) else rec.related,
                  lineage=rec.lineage)


def pattern(window):
    """Equality pattern: thread fields relabeled by first appearance (actor
    before related within a record); returns (pattern window, order), where
    order[k] is the original label of pattern index k."""
    idx, order, out = {}, [], []
    def lab(v):
        if not _is_thread_field(v):
            return v
        if v not in idx:
            idx[v] = len(order); order.append(v)
        return idx[v]
    for r in window:
        a = lab(r.actor); rel = lab(r.related)
        out.append(Record(kind=r.kind, actor=a, obj=r.obj, related=rel, lineage=r.lineage))
    return tuple(out), tuple(order)


def _windows(cfg, progs, rung):
    """(reset, structural window, prob, final) for every path and endpoint."""
    w_T = endpoint_prior(LAW)
    for T in LAW.endpoints():
        u = LAW.offset(T)
        for recs, prob, final in paths(cfg, progs, T):
            yield (u == 0, tuple(project(r, rung) for r in recs[u:]), w_T * prob, final)


def surface_and_pattern_aggregates(cfg, progs, rung, pool):
    n = cfg.n_threads
    sigmas = [dict(zip(range(n), toks)) for toks in itertools.permutations(pool, n)]
    w_sigma = Fraction(1, len(sigmas))
    surface, patt = {}, {}
    for reset, win, mass, final in _windows(cfg, progs, rung):
        pw, order = pattern(win)                       # order: pattern index -> structural thread
        d = patt.setdefault((reset, pw), {})
        d[(final, order)] = d.get((final, order), Fraction(0)) + mass
        for sig in sigmas:
            sw = tuple(rename(r, sig) for r in win)
            e = surface.setdefault((reset, sw), {})
            key = (final, tuple(sig[i] for i in range(n)))
            e[key] = e.get(key, Fraction(0)) + mass * w_sigma
    return surface, patt


def _state_marginal(joint):
    tot = sum(joint.values(), Fraction(0)); out = {}
    for (s, _), m in joint.items():
        out[s] = out.get(s, Fraction(0)) + m / tot
    return out


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
@pytest.mark.parametrize("rung", ["r1", "r3"])
def test_surface_posterior_is_the_pattern_posterior(eps, rung):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    pool = tuple(f"tok{j}" for j in range(cfg.n_threads + 1))
    surface, patt = surface_and_pattern_aggregates(cfg, progs, rung, pool)
    assert sum((sum(v.values(), Fraction(0)) for v in surface.values()), Fraction(0)) == 1
    assert sum((sum(v.values(), Fraction(0)) for v in patt.values()), Fraction(0)) == 1
    n_assign = {}                                        # k distinct threads -> token assignments
    for (reset, sw), joint in surface.items():
        pw, order = pattern(sw)
        k = len(order)
        pj = patt[(reset, pw)]
        # 1. same posterior over structural states
        assert _state_marginal(joint) == _state_marginal(pj), (reset, sw)
        # 1'. the pattern class's mass splits uniformly over token assignments
        n_assign.setdefault(k, Fraction(1))
        n_assign[k] = Fraction(1)
        for j in range(k):
            n_assign[k] *= len(pool) - j
        assert sum(joint.values(), Fraction(0)) * n_assign[k] == sum(pj.values(), Fraction(0)), (reset, sw)
        # 2. named query == pattern-indexed query, for every token in the window
        for x in order:                                  # tokens present, in first-appearance order
            kx = order.index(x)
            named = {}
            for (s, toks), m in joint.items():
                thread = toks.index(x)                   # σ⁻¹(x)
                a = q2_status(s, thread)
                named[a] = named.get(a, Fraction(0)) + m
            patterned = {}
            for (s, binding), m in pj.items():
                a = q2_status(s, binding[kx])
                patterned[a] = patterned.get(a, Fraction(0)) + m
            tot_n, tot_p = sum(named.values(), Fraction(0)), sum(patterned.values(), Fraction(0))
            assert {a: m / tot_n for a, m in named.items()} == {a: m / tot_p for a, m in patterned.items()}, (reset, sw, x)
    # the surface partition is strictly finer than the pattern partition (tokens carry no information)
    assert len(surface) > len(patt)


@pytest.mark.parametrize("eps", [Fraction(1), Fraction(1, 2)])
def test_pattern_partition_refines_down_the_ladder(eps):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    classes = {}
    for rung in ("r1", "r3"):
        classes[rung] = {}
        for reset, win, mass, final in _windows(cfg, progs, rung):
            pw, _ = pattern(win)
            classes[rung].setdefault((reset, pw), Fraction(0))
            classes[rung][(reset, pw)] += mass
    # every r3 pattern class projects to exactly one r1 pattern class
    r3_to_r1 = {}
    for reset, win, mass, final in _windows(cfg, progs, "r3"):
        pw3, _ = pattern(win)
        pw1, _ = pattern(tuple(project(r, "r1") for r in win))
        assert r3_to_r1.setdefault((reset, pw3), (reset, pw1)) == (reset, pw1)
    assert len(classes["r3"]) >= len(classes["r1"]) and set(r3_to_r1.values()) == set(classes["r1"])


# ---- 4. the corpus-track state: the state as the observer can name it ------------

UNSEEN = "?"


def quotient(state, binding, cfg):
    """The state re-expressed in the window's names — the corpus-track
    state (v0.2.9 §2, amended per the Codex read of 2026-09-12 [rv-4] [rv-5]).

    Named threads keep their fields under their pattern index. Unnamed
    threads are canonicalized: their fields, and every reference to them,
    are written under anonymous labels a0, a1, … chosen as the
    lexicographically least representation over all orderings of the
    unnamed threads, so relational structure among anonymous threads
    (which anonymous thread owns a lock, which waits, whether two
    references are the same thread) is kept while their structural
    identity is not. A field the kernel never writes under the
    configuration is excluded: the round-robin cursor is constant at
    ε = 1 (Part II §1, v0.2.6) and mapping it through the binding would
    inject binding entropy into the state ([rv-5]); at ε < 1 it is live
    and is mapped like any other thread reference. Program role is not a
    field of the state and is deliberately absent: which program a named
    thread runs is the binding's business, so role uncertainty lives in
    H(S, β | q, w), not in q."""
    import itertools
    n = len(state.pc)
    named = {t: k for k, t in enumerate(binding)}
    unnamed = [t for t in range(n) if t not in named]
    best = None
    for perm in itertools.permutations(unnamed):
        lab = dict(named)
        for j, t in enumerate(perm):
            lab[t] = f"a{j}"
        nm = lambda t: (lab[t] if t is not None else None)
        rep = (tuple((state.pc[t], state.status[t]) for t in binding),
               tuple((state.pc[t], state.status[t]) for t in perm),
               tuple(sorted(str(nm(t)) for t in state.running)),
               tuple(str(nm(o)) for o in state.lock_owner),
               tuple(tuple(str(nm(t)) for t in q) for q in state.lock_wq),
               tuple(tuple((str(nm(t)), r) for t, r in q) for q in state.dev_q),
               (str(nm(state.rr_cursor)) if cfg.epsilon < 1 else None))
        if best is None or rep < best:
            best = rep
    return best


def _H(dist):
    from yupi.queries import state_entropy_bits
    tot = sum(dist.values(), Fraction(0))
    return state_entropy_bits({k: m / tot for k, m in dist.items()})


def corpus_track_entropies(cfg, progs, rung):
    """Law-mass means over pattern windows of: H(S_structural | w),
    H(quotient | w), H(binding | w), H(S, binding | w) — and the canonical
    H(S | window) for the same rung, for comparison."""
    from yupi.queries import state_entropy_bits
    patt, canon = {}, {}
    for reset, win, mass, final in _windows(cfg, progs, rung):
        pw, order = pattern(win)
        d = patt.setdefault((reset, pw), {})
        d[(final, order)] = d.get((final, order), Fraction(0)) + mass
        c = canon.setdefault((reset, win), {})
        c[final] = c.get(final, Fraction(0)) + mass
    out = dict(H_S=0.0, H_quotient=0.0, H_binding=0.0, H_joint=0.0, H_canonical=0.0, chain_rule_gap=0.0)
    for joint in patt.values():
        tot = float(sum(joint.values(), Fraction(0)))
        s, b, q, sbq = {}, {}, {}, {}
        for (st, bind), m in joint.items():
            s[st] = s.get(st, Fraction(0)) + m
            b[bind] = b.get(bind, Fraction(0)) + m
            qq = quotient(st, bind, cfg)
            q[qq] = q.get(qq, Fraction(0)) + m
            sbq[(st, bind, qq)] = sbq.get((st, bind, qq), Fraction(0)) + m
        H_joint = _H(joint)
        # chain rule: H(S, binding | w) = H(quotient | w) + H(S, binding | quotient, w)
        H_rest = 0.0
        byq = {}
        for (st, bind, qq), m in sbq.items():
            byq.setdefault(qq, {})[(st, bind)] = m
        for qq, dd in byq.items():
            H_rest += float(sum(dd.values(), Fraction(0)) / sum(joint.values(), Fraction(0))) * _H(dd)
        out["H_S"] += tot * _H(s); out["H_quotient"] += tot * _H(q); out["H_binding"] += tot * _H(b)
        out["H_joint"] += tot * H_joint
        out["chain_rule_gap"] = max(out["chain_rule_gap"], abs(H_joint - (_H(q) + H_rest)))
    for j in canon.values():
        out["H_canonical"] += float(sum(j.values(), Fraction(0))) * _H(j)
    return out


# Documentary pins (law-mass means, bits, C1 (8,4,2)), corrected 2026-09-12 after the
# Codex read: the first pins (H_quotient 1.8216 / 1.6567 / 1.2709 / 1.0941) mapped the
# ε = 1 cursor through the binding and collapsed anonymous threads to one symbol
# ([rv-4] [rv-5]); they are preserved in the proposal's ledger, not here. H_quotient
# and H_canonical are DIFFERENT targets (the state in the window's names vs the
# structural state under σ₀); the comparison is informative, not a decomposition
# ([rv-6]). At ε = ½ the cursor is live and mapped; its contribution dominates
# H_quotient there, so the figure without the cursor coordinate is pinned beside it.
PINNED = {
    (Fraction(1), "r1"): dict(H_canonical=0.5230, H_quotient=0.6238, H_binding=2.4238, H_S=2.3808, H_joint=2.9468),
    (Fraction(1), "r3"): dict(H_canonical=0.4452, H_quotient=0.4565, H_binding=2.3343, H_S=2.2393, H_joint=2.7795),
    (Fraction(1, 2), "r1"): dict(H_canonical=0.2597, H_quotient=1.3078, H_binding=2.0093, H_S=2.2681, H_joint=2.2690),
    (Fraction(1, 2), "r3"): dict(H_canonical=0.2316, H_quotient=1.1287, H_binding=1.8583, H_S=2.0890, H_joint=2.0899),
}
PINNED_WITHOUT_CURSOR = {(Fraction(1, 2), "r1"): 0.4729, (Fraction(1, 2), "r3"): 0.2939}   # ε = ½ only; at ε = 1 the cursor is already excluded


@pytest.mark.parametrize("eps,rung", sorted(PINNED, key=str))
def test_corpus_track_state_entropy_and_chain_rule(eps, rung):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    e = corpus_track_entropies(cfg, progs, rung)
    assert e["chain_rule_gap"] < 1e-9                                   # H(S,b|w) = H(q|w) + H(S,b|q,w): an identity for any deterministic q, checked in floats
    assert e["H_quotient"] <= e["H_joint"] + 1e-9 and e["H_S"] <= e["H_joint"] + 1e-9
    for k, v in PINNED[(eps, rung)].items():
        assert round(e[k], 4) == v, (k, e[k])
    if (eps, rung) in PINNED_WITHOUT_CURSOR:
        import test_naming_bridge as tb
        orig = tb.quotient
        try:
            tb.quotient = lambda st, b, c: orig(st, b, c)[:-1] + (None,)
            e2 = corpus_track_entropies(cfg, progs, rung)
        finally:
            tb.quotient = orig
        assert round(e2["H_quotient"], 4) == PINNED_WITHOUT_CURSOR[(eps, rung)]


# ---- 5. the 1.208-bit counterexample is the empty-window case ------------------------

def test_fresh_token_query_is_the_uniform_mixture_of_the_counterexample():
    """Clause 2′'s counterexample (tests/test_naming_counterexample.py): at
    C1 tick 4 with no observation, a uniformly bound name's Q2 distribution
    is the mixture of the four structural threads' and has 1.208 bits. In
    the pattern framework that is the query about a token the (empty)
    window never named: the UNSEEN class, whose answer is the mixture over
    the unnamed threads under the prior. Same distribution, exactly
    ([rv-2] of the 2026-09-12 Codex read)."""
    from yupi.enumerator import paths as _paths
    from yupi.queries import entropy_bits
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), c1_programs()
    prior = {}
    for _, prob, final in _paths(cfg, progs, 4):
        prior[final] = prior.get(final, Fraction(0)) + prob
    # pattern side: empty window, binding () — every thread is unnamed; a fresh token is UNSEEN,
    # i.e. one of the n unnamed threads uniformly (σ is a uniform injection)
    unseen = {}
    for s, m in prior.items():
        for t in range(cfg.n_threads):
            a = q2_status(s, t)
            unseen[a] = unseen.get(a, Fraction(0)) + m / cfg.n_threads
    assert unseen == {"RUNNING": Fraction(23, 48), "RUNNABLE": Fraction(23, 48), "IO_BLOCKED": Fraction(1, 24)}
    assert round(entropy_bits(unseen), 3) == 1.208
