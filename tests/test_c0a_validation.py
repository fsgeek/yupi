# tests/test_c0a_validation.py
"""Part II §6: filter must match path-sum enumeration exactly (Fraction ==),
on every distinct observation sequence, at every prefix, for every rung."""
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import c0a_programs
from yupi.enumerator import paths, posterior_by_paths
from yupi.interfaces import project
from yupi.filter import initial_belief, step

CFG, PROGS, H = WorldConfig.c0a(), c0a_programs(), 6

def test_bit_for_bit_all_histories_all_rungs():
    for rung in ("r1", "r2", "r3", "r4"):
        obs_seqs = {tuple(project(r, rung) for r in recs) for recs, _, _ in paths(CFG, PROGS, H)}
        for obs in sorted(obs_seqs, key=repr):
            belief = initial_belief(CFG)
            for i, o in enumerate(obs, 1):
                belief = step(belief, o, rung, CFG, PROGS)
                exact = posterior_by_paths(CFG, PROGS, list(obs[:i]), rung)
                assert belief == exact, (rung, obs[:i])
