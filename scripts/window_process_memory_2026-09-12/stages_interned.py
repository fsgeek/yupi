"""C: new (interned) recursion at (T_ep,8,2) eps: staged RSS separating coarse aggregates from coarse mass_T projections."""
import sys, time, resource, gc
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import programs_for
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregate
from yupi.interfaces import project
def peak(): return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6,2)
def cur():
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS'): return round(int(l.split()[1])/1e6,2)
T_ep=int(sys.argv[1]); eps=Fraction(sys.argv[2]); law=WindowLaw(T_ep=T_ep,L=8,B=2)
cfg=WorldConfig.c1(epsilon=eps); progs=programs_for("c1prime-loop")
t0=time.time()
def mark(s): print(f"[{time.time()-t0:7.0f}s] cur={cur()} GB peak={peak()} GB  {s}", flush=True)
mark("start")
st={}
fine=window_law_aggregate(cfg,progs,law,"r4",st)
mT=st["mass_T"]
mark(f"NEW r4 recursion + fine mass_T: windows {len(fine)} agg entries {sum(len(v) for v in fine.values())} mass_T entries {sum(len(v) for v in mT.values())}")
nbits=sum(m.numerator.bit_length()+m.denominator.bit_length() for j in fine.values() for m in j.values())/sum(len(v) for v in fine.values())
mark(f"fine agg fractions mean bits {nbits:.1f}")
proj={}
for r in ("r3","r2","r1","r0"):
    recs={}; proj[r]={}
    for (reset,win),joint in fine.items():
        proj[r][(reset,win)]=(reset,tuple(recs.setdefault(x,x) for x in (project(y,r) for y in win)))
    mark(f"projection map {r} built ({len(recs)} distinct records)")
out={}
for r in ("r3","r2","r1","r0"):
    coarse={}
    for k,joint in fine.items():
        d=coarse.setdefault(proj[r][k],{})
        for s,m in joint.items(): d[s]=d.get(s,Fraction(0))+m
    out[r]=coarse
    mark(f"coarse agg {r}: windows {len(coarse)} entries {sum(len(v) for v in coarse.values())}")
outT={}
for r in ("r3","r2","r1","r0"):
    cT={}
    for k,e0 in mT.items():
        e=cT.setdefault(proj[r][k],{})
        for T,m in e0.items(): e[T]=e.get(T,Fraction(0))+m
    outT[r]=cT
    mark(f"coarse mass_T {r}: entries {sum(len(v) for v in cT.values())}")
# compact form of ALL mass_T (fine + coarse): per window a tuple of T's and a tuple of numerators over a common denominator per T
import math
def compact(mt):
    D={}
    for e in mt.values():
        for T,m in e.items(): D[T]=D.get(T,1)*m.denominator//math.gcd(D.get(T,1),m.denominator)
    return {k:(tuple(e.keys()), tuple(m.numerator*(D[T]//m.denominator) for T,m in e.items())) for k,e in mt.items()}, D
comp={}
for r,mt in [("r4",mT)]+list(outT.items()):
    comp[r]=compact(mt); mark(f"compact mass_T {r} built (int numerators over per-T lcm; lcm bits max {max(d.bit_length() for d in comp[r][1].values())})")
del proj; gc.collect(); mark("projection maps freed")
del outT; gc.collect(); mark("dict-of-Fraction coarse mass_T freed (compact kept)")
del mT; st.pop("mass_T"); gc.collect(); mark("fine dict-of-Fraction mass_T freed (compact kept)")
