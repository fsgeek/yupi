"""The per-window link between probe error and model excess (2026-09-24): do the
windows where the probe reads the lock's state worst from the boundary
activation coincide with the windows where the model over-pays on the record
predicted from that same position?

  uv run --extra learner python scripts/learner_probe_link.py --census ~/.cache/yupi-scratch/census/<run>-k7-test.jsonl \\
      --per-example ~/.cache/yupi-scratch/probes/<run>-held-k7-test-per-example.jsonl --probe-raw docs/learner-probe-owner-<cell>-seed<s>-held-<date>.json \\
      [--layer best|L] [--lock 0] [--voi ~/.cache/yupi-scratch/probes/<name>-k7-test-voi.jsonl] \\
      [--corpus-dir corpus/<name>/<rid> --k 7] [--class-freq ~/.cache/yupi-scratch/probes/<name>-k7-test-classfreq.jsonl] --raw docs/learner-probe-link-<cell>-seed<s>-<target>-<date>.json

Join on the test-window index i (both files index the same split); one probe
example per (window, lock) at the chosen layer (default: the layer with the best
OIR for that lock in the probe raw). Reports Pearson and Spearman correlation of
the probe's per-example CE with the window's structural excess and with its
KIND-field excess; mean excess by probe-CE quartile; the same on the examples
the prefix determines (H(Z | h) = 0), where probe CE is pure representational
error; and a permutation null (shuffled CE, 200 draws) for the top-vs-bottom
quartile gap. With --voi (the exact per-window rows of scripts/learner_probe_voi.py)
the determined-subset analysis is repeated on RESIDUALS: probe CE and excess with
their means removed within 50 bins of the ceiling's own next-record entropy H(next),
and, always, within the window's exact class (the census key: windows of one class
share the whole exact side, so only the model's treatment of the names and its own
per-window error remain), so that "hard window for both" cannot masquerade as a
link; and BETWEEN classes, on class means (>= 3 windows), where the realized-record
noise that dominates single windows (§13) is averaged down. With --corpus-dir the
whole analysis is repeated on the RELEVANT windows only: those whose realized record
k + 1 has lock l as its object (an ACQUIRE, BLOCK or RELEASE on l, in the pattern
observer's lock index), where the lock's state is what the prediction turns on.
With --class-freq (scripts/learner_class_frequency.py) the determined-subset link is
also computed on residuals after removing means within 50 bins of log(1 + training
count of the window's class), and the confound's own strength is reported: Spearman
of log training count with probe CE and with excess. Correlational only; nothing
here is causal.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def next_record_lock(recs, k):
    """Pattern lock index of record k + 1's object (None if it is not a lock event),
    with the pattern indices fixed by the first k + 1 records."""
    from yupi.naming import pattern_all
    if len(recs) < k + 1:
        return None
    pw, _ = pattern_all(recs[:k + 1])
    obj = pw[k].obj
    return obj[1] if obj is not None and obj[0] == "LOCK" else None


def _git():
    try:
        h = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], text=True).strip() != ""
        return h + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def _rank(x):
    order = np.argsort(x, kind="stable"); r = np.empty(len(x)); r[order] = np.arange(len(x))
    # average ties
    xs = x[order]; i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def pearson(x, y):
    x = x - x.mean(); y = y - y.mean()
    d = float(np.sqrt((x * x).sum() * (y * y).sum()))
    return float((x * y).sum() / d) if d > 0 else None


def spearman(x, y):
    return pearson(_rank(x), _rank(y))


def quartiles(ce, ex, rng=None, draws=200):
    """Mean excess in each probe-CE quartile, the top−bottom gap, and its permutation null."""
    q = np.quantile(ce, [0.25, 0.5, 0.75])
    bins = np.digitize(ce, q)
    means = [float(ex[bins == b].mean()) if (bins == b).any() else None for b in range(4)]
    gap = means[3] - means[0] if means[0] is not None and means[3] is not None else None
    null = None
    if gap is not None and rng is not None:
        gaps = []
        for _ in range(draws):
            perm = rng.permutation(len(ce)); b2 = bins[perm]
            gaps.append(float(ex[b2 == 3].mean() - ex[b2 == 0].mean()))
        gaps = np.array(gaps)
        null = dict(mean=float(gaps.mean()), sd=float(gaps.std(ddof=1)), p_ge=float(np.mean(gaps >= gap)))
    return dict(cuts=[float(v) for v in q], means=means, gap=gap, null=null)


def partial_out(x, groups):
    """x minus its mean within each group (a fixed-effects residual). Groups with a
    single member contribute a zero residual and are excluded by `mask`."""
    x = np.asarray(x, dtype=np.float64); groups = np.asarray(groups)
    labels, inv, counts = np.unique(groups, return_inverse=True, return_counts=True)
    sums = np.bincount(inv, weights=x, minlength=len(labels))
    res = x - sums[inv] / counts[inv]
    return res, counts[inv] > 1


def residualized(ce, ex, groups, rng):
    """Spearman and quartile gap of (ce, ex) after removing the group means of both:
    within-group dependence only."""
    ce_r, m1 = partial_out(ce, groups); ex_r, m2 = partial_out(ex, groups)
    m = m1 & m2
    if m.sum() < 100:
        return None
    q = quartiles(ce_r[m], ex_r[m], rng)
    return dict(n=int(m.sum()), n_groups=int(len(np.unique(groups[m]))), spearman=spearman(ce_r[m], ex_r[m]),
                pearson=pearson(ce_r[m], ex_r[m]), gap=q["gap"], null=q["null"])


def class_level(ce, ex, cls, rng, min_n=3, draws=200):
    """Between-class link: per class (>= min_n windows) the mean probe CE and the mean
    excess (an unbiased estimate of the class's KL, §13); Spearman across classes
    weighted by nothing, and the mean-excess gap between the top and bottom quartile
    of classes by mean probe CE, with a permutation null over class labels."""
    labels, inv, counts = np.unique(cls, return_inverse=True, return_counts=True)
    keep = counts >= min_n
    if keep.sum() < 50:
        return None
    ce_c = np.bincount(inv, weights=ce, minlength=len(labels)) / counts
    ex_c = np.bincount(inv, weights=ex, minlength=len(labels)) / counts
    ce_c, ex_c = ce_c[keep], ex_c[keep]
    q = quartiles(ce_c, ex_c, rng, draws=draws)
    return dict(n_classes=int(keep.sum()), n_windows=int(counts[keep].sum()), spearman=spearman(ce_c, ex_c),
                pearson=pearson(ce_c, ex_c), quartile_means=q["means"], gap=q["gap"], null=q["null"])


def analyse(ce, h, ex_struct, ex_kind, rng, h_next=None, cls=None, h_bins=50, freq=None):
    out = dict(n=int(len(ce)), ce_mean=float(ce.mean()), excess_mean=float(ex_struct.mean()), kind_excess_mean=float(ex_kind.mean()),
               pearson_struct=pearson(ce, ex_struct), spearman_struct=spearman(ce, ex_struct),
               pearson_kind=pearson(ce, ex_kind), spearman_kind=spearman(ce, ex_kind),
               quartiles_struct=quartiles(ce, ex_struct, rng), quartiles_kind=quartiles(ce, ex_kind, rng))
    det = h == 0.0
    if det.sum() >= 50:
        out["determined"] = dict(n=int(det.sum()), ce_mean=float(ce[det].mean()), excess_mean=float(ex_struct[det].mean()),
                                 pearson_struct=pearson(ce[det], ex_struct[det]), spearman_struct=spearman(ce[det], ex_struct[det]),
                                 pearson_kind=pearson(ce[det], ex_kind[det]), spearman_kind=spearman(ce[det], ex_kind[det]),
                                 quartiles_struct=quartiles(ce[det], ex_struct[det], rng), quartiles_kind=quartiles(ce[det], ex_kind[det], rng))
        if h_next is not None:
            cuts = np.quantile(h_next[det], np.linspace(0, 1, h_bins + 1)[1:-1])
            g = np.digitize(h_next[det], cuts)
            out["determined"]["residual_h_next"] = dict(bins=h_bins, struct=residualized(ce[det], ex_struct[det], g, rng),
                                                        kind=residualized(ce[det], ex_kind[det], g, rng))
        if freq is not None:
            lf = np.log1p(freq[det])
            cuts = np.quantile(lf, np.linspace(0, 1, h_bins + 1)[1:-1])
            g = np.digitize(lf, cuts)
            out["determined"]["class_frequency"] = dict(bins=h_bins, spearman_freq_ce=spearman(lf, ce[det]),
                                                        spearman_freq_excess=spearman(lf, ex_struct[det]),
                                                        struct=residualized(ce[det], ex_struct[det], g, rng),
                                                        kind=residualized(ce[det], ex_kind[det], g, rng))
        if cls is not None:
            out["determined"]["residual_class"] = dict(struct=residualized(ce[det], ex_struct[det], cls[det], rng),
                                                       kind=residualized(ce[det], ex_kind[det], cls[det], rng))
            out["determined"]["class_level"] = dict(struct=class_level(ce[det], ex_struct[det], cls[det], rng),
                                                    kind=class_level(ce[det], ex_kind[det], cls[det], rng))
    if (~det).sum() >= 50:
        u = ~det
        out["uncertain"] = dict(n=int(u.sum()), ce_mean=float(ce[u].mean()), h_mean=float(h[u].mean()), excess_mean=float(ex_struct[u].mean()),
                                pearson_struct=pearson(ce[u] - h[u], ex_struct[u]), spearman_struct=spearman(ce[u] - h[u], ex_struct[u]))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--census", required=True)
    ap.add_argument("--per-example", required=True)
    ap.add_argument("--probe-raw", required=True)
    ap.add_argument("--layer", default="best")
    ap.add_argument("--lock", type=int, default=None, help="one lock index; default: every lock in the probe raw, reported separately")
    ap.add_argument("--voi", help="exact per-window rows (learner_probe_voi.py) for the H(next) stratification")
    ap.add_argument("--corpus-dir", help="with --k: also analyse the windows whose realized record k+1 is an event on lock l")
    ap.add_argument("--k", type=int, default=7)
    ap.add_argument("--class-freq", help="per-window training counts of the window's class (learner_class_frequency.py)")
    ap.add_argument("--split", default="test")
    ap.add_argument("--raw")
    a = ap.parse_args(argv)
    voi = {}
    if a.voi:
        for line in Path(a.voi).read_text().splitlines():
            r = json.loads(line); voi[r["i"]] = r
    freq = {}
    if a.class_freq:
        for line in Path(a.class_freq).read_text().splitlines():
            r = json.loads(line); freq[r["i"]] = r["train_count"]
    relevant = None
    if a.corpus_dir:
        from yupi.corpus.vocab import VOCAB
        from yupi.corpus.writer import read_split
        from yupi.learner.evaluate import surface_records
        relevant = {}
        for i, (w, _) in enumerate(read_split(a.corpus_dir, a.split)):
            _, recs = surface_records(tuple(VOCAB[t] for t in w))
            relevant[i] = next_record_lock(recs, a.k)
    census = {}
    for line in Path(a.census).read_text().splitlines():
        r = json.loads(line); census[r["i"]] = r
    praw = json.loads(Path(a.probe_raw).read_text())
    locks = sorted({v["lock"] for v in praw["results"].values()})
    if a.lock is not None:
        locks = [a.lock]
    layer_for = {}
    for l in locks:
        if a.layer == "best":
            best = max((v for v in praw["results"].values() if v["lock"] == l), key=lambda v: (v["oir"] if v["oir"] is not None else -1))
            layer_for[l] = best["layer"]
        else:
            layer_for[l] = int(a.layer)
    rows = {l: [] for l in locks}
    for line in Path(a.per_example).read_text().splitlines():
        r = json.loads(line)
        if r["lock"] in rows and r["layer"] == layer_for[r["lock"]] and r["i"] in census and (not voi or r["i"] in voi) and (not freq or r["i"] in freq):
            c = census[r["i"]]
            hn = voi[r["i"]]["locks"][str(r["lock"])]["h_next"] if voi else float("nan")
            rel = 1.0 if (relevant is not None and relevant.get(r["i"]) == r["lock"]) else 0.0
            fq = float(freq[r["i"]]) if freq else float("nan")
            rows[r["lock"]].append((r["ce"], r["h"], c["structural"], c["by_field"]["kind"], hn, float(c["key"]), rel, fq))
    rng = np.random.default_rng(0)
    out = dict(census=a.census, census_sha256=hashlib.sha256(Path(a.census).read_bytes()).hexdigest(),
               per_example=a.per_example, per_example_sha256=hashlib.sha256(Path(a.per_example).read_bytes()).hexdigest(),
               probe_raw=a.probe_raw, run=praw.get("run"), seed=praw.get("seed"), target=praw.get("target"), git=_git(), by_lock={},
               voi=a.voi, voi_sha256=hashlib.sha256(Path(a.voi).read_bytes()).hexdigest() if a.voi else None,
               class_freq=a.class_freq, class_freq_sha256=hashlib.sha256(Path(a.class_freq).read_bytes()).hexdigest() if a.class_freq else None)
    for l in locks:
        arr = np.array(rows[l], dtype=np.float64)
        if len(arr) < 50:
            continue
        ce, h, es, ek, hn, cls, rel, fq = arr.T
        res = analyse(ce, h, es, ek, rng, h_next=hn if voi else None, cls=cls.astype(np.int64), freq=fq if freq else None); res["layer"] = layer_for[l]
        if relevant is not None:
            m = rel == 1.0
            res["relevant"] = analyse(ce[m], h[m], es[m], ek[m], rng, h_next=hn[m] if voi else None, cls=cls[m].astype(np.int64),
                                      freq=fq[m] if freq else None) if m.sum() >= 100 else None
            res["n_relevant"] = int(m.sum())
        out["by_lock"][str(l)] = res
        f = lambda v: "—" if v is None else f"{v:+.3f}"
        print(f"lock {l} layer {layer_for[l]}: n={res['n']}  probe CE {res['ce_mean']:.3f}  excess {res['excess_mean']:.4f}  "
              f"ρ(CE, excess)={f(res['spearman_struct'])} r={f(res['pearson_struct'])}  ρ(CE, kind)={f(res['spearman_kind'])}  "
              f"quartile means {['%.4f' % m if m is not None else '—' for m in res['quartiles_struct']['means']]} gap {f(res['quartiles_struct']['gap'])} "
              f"(null sd {res['quartiles_struct']['null']['sd']:.4f}, p {res['quartiles_struct']['null']['p_ge']:.3f})")
        if "determined" in res:
            d = res["determined"]
            print(f"   determined n={d['n']}: probe CE {d['ce_mean']:.3f}  excess {d['excess_mean']:.4f}  ρ(CE, excess)={f(d['spearman_struct'])}  "
                  f"ρ(CE, kind)={f(d['spearman_kind'])}  quartile means {['%.4f' % m if m is not None else '—' for m in d['quartiles_struct']['means']]} "
                  f"gap {f(d['quartiles_struct']['gap'])} (p {d['quartiles_struct']['null']['p_ge']:.3f})")
            for nm, key in (("H(next) bins", "residual_h_next"), ("class", "residual_class")):
                if key in d and d[key]["struct"]:
                    w = d[key]["struct"]; wk = d[key]["kind"]
                    print(f"   determined, residual within {nm}: n={w['n']} groups={w['n_groups']}  ρ={f(w['spearman'])}  gap {f(w['gap'])} "
                          f"(null sd {w['null']['sd']:.4f}, p {w['null']['p_ge']:.3f})  kind: ρ={f(wk['spearman'])} gap {f(wk['gap'])} (p {wk['null']['p_ge']:.3f})")
            if d.get("class_frequency", {}).get("struct"):
                cf = d["class_frequency"]; w = cf["struct"]
                print(f"   determined, class frequency: ρ(log count, probe CE)={f(cf['spearman_freq_ce'])} ρ(log count, excess)={f(cf['spearman_freq_excess'])}; "
                      f"residual within count bins: ρ={f(w['spearman'])} gap {f(w['gap'])} (p {w['null']['p_ge']:.3f})")
            if d.get("class_level", {}).get("struct"):
                c = d["class_level"]["struct"]; ck = d["class_level"]["kind"]
                print(f"   determined, between classes (>= 3 windows): classes={c['n_classes']} windows={c['n_windows']}  ρ={f(c['spearman'])}  "
                      f"quartile means {['%.4f' % m for m in c['quartile_means']]} gap {f(c['gap'])} (null sd {c['null']['sd']:.4f}, p {c['null']['p_ge']:.3f})"
                      f"  kind: ρ={f(ck['spearman'])} gap {f(ck['gap'])} (p {ck['null']['p_ge']:.3f})")
        if res.get("relevant"):
            v = res["relevant"]; d = v.get("determined", {})
            print(f"   RELEVANT (record k+1 on lock {l}) n={v['n']}: probe CE {v['ce_mean']:.3f}  excess {v['excess_mean']:.4f}  ρ={f(v['spearman_struct'])}  "
                  f"gap {f(v['quartiles_struct']['gap'])} (p {v['quartiles_struct']['null']['p_ge']:.3f})")
            if d:
                if d.get("class_frequency", {}).get("struct"):
                    cf = d["class_frequency"]; w = cf["struct"]
                    print(f"      class frequency: ρ(log count, CE)={f(cf['spearman_freq_ce'])} ρ(log count, excess)={f(cf['spearman_freq_excess'])}; residual: ρ={f(w['spearman'])} gap {f(w['gap'])} (p {w['null']['p_ge']:.3f})")
                print(f"      determined n={d['n']}: excess {d['excess_mean']:.4f}  ρ={f(d['spearman_struct'])}  gap {f(d['quartiles_struct']['gap'])} (p {d['quartiles_struct']['null']['p_ge']:.3f})"
                      + (f"  within class: ρ={f(d['residual_class']['struct']['spearman'])} gap {f(d['residual_class']['struct']['gap'])} (p {d['residual_class']['struct']['null']['p_ge']:.3f})" if d.get("residual_class", {}).get("struct") else "")
                      + (f"  between classes: ρ={f(d['class_level']['struct']['spearman'])} gap {f(d['class_level']['struct']['gap'])} (p {d['class_level']['struct']['null']['p_ge']:.3f})" if d.get("class_level", {}).get("struct") else ""))
        if "uncertain" in res:
            u = res["uncertain"]
            print(f"   uncertain n={u['n']}: probe CE−H {u['ce_mean'] - u['h_mean']:.3f}  excess {u['excess_mean']:.4f}  ρ(CE−H, excess)={f(u['spearman_struct'])}")
    if a.raw:
        Path(a.raw).write_text(json.dumps(out, indent=2, default=str) + "\n")
        print(f"raw -> {a.raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
