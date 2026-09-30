"""The relay rung r1ʀ (docs/relay-intervention-design-v0.1.md §2–§3).

r1ʀ is r1 with the OBJECT slot (which r1 masks) filled, per record t, by
the KIND of the most recent earlier record in the same window with the same
actor as t (NONE when there is none, or t has no actor). A window-level
transform: window-local, literal under Π_all renaming, token-matched,
paired with the r1 corpus. The rung's name in code and on disk is "r1R".
"""
from fractions import Fraction as F

import pytest

from yupi.config import WorldConfig
from yupi.corpus import windows as W
from yupi.corpus.manifest import Manifest, Split, validate
from yupi.corpus.rendering import EpisodeTable, render, unrender
from yupi.corpus.vocab import MASKED as TOK_MASKED, NONE as TOK_NONE, VOCAB_SHA256
from yupi.interfaces import MASKED, Lit, RELAY_RUNGS, drop_relay, project, project_window, relay_next, relay_window
from yupi.naming import extend_binding, pattern_all, rename_all
from yupi.pattern_ceiling import (derive_relay_table, key_from_serial, record_from_serial, serial_key,
                                  serial_record)
from yupi.programs import c1_prime_loop_programs, c1_programs
from yupi.records import Record
from yupi.window import WindowLaw

KEY = bytes(range(32))
SMALL = WindowLaw(8, 4, 2)
FROZEN = WindowLaw(40, 8, 2)


def R1(kind, actor=None):
    return Record(kind, actor, MASKED, MASKED, MASKED)


def RR(kind, actor=None, relay=None):
    return Record(kind, actor, relay, MASKED, MASKED)


# ---- the transform ---------------------------------------------------------------

def test_relay_window_hand_example_pinned():
    w = (R1("DISPATCH", 2), R1("STEP", 2), R1("IDLE"), R1("DISPATCH", 0), R1("ACQUIRE", 2),
         R1("BLOCK", 0), R1("DISPATCH", 2))
    assert relay_window(w) == (
        RR("DISPATCH", 2, None),               # first record of the window: nothing earlier
        RR("STEP", 2, Lit("DISPATCH")),
        RR("IDLE", None, None),                # no actor
        RR("DISPATCH", 0, None),               # thread 0 not seen earlier in the window
        RR("ACQUIRE", 2, Lit("STEP")),         # most recent earlier record of thread 2, not the first
        RR("BLOCK", 0, Lit("DISPATCH")),
        RR("DISPATCH", 2, Lit("ACQUIRE")),
    )
    assert drop_relay(relay_window(w)) == w


def test_relay_next_is_the_step_of_relay_window():
    w = (R1("DISPATCH", 1), R1("IO_ISSUE", 1), R1("DISPATCH", 3))
    assert relay_next(w, R1("STEP", 1)) == RR("STEP", 1, Lit("IO_ISSUE"))
    assert relay_next(w, R1("STEP", 3)) == RR("STEP", 3, Lit("DISPATCH"))
    assert relay_next(w, R1("STEP", 0)) == RR("STEP", 0, None)
    assert relay_next(w, R1("IDLE")) == RR("IDLE", None, None)
    assert relay_window(w + (R1("STEP", 1),))[-1] == relay_next(w, R1("STEP", 1))


def test_relay_is_window_local():
    # the same last three records after different histories get the same relays
    tail = (R1("STEP", 1), R1("DISPATCH", 0), R1("STEP", 0))
    a = relay_window((R1("BLOCK", 1),) + tail)[1:]
    b = relay_window(tail)
    assert a[0].obj == Lit("BLOCK") and b[0].obj is None      # only the history inside the window counts
    assert a[1:] == b[1:]


def test_relay_rejects_non_r1_records():
    with pytest.raises(ValueError):
        relay_window((Record("ACQUIRE", 0, ("LOCK", 0), MASKED, MASKED),))


def test_relay_is_not_a_per_record_projection():
    assert RELAY_RUNGS == {"r1R": "r1"}
    with pytest.raises(ValueError):
        project(R1("STEP", 0), "r1R")
    w = (Record("DISPATCH", 0, None, None, None), Record("ACQUIRE", 0, ("LOCK", 1), None, None))
    assert project_window(w, "r1R") == (RR("DISPATCH", 0, None), RR("ACQUIRE", 0, Lit("DISPATCH")))
    assert project_window(w, "r2") == tuple(project(r, "r2") for r in w)     # base rungs unchanged


# ---- literal under renaming ----------------------------------------------------------

def test_lit_passes_through_pi_all_and_renaming():
    rec = RR("STEP", 7, Lit("DISPATCH"))
    pr, b = extend_binding(((), (), (), ()), rec)
    assert pr == RR("STEP", 0, Lit("DISPATCH")) and b == ((7,), (), (), ())
    sigma = {"thread": {7: "T33"}, "lock": {}, "device": {}, "request": {}}
    assert rename_all(rec, sigma) == Record("STEP", "T33", Lit("DISPATCH"), MASKED, MASKED)


def test_relay_commutes_with_pattern():
    w = (R1("DISPATCH", 3), R1("STEP", 3), R1("DISPATCH", 1), R1("ACQUIRE", 3), R1("STEP", 1))
    pw, b = pattern_all(w)
    pr, br = pattern_all(relay_window(w))
    assert pr == relay_window(pw) and br == b


# ---- rendering: token-matched, vocabulary unchanged --------------------------------------

def test_render_relay_in_object_slot():
    cfg = WorldConfig.c1()
    t = EpisodeTable.draw(KEY, 0, cfg)
    toks = render(RR("ACQUIRE", 1, Lit("STEP")), t)
    assert toks == ("ACQUIRE", t.thread[1], "STEP", TOK_MASKED, TOK_MASKED)
    assert render(RR("DISPATCH", 1, None), t) == ("DISPATCH", t.thread[1], TOK_NONE, TOK_MASKED, TOK_MASKED)
    assert unrender(toks, t) == RR("ACQUIRE", 1, Lit("STEP"))
    assert VOCAB_SHA256 == "ed9a50c5029403554cfe34d8d29758cad172f4414c2fcd06fb687f949a789604"


@pytest.mark.parametrize("law,progs,eps", [(SMALL, c1_programs(), F(1)),
                                           (FROZEN, c1_prime_loop_programs(), F(1)),
                                           (FROZEN, c1_prime_loop_programs(), F(1, 2))])
def test_r1R_window_is_the_paired_r1_window_relayed(law, progs, eps):
    cfg = WorldConfig.c1(epsilon=eps)
    for ep in range(150):
        w1 = W.draw_window(cfg, progs, law, "r1", KEY, ep)
        wr = W.draw_window(cfg, progs, law, "r1R", KEY, ep)
        assert (wr.T, wr.U) == (w1.T, w1.U)
        assert wr.records == relay_window(w1.records)
        t = EpisodeTable.draw(KEY, ep, cfg)
        t1, tr = W.serialize(w1, t), W.serialize(wr, t)
        assert len(tr) == len(t1)                                      # token-matched
        body = 1 if w1.reset else 0
        dropped = list(tr[:body])
        for i in range(body, len(tr), 5):
            dropped.extend(tr[i:i + 2] + (TOK_MASKED,) + tr[i + 3:i + 5])
        assert tuple(dropped) == t1                                    # dropping the relay slot gives r1
        assert W.deserialize(tr, t) == (wr.reset, wr.records)


def test_manifest_accepts_r1R():
    m = Manifest.new(programs="c1prime-loop", epsilon=F(1), T_ep=40, L=8, B=2, rung="r1R", run_key=KEY,
                     splits=(Split("train", 0, 10),), git_commit="x")
    validate(m)
    assert m.name() == "c1prime-loop-40-8-2-r1R-eps1"


# ---- exact serialization and the derived table ------------------------------------------

def test_serial_record_with_relay():
    r = RR("STEP", 0, Lit("IO_COMPLETE"))
    assert serial_record(r) == "STEP,0,K:IO_COMPLETE,MASKED,MASKED"
    assert record_from_serial(serial_record(r)) == r
    assert record_from_serial("IDLE,NONE,NONE,MASKED,MASKED") == RR("IDLE", None, None)
    key = (True, (RR("DISPATCH", 0, None), RR("STEP", 0, Lit("DISPATCH"))))
    assert key_from_serial(serial_key(key)) == key


def test_derive_relay_table_hand_example():
    pw = (R1("DISPATCH", 0), R1("STEP", 0), R1("DISPATCH", 1))
    table = {(False, pw): (F(1, 3), {R1("STEP", 1): F(1, 2), R1("BLOCK", 0): F(1, 4), R1("IDLE"): F(1, 4)}),
             (True, (R1("DISPATCH", 0),)): (F(2, 3), {R1("STEP", 0): F(1)})}
    out = derive_relay_table(table)
    assert out == {
        (False, (RR("DISPATCH", 0, None), RR("STEP", 0, Lit("DISPATCH")), RR("DISPATCH", 1, None))):
            (F(1, 3), {RR("STEP", 1, Lit("DISPATCH")): F(1, 2), RR("BLOCK", 0, Lit("STEP")): F(1, 4),
                       RR("IDLE", None, None): F(1, 4)}),
        (True, (RR("DISPATCH", 0, None),)): (F(2, 3), {RR("STEP", 0, Lit("DISPATCH")): F(1)}),
    }
