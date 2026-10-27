"""Declared: docs/open-factual-declared-2026-10-27.md. Scorer written before any B2 data existed.

Labels each response correct (names a work in the frozen Wikidata answer set), refusal (exp27's refusal markers, and
no valid work), or wrong (neither). Matching: lowercase, punctuation to spaces, leading article dropped, whole-word
match of any accepted name in the response with the entity's own name removed; names under 4 characters
only as the whole answer or quoted/emphasised. Then AUCs of mean per-token entropy:
wrong vs correct (within open-factual), and correct open-factual vs exp27-style knowable (from Arm B's data).

  python scripts/open_factual_score.py --dir DIR --sets FILE --armb DIR [--out FILE]
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np

from entropy_only_observer import auc
from escape_hatch_open_score import REFUSAL


def norm(s):
    s = re.sub(r"[^\w\s]", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return re.sub(r"^(the|a|an) ", "", s)


def label(resp, names, entity):
    text = " " + norm(resp).replace(norm(entity), " ") + " "
    for n in names:
        k = norm(n)
        if not k:
            continue
        if len(k) < 4:  # short titles ("It") match only as the whole answer, or quoted or emphasised
            if norm(resp) == k or re.search(r"[\"'*_\u201c\u2018]" + re.escape(n) + r"[\"'*_\u201d\u2019]", resp, re.I):
                return "correct"
        elif re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", text):
            return "correct"
    return "refusal" if any(m in resp.lower() for m in REFUSAL) else "wrong"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--sets", required=True)
    ap.add_argument("--armb", required=True, help="Arm B data dir, for the knowable comparison")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sets = {r["qid"]: [n for w in r["works"] for n in w] for r in json.load(open(a.sets))["rows"] if r["n_works"] >= 3}
    rows = []
    for p in sorted(Path(a.dir).glob("*.jsonl")):
        R = [r for r in map(json.loads, open(p)) if r["qid"] in sets]  # entities with < 3 works excluded
        lab = np.array([label(r["response"], sets[r["qid"]], r["entity"]) for r in R])
        mean = np.array([np.mean(r["entropies"]) if r["entropies"] else 0.0 for r in R])
        K = np.array([np.mean(json.loads(l)["entropies"]) for l in open(Path(a.armb) / p.name)
                      if json.loads(l)["category"] == "knowable"])
        cnt = {c: int((lab == c).sum()) for c in ("correct", "wrong", "refusal")}
        res = dict(family=p.stem, counts=cnt, scored=cnt["correct"] >= 10 and cnt["wrong"] >= 10)
        cw = (lab == "correct") | (lab == "wrong")
        res["AUC_wrong_vs_correct"] = auc(mean[cw], lab[cw] == "wrong", np.ones(cw.sum())) if res["scored"] else None
        s = np.concatenate([mean[lab == "correct"], K]); y = np.r_[np.ones((lab == "correct").sum(), bool), np.zeros(len(K), bool)]
        res["AUC_correct_open_vs_knowable"] = auc(s, y, np.ones(len(y)))
        res["median_mean_entropy"] = {c: float(np.median(mean[lab == c])) if (lab == c).any() else None for c in cnt}
        res["by_relation_wrong_rate"] = {rel: float(np.mean([l == "wrong" for l, r in zip(lab, R) if r["relation"] == rel]))
                                         for rel in ("novel", "film", "album")}
        rows.append(res)
        print(json.dumps(res), flush=True)
    sc = [r for r in rows if r["scored"]]
    verdict = dict(n_models=len(rows), n_scored=len(sc),
                   O1=int(sum(r["AUC_wrong_vs_correct"] <= 0.75 for r in sc)),
                   O2=int(sum(r["AUC_correct_open_vs_knowable"] >= 0.70 for r in rows)))
    print(verdict)
    if a.out:
        Path(a.out).write_text(json.dumps(dict(declared="docs/open-factual-declared-2026-10-27.md", rows=rows,
                                               verdict=verdict), indent=1))


if __name__ == "__main__":
    main()
