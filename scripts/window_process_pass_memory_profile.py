"""Stage-by-stage memory of one (40,8,2) pass on the current instrument (relaunched 2026-09-11;
the 2026-09-06 run's log was lost when /tmp was cleared). Read-only diagnostic."""
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
eps=Fraction(sys.argv[1]); law=WindowLaw(T_ep=40,L=8,B=2)
cfg=WorldConfig.c1(epsilon=eps); progs=programs_for("c1prime-loop")
t0=time.time()
def mark(s): print(f"[{time.time()-t0:7.0f}s] cur={cur()} GB peak={peak()} GB  {s}", flush=True)
mark("start")
stats={}
fine=window_law_aggregate(cfg, progs, law, "r4", stats)
mark("after r4 recursion: fine agg + mass_T(r4) live")
mT=stats["mass_T"]
print("  r4 windows", len(fine), "agg entries", sum(len(v) for v in fine.values()), "mass_T entries", sum(len(v) for v in mT.values()), flush=True)
out={}; outT={}
for r in ("r3","r2","r1","r0"):
    coarse={}; coarseT={}
    for (reset,win),joint in fine.items():
        key=(reset,tuple(project(x,r) for x in win))
        d=coarse.setdefault(key,{})
        for s,m in joint.items(): d[s]=d.get(s,Fraction(0))+m
        e=coarseT.setdefault(key,{})
        for T,m in mT[(reset,win)].items(): e[T]=e.get(T,Fraction(0))+m
    out[r]=coarse; outT[r]=coarseT
    mark(f"after projecting {r}: agg {len(coarse)} windows, mass_T entries {sum(len(v) for v in coarseT.values())}")
del outT; del mT; stats.pop("mass_T",None); gc.collect()
mark("after deleting mass_T and every mass_T projection (agg + agg projections only)")
del out; gc.collect(); mark("after deleting agg projections (fine agg only)")
