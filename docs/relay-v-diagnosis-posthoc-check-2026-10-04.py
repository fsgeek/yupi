"""Post-hoc descriptive check behind docs/relay-v-diagnosis-results-v0.1.md point 3 (run inline 2026-10-04,
saved verbatim here): ι4 at each rung by decile of Δι, and the exact-zero set's profile, primary arm."""
import sys, numpy as np
sys.path.insert(0,'scripts')
import relay_paired as rp, relay_v_diagnosis as d
from yupi.naming import pattern_all
from yupi.pattern_ceiling import serial_key
r1, r1R = d.ARMS['primary']
c1=[rp.load_census(r) for r in r1]; cR=[rp.load_census(r) for r in r1R]
ids=sorted(c1[0][1]); recs1=rp.load_records(c1[0][0]['corpus'],ids,'r1'); recsR=rp.load_records(cR[0][0]['corpus'],ids,'r1R')
diota,_=rp.load_diota(d.EXACT_SIDE,'1')
_,y,x,z,_=rp.join([r for _,r in c1],[r for _,r in cR],recs1,recsR,diota)
i1=d.iota4(d.CACHE/'c1prime-loop-40-8-2-r1-eps1-k7-kind-m123456.jsonl'); iR=d.iota4(d.CACHE/'c1prime-loop-40-8-2-r1R-eps1-k7-kind-m123456.jsonl')
a1=[];aR=[];nr=[]
for i in ids:
    (s1,q1),(sR,qR)=recs1[i],recsR[i]
    k1=serial_key((s1,pattern_all(q1[:7])[0])); kR=serial_key((sR,pattern_all(qR[:7])[0]))
    a1.append(i1[k1]); aR.append(iR[kR]); nr.append(kR.split('|',1)[1].count('K:'))
a1=np.array(a1);aR=np.array(aR);nr=np.array(nr)
e=np.quantile(x,np.linspace(0,1,11)); idx=np.clip(np.searchsorted(e,x,side='right')-1,0,9)
print('dec mean_dIota mean_i4_r1 mean_i4_r1R mean_dEx')
for q in range(10):
    s=idx==q; print(q, round(x[s].mean(),4), round(a1[s].mean(),4), round(aR[s].mean(),4), round(y[s].mean(),5))
print('exact-zero set: n',z.sum(),'i4_r1',a1[z].mean().round(4),'i4_r1R',aR[z].mean().round(4),'n_relay',nr[z].mean().round(2),'| all: i4_r1',a1.mean().round(4),'n_relay',nr.mean().round(2))
print('zero set share with i4_r1==0:', (a1[z]==0).mean().round(3), ' all:', (a1==0).mean().round(3))
