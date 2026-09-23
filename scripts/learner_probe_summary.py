"""Summarize probe raws (scripts/learner_probe_owner.py) per cell and target:
best-layer OIR per seed and pooled (mean ± sd over seeds), the layer, CE on
the determined subset, argmax accuracy. Every figure from the raws.

  uv run python scripts/learner_probe_summary.py docs/learner-probe-owner-*-held-2026-09-23.json [--lock 0]
"""
import argparse
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raws", nargs="+")
    ap.add_argument("--lock", type=int, default=0)
    ap.add_argument("--layers", default="1,2,3,4")
    a = ap.parse_args(argv)
    layers = [int(x) for x in a.layers.split(",")]
    cells = defaultdict(list)
    for f in a.raws:
        r = json.loads(Path(f).read_text())
        cell = Path(f).name.split("owner-")[1].split("-2M")[0]
        rows = [r["results"][f"l{a.lock}/L{L}"] for L in layers if f"l{a.lock}/L{L}" in r["results"]]
        best = max(rows, key=lambda x: x["oir"])
        cells[(cell, r.get("target", "owner"), r.get("readout", "linear"))].append((r["seed"], best))
    print("| cell | target | readout | seeds | best-layer OIR per seed | pooled OIR ± sd | layer(s) | CE determined subset | H(Z|h) | acc |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for (cell, target, readout), rows in sorted(cells.items()):
        rows.sort()
        oirs = [b["oir"] for _, b in rows]
        det = [b["ce_determined"] for _, b in rows if b["ce_determined"] is not None]
        print(f"| {cell} | {target} | {readout} | {len(rows)} | {' / '.join(f'{x:.2f}' for x in oirs)} | "
              f"**{st.mean(oirs):.2f}** ± {st.stdev(oirs) if len(oirs) > 1 else 0:.2f} | {','.join(str(b['layer']) for _, b in rows)} | "
              f"{st.mean(det):.3f} ({min(det):.3f}–{max(det):.3f}) | {rows[0][1]['h_z_given_h']:.3f} | {st.mean(b['acc'] for _, b in rows):.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
