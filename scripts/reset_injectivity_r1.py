"""EXPLORATORY check (2026-10-13; whole-draft review W8): structural-observer injectivity from reset at r1 on the
frozen world (WorldConfig.c1, c1prime-loop programs), for windows of up to 8 records. It enumerates every
transition path from initial_state and confirms that distinct paths never share an r1 projection, i.e. every reset
window of length <= 8 has a point-mass state posterior for an observer with structural ids. Also r0 for contrast.

  uv run python scripts/reset_injectivity_r1.py --eps 1 --L 8
"""
import argparse
import json
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.interfaces import project
from yupi.kernel import enabled
from yupi.programs import c1_prime_loop_programs
from yupi.records import record_of
from yupi.state import initial_state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eps", default="1")
    ap.add_argument("--L", type=int, default=8)
    a = ap.parse_args()
    cfg = WorldConfig.c1(epsilon=Fraction(a.eps))
    progs = c1_prime_loop_programs()
    out = {"eps": a.eps, "L": a.L, "rungs": {}}
    for rung in ("r1", "r0"):
        frontier = {(): {initial_state(cfg)}}       # r-projected prefix -> set of states reachable with it
        worst = []
        for t in range(1, a.L + 1):
            nxt = {}
            for key, states in frontier.items():
                for s in states:
                    for tr, p in enabled(s, cfg, progs):
                        if p == 0:
                            continue
                        k2 = key + (project(record_of(tr), rung),)
                        nxt.setdefault(k2, set()).add(tr.next_state)
            frontier = nxt
            mx = max(len(v) for v in frontier.values())
            worst.append(dict(t=t, n_prefixes=len(frontier), max_states_per_prefix=mx))
            print(rung, worst[-1], flush=True)
        out["rungs"][rung] = worst
    print(json.dumps(out))


if __name__ == "__main__":
    main()
