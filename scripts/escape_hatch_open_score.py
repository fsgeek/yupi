"""Declared: docs/escape-hatch-open-declared-2026-10-27.md. Scorer written before any Arm B data existed.

MEAN, RESOLVE and LEN per response; AUCs per model for U vs K, U vs OL, U vs OS, OS vs K and OL vs K; the B0–B4
verdicts; refusal rates by exp27's own refusal markers.

  python scripts/escape_hatch_open_score.py --dir DIR [--out FILE]
"""
import argparse
import json
from pathlib import Path

import numpy as np

from entropy_only_observer import auc

REFUSAL = ["i don't", "i cannot", "i'm not", "no such", "doesn't exist", "not aware", "cannot find", "unable to",
           "fictional", "made up", "not real", "i apologize", "don't have information", "cannot provide",
           "not familiar", "cannot verify", "there is no", "no evidence", "i don't know", "i'm sorry",
           "i couldn't find", "no record", "i'm unable", "not possible", "no way to"]  # exp27 check_answer_correct


def feats(e, resp):
    e = np.asarray(e, float)
    if len(e) == 0:
        return 0.0, 0.0, 0
    k = int(e.argmax()); after = e[k + 1:]
    return float(e.mean()), float(e[k] - after.mean()) if len(after) else 0.0, len(resp.split())


def contrast(F, cat, pos_cat, neg_cat, j):
    s = np.array([f[j] for f, c in zip(F, cat) if c in (pos_cat, neg_cat)])
    y = np.array([c == pos_cat for c in cat if c in (pos_cat, neg_cat)])
    return auc(s, y, np.ones(len(y)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    rows = []
    for p in sorted(Path(a.dir).glob("*.jsonl")):
        R = [json.loads(l) for l in open(p)]
        F = [feats(r["entropies"], r["response"]) for r in R]; cat = [r["category"] for r in R]
        res = dict(family=p.stem, n={c: cat.count(c) for c in sorted(set(cat))})
        for j, name in enumerate(("MEAN", "RESOLVE", "LEN")):
            res[name] = {f"{x}_vs_{y}": contrast(F, cat, x, y, j) for x, y in (
                ("unknowable", "knowable"), ("unknowable", "open_long"), ("unknowable", "open_short"),
                ("open_short", "knowable"), ("open_long", "knowable"))}
        res["refusal_rate"] = {c: float(np.mean([any(m in r["response"].lower() for m in REFUSAL)
                                                 for r in R if r["category"] == c])) for c in sorted(set(cat))}
        res["median_len"] = {c: float(np.median([f[2] for f, cc in zip(F, cat) if cc == c])) for c in sorted(set(cat))}
        rows.append(res)
        print(p.stem, json.dumps({k: {kk: round(v, 3) for kk, v in res[k].items()} for k in ("MEAN", "RESOLVE", "LEN")}),
              "refusal", {k: round(v, 2) for k, v in res["refusal_rate"].items()}, flush=True)
    U_OL = "unknowable_vs_open_long"
    verdict = dict(
        n_models=len(rows),
        B0=sum(r["MEAN"]["unknowable_vs_knowable"] >= 0.80 for r in rows),
        B1=sum(r["MEAN"][U_OL] <= 0.70 for r in rows),
        B2=sum(r["MEAN"]["open_short_vs_knowable"] >= 0.70 for r in rows),
        B3=sum(abs(r["RESOLVE"][U_OL] - 0.5) > abs(r["MEAN"][U_OL] - 0.5) for r in rows),
        B4=sum(r["LEN"][U_OL] <= 0.70 for r in rows))
    verdict = {k: int(v) for k, v in verdict.items()}
    print(verdict)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/escape-hatch-open-declared-2026-10-27.md", rows=rows,
                                               verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
