"""Reviewer script (Claude, skeleton v0.7 review, 2026-10-15), archived by the owner: grid-rounded identifiability. Superseded by scripts/identifiability_tolerance.py."""
import json,sys
from fractions import Fraction
from collections import defaultdict
f=sys.argv[1]
rows=[json.loads(l) for l in open(f)]
M=sum(r['mass'] for r in rows)
kinds=sorted({k for r in rows for k,_ in r['p_star']})
print(f.split('/')[-1], 'classes',len(rows),'kinds',kinds)
def vec(r):
    d=dict(r['p_star']); return tuple(float(Fraction(d.get(k,'0'))) for k in kinds)
V=[vec(r) for r in rows]
# templates: P* vectors among G==0 classes with H*>0 or any
tmpl=defaultdict(float)
for r,v in zip(rows,V):
    if abs(r['g'])<1e-12: tmpl[tuple(round(x,6) for x in v)]+=r['mass']/M
print(' distinct P* among G=0 classes:',len(tmpl),' top:',sorted(tmpl.items(),key=lambda t:-t[1])[:6])
for tol in [0,0.005,0.01,0.02,0.05,0.1]:
    g=defaultdict(list)
    for r,v in zip(rows,V):
        key=tuple(round(x/tol) for x in v) if tol else tuple(round(x,12) for x in v)
        g[key].append(r)
    m1=0;m25=0;n=0
    for key,rs in g.items():
        gs=[r['g'] for r in rs]; sp=max(gs)-min(gs)
        if sp>=0.1: m1+=sum(r['mass'] for r in rs); n+=1
        if sp>=0.25: m25+=sum(r['mass'] for r in rs)
    print(f' tol {tol}: groups {len(g)} groups_span>=0.1 {n} mass>=0.1 {m1/M:.4f} mass>=0.25 {m25/M:.4f}')
# within H* bins (0.05) spread of G, for comparison; and distinct P* mass concentration
