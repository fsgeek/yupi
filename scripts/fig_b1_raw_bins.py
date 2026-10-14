"""Figure for paper 1 §4a (2026-10-13): raw per-model KIND shortfall by ι_kind,4 bin, no controls.
Source: docs/b1-fe-coarse-robustness-2026-10-13.json. One thin line per model; blue = 15 epochs (converged),
orange = 5 epochs (held-out). Rows ε, columns rung.

  uv run --extra learner python scripts/fig_b1_raw_bins.py
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RAW = "docs/b1-fe-coarse-robustness-2026-10-13.json"
OUT = "docs/figures/b1-raw-bins-2026-10-13.png"
LABELS = ["0", "≤.001", "≤.01", "≤.05", "≤.2", "≤.4", ">.4"]
COL = {"converged_e15": "#2a78d6", "D1_heldout": "#eb6834"}
NAME = {"converged_e15": "15 epochs", "D1_heldout": "5 epochs (held-out)"}
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"

d = json.load(open(RAW))
fig, axes = plt.subplots(2, 4, figsize=(11, 5.2), sharex=True, sharey=True, facecolor=SURF)
for i, eps in enumerate(["1", "1/2"]):
    for j, rung in enumerate(["r1", "r2", "r3", "r4"]):
        ax = axes[i][j]
        ax.set_facecolor(SURF)
        for fam in ("D1_heldout", "converged_e15"):
            for r in d["families"][fam]["runs"]:
                if r["rung"] == rung and r["eps"] == eps:
                    y = [b["mean_excess"] for b in r["bins"]]
                    ax.plot(range(7), y, color=COL[fam], lw=1.2, marker="o", ms=3.5, alpha=0.9,
                            markeredgecolor=SURF, markeredgewidth=0.8)
        ax.set_title(f"{rung}, ε = {'½' if eps == '1/2' else '1'}", fontsize=10, color=INK)
        ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(GRID)
        ax.tick_params(colors=INK2, labelsize=8)
        ax.axhline(0, color=INK2, lw=0.6)
for ax in axes[1]:
    ax.set_xticks(range(7)); ax.set_xticklabels(LABELS, fontsize=7.5)
    ax.set_xlabel("exact far information ι₄ (bits), bin", fontsize=8.5, color=INK2)
for ax in axes[:, 0]:
    ax.set_ylabel("KIND shortfall (bits)", fontsize=8.5, color=INK2)
handles = [plt.Line2D([], [], color=COL[f], lw=1.6, marker="o", ms=4) for f in ("converged_e15", "D1_heldout")]
fig.legend(handles, [NAME[f] for f in ("converged_e15", "D1_heldout")], loc="upper center", ncol=2, frameon=False,
           fontsize=9, labelcolor=INK, bbox_to_anchor=(0.5, 0.95))
fig.suptitle("KIND shortfall by exact far information, one line per model, no controls (5-epoch held-out set covers 5 of 8 cells)",
             fontsize=10.5, color=INK, y=0.995)
fig.tight_layout(rect=(0, 0, 1, 0.90))
fig.savefig(OUT, dpi=170, facecolor=SURF)
print(OUT)
