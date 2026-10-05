import sys, json, numpy as np
from math import log2
sys.path.insert(0,'/home/tony/projects/yupi/scripts')
import relay_paired as rp, relay_v_diagnosis as dg
from yupi.naming import pattern_all
from yupi.pattern_ceiling import load_table, serial_key
K=7
def io(p):
    o={}
    for l in open(p):
        d=json.loads(l); o[d['k']]=d
    return o
i1=io(dg.CACHE/'c1prime-loop-40-8-2-r1-eps1-k7-kind-m123456.jsonl'); iR=io(dg.CACHE/'c1prime-loop-40-8-2-r1R-eps1-k7-kind-m123456.jsonl')
tab=load_table(dg.TABLES/'c1prime-loop-40-8-2-r1-eps1-k7.jsonl')
hk={};lm={}
for key,(mass,star) in tab.items():
    kd={}
    for r,p in star.items(): kd[r.kind]=kd.get(r.kind,0)+p
    hk[serial_key(key)]=-sum(float(p)*log2(float(p)) for p in kd.values() if p>0)
    lm[serial_key(key)]=log2(float(mass))
diota,_=rp.load_diota(dg.EXACT_SIDE,'1')
out={}
for arm,(r1,r1R) in dg.ARMS.items():
    c1=[rp.load_census(r) for r in r1]; cR=[rp.load_census(r) for r in r1R]
    ids=sorted(c1[0][1])
    if arm=='primary':
        recs1=rp.load_records(c1[0][0]['corpus'],ids,'r1'); recsR=rp.load_records(cR[0][0]['corpus'],ids,'r1R')
        keys1=[];keysR=[]
        for i in ids:
            (s1,q1),(sR,qR)=recs1[i],recsR[i]
            keys1.append(serial_key((s1,pattern_all(q1[:K])[0]))); keysR.append(serial_key((sR,pattern_all(qR[:K])[0])))
        out['k1']=np.array(keys1); out['kR']=np.array(keysR); out['ids']=np.array(ids)
        out['nrec']=np.array([len(recs1[i][1]) for i in ids])
    else:
        assert list(out['ids'])==ids
    for rung,rows in (('r1',c1),('r1R',cR)):
        for s,(c,r) in enumerate(rows):
            out[f'y_{rung}_{arm}_s{s}']=np.array([r[i]['by_field']['kind'] for i in ids])
            out[f'key_{rung}_{arm}_s{s}']=np.array([str(r[i]['key']) for i in ids])
k1=out['k1'];kR=out['kR']
for j in range(1,7):
    out[f'i{j}_r1']=np.array([i1[k][f'iota_{j}'] for k in k1]); out[f'i{j}_r1R']=np.array([iR[k][f'iota_{j}'] for k in kR])
out['H']=np.array([hk[k] for k in k1]); out['lm']=np.array([lm[k] for k in k1])
out['dio']=np.array([diota[k][1] for k in k1]); out['zero']=np.array([diota[k][2] for k in k1])
np.savez('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz',**out)
print('ok',len(k1))
