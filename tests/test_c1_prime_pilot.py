"""Pins for `docs/c1-prime-pilot-note-v0.1.md`: at T ≤ 14 no C1-shaped
world reaches recurring contention — about five instructions execute in
fourteen records and re-acquisition has probability ≈ 0.003 — so the pilot
is blocked by the horizon, not the programs.
"""
from fractions import Fraction

import pytest

from yupi.config import WorldConfig
from yupi.enumerator import paths
from yupi.programs import programs_for


def _stats(name, T):
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), programs_for(name)
    ps = paths(cfg, progs, T)
    instr = sum(p * sum(s.pc) for _, p, s in ps)
    disp = sum(p * sum(1 for r in recs if r.kind == "DISPATCH") for recs, p, _ in ps)
    reacq = sum(p for recs, p, _ in ps
                if any(sum(1 for r in recs if r.kind == "ACQUIRE" and r.actor == i) >= 2 for i in (0, 2)))
    return len(ps), float(instr), float(disp), float(reacq)


@pytest.mark.parametrize("name,n_paths,instr,disp,reacq", [
    ("c1", 308690, 4.85, 7.13, 0.0), ("c1prime", 396978, 4.99, 7.14, 0.003)])
def test_throughput_at_T14(name, n_paths, instr, disp, reacq):
    n, i, d, r = _stats(name, 14)
    assert n == n_paths
    assert round(i, 2) == instr and round(d, 2) == disp
    assert round(r, 3) == reacq
    assert d > 7 and i < 5.1          # half the records are DISPATCH; ~5 instructions in 14 records


def test_c1prime_same_price_as_c1_and_no_termination():
    cfg, progs = WorldConfig.c1(epsilon=Fraction(1)), programs_for("c1prime")
    ps = paths(cfg, progs, 14)
    assert sum(p * sum(1 for st in s.status if st[0] == "TERMINATED") for _, p, s in ps) == 0
    assert max(max(s.pc) for _, _, s in ps) == 6
