"""D: common-denominator hypothesis — per tick, lcm of frontier denominators, factored."""
import sys, math
from fractions import Fraction
from yupi.config import WorldConfig
from yupi.programs import programs_for
from yupi.window import WindowLaw
from yupi.kernel import enabled
from yupi.state import initial_state
def factor(n):
    f={}; d=2
    while d*d<=n:
        while n%d==0: f[d]=f.get(d,0)+1; n//=d
        d+=1
    if n>1: f[n]=f.get(n,0)+1
    return f
for eps in (Fraction(1),Fraction(1,2)):
    cfg=WorldConfig.c1(epsilon=eps); progs=programs_for("c1prime-loop")
    dist={initial_state(cfg):Fraction(1)}
    for t in range(1,int(sys.argv[1])+1):
        nxt={}
        for s,m in dist.items():
            for tr,p in enabled(s,cfg,progs):
                nxt[tr.next_state]=nxt.get(tr.next_state,Fraction(0))+m*p
        dist=nxt
        l=1
        for m in dist.values(): l=l*m.denominator//math.gcd(l,m.denominator)
        print(f"eps={eps} t={t:2d} states={len(dist):5d} lcm(denoms)={factor(l)} bits={l.bit_length()}", flush=True)
