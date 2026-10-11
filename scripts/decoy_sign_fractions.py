"""Sign fractions of Δι_4 for the decoy and the relay at k = 7 (2026-10-11): sources the
inventory A4 "27 %" figure, which no committed raw held. Reuses decoy_iota_check.job."""
import sys, json
sys.path.insert(0, "/home/tony/projects/yupi/scripts")
import decoy_iota_check as D
from concurrent.futures import ProcessPoolExecutor
def main():
    jobs = [(e, w, 4) for e in ("1", "1/2") for w in ("r1", "decoy")]
    with ProcessPoolExecutor(4) as ex:
        res = list(ex.map(D.job, jobs))
    pcs = {(e, w): pc for e, w, m, s, pc in res}
    out = {}
    for e in ("1", "1/2"):
        mass = {D.serial_key(k): float(v[0]) for k, v in D.load_table(D.TABLES / f"c1prime-loop-40-8-2-r1-{D._tag(e)}-k7.jsonl").items()}
        rows = [json.loads(l) for l in open(D.RELAY / f"c1prime-loop-40-8-2-r1R-{D._tag(e)}-k7-kind-diota4.jsonl")]
        W = neg = pos = zero = rneg = 0.0; my = 0.0
        for r in rows:
            k, w = r["k"], mass[r["k"]]
            y = pcs[(e, "r1")][k] - pcs[(e, "decoy")][k]
            W += w; my += w * y
            neg += w * (y < -1e-12); pos += w * (y > 1e-12); zero += w * (abs(y) <= 1e-12)
            rneg += w * (r["d_iota4"] < -1e-12)
        out[e] = dict(mean_d_iota4_decoy=my / W, frac_decoy_further_back=neg / W, frac_decoy_closer=pos / W,
                      frac_decoy_zero=zero / W, frac_relay_further_back=rneg / W, W=W)
    print(json.dumps(out, indent=1))
if __name__ == "__main__":
    main()
