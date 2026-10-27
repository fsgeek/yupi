"""Post hoc (2026-10-27, not declared; written after B2's verdicts were seen): confound checks for O1.

1. Length: AUC of word count, wrong vs correct.
2. Committed fabrications only: wrong responses that put a title in emphasis or quotes and carry no hedge words,
   against correct responses. Entropy AUC.
3. Answer-only entropy: the mean entropy of the first 12 generated tokens, where the title is usually stated, which
   shrinks the influence of any explanation that follows.

  python scripts/open_factual_posthoc.py --dir DIR --sets FILE
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from entropy_only_observer import auc  # noqa: E402
from open_factual_score import label  # noqa: E402

HEDGE = ("not a widely", "not widely", "not well", "may not", "might not", "i'm not sure", "uncertain", "however",
         "not aware", "not familiar", "limited information", "obscure", "lesser-known", "less well-known")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--sets", required=True)
    a = ap.parse_args()
    sets = {r["qid"]: [n for w in r["works"] for n in w] for r in json.load(open(a.sets))["rows"] if r["n_works"] >= 3}
    for p in sorted(Path(a.dir).glob("*.jsonl")):
        R = [r for r in map(json.loads, open(p)) if r["qid"] in sets]
        lab = np.array([label(r["response"], sets[r["qid"]], r["entity"]) for r in R])
        mean = np.array([np.mean(r["entropies"]) for r in R]); head = np.array([np.mean(r["entropies"][:12]) for r in R])
        ln = np.array([len(r["response"].split()) for r in R])
        committed = np.array([bool(re.search(r"\*\*.+?\*\*|\*.+?\*|\".+?\"|“.+?”", r["response"]) or len(r["response"].split()) <= 6)
                              and not any(h in r["response"].lower() for h in HEDGE) for r in R])
        cw = (lab == "correct") | (lab == "wrong"); y = lab[cw] == "wrong"
        fab = (lab == "correct") | ((lab == "wrong") & committed); yf = lab[fab] == "wrong"
        one = lambda s, m, yy: auc(s[m], yy, np.ones(m.sum())) if yy.sum() >= 5 and (~yy).sum() >= 5 else None
        print("%-8s n_wrong %2d (committed %2d) | AUC mean %.3f len %.3f head12 %s | committed-only: mean %s head12 %s | median len correct %d wrong %d" % (
            p.stem, (lab == "wrong").sum(), ((lab == "wrong") & committed).sum(), one(mean, cw, y), one(ln.astype(float), cw, y),
            "%.3f" % one(head, cw, y) if one(head, cw, y) else None,
            "%.3f" % one(mean, fab, yf) if one(mean, fab, yf) else None, "%.3f" % one(head, fab, yf) if one(head, fab, yf) else None,
            np.median(ln[lab == "correct"]), np.median(ln[lab == "wrong"])))


if __name__ == "__main__":
    main()
