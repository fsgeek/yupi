"""Executable witness 11 (Part II §9 item 11) — predictive rung discrimination.

Pins the 2026-09-03 search (`docs/w11-predictive-rung-search-v0.1.md`,
producer `scripts/w11_predictive_rung_search.py`) so the interface-witness
suite carries it. Recomputed here from the enumerator and `yupi.predict`,
sharing no code with the search script beyond the world.

1. The a-priori emptiness of the map-v4 candidate region: at (14, 12, 2)
   and (14, 14, 2) the r1 partition of windows already equals the r4
   partition (identical `n_windows` per rung in the committed ceilings
   artifacts; r4 refines r1, so equal counts ⇒ equal partitions ⇒
   identical per-window beliefs ⇒ no functional of the belief, τ included,
   can separate any adjacent pair). Read from the artifacts; no enumeration.

2. At (14, 2, 2), the only law with candidate windows (a rung split that
   leaves every Q1/Q2/Q3/Q5 pushforward and the statutory Q4@4 forecast
   exactly unchanged), all of them r3 → r4 and truncated:
   - ε = 1: eight candidates, every one belief-INERT (each piece's belief
     equals the parent's), so no functional of any kind moves;
   - ε = ½: four candidates, each a two-state support differing ONLY in
     the cursor κ. The [IO_COMPLETE(0), IO_COMPLETE(3)] window (and its
     mirror) is the exact-corner witness on the PRIMARY horizon: next-2
     kinds moves by TV = 91258/11287135 ≈ 0.0081 > 0 while ttw4 and lin4
     stay put — below the borrowed Δ_τ = 1/100. The [IO_COMPLETE(2),
     IO_COMPLETE(3)] window (and mirror) moves time-to-next-wake at W = 8
     by 274301873/19544223744 ≈ 0.0140 ≥ Δ_τ, but the statutory Q4 at the
     same secondary horizon moves by 3404179/271447552 ≈ 0.0125 too, so it
     is not a witness at a consistent horizon.
"""
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.forecast import q4_forward
from yupi.interfaces import project
from yupi.predict import next_complete_lineage, next_kinds, time_to_wake
from yupi.programs import c1_programs
from yupi.queries import all_queries, pushforward
from yupi.window import WindowLaw, endpoint_prior

DOCS = pathlib.Path(__file__).parent.parent / "docs"
DELTA_TAU = Fraction(1, 100)


@pytest.mark.parametrize("L", [12, 14])
def test_candidate_region_has_no_split_by_counting(L):
    d = json.load(open(DOCS / f"c1-query-ceilings-14-{L}-2-corrected-2026-08-20.json"))
    for eps in ("1", "1/2"):
        counts = {r["rung"]: r["n_windows"] for r in d["rows"] if r["eps"] == eps}
        assert set(counts) == {"r1", "r2", "r3", "r4"}
        assert len(set(counts.values())) == 1, (L, eps, counts)


@pytest.mark.parametrize("L", [2, 4, 6, 8, 10])
def test_short_contexts_do_split(L):
    d = json.load(open(DOCS / f"c1-query-ceilings-14-{L}-2-corrected-2026-08-20.json"))
    for eps in ("1", "1/2"):
        c = {r["rung"]: r["n_windows"] for r in d["rows"] if r["eps"] == eps}
        assert c["r1"] < c["r2"] < c["r3"] < c["r4"], (L, eps, c)


def _tv(a, b):
    keys = set(a) | set(b)
    return sum(abs(a.get(k, Fraction(0)) - b.get(k, Fraction(0))) for k in keys) / 2


def _mix(belief, fn):
    out = {}
    for s, m in belief.items():
        for k, q in fn(s).items():
            out[k] = out.get(k, Fraction(0)) + m * q
    return out


def _belief(joint):
    mass = sum(joint.values(), Fraction(0))
    return mass, {s: m / mass for s, m in joint.items()}


class _World:
    """r3 → r4 splits of truncated (14, 2, 2) windows at one ε, with the
    statutory fact set and the τ functionals."""

    def __init__(self, eps):
        self.cfg = cfg = WorldConfig.c1(epsilon=eps)
        self.progs = progs = c1_programs()
        law = WindowLaw(T_ep=14, L=2, B=2)
        w_T = endpoint_prior(law)
        self.r3, self.r4, parent = {}, {}, {}
        for T in law.endpoints():
            u = law.offset(T)
            if u == 0:
                continue
            for recs, prob, final in paths(cfg, progs, T):
                win = recs[u:]
                k3 = tuple(project(r, "r3") for r in win)
                k4 = tuple(project(r, "r4") for r in win)
                self.r3.setdefault(k3, {})
                self.r3[k3][final] = self.r3[k3].get(final, Fraction(0)) + w_T * prob
                self.r4.setdefault(k4, {})
                self.r4[k4][final] = self.r4[k4].get(final, Fraction(0)) + w_T * prob
                parent[k4] = k3
        self.children = {}
        for k4, k3 in parent.items():
            self.children.setdefault(k3, []).append(k4)
        self.facts = [(n, f) for n, f in all_queries(cfg) if n.startswith(("Q1", "Q2", "Q3", "Q5"))]
        m4, mk, mw, ml = {}, {}, {}, {}
        self.fn = {
            "Q4@4": lambda s: q4_forward(s, cfg, progs, 4, m4),
            "Q4@8": lambda s: q4_forward(s, cfg, progs, 8, m4),
            "kinds2": lambda s: next_kinds(s, cfg, progs, 2, mk),
            "ttw4": lambda s: time_to_wake(s, cfg, progs, 4, mw),
            "lin4": lambda s: next_complete_lineage(s, cfg, progs, 4, ml),
            "ttw8": lambda s: time_to_wake(s, cfg, progs, 8, mw),
            "lin8": lambda s: next_complete_lineage(s, cfg, progs, 8, ml),
        }

    def unchanged(self, b, parent):
        return (all(pushforward(b, f) == pushforward(parent, f) for _, f in self.facts)
                and _mix(b, self.fn["Q4@4"]) == _mix(parent, self.fn["Q4@4"]))

    def candidates(self):
        out = []
        for k3, k4s in self.children.items():
            if len(k4s) < 2:
                continue
            _, parent = _belief(self.r3[k3])
            pieces = [_belief(self.r4[k])[1] for k in k4s]
            if all(self.unchanged(b, parent) for b in pieces):
                out.append((k3, parent, list(zip(k4s, pieces))))
        return out

    def window(self, kinds_actors):
        for k3, parent, pieces in self.candidates():
            if tuple((r.kind, r.actor) for r in k3) == kinds_actors:
                return parent, pieces
        raise KeyError(kinds_actors)

    def tv(self, b, parent, name):
        return _tv(_mix(b, self.fn[name]), _mix(parent, self.fn[name]))


@pytest.fixture(scope="module")
def world_half():
    return _World(Fraction(1, 2))


@pytest.fixture(scope="module")
def world_one():
    return _World(Fraction(1))


def test_eps_one_candidates_are_all_inert(world_one):
    cands = world_one.candidates()
    assert len(cands) == 8
    for _, parent, pieces in cands:
        assert all(b == parent for _, b in pieces)


def test_eps_half_candidates_differ_only_in_cursor(world_half):
    cands = world_half.candidates()
    assert len(cands) == 4
    for _, parent, pieces in cands:
        assert len(parent) == 2 and all(set(b) == set(parent) for _, b in pieces)
        s_a, s_b = sorted(parent, key=lambda s: s.rr_cursor)
        assert s_a.rr_cursor != s_b.rr_cursor
        assert {s_a.rr_cursor, s_b.rr_cursor} in ({1, 2}, {2, 3})
        for f in ("pc", "status", "running", "lock_owner", "lock_wq", "dev_q"):
            assert getattr(s_a, f) == getattr(s_b, f), f
        assert any(b != parent for _, b in pieces)   # not inert


def test_exact_corner_witness_on_primary_horizon(world_half):
    parent, pieces = world_half.window((("IO_COMPLETE", 0), ("IO_COMPLETE", 3)))
    tvs = {n: max(world_half.tv(b, parent, n) for _, b in pieces)
           for n in ("kinds2", "ttw4", "lin4", "Q4@8")}
    assert tvs["kinds2"] == Fraction(91258, 11287135)   # ≈ 0.0081: > 0, < Δ_τ
    assert 0 < tvs["kinds2"] < DELTA_TAU
    assert tvs["ttw4"] == 0 and tvs["lin4"] == 0
    assert tvs["Q4@8"] < Fraction(1, 10000)             # secondary fact forecast ~unchanged


def test_secondary_horizon_separation_is_matched_by_q4(world_half):
    parent, pieces = world_half.window((("IO_COMPLETE", 2), ("IO_COMPLETE", 3)))
    tvs = {n: max(world_half.tv(b, parent, n) for _, b in pieces)
           for n in ("kinds2", "ttw4", "lin4", "ttw8", "Q4@8")}
    assert tvs["ttw8"] == Fraction(274301873, 19544223744)   # ≈ 0.0140 ≥ Δ_τ
    assert tvs["ttw8"] >= DELTA_TAU
    assert tvs["Q4@8"] == Fraction(3404179, 271447552)       # ≈ 0.0125 ≥ Δ_τ — Q4 moves too
    assert tvs["Q4@8"] >= DELTA_TAU
    assert tvs["kinds2"] == 0 and tvs["ttw4"] == 0 and tvs["lin4"] == 0


def test_no_candidate_survives_delta_on_a_consistent_horizon(world_half):
    for _, parent, pieces in world_half.candidates():
        primary = max(world_half.tv(b, parent, n) for _, b in pieces for n in ("kinds2", "ttw4", "lin4"))
        assert primary < DELTA_TAU
        strict = all(world_half.tv(b, parent, "Q4@8") == 0 for _, b in pieces)
        assert not strict
