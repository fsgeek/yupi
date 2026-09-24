"""Tables from the per-window link raws (scripts/learner_probe_link.py).

  uv run python scripts/learner_probe_link_summary.py docs/learner-probe-link-*-held-2026-09-24.json

Per (cell, lock): for every seed the determined-subset quartile gap (top − bottom
probe-CE quartile in mean excess, bits) with its permutation p, on ALL windows and
on the RELEVANT windows (record k+1 on lock l); then the class-fixed-effects gap
and the between-class Spearman on the relevant determined windows; and the relevant
determined gap after removing means within 50 bins of log(1 + training count).
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def cell_of(path):
    m = re.search(r"link-(r\d-eps[0-9_]+)-2M-seed(\d+)", path)
    return m.group(1), int(m.group(2))


def fmt(g, p):
    if g is None:
        return "—"
    star = "**" if p is not None and p <= 0.025 else ""
    return f"{star}{g:+.3f}{star} ({p:.2f})" if p is not None else f"{g:+.3f}"


def main(paths):
    by = defaultdict(dict)
    for p in paths:
        d = json.loads(Path(p).read_text())
        cell, seed = cell_of(p)
        for l, r in d["by_lock"].items():
            by[(cell, int(l))][seed] = r
    print("| cell | lock | seed | layer | all determined: gap (p) | relevant n | relevant determined: gap (p) | … residual within training-count bins: gap (p) | within class: gap (p) | between classes: ρ (p) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for (cell, l), seeds in sorted(by.items()):
        for seed, r in sorted(seeds.items()):
            det = r.get("determined", {}); qa = det.get("quartiles_struct", {})
            rel = r.get("relevant") or {}; rd = rel.get("determined", {}); qr = rd.get("quartiles_struct", {})
            wc = (rd.get("residual_class") or {}).get("struct") or {}
            bc = (rd.get("class_level") or {}).get("struct") or {}
            cf = (rd.get("class_frequency") or {}).get("struct") or {}
            print(f"| {cell} | {l} | {seed} | {r['layer']} | {fmt(qa.get('gap'), (qa.get('null') or {}).get('p_ge'))} | {r.get('n_relevant', '—')} | "
                  f"{fmt(qr.get('gap'), (qr.get('null') or {}).get('p_ge'))} | {fmt(cf.get('gap'), (cf.get('null') or {}).get('p_ge'))} | {fmt(wc.get('gap'), (wc.get('null') or {}).get('p_ge'))} | "
                  f"{fmt(bc.get('spearman'), (bc.get('null') or {}).get('p_ge'))} |")
    # counts of positive / significant per cell on the relevant determined windows
    print()
    print("| cell | (lock, seed) pairs | relevant determined gap > 0 | p ≤ 0.025 | … after training-count residualization: gap > 0 | p ≤ 0.025 | within-class p ≤ 0.025 | between-class ρ > 0.1 and p ≤ 0.025 |")
    print("|---|---|---|---|---|---|---|---|")
    cells = defaultdict(list)
    for (cell, l), seeds in by.items():
        for seed, r in seeds.items():
            cells[cell].append(r)
    for cell, rs in sorted(cells.items()):
        n = pos = sig = wsig = bsig = fpos = fsig = 0
        for r in rs:
            rd = (r.get("relevant") or {}).get("determined") or {}
            q = rd.get("quartiles_struct") or {}
            if q.get("gap") is None:
                continue
            n += 1; pos += q["gap"] > 0; sig += q["null"]["p_ge"] <= 0.025
            cf = (rd.get("class_frequency") or {}).get("struct") or {}
            if cf:
                fpos += cf["gap"] > 0; fsig += cf["null"]["p_ge"] <= 0.025 and cf["gap"] > 0
            wc = (rd.get("residual_class") or {}).get("struct") or {}
            wsig += bool(wc) and wc["null"]["p_ge"] <= 0.025 and wc["gap"] > 0
            bc = (rd.get("class_level") or {}).get("struct") or {}
            bsig += bool(bc) and bc["spearman"] is not None and bc["spearman"] > 0.1 and bc["null"]["p_ge"] <= 0.025
        print(f"| {cell} | {n} | {pos} | {sig} | {fpos} | {fsig} | {wsig} | {bsig} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
