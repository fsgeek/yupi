"""Tables from the release-actor raws (scripts/learner_release_actor.py).

  uv run python scripts/learner_release_actor_summary.py docs/learner-release-actor-*-2026-09-24.json

Per cell and kind (RELEASE, BLOCK, ACQUIRE): per seed the ACTOR-field excess, the
ceiling's H*(actor | kind) and the exposure ratio; then, where labels were given,
the same on windows whose lock has a prefix-determined owner vs an uncertain one.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main(paths):
    by = defaultdict(dict)
    for p in paths:
        d = json.loads(Path(p).read_text())
        m = re.search(r"actor-(r\d-eps[0-9_]+)-2M-seed(\d+)", p)
        by[m.group(1)][int(m.group(2))] = d
    for kind in ("RELEASE", "BLOCK", "ACQUIRE"):
        print(f"\n**{kind}** (record k + 1 realized as {kind}; ACTOR-field excess vs the ceiling's H*(actor | {kind}), bits):\n")
        print("| cell | seeds | share of windows | actor excess per seed | pooled ± sd | H*(actor | kind) | exposure ratio per seed | pooled |")
        print("|---|---|---|---|---|---|---|---|")
        for cell, seeds in sorted(by.items()):
            ss = sorted(seeds)
            st = [seeds[s]["by_kind"].get(kind) for s in ss]
            if not all(st):
                continue
            ex = np.array([t["actor_excess"] for t in st]); h = np.array([t["h_actor"] for t in st]); er = np.array([t["exposure_ratio"] for t in st])
            print(f"| {cell} | {len(ss)} | {np.mean([t['frac'] for t in st]):.3f} | {' / '.join(f'{v:.3f}' for v in ex)} | **{ex.mean():.3f}** ± {ex.std(ddof=1) if len(ex) > 1 else 0:.3f} | "
                  f"{h.mean():.3f} | {' / '.join(f'{v:.2f}' for v in er)} | **{er.mean():.2f}** |")
        rows = []
        for cell, seeds in sorted(by.items()):
            for s in sorted(seeds):
                o = seeds[s].get("by_kind_owner", {}).get(kind)
                if o:
                    det, unc = o.get("determined"), o.get("uncertain")
                    rows.append((cell, s, det, unc))
        if rows:
            print(f"\nBy whether the prefix determines the lock's owner ({kind} windows with §16 labels):\n")
            print("| cell | seed | determined: n / actor excess / H* / exposure | uncertain: n / actor excess / H* / exposure |")
            print("|---|---|---|---|")
            f = lambda t: "—" if not t else f"{t['n']} / {t['actor_excess']:.3f} / {t['h_actor']:.3f} / {('%.2f' % t['exposure_ratio']) if t['exposure_ratio'] is not None else '—'}"
            for cell, s, det, unc in rows:
                print(f"| {cell} | {s} | {f(det)} | {f(unc)} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
