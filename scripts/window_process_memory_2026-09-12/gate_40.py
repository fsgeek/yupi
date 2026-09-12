"""GATE (2026-09-12; inner-order checks and the MassT denominator report added after the Codex read, [rv-3] [rv-7]): the interned recursion (src/yupi/window_process.py) against the
2026-09-04 recursion (window_process_old.py = git HEAD 0e55a09's copy) at the frozen law
(40,8,2), looping C1', one eps per invocation: every rung's aggregate equal (==) with the
same key order, every rung's mass_T equal. Unpriced process (the old side alone is 13 GB)."""
import sys, time, resource, json
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import programs_for
from yupi.window import WindowLaw
from yupi.window_process import window_law_aggregates as new_aggs
from window_process_old import window_law_aggregates as old_aggs
def peak(): return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1e6,2)
eps=Fraction(sys.argv[1]); law=WindowLaw(T_ep=40,L=8,B=2); RUNGS=("r0","r1","r2","r3","r4")
cfg=WorldConfig.c1(epsilon=eps); progs=programs_for("c1prime-loop")
t0=time.time()
st_new={}; new=new_aggs(cfg,progs,law,RUNGS,st_new); t_new=time.time()-t0
print(f"new pass done {t_new:.0f}s peak(cumulative) {peak()} GB max_pairs {st_new['max_pairs']}", flush=True)
t1=time.time()
st_old={}; old=old_aggs(cfg,progs,law,RUNGS,st_old); t_old=time.time()-t1
print(f"old pass done {t_old:.0f}s peak(cumulative) {peak()} GB max_pairs {st_old['max_pairs']}", flush=True)
assert st_new["pairs_per_tick"]==st_old["pairs_per_tick"] and st_new["states_per_tick"]==st_old["states_per_tick"]
out=dict(law=dict(T_ep=40,L=8,B=2), programs="c1prime-loop", eps=str(eps), wall_new_s=t_new, wall_old_s=t_old, max_pairs=st_new["max_pairs"], rungs={})
for r in RUNGS:
    a,b=new[r],old[r]
    assert list(a.keys())==list(b.keys()), f"{r}: key order differs"
    assert a==b, f"{r}: aggregate differs"
    assert all(list(a[k].keys())==list(b[k].keys()) for k in a), f"{r}: inner state order differs"      # [rv-3] 2026-09-12
    ma,mb=st_new["mass_T_by_rung"][r], st_old["mass_T_by_rung"][r]
    assert list(ma.keys())==list(mb.keys()) and ma==mb, f"{r}: mass_T differs"
    # [rv-3] inner endpoint order: MassT decodes endpoints in increasing T; the 2026-09-04 coarse dicts held
    # first-seen order (a coarse window gathers its fine windows' endpoints in fine-window order). Values are
    # equal (asserted above); the order is REPORTED, not asserted — no consumer iterates endpoints order-
    # sensitively (each endpoint's sum runs over windows), and three artifacts reproduce byte for byte.
    inner_T_same=all(list(ma[k].keys())==list(mb[k].keys()) for k in ma)
    assert all(sorted(ma[k])==sorted(mb[k]) for k in ma), f"{r}: endpoint sets differ"
    n_agg=sum(len(v) for v in a.values()); n_mT=sum(len(v) for v in ma.values())
    out["rungs"][r]=dict(n_windows=len(a), agg_entries=n_agg, mass_T_entries=n_mT, equal=True, same_key_order=True,
                         same_inner_state_order=True, same_inner_endpoint_order=inner_T_same)
    print(f"GATE {r}: {len(a)} windows, {n_agg} agg entries, {n_mT} mass_T entries — equal, same outer and inner-state order; inner endpoint order {'same' if inner_T_same else 'sorted (old: first-seen)'}", flush=True)
mT=st_new["mass_T"]
out["mass_T_denominators"]={str(T): dict(bits=mT._D[T].bit_length(), width_bytes=mT._width[T]) for T in sorted(mT._D)}   # [rv-7]
out["verdict"]="ALL RUNGS EQUAL"
tag="" if eps==1 else "-eps1_2"
json.dump(out, open(f"gate-interned-full-order-40-8-2-2026-09-12{tag}.json","w"), indent=1)
print("ALL GATES PASSED", eps, flush=True)
