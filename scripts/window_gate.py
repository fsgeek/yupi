"""Two-path gate for a window law on the window-process recursion: every
(or the N largest-support) window's posterior from the exact filter
(`window_filter.filter_window_with_evidence`, filter side of the firewall)
compared Fraction for Fraction with the recursion's aggregate
(`window_process.window_law_aggregate`, enumerator side). Both the window's
law mass and its normalized state marginal must agree exactly.

(run: python scripts/window_gate.py T_ep L B rung [--top N] [out.json];
 programs from YUPI_PROGRAMS, ε grid from yupi.eps_grid)

Owed by `docs/looping-exit-law-freeze-v0.1.md` §5 item 2: price the gate on
the largest supports first (--top 40), then run it in full under B2
(≤ 8 GB per filtering process). Any mismatch voids the law. Exploratory
instrument; the gate's PASS is what makes a ceiling under the law
statutory, nothing here is a ceiling itself.
"""
import json
import os
import resource
import sys
import time
from fractions import Fraction

from yupi.config import WorldConfig
from yupi.eps_grid import eps_grid
from yupi.programs import programs_for
from yupi.window import WindowLaw
from yupi.window_filter import filter_window_with_evidence
from yupi.window_process import window_law_aggregate


def gate(cfg, progs, law, rung, top=None):
    """Run the gate; returns a dict with n, mismatches (list of window
    descriptions), seconds, max_support, and per-window seconds for the
    slowest ten. Exact comparison; no tolerance."""
    agg = window_law_aggregate(cfg, progs, law, rung)
    items = sorted(agg.items(), key=lambda kv: -len(kv[1]))
    if top is not None:
        items = items[:top]
    mismatches = []
    timings = []
    t0 = time.time()
    for (reset, window), joint in items:
        mass = sum(joint.values(), Fraction(0))
        expected = {s: m / mass for s, m in joint.items()}
        t1 = time.time()
        post, evidence = filter_window_with_evidence(cfg, progs, law, list(window), rung, reset)
        timings.append((time.time() - t1, len(joint)))
        if evidence != mass or post.state_marginal() != expected:
            mismatches.append(dict(reset=reset, window=[r.kind for r in window], support=len(joint),
                                   mass_recursion=str(mass), mass_filter=str(evidence)))
    timings.sort(reverse=True)
    return dict(n=len(items), n_windows_total=len(agg), mismatches=mismatches, seconds=time.time() - t0,
                max_support=max((len(j) for _, j in items), default=0),
                slowest=[dict(seconds=s, support=k) for s, k in timings[:10]],
                mean_seconds_per_window=(sum(s for s, _ in timings) / len(timings)) if timings else None)


def main():
    args = [a for a in sys.argv[1:]]
    top = None
    if "--top" in args:
        i = args.index("--top")
        top = int(args[i + 1])
        args = args[:i] + args[i + 2:]
    T_ep, L, B = (int(a) for a in args[:3])
    rung = args[3]
    law = WindowLaw(T_ep=T_ep, L=L, B=B)
    out = dict(law=dict(T_ep=T_ep, L=L, B=B), rung=rung, top=top,
               programs=os.environ.get("YUPI_PROGRAMS", "c1"), rows=[])
    for eps in eps_grid():
        cfg = WorldConfig.c1(epsilon=eps)
        r = gate(cfg, programs_for(), law, rung, top)
        r["eps"] = str(eps)
        r["peak_rss_kb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        out["rows"].append(r)
        n_total = r["n_windows_total"]
        est = r["mean_seconds_per_window"] * n_total if r["mean_seconds_per_window"] else None
        print(f"eps={str(eps):>3} {rung} ({T_ep},{L},{B}): gated {r['n']}/{n_total} windows, "
              f"mismatches={len(r['mismatches'])}, {r['seconds']:.1f}s, max support {r['max_support']}, "
              f"mean {r['mean_seconds_per_window']:.4f}s/window → full run ≈ {est/3600:.2f} h at this rate "
              f"(top-N is the slowest tail), rss={r['peak_rss_kb']/1e6:.2f}GB", flush=True)
    if len(args) > 4:
        json.dump(out, open(args[4], "w"), indent=1)
        print(f"raw JSON -> {args[4]}", flush=True)


if __name__ == "__main__":
    main()
