"""Rung degeneracy by truncation depth (`docs/partition-identity-note-v0.1.md`):
the r1..r4 window partitions coincide iff the window law drops at most two
records (U = T_ep − L ≤ 2). Pinned two ways — from every committed C1
ceilings artifact, and by fresh enumeration on C0b (both disciplines) and
C1 at B = 1 — plus the fieldless-prefix fact the argument rests on.
"""
import glob
import json
import pathlib
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.interfaces import project
from yupi.programs import c0b_programs, c1_programs
from yupi.window import WindowLaw

DOCS = pathlib.Path(__file__).parent.parent / "docs"
RUNGS = ("r1", "r2", "r3", "r4")


def test_every_committed_ceilings_artifact_obeys_u_le_2():
    files = sorted(glob.glob(str(DOCS / "c1-query-ceilings-*.json")))
    assert len(files) >= 40
    n_rows = 0
    for f in files:
        d = json.load(open(f))
        law = d["law"]
        U = law["T_ep"] - law["L"]
        for eps in {r["eps"] for r in d["rows"]}:
            counts = [next(r["n_windows"] for r in d["rows"] if r["eps"] == eps and r["rung"] == g)
                      for g in RUNGS]
            assert counts == sorted(counts), (f, eps, counts)      # refinement
            assert (len(set(counts)) == 1) == (U <= 2), (f, eps, U, counts)
            n_rows += 1
    assert n_rows >= 70


def _counts(cfg, progs, T_ep, B, L, cache):
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    keys = {g: set() for g in RUNGS}
    for T in law.endpoints():
        u = law.offset(T)
        for recs, _, _ in cache[T]:
            for g in RUNGS:
                keys[g].add((u == 0, tuple(project(x, g) for x in recs[u:])))
    return [len(keys[g]) for g in RUNGS]


@pytest.mark.parametrize("disc", ["fifo", "stochastic"])
def test_c0b_partitions_coincide_iff_u_le_2(disc):
    cfg, progs = WorldConfig.c0b(discipline=disc), c0b_programs()
    cache = {T: paths(cfg, progs, T) for T in range(1, 9)}
    expect_equal = {"fifo": 102, "stochastic": 142}[disc]
    for L in range(1, 9):
        c = _counts(cfg, progs, 8, 1, L, cache)
        if 8 - L <= 2:
            assert c == [expect_equal] * 4, (L, c)
        else:
            assert c[0] < c[3], (L, c)


def test_c1_b1_partitions_coincide_iff_u_le_2():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs()
    cache = {T: paths(cfg, progs, T) for T in range(1, 11)}
    for L, expect in ((7, None), (8, 17624), (9, 24700), (10, 24878)):
        c = _counts(cfg, progs, 10, 1, L, cache)
        if expect is None:
            assert c[0] == 12471 and c[3] == 13090, c
        else:
            assert c == [expect] * 4, (L, c)


def test_fieldless_prefix():
    """C1: the first two records from reset are always DISPATCH; C0b: DISPATCH
    then IO_ISSUE with forced object and request id 0."""
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1, 2)), c1_programs()
    firsts = {tuple(r.kind for r in recs[:2]) for recs, _, _ in paths(cfg, progs, 3)}
    assert firsts == {("DISPATCH", "DISPATCH")}
    cfg, progs = WorldConfig.c0b(discipline="stochastic"), c0b_programs()
    seconds = {(recs[0].kind, recs[1].kind, recs[1].obj, recs[1].lineage)
               for recs, _, _ in paths(cfg, progs, 2)}
    assert seconds == {("DISPATCH", "IO_ISSUE", ("DEV", 0), 0)}
