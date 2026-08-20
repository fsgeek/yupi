"""Drift table: buggy-kernel raws vs corrected-kernel raws (2026-08-20).

(run: python scripts/corrected_drift_table.py)

Round-two audit repair: the first drift table was produced by an uncommitted
scratch script whose leaf filter (a regex) silently excluded leaves such as
`resolved_mass` and the per-endpoint Q4 gaps, understating three cells. This
committed producer uses ALL shared numeric leaves — counts included, reported
separately from [0,1)-scale quantities by a size heuristic documented here:
a leaf with |old| >= 10 is classed a count, otherwise a quantity. Both
classes' maxima are printed per pair.
"""
import glob
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield path, float(o)

def pairs():
    out = []
    for new in sorted(glob.glob(os.path.join(REPO, "docs", "c1-*-corrected-2026-08-20.json"))):
        stem = os.path.basename(new).replace("-corrected-2026-08-20.json", "")
        cands = [f for f in glob.glob(os.path.join(REPO, "docs", stem + "*raw*.json"))
                 if "corrected" not in f and "perT" not in f]
        if not cands and stem == "c1-support-exact":
            cands = glob.glob(os.path.join(REPO, "docs", "c1-support-exact-2026-08-14.json"))
        if cands:
            out.append((sorted(cands)[-1], new, stem))
        else:
            print(f"| {stem} | (no buggy-kernel counterpart) | — | — |")
    return out

def main():
    print("| note | max quantity drift | where | max count drift |")
    print("|---|---|---|---|")
    for old_f, new_f, stem in pairs():
        old = dict(leaves(json.load(open(old_f))))
        new = dict(leaves(json.load(open(new_f))))
        shared = set(old) & set(new)
        q = [(abs(old[k] - new[k]), k) for k in shared if abs(old[k]) < 10]
        c = [(abs(old[k] - new[k]), k) for k in shared if abs(old[k]) >= 10]
        mq = max(q) if q else (0.0, "-")
        mc = max(c) if c else (0.0, "-")
        where = f"{mq[1].lstrip('.')} {old.get(mq[1],0):.4f}→{new.get(mq[1],0):.4f}" if mq[0] > 0 else "—"
        print(f"| {stem} | {mq[0]:.5f} | {where} | {mc[0]:.0f} |")

if __name__ == "__main__":
    main()
