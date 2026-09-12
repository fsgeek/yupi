"""B: interned recursion at (T_ep,8,2) eps: staged RSS + wall, then the original recursion in the same process, and equality of agg per rung and mass_T."""
import sys, time, resource, gc
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import programs_for
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregate, window_law_aggregates
from yupi.interfaces import project
from wp_interned import window_law_aggregate_interned, project_interned
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
fine=window_law_aggregate_interned(cfg,progs,law,"r4",st)
mark(f"INTERNED r4 recursion done: windows {len(fine)} agg entries {sum(len(v) for v in fine.values())} mass_T entries {sum(len(v) for v in st['mass_T'].values())} max_pairs {st['max_pairs']} states {st['n_distinct_states']} projected records {st['n_distinct_records']}")
t1=time.time()
out,outT=project_interned(fine, st["mass_T"], ("r3","r2","r1","r0"))
mark(f"INTERNED projections r3..r0 done ({time.time()-t1:.0f}s): windows " + " ".join(f"{r}={len(out[r])}" for r in out))
# compact mass_T: per window, tuple of (T, Fraction) -> measure the dict overhead alone
gc.collect(); mark("after gc")
# ---- original, same process
t2=time.time()
st0={}
fine0=window_law_aggregate(cfg,progs,law,"r4",st0)
mark(f"ORIGINAL r4 recursion done ({time.time()-t2:.0f}s vs interned {t1-t0:.0f}s)")
assert fine0==fine, "agg r4 differs"
assert st0["mass_T"]==st["mass_T"], "mass_T r4 differs"
mark("GATE r4: agg and mass_T equal")
for r in ("r3","r2","r1","r0"):
    coarse={}; coarseT={}
    for (reset,win),joint in fine0.items():
        key=(reset,tuple(project(x,r) for x in win))
        d=coarse.setdefault(key,{})
        for s,m in joint.items(): d[s]=d.get(s,Fraction(0))+m
        e=coarseT.setdefault(key,{})
        for T,m in st0["mass_T"][(reset,win)].items(): e[T]=e.get(T,Fraction(0))+m
    assert coarse==out[r] and coarseT==outT[r], r
    mark(f"GATE {r}: agg and mass_T equal")
print("ALL GATES PASSED", flush=True)
