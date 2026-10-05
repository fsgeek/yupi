"""The decoy rung r1ᴅ ("r1D") and the self-copy rung r1ꜱ ("r1S")
(docs/three-arm-design-v0.1.md §2–§3), beside the relay r1ʀ ("r1R").

Both are window-level rungs over r1 whose value sits in the OBJECT slot that r1
masks, as an `interfaces.Lit` (NONE when absent):
  r1D: record t's OBJECT = KIND of record t − 1 in the window; NONE for the first record.
  r1S: record t's OBJECT = KIND of record t.
Per rung: a hand example pinned; the next-record map is the last step of the window
map; window-locality; injectivity (dropping the slot gives r1); non-r1 records are
refused; the map commutes with Π_all; the manifest names the rung; the corpus window
is the paired r1 window mapped and is token-matched; the table derived by the
push-forward equals the recursion route and brute force at (8, 4, 2); the gates detect
a broken derivation; ι_kind,m is unchanged for every class at r1S and changed for
some class at r1D.
"""
from fractions import Fraction as F

import pytest

from yupi.config import WorldConfig
from yupi.corpus import windows as W
from yupi.corpus.manifest import Manifest, Split, validate
from yupi.corpus.rendering import EpisodeTable
from yupi.corpus.vocab import MASKED as TOK_MASKED
from yupi.implicit_info import implicit_info
from yupi.interfaces import (MASKED, RELAY_RUNGS, WINDOW_RUNGS, Lit, base_rung, drop_relay, next_map, project,
                             project_window, relay_next, relay_window, window_map)
from yupi.naming import pattern_all
from yupi.pattern_ceiling import ceiling_table, derive_relay_table, relay_gates
from yupi.pattern_enumerator import relay_table_by_paths
from yupi.programs import c1_prime_loop_programs, c1_programs
from yupi.records import Record
from yupi.window import WindowLaw

KEY = bytes(range(32))
SMALL = WindowLaw(8, 4, 2)
FROZEN = WindowLaw(40, 8, 2)
NEW = ("r1D", "r1S")
PROGS = {"c1": c1_programs, "c1prime-loop": c1_prime_loop_programs}


def R1(kind, actor=None):
    return Record(kind, actor, MASKED, MASKED, MASKED)


def RW(kind, actor=None, val=None):
    return Record(kind, actor, val, MASKED, MASKED)


HAND = (R1("DISPATCH", 2), R1("STEP", 2), R1("IDLE"), R1("DISPATCH", 0), R1("ACQUIRE", 2),
        R1("BLOCK", 0), R1("DISPATCH", 2))          # the window of test_relay_window_hand_example_pinned


# ---- the registry -----------------------------------------------------------------------

def test_registry():
    assert RELAY_RUNGS == {"r1R": "r1"}                       # unchanged
    assert set(WINDOW_RUNGS) == {"r1R", "r1D", "r1S"}
    assert all(base_rung(r) == "r1" for r in WINDOW_RUNGS)
    assert window_map("r1R") is relay_window and next_map("r1R") is relay_next
    with pytest.raises(KeyError):
        window_map("r1")


# ---- the transforms ---------------------------------------------------------------------

def test_decoy_hand_example_pinned():
    assert window_map("r1D")(HAND) == (
        RW("DISPATCH", 2, None),                # first record of the window: nothing earlier
        RW("STEP", 2, Lit("DISPATCH")),
        RW("IDLE", None, Lit("STEP")),          # no actor: the decoy does not care
        RW("DISPATCH", 0, Lit("IDLE")),
        RW("ACQUIRE", 2, Lit("DISPATCH")),      # record t − 1, not thread 2's latest (STEP)
        RW("BLOCK", 0, Lit("ACQUIRE")),
        RW("DISPATCH", 2, Lit("BLOCK")),
    )


def test_self_copy_hand_example_pinned():
    assert window_map("r1S")(HAND) == tuple(RW(r.kind, r.actor, Lit(r.kind)) for r in HAND)
    assert window_map("r1S")(HAND)[2] == RW("IDLE", None, Lit("IDLE"))


@pytest.mark.parametrize("rung", NEW)
def test_next_map_is_the_last_step_of_window_map(rung):
    wm, nm = window_map(rung), next_map(rung)
    for k in range(len(HAND)):
        w = HAND[:k]
        for rec in (R1("STEP", 1), R1("IDLE"), R1("DISPATCH", 2)):
            assert wm(w + (rec,))[-1] == nm(w, rec)
    assert nm((), R1("STEP", 1)) == (RW("STEP", 1, None) if rung == "r1D" else RW("STEP", 1, Lit("STEP")))
    assert nm(HAND, R1("STEP", 1)) == RW("STEP", 1, Lit("DISPATCH" if rung == "r1D" else "STEP"))


@pytest.mark.parametrize("rung", NEW)
def test_window_locality(rung):
    wm = window_map(rung)
    tail = (R1("STEP", 1), R1("DISPATCH", 0), R1("STEP", 0))
    a = wm((R1("BLOCK", 1),) + tail)[1:]
    b = wm(tail)
    assert a[1:] == b[1:]
    if rung == "r1D":
        assert a[0].obj == Lit("BLOCK") and b[0].obj is None   # only the history inside the window counts
    else:
        assert a[0] == b[0]


@pytest.mark.parametrize("rung", NEW)
def test_drop_recovers_r1(rung):
    assert drop_relay(window_map(rung)(HAND)) == HAND
    assert drop_relay(window_map(rung)(())) == ()


@pytest.mark.parametrize("rung", NEW)
def test_rejects_non_r1_records(rung):
    bad = Record("ACQUIRE", 0, ("LOCK", 0), MASKED, MASKED)
    with pytest.raises(ValueError):
        window_map(rung)((bad,))
    with pytest.raises(ValueError):
        next_map(rung)((), bad)
    with pytest.raises(ValueError):
        project(R1("STEP", 0), rung)


@pytest.mark.parametrize("rung", NEW)
def test_commutes_with_pattern(rung):
    w = (R1("DISPATCH", 3), R1("STEP", 3), R1("DISPATCH", 1), R1("ACQUIRE", 3), R1("STEP", 1))
    pw, b = pattern_all(w)
    pr, br = pattern_all(window_map(rung)(w))
    assert pr == window_map(rung)(pw) and br == b


@pytest.mark.parametrize("rung", NEW)
def test_project_window(rung):
    w = (Record("DISPATCH", 0, None, None, None), Record("ACQUIRE", 0, ("LOCK", 1), None, None))
    assert project_window(w, rung) == window_map(rung)(tuple(project(r, "r1") for r in w))


# ---- manifest and corpus windows ----------------------------------------------------------

@pytest.mark.parametrize("rung", NEW)
def test_manifest_accepts_the_rung(rung):
    m = Manifest.new(programs="c1prime-loop", epsilon=F(1), T_ep=40, L=8, B=2, rung=rung, run_key=KEY,
                     splits=(Split("train", 0, 10),), git_commit="x")
    validate(m)
    assert m.name() == f"c1prime-loop-40-8-2-{rung}-eps1"


@pytest.mark.parametrize("rung", NEW)
@pytest.mark.parametrize("law,progs,eps", [(SMALL, c1_programs(), F(1)),
                                           (FROZEN, c1_prime_loop_programs(), F(1)),
                                           (FROZEN, c1_prime_loop_programs(), F(1, 2))])
def test_window_is_the_paired_r1_window_mapped(rung, law, progs, eps):
    cfg = WorldConfig.c1(epsilon=eps)
    for ep in range(150):
        w1 = W.draw_window(cfg, progs, law, "r1", KEY, ep)
        wr = W.draw_window(cfg, progs, law, rung, KEY, ep)
        assert (wr.T, wr.U) == (w1.T, w1.U)
        assert wr.records == window_map(rung)(w1.records)
        t = EpisodeTable.draw(KEY, ep, cfg)
        t1, tr = W.serialize(w1, t), W.serialize(wr, t)
        assert len(tr) == len(t1)                                      # token-matched
        body = 1 if w1.reset else 0
        dropped = list(tr[:body])
        for i in range(body, len(tr), 5):
            dropped.extend(tr[i:i + 2] + (TOK_MASKED,) + tr[i + 3:i + 5])
        assert tuple(dropped) == t1                                    # dropping the slot gives r1
        assert W.deserialize(tr, t) == (wr.reset, wr.records)


# ---- the exact side at (8, 4, 2) -----------------------------------------------------------

@pytest.mark.parametrize("rung", NEW)
@pytest.mark.parametrize("progname", ["c1", "c1prime-loop"])
@pytest.mark.parametrize("eps", [F(1), F(1, 2)])
@pytest.mark.parametrize("k", [None, 1, 2, 3, 4])
def test_derived_equals_recursion_route(rung, progname, eps, k):
    cfg, progs = WorldConfig.c1(epsilon=eps), PROGS[progname]()
    t = ceiling_table(cfg, progs, SMALL, ("r1", rung), prefix_len=k)
    derived = derive_relay_table(t["r1"], rung=rung)
    assert derived == t[rung]
    g = relay_gates(t["r1"], derived, rung=rung)
    assert g["n_classes"] == len(t["r1"]) and g["gate_A_kind"] and g["gate_B_record"]
    assert sum(m for m, _ in derived.values()) == (1 if k is None else sum(m for m, _ in t["r1"].values()))
    for key in derived:
        assert (key[0], drop_relay(key[1])) in t["r1"]


@pytest.mark.parametrize("rung", NEW)
@pytest.mark.parametrize("eps", [F(1), F(1, 2)])
def test_derived_equals_brute_force(rung, eps):
    cfg, progs = WorldConfig.c1(epsilon=eps), c1_programs()
    derived = derive_relay_table(ceiling_table(cfg, progs, SMALL, ("r1",))["r1"], rung=rung)
    assert derived == relay_table_by_paths(cfg, progs, SMALL, rung=rung)


@pytest.mark.parametrize("rung", NEW)
def test_rung_tables_differ_from_relay(rung):
    """The rung argument is honoured: the derived table is not the relay's."""
    cfg, progs = WorldConfig.c1(), c1_programs()
    r1 = ceiling_table(cfg, progs, SMALL, ("r1",))["r1"]
    assert derive_relay_table(r1, rung=rung) != derive_relay_table(r1)
    assert derive_relay_table(r1) == derive_relay_table(r1, rung="r1R")


@pytest.mark.parametrize("rung", NEW)
def test_gates_detect_a_broken_derivation(rung):
    cfg, progs = WorldConfig.c1(), c1_programs()
    r1 = ceiling_table(cfg, progs, SMALL, ("r1",))["r1"]
    good = derive_relay_table(r1, rung=rung)
    key, a, b = next((k, a, b) for k, (_, s) in good.items() for a in s for b in s
                     if a.kind != b.kind and s[a] != s[b])
    m, star = good[key]
    swapped = dict(star); swapped[a], swapped[b] = star[b], star[a]      # same multiset, KIND marginal moved
    g = relay_gates(r1, {**good, key: (m, swapped)}, rung=rung)
    assert g["gate_B_record"] and not g["gate_A_kind"]
    merged = dict(star); merged[a] = star[a] + star[b]; del merged[b]    # entropy changed
    g = relay_gates(r1, {**good, key: (m, merged)}, rung=rung)
    assert not g["gate_B_record"]
    # the relay's table is not a valid r1D / r1S table (wrong class image)
    g = relay_gates(r1, derive_relay_table(r1), rung=rung)
    assert not (g["gate_A_kind"] and g["gate_B_record"])


def _iota_by_r1_class(rung, m):
    cfg, progs = WorldConfig.c1(), c1_programs()
    out = []
    for k in (None, 4):
        r1 = ceiling_table(cfg, progs, SMALL, ("r1",), prefix_len=k)["r1"]
        rr = derive_relay_table(r1, rung=rung)
        i1 = implicit_info(r1, m, target=lambda r: r.kind)["per_class"]
        ir = implicit_info(rr, m, target=lambda r: r.kind)["per_class"]
        wm = window_map(rung)
        out.append({key: (i1[key], ir[(key[0], wm(key[1]))]) for key in r1})
    return out


@pytest.mark.parametrize("m", [1, 2, 3, 4])
def test_self_copy_leaves_iota_kind_unchanged_per_class(m):
    for pairs in _iota_by_r1_class("r1S", m):
        assert pairs and all(a == b for a, b in pairs.values()), m


def test_decoy_moves_iota_kind_1_somewhere():
    assert any(a != b for pairs in _iota_by_r1_class("r1D", 1) for a, b in pairs.values())


# ---- the pairing check (scripts/relay_corpus_check.py, three-arm design v0.1 §5) -----------

@pytest.mark.parametrize("rung", NEW)
def test_corpus_pairing_check(rung, tmp_path):
    import sys
    from pathlib import Path

    import numpy as np

    from yupi.corpus.vocab import TOKEN_ID
    from yupi.corpus.writer import generate
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import relay_corpus_check as C
    out = {}
    for r in ("r1", rung):
        m = Manifest.new(programs="c1prime-loop", epsilon=F(1), T_ep=40, L=8, B=2, rung=r, run_key=KEY,
                         splits=(Split("test", 2_000_000, 2_000_100),), git_commit="t")
        out[r], _ = generate(m, tmp_path, workers=1)
    d1, dr = out["r1"], out[rung]
    rep = C.check_split(d1, dr, "test", rung)
    assert rep["passed"] and rep[f"n_{rung}"] == 100 and rep["n_windows_with_a_kind_relay"] > 50
    assert C.check_manifests(d1, dr, rung)["passed"] and not C.check_manifests(d1, dr)["passed"]
    assert not C.check_split(d1, dr, "test")["relay_recomputed_equal"]          # not the relay
    raw = np.fromfile(dr / "test.tokens", dtype="<u2").reshape(100, 41)
    row = next(i for i in range(100) if raw[i, 0] != TOKEN_ID["RESET"])
    raw[row, 2] = TOKEN_ID["IDLE"] if raw[row, 2] != TOKEN_ID["IDLE"] else TOKEN_ID["STEP"]
    raw.tofile(dr / "test.tokens")
    rep = C.check_split(d1, dr, "test", rung)
    assert rep["drop_relay_equals_r1"] and not rep["relay_recomputed_equal"] and not rep["passed"]
