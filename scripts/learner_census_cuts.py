"""Cuts of the window census: for each census raw, the one-way variance split
(class vs within-class) and the signed attribution of the total excess to the
predicted record's outcome (kind, fresh/bound actor, kind × actor) and to the
number of distinct actors seen. Reads the per-window files the census raws
name; rows are matched to windows through the corpus split.

  uv run --extra learner python scripts/learner_census_cuts.py docs/learner-window-census-*-2026-09-21.json \\
      --raw docs/learner-window-census-cuts-2026-09-21.json [--md]

`--md` prints the note's tables (every figure from the raw it just wrote).
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

from yupi.corpus.vocab import VOCAB
from yupi.corpus.writer import read_split
from yupi.learner.census import attribute, contrast, record_features, variance_split
from yupi.learner.evaluate import surface_records

KINDS_ORDER = ("DISPATCH", "RELEASE", "BLOCK", "ACQUIRE", "IO_ISSUE", "IO_COMPLETE", "STEP", "IDLE")


def one(raw_path: Path) -> dict:
    raw = json.loads(raw_path.read_text())
    pw = Path(raw["per_window_file"])
    if hashlib.sha256(pw.read_bytes()).hexdigest() != raw["per_window_sha256"]:
        raise SystemExit(f"refused: {pw} does not match the sha256 in {raw_path}")
    rows = [json.loads(l) for l in pw.read_text().splitlines()]
    split = read_split(raw["corpus"], raw["split"])
    k = raw["k"]
    feats = []
    for r in rows:
        toks = tuple(VOCAB[t] for t in split[r["i"]][0])
        _, recs = surface_records(toks)
        feats.append(record_features(recs[:k], recs[k]))
    return dict(census_raw=str(raw_path), rung=raw["rung"], eps=raw["eps"], seed=raw["seed"], k=k, n=len(rows),
                mean=raw["summary"]["mean"], variance=variance_split(rows), attribution=attribute(rows, feats))


def markdown(out: dict) -> str:
    cells = out["cells"]
    lines = ["| cell | seed | n | mean | classes | between share (ANOVA) | BLOCK+ACQUIRE share | share by predicted kind: " +
             " / ".join(KINDS_ORDER[:7]) + " |", "|---|---|---|---|---|---|---|---|"]
    for c in cells:
        v, a = c["variance"], c["attribution"]["kind"]
        ba = sum(a[kk]["share"] for kk in ("BLOCK", "ACQUIRE") if kk in a)
        shares = " / ".join(f"{a[kk]['share']:.2f}" if kk in a else "—" for kk in KINDS_ORDER[:7])
        lines.append(f"| {c['rung']} ε={c['eps']} | {c['seed']} | {c['n']} | {c['mean']:.3f} | {v['n_classes']} | "
                     f"{v['between_share']:.2f} | **{ba:.2f}** | {shares} |")
    lines.append("")
    lines.append("| cell | seed | mean on BLOCK (kind / actor / obj) | mean on ACQUIRE (kind / actor / obj) | mean on RELEASE | mean on DISPATCH | fresh-actor share (frac of windows) |")
    lines.append("|---|---|---|---|---|---|---|")
    for c in cells:
        a = c["attribution"]["kind"]; f = c["attribution"]["actor"]
        def m(kk):
            if kk not in a:
                return "—"
            b = a[kk]["by_field"]
            return f"{a[kk]['mean']:.3f} ({b['kind']:.2f} / {b['actor']:.2f} / {b['obj']:.2f})"
        lines.append(f"| {c['rung']} ε={c['eps']} | {c['seed']} | {m('BLOCK')} | {m('ACQUIRE')} | {a['RELEASE']['mean']:.3f} | "
                     f"{a['DISPATCH']['mean']:.3f} | {f['fresh']['share']:.2f} ({f['fresh']['frac']:.2f}) |")
    return "\n".join(lines)


def gaps(cells: list, base: str = "r2", others=("r1", "r3")) -> dict:
    """Per predicted kind, the contribution frac_kind × (mean_base − mean_other)
    to the gap in total excess between rungs (same ε), per seed and pooled
    (mean ± sd over seeds); the contributions sum to the gap per seed."""
    by = {}
    for c in cells:
        by.setdefault((c["rung"], c["eps"]), {})[c["seed"]] = c
    out = {}
    for (rung, eps), seeds in by.items():
        if rung != base:
            continue
        for other in others:
            o = by.get((other, eps))
            if not o:
                continue
            per_seed = {}
            for sd_, c in seeds.items():
                if sd_ not in o:
                    continue
                a, b = c["attribution"]["kind"], o[sd_]["attribution"]["kind"]
                per_seed[sd_] = {kk: a[kk]["frac"] * (a[kk]["mean"] - b[kk]["mean"]) for kk in a if kk in b}
                per_seed[sd_]["_gap"] = c["mean"] - o[sd_]["mean"]
            kinds = sorted({kk for v in per_seed.values() for kk in v})
            pooled = {}
            for kk in kinds:
                vals = [v[kk] for v in per_seed.values() if kk in v]
                pooled[kk] = dict(mean=sum(vals) / len(vals),
                                  sd=(sum((x - sum(vals) / len(vals)) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5 if len(vals) > 1 else 0.0,
                                  per_seed=vals)
            out[f"{base}-{other} eps={eps}"] = dict(per_seed=per_seed, pooled=pooled)
    return out


def markdown_gaps(g: dict) -> str:
    lines = ["| gap | total gap (per seed) | " + " | ".join(KINDS_ORDER[:7]) + " |", "|---|---|" + "---|" * 7]
    for name, d in g.items():
        tot = d["pooled"]["_gap"]
        cells = []
        for kk in KINDS_ORDER[:7]:
            if kk in d["pooled"]:
                pk = d["pooled"][kk]
                cells.append(f"{pk['mean']:+.3f} ± {pk['sd']:.3f}")
            else:
                cells.append("—")
        lines.append(f"| {name} | {tot['mean']:+.3f} ({', '.join(f'{x:+.3f}' for x in tot['per_seed'])}) | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("raws", nargs="+")
    ap.add_argument("--raw", required=True)
    ap.add_argument("--md", action="store_true")
    ap.add_argument("--contrast", default=None, help="seed-group contrast within one cell, e.g. 'high=2,5 low=1,3,4,6'")
    a = ap.parse_args(argv)
    cells = [one(Path(p)) for p in sorted(a.raws)]
    cells.sort(key=lambda c: (c["rung"], c["eps"], c["seed"]))
    out = dict(cells=cells, gaps=gaps(cells), inputs=sorted(a.raws))
    if a.contrast:
        groups = {kv.split("=")[0]: [int(x) for x in kv.split("=")[1].split(",")] for kv in a.contrast.split()}
        out["contrast"] = contrast(cells, groups["high"], groups["low"])
    Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
    print(f"raw -> {a.raw}", file=sys.stderr)
    if a.md:
        back = json.loads(Path(a.raw).read_text())
        print(markdown(back))
        print()
        print(markdown_gaps(back["gaps"]))
        if "contrast" in back:
            c = back["contrast"]
            print()
            print(f"| contrast seeds {c['high']} ({c['high_mean']:.3f}) − seeds {c['low']} ({c['low_mean']:.3f}) | gap | " +
                  " | ".join(KINDS_ORDER[:7]) + " |")
            print("|---|---|" + "---|" * 7)
            print(f"| frac × Δmean by predicted kind | {c['gap']:+.3f} | " +
                  " | ".join(f"{c['by_kind'][k]:+.3f}" if k in c["by_kind"] else "—" for k in KINDS_ORDER[:7]) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
