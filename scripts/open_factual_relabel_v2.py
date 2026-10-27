"""Post hoc (2026-10-27, after Codex's review): B2 labels with the two matching bugs Codex found fixed.

1. A title that contains the entity's own name ("The Soft Machine") is matched against the full response, not the
   response with the entity removed.
   An eponymous title (equal to the entity's name) counts only as the whole answer or quoted/emphasised, since
   every response names the entity.
2. Accepted titles that normalise to a bare relation word ("The Album" -> "album", likewise novel/film) are ignored:
   they match the prompt's own phrasing.
The declared verdicts stand on the v1 labels; this reports how far they move.

  python scripts/open_factual_relabel_v2.py --dir DIR --sets FILE
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from entropy_only_observer import auc  # noqa: E402
from escape_hatch_open_score import REFUSAL  # noqa: E402
from open_factual_score import norm  # noqa: E402

GENERIC = {"album", "novel", "film", "movie", "book", "record"}


def label_v2(resp, names, entity):
    full = " " + norm(resp) + " "
    stripped = " " + norm(resp).replace(norm(entity), " ") + " "
    for n in names:
        k = norm(n)
        if not k or k in GENERIC:
            continue
        text = full if norm(entity) in k else stripped
        if k == norm(entity) or len(k) < 4:  # eponymous or short titles: only as the whole answer, or quoted/emphasised
            if norm(resp) == k or re.search(r"[\"'*_“‘]" + re.escape(n) + r"[\"'*_”’]", resp, re.I):
                return "correct"
        elif re.search(r"(?<!\w)" + re.escape(k) + r"(?!\w)", text):
            return "correct"
    return "refusal" if any(m in resp.lower() for m in REFUSAL) else "wrong"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--sets", required=True)
    a = ap.parse_args()
    sets = {r["qid"]: [n for w in r["works"] for n in w] for r in json.load(open(a.sets))["rows"] if r["n_works"] >= 3}
    for p in sorted(Path(a.dir).glob("*.jsonl")):
        R = [r for r in map(json.loads, open(p)) if r["qid"] in sets]
        lab = np.array([label_v2(r["response"], sets[r["qid"]], r["entity"]) for r in R])
        m = np.array([np.mean(r["entropies"]) for r in R])
        cw = (lab == "correct") | (lab == "wrong"); y = lab[cw] == "wrong"
        per = {rel: (lambda L, M: auc(M[(L == "correct") | (L == "wrong")], L[(L == "correct") | (L == "wrong")] == "wrong",
                                      np.ones(((L == "correct") | (L == "wrong")).sum())))(
            lab[[r["relation"] == rel for r in R]], m[[r["relation"] == rel for r in R]]) for rel in ("novel", "film", "album")}
        print(p.stem, {c: int((lab == c).sum()) for c in ("correct", "wrong", "refusal")},
              "pooled %.3f" % auc(m[cw], y, np.ones(cw.sum())), {k: round(v, 3) for k, v in per.items()})


if __name__ == "__main__":
    main()
