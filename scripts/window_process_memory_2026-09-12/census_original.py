"""A: original recursion census at (T_ep,8,2) eps=1: RSS by stage (no mass_T, then with), object identity census."""
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
fine=window_law_aggregate(cfg,progs,law,"r4",None)   # no stats -> no mass_T
mark(f"ORIGINAL r4 recursion, no mass_T: windows {len(fine)} entries {sum(len(v) for v in fine.values())}")
sid=set(); sval=set(); rid=set(); rval=set(); wid=set()
nbits=0; nfrac=0
for (reset,win),joint in fine.items():
    wid.add(id(win))
    for x in win: rid.add(id(x)); rval.add(x)
    for s,m in joint.items():
        sid.add(id(s)); sval.add(s); nfrac+=1; nbits+=m.numerator.bit_length()+m.denominator.bit_length()
mark(f"census: state objects {len(sid)} distinct values {len(sval)}; record objects {len(rid)} distinct values {len(rval)}; window tuples {len(wid)}; fractions {nfrac} mean bits {nbits/nfrac:.1f}")
out={}
for r in ("r3","r2","r1","r0"):
    coarse={}
    for (reset,win),joint in fine.items():
        key=(reset,tuple(project(x,r) for x in win))
        d=coarse.setdefault(key,{})
        for s,m in joint.items(): d[s]=d.get(s,Fraction(0))+m
    out[r]=coarse
    mark(f"projected {r}: windows {len(coarse)} entries {sum(len(v) for v in coarse.values())}")
del out; gc.collect(); mark("projections freed")
