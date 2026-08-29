"""Regenerate the per-endpoint fields of committed D8 attribution artifacts
after the 2026-08-29 endpoint-conditioning fix (truthsayer review, Finding 1).

(run: python scripts/d8_regen_per_endpoint.py IN.json OUT.json [--workers N])

For every cell: rebuild the latent/visible tables (same code path as the
measurement), recompute `per_endpoint_an` / `per_endpoint_un` with the
corrected functions, and CHECK that the law mean of each corrected series
equals the stored law-level `delta_an` / `delta_un` (|diff| ≤ 1e-9) — the
identity the old code preserved by accident and the new code must preserve
by construction; a cell failing that check is written with `regen_failed`
and the run exits nonzero. Every other field is copied verbatim. The
original pooled values are kept under `pooled_pre_2026_08_29_per_endpoint_an`
/ `..._un` (names chosen so the prediction loader's `per_endpoint_*` fan-out
does not pick them up) so the correction is diffable. Append-only: the input file is
never modified; OUT must be a new versioned path (the `-corrected` tag makes
the prediction loader prefer it over its untagged sibling).
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from yupi.attribution import latent_table, per_offset_anchored, visible_table  # noqa: E402
from yupi.d8_benchmark import world_of  # noqa: E402
from yupi.d8_measure import per_offset_unanchored  # noqa: E402
from yupi.window import WindowLaw  # noqa: E402

TOL = 1e-9


def regen_group(args):
    key, cells = args
    cache = {}
    out = []
    for c in cells:
        t = time.perf_counter()
        law = WindowLaw(c["T_ep"], c["L"], c["B"])
        cell = dict(world=c["world"], discipline=c["discipline"], eps=c["eps"], law=law, rung=c["rung"])
        cfg, progs = world_of(cell)
        lat = latent_table(cfg, progs, law, c["rung"], cache)
        vis, src = visible_table(lat, law.B)
        pa = per_offset_anchored(lat, vis, src, law)
        pu = per_offset_unanchored(lat, vis, law)
        del lat, vis, src
        ma = sum(pa.values()) / len(pa)
        mu = sum(pu.values()) / len(pu)
        ok = abs(ma - c["delta_an"]) <= TOL and abs(mu - c["delta_un"]) <= TOL
        new = dict(c)
        new["pooled_pre_2026_08_29_per_endpoint_an"] = c["per_endpoint_an"]
        new["pooled_pre_2026_08_29_per_endpoint_un"] = c["per_endpoint_un"]
        new["per_endpoint_an"] = {str(T): v for T, v in pa.items()}
        new["per_endpoint_un"] = {str(T): v for T, v in pu.items()}
        new["regen_per_endpoint"] = dict(date="2026-08-29", mean_an=ma, mean_un=mu,
                                         mean_matches_law_level=ok, wall_s=time.perf_counter() - t)
        if not ok:
            new["regen_failed"] = True
        out.append(new)
        print(f"[{time.strftime('%H:%M:%S')}] {c['world']}|{c['eps']}|{c['T_ep']}|{c['L']}|{c['B']}|{c['rung']}: "
              f"{'ok' if ok else 'MEAN MISMATCH'} {time.perf_counter() - t:.1f}s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp")
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    assert not os.path.exists(a.out), "append-only: refuse to overwrite an existing artifact"
    d = json.load(open(a.inp))
    groups = {}
    for c in d["cells"]:
        groups.setdefault((c["world"], c["discipline"], c["eps"], c["T_ep"]), []).append(c)
    jobs = sorted(groups.items(), key=lambda kv: -kv[0][3])
    print(f"{len(d['cells'])} cells in {len(jobs)} groups on {a.workers} workers", flush=True)
    cells = []
    with Pool(a.workers) as pool:
        for res in pool.imap_unordered(regen_group, jobs):
            cells.extend(res)
    key = lambda c: (c["world"], c["discipline"], c["eps"], c["T_ep"], c["L"], c["B"], c["rung"])
    cells.sort(key=key)
    failed = [c for c in cells if c.get("regen_failed")]
    out = dict(d)
    out["cells"] = cells
    out["correction"] = dict(date="2026-08-29", source=os.path.basename(a.inp),
                             fields=["per_endpoint_an", "per_endpoint_un"],
                             reason="truthsayer review 2026-08-29 Finding 1: per-endpoint values were pooled by offset "
                                    "(every reset-visible endpoint T <= L shares u = 0); now conditioned on endpoint T = u + n",
                             law_level_fields_unchanged=True, cells_failed=len(failed))
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"{a.out}: {len(cells)} cells, {len(failed)} failed mean check", flush=True)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
