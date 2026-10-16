"""Reviewer script (Claude, skeleton v0.8 review, 2026-10-15), archived by the owner: R/G/swap susceptibility in TV balls.
  python3 -I scripts/review/tolerance_r_g_swap.py r1,r3 1   (rows: ~/.cache/yupi-scratch/split-v2, pinned in docs/split-v2-rows-sha256-2026-10-15.txt)"""
import json, sys
from fractions import Fraction
from pathlib import Path
import numpy as np
ROWS = Path.home()/".cache/yupi-scratch/split-v2"
DELTAS=(0.01,0.02,0.05)
for eps in sys.argv[2].split(","):
  for rung in sys.argv[1].split(","):
    items={}; hs={}
    for l in open(ROWS/f"c1prime-loop-40-8-2-{rung}-eps{eps}-k7.jsonl"):
        r=json.loads(l)
        key=(tuple(sorted(map(tuple,r["p_star"]))), round(r["g"]+0.0,9))
        items[key]=items.get(key,0)+r["mass"]; hs[key]=r["h_star"]
    kinds=sorted({k for key in items for k,_ in key[0]})
    keys=list(items)
    P=np.array([[float(Fraction(dict(k[0]).get(x,"0"))) for x in kinds] for k in keys])
    G=np.array([k[1] for k in keys]); H=np.array([hs[k] for k in keys]); Rr=H-G
    W=np.array([items[k] for k in keys]); W=W/W.sum()
    n=len(keys); out=dict(eps=eps,rung=rung,K=len(kinds))
    acc={d:dict(UG=0,UR=0,USwap=0,UShare=0,dHmax_wmean=0) for d in DELTAS}
    share=np.where(H>1e-9,G/np.maximum(H,1e-12),0)
    for i0 in range(0,n,256):
        sl=slice(i0,i0+256); w=W[sl]
        tv=0.5*np.abs(P[sl,None,:]-P[None,:,:]).sum(-1)
        dG=G[None,:]-G[sl,None]; dR=Rr[None,:]-Rr[sl,None]; dH=np.abs(H[None,:]-H[sl,None])
        dS=np.abs(share[None,:]-share[sl,None])
        for d in DELTAS:
            inb=tv<=d+1e-15
            acc[d]["UG"]+=(w*(inb&(np.abs(dG)>=0.1)).any(1)).sum()
            acc[d]["UR"]+=(w*(inb&(np.abs(dR)>=0.1)).any(1)).sum()
            acc[d]["USwap"]+=(w*(inb&(((dG>=0.05)&(dR<=-0.05))|((dG<=-0.05)&(dR>=0.05)))).any(1)).sum()
            acc[d]["UShare"]+=(w*(inb&(dS>=0.1)).any(1)).sum()
            acc[d]["dHmax_wmean"]+=(w*np.where(inb,dH,0).max(1)).sum()
    for d in DELTAS: out[d]={k:round(v,4) for k,v in acc[d].items()}
    print(out,flush=True)
