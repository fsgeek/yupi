"""Owner's independent re-derivation of the reviewer's load-bearing numbers (2026-10-04). Run inline twice that
evening, merged here verbatim in substance: last-kind fixed effects, n_relay identity, zero/non-zero paired gains,
paired model F, and binned ι4_r1 effects. Outputs are recorded in README.md."""
import sys
from math import log2
import numpy as np
sys.path.insert(0, 'scripts')
import relay_paired as rp, relay_v_diagnosis as dg, relay_free_difficulty as fd
from yupi.naming import pattern_all
from yupi.pattern_ceiling import load_table, serial_key

i1 = fd.iota(dg.CACHE / 'c1prime-loop-40-8-2-r1-eps1-k7-kind-m123456.jsonl')
iR = fd.iota(dg.CACHE / 'c1prime-loop-40-8-2-r1R-eps1-k7-kind-m123456.jsonl')
hk, lm = {}, {}
for key, (mass, star) in load_table(dg.TABLES / 'c1prime-loop-40-8-2-r1-eps1-k7.jsonl').items():
    kd = {}
    for r, p in star.items():
        kd[r.kind] = kd.get(r.kind, 0.0) + float(p)
    hk[serial_key(key)] = -sum(p * log2(p) for p in kd.values() if p > 0)
    lm[serial_key(key)] = log2(float(mass))
for arm in ('primary', 'secondary'):
    r1, r1R = dg.ARMS[arm]
    c1 = [rp.load_census(r) for r in r1]; cR = [rp.load_census(r) for r in r1R]
    ids = sorted(c1[0][1])
    recs1 = rp.load_records(c1[0][0]['corpus'], ids, 'r1'); recsR = rp.load_records(cR[0][0]['corpus'], ids, 'r1R')
    L1, LR, S1, SR, H, M, G, LK, NA, NR = [], [], [], [], [], [], [], [], [], []
    for i in ids:
        (s1, q1), (sR, qR) = recs1[i], recsR[i]
        k1 = serial_key((s1, pattern_all(q1[:7])[0])); kR = serial_key((sR, pattern_all(qR[:7])[0]))
        (a, b), (c, d) = i1[k1], iR[kR]
        L1.append(b); LR.append(d); S1.append(a - b); SR.append(c - d); H.append(hk[k1]); M.append(lm[k1]); G.append(k1)
        LK.append(q1[6].kind); NA.append(len({r.actor for r in q1[:7]})); NR.append(kR.split('|', 1)[1].count('K:'))
    L1, LR, S1, SR, H, M, NA, NR = map(np.array, (L1, LR, S1, SR, H, M, NA, NR)); G = np.array(G); LK = np.array(LK)
    print(arm, 'n_relay == 7 - distinct actors in all windows:', bool((NR == 7 - NA).all()))
    kinds = sorted(set(LK)); fe = [(LK == k).astype(float) for k in kinds[1:]]
    ind = (L1 > 0).astype(float)
    y1 = np.array([np.mean([r[i]['by_field']['kind'] for _, r in c1]) for i in ids])
    yR = np.array([np.mean([r[i]['by_field']['kind'] for _, r in cR]) for i in ids])
    for rung, y in (('r1', y1), ('r1R', yR)):
        X = np.column_stack([np.ones(len(y)), L1, LR, ind, S1, SR, H, M] + fe)
        b, se, _ = dg.ols_cr1(y, X, G)
        print(f'  {rung} {arm} +lastkind FE: iota4_r1 {b[1]:+.4f} (t {b[1]/se[1]:+.1f})  iota4_r1R {b[2]:+.4f} '
              f'(t {b[2]/se[2]:+.1f})  step {b[3]:+.4f} (t {b[3]/se[3]:+.1f})')
    dy = y1 - yR; z = L1 == 0
    print(f'  paired gain: all {dy.mean():+.5f}  zero-set {dy[z].mean():+.5f}  nonzero {dy[~z].mean():+.5f}')
    X = np.column_stack([np.ones(len(dy)), L1, LR, ind, S1, SR, H, M]); b, se, _ = dg.ols_cr1(dy, X, G)
    print(f'  paired model F: iota4_r1 {b[1]:+.4f} (t {b[1]/se[1]:+.1f}) step {b[3]:+.4f} (t {b[3]/se[3]:+.1f})')
    edges = [0, 1e-3, 1e-2, 5e-2, 0.1, 0.2, 0.4, 0.6, np.inf]
    bins = [((L1 > lo) & (L1 <= hi)).astype(float) for lo, hi in zip(edges[:-1], edges[1:])]
    for rung, y in (('r1', y1), ('r1R', yR)):
        X = np.column_stack([np.ones(len(y))] + bins + [S1, SR, H, M]); b, se, _ = dg.ols_cr1(y, X, G)
        print(f'  {rung} {arm} bins vs iota4_r1=0: ' + ' '.join(
            f'({lo:g},{hi:g}]{b[j+1]:+.3f}(t{b[j+1]/se[j+1]:+.1f})' for j, (lo, hi) in enumerate(zip(edges[:-1], edges[1:]))))
