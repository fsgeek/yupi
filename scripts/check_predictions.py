"""Check pre-stated predictions against every committed artifact.

(run: python scripts/check_predictions.py predictions.json [--docs DIR] [--out out.json])

predictions.json: a list of {id, select, relation, value, tol?, quantifier? (all|any), note?}.
Exit status: 0 all PASS; 1 any FAIL; 2 no FAIL but some NO_CHECK.
Unknown artifact families are listed in the output — they are files the
checker cannot see into, which is different from files that say nothing.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from yupi.predictions import evaluate, load_artifacts  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions")
    ap.add_argument("--docs", default=os.path.join(os.path.dirname(__file__), "..", "docs"))
    ap.add_argument("--out")
    a = ap.parse_args()
    preds = json.load(open(a.predictions))
    cells, unknown = load_artifacts(a.docs)
    results = [evaluate(p, cells) for p in preds]
    print(f"{len(cells)} cells from {len({c['artifact'] for c in cells})} artifacts; "
          f"{sum(c['superseded'] for c in cells)} superseded (excluded unless asked); "
          f"unknown families: {len(unknown)}")
    for n in unknown:
        print(f"  unknown: {n}")
    for p, r in zip(preds, results):
        print(f"{r['status']:8s} {r['id']:12s} matched={r['n_matched']:4d} fail={r['n_fail']:4d}  "
              f"{p['relation']} {p['value']}  {p.get('note', '')}")
        for c in r["failures"][:10]:
            print(f"           {c['artifact']} eps={c['eps']} rung={c['rung']} disc={c['discipline']} "
                  f"L={c['L']} T={c['T']} {c['quantity']}={c['value']}")
        if len(r["failures"]) > 10:
            print(f"           ... {len(r['failures']) - 10} more failures")
    if a.out:
        json.dump(dict(unknown=unknown, results=results), open(a.out, "w"), indent=1, default=str)
    statuses = {r["status"] for r in results}
    sys.exit(1 if "FAIL" in statuses else (2 if "NO_CHECK" in statuses else 0))


if __name__ == "__main__":
    main()
