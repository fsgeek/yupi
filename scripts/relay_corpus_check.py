"""Pairing and coverage check for an r1ʀ ("r1R") corpus against the r1 corpus it is
paired with (docs/relay-intervention-design-v0.1.md §2 item 4).

  uv run python scripts/relay_corpus_check.py --r1 corpus/<r1 name>/<id> --r1R corpus/<r1R name>/<id> \\
      [--table-k7 ~/.cache/yupi-scratch/ceilings/c1prime-loop-40-8-2-r1R-eps1-k7.jsonl] --out docs/<raw>.json

Per split: equal window counts and lengths (token-matched), byte-identical renaming
tables (same episodes, endpoints, injections), and — token for token over the whole
padded array — the r1R windows with every relay slot (the OBJECT slot of each
record) set back to MASKED equal the r1 windows. The relay slot must also equal the
relay recomputed from the r1 tokens (KIND of the most recent earlier record in the
window with the same actor token; NONE if none, or no actor). Manifests must agree on
every field but the rung, the git commit and the rung-derived corpus name.
With --table-k7: every test window with at least 7 records has its k = 7 pattern
class in the r1R table, and that class is the relayed r1 class of the paired window.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from yupi.corpus.vocab import KINDS, TOKEN_ID, VOCAB

RESET_ID, MASKED_ID, NONE_ID = TOKEN_ID["RESET"], TOKEN_ID["MASKED"], TOKEN_ID["NONE"]
KIND_IDS = {TOKEN_ID[k] for k in KINDS}


def _load(d: Path, split: str):
    lens = np.fromfile(d / f"{split}.index", dtype="<u4")
    toks = np.fromfile(d / f"{split}.tokens", dtype="<u2")
    return lens, toks.reshape(len(lens), -1) if len(lens) else toks.reshape(0, 0)


def _relay_mask(arr, lens):
    """Boolean mask of relay-slot positions inside each window's length."""
    n, width = arr.shape
    reset = arr[:, 0] == RESET_ID
    cols = np.arange(width)[None, :]
    off = reset.astype(int)[:, None]
    rel = cols - off
    return (rel >= 0) & (rel % 5 == 2) & (cols < lens[:, None].astype(int))


def _recompute_ok(r1, rr, lens):
    bad = 0
    with_kind = 0
    for i in range(r1.shape[0]):
        row1, rowr = r1[i].tolist(), rr[i].tolist()
        off = 1 if row1 and row1[0] == RESET_ID else 0
        last = {}
        any_kind = False
        for j in range(off, int(lens[i]), 5):
            kind, actor = row1[j], row1[j + 1]
            expect = last.get(actor, NONE_ID) if actor != NONE_ID else NONE_ID
            if rowr[j + 2] != expect:
                bad += 1
            any_kind |= expect in KIND_IDS
            if actor != NONE_ID:
                last[actor] = kind
        with_kind += any_kind
    return bad == 0, with_kind


def check_split(d1: Path, dr: Path, split: str) -> dict:
    d1, dr = Path(d1), Path(dr)
    l1, a1 = _load(d1, split)
    lr, ar = _load(dr, split)
    rep = dict(split=split, n_r1=int(len(l1)), n_r1R=int(len(lr)))
    same_shape = a1.shape == ar.shape and len(l1) == len(lr)
    rep["lengths_equal"] = bool(same_shape and np.array_equal(l1, lr))
    rep["tables_identical"] = (d1 / f"{split}.table.jsonl").read_bytes() == (dr / f"{split}.table.jsonl").read_bytes()
    if same_shape:
        dropped = ar.copy()
        dropped[_relay_mask(ar, lr)] = MASKED_ID
        rep["drop_relay_equals_r1"] = bool(np.array_equal(dropped, a1))
        ok, with_kind = _recompute_ok(a1, ar, l1)
    else:
        rep["drop_relay_equals_r1"], ok, with_kind = False, False, 0
    rep["relay_recomputed_equal"] = ok
    rep["n_windows_with_a_kind_relay"] = with_kind
    rep["passed"] = bool(rep["lengths_equal"] and rep["tables_identical"] and rep["drop_relay_equals_r1"] and ok)
    return rep


def check_manifests(d1: Path, dr: Path) -> dict:
    m1 = json.loads((Path(d1) / "manifest.json").read_text())
    mr = json.loads((Path(dr) / "manifest.json").read_text())
    diff = sorted(k for k in set(m1) | set(mr) if m1.get(k) != mr.get(k))
    return dict(differing_fields=diff, rungs=(m1.get("rung"), mr.get("rung")),
                passed=(set(diff) <= {"rung", "git_commit"} and m1.get("rung") == "r1" and mr.get("rung") == "r1R"))


def class_coverage(d1: Path, dr: Path, table_path: Path, k: int = 7) -> dict:
    from yupi.corpus.rendering import EpisodeTable
    from yupi.corpus.windows import deserialize
    from yupi.corpus.writer import read_split
    from yupi.interfaces import relay_window
    from yupi.naming import pattern_all
    from yupi.pattern_ceiling import load_table
    table = load_table(table_path)
    w1, wr = read_split(d1, "test"), read_split(dr, "test")
    n = missing = mismatch = 0
    for (t1, tab), (tr, _) in zip(w1, wr):
        et = EpisodeTable.from_json(tab)
        reset, r1 = deserialize(tuple(VOCAB[t] for t in t1), et)
        _, rr = deserialize(tuple(VOCAB[t] for t in tr), et)
        if len(rr) < k:
            continue
        n += 1
        key = (reset, pattern_all(rr[:k])[0])
        if key not in table:
            missing += 1
        if key != (reset, relay_window(pattern_all(r1[:k])[0])):
            mismatch += 1
    return dict(k=k, table=str(table_path), n_windows=n, missing_classes=missing, relayed_class_mismatch=mismatch,
                passed=(missing == 0 and mismatch == 0 and n > 0))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--r1", required=True)
    ap.add_argument("--r1R", required=True)
    ap.add_argument("--table-k7")
    ap.add_argument("--splits", default="train,val,test")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if Path(a.out).exists():
        raise SystemExit(f"refusing to overwrite {a.out}")
    rep = dict(design="docs/relay-intervention-design-v0.1.md §2 item 4", r1=a.r1, r1R=a.r1R,
               git=subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
               manifests=check_manifests(Path(a.r1), Path(a.r1R)), splits=[])
    print(rep["manifests"], flush=True)
    for s in a.splits.split(","):
        r = check_split(Path(a.r1), Path(a.r1R), s)
        rep["splits"].append(r)
        print(r, flush=True)
    ok = rep["manifests"]["passed"] and all(r["passed"] for r in rep["splits"])
    if a.table_k7:
        rep["class_coverage_k7"] = class_coverage(Path(a.r1), Path(a.r1R), Path(a.table_k7))
        print(rep["class_coverage_k7"], flush=True)
        ok &= rep["class_coverage_k7"]["passed"]
    rep["all_passed"] = bool(ok)
    Path(a.out).write_text(json.dumps(rep, indent=1) + "\n")
    print("PAIRING PASSED" if ok else "PAIRING FAILED", "->", a.out)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
