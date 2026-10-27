"""Declared audit for Arm B2 (docs/open-factual-declared-2026-10-27.md), written before any B2 data existed.

Samples up to 20 *wrong* responses per model (seed 20261027). For each, it extracts a candidate title (the first
emphasised or quoted span, else the first line with the prompt's lead-in removed) and searches Wikidata. A response
counts as misclassified if any search hit links to the entity by any property.

  python scripts/open_factual_audit.py --dir DIR --sets FILE [--out FILE]
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from open_factual_score import label  # noqa: E402

UA = "yupi-research/0.1 (exact-world epistemic observability research; https://wamason.com)"


def candidate(resp, entity):
    m = re.search(r"\*\*(.+?)\*\*|\*(.+?)\*|\"(.+?)\"|“(.+?)”|_(.+?)_", resp)
    if m:
        return next(g for g in m.groups() if g)
    line = resp.strip().split("\n")[0]
    line = re.sub(r"(?i)^.*?\b(is|was|called|titled)\b\s*", "", line)
    line = re.sub(re.escape(entity), "", line)
    line = re.sub(r"\s*\(\d{4}.*$", "", line)
    return re.sub(r"(?i)\s+(by|from|directed by)\s*$", "", line.strip(" .,:;()")).strip(" .,:;()")[:80]


def links_to(item, qid):
    q = f"ASK {{ wd:{item} ?p wd:{qid} }}"
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
        return json.load(r)["boolean"]


def search(title):
    url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        dict(action="wbsearchentities", search=title, language="en", format="json", limit=7))
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
        return [s["id"] for s in json.load(r).get("search", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--sets", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    sets = {r["qid"]: [n for w in r["works"] for n in w] for r in json.load(open(a.sets))["rows"] if r["n_works"] >= 3}
    out = {}
    for p in sorted(Path(a.dir).glob("*.jsonl")):
        R = [r for r in map(json.loads, open(p)) if r["qid"] in sets]
        wrong = [r for r in R if label(r["response"], sets[r["qid"]], r["entity"]) == "wrong"]
        rng = np.random.default_rng(20261027)
        sample = [wrong[i] for i in rng.permutation(len(wrong))[:20]]
        recs = []
        for r in sample:
            t = candidate(r["response"], r["entity"])
            hit = any(links_to(i, r["qid"]) for i in search(t)) if t else False
            recs.append(dict(entity=r["entity"], title=t, response=r["response"][:160], misclassified=hit))
            time.sleep(0.5)
        rate = float(np.mean([x["misclassified"] for x in recs])) if recs else None
        out[p.stem] = dict(n_wrong=len(wrong), n_audited=len(recs), misclassified_rate=rate, records=recs)
        print(p.stem, len(wrong), len(recs), rate, flush=True)
    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
