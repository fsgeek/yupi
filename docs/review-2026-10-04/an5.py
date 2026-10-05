import numpy as np, statsmodels.api as sm
A=np.load('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz')
k1=A['k1'];_,g=np.unique(k1,return_inverse=True)
l1=A['i4_r1'];lR=A['i4_r1R'];s1=A['i1_r1']-l1;sR=A['i1_r1R']-lR;H=A['H'];m=A['lm'];ind=(l1>0).astype(float)
recs=[[r.split(',') for r in s.split('|',1)[1].split(';')] for s in k1]
def dummies(v):
    u=np.unique(v); return np.column_stack([(v==x).astype(float) for x in u[1:]])
last=np.array([r[6][0] for r in recs]); pen=np.array([r[5][0] for r in recs])
lastpair=np.array([r[5][0]+'>'+r[6][0] for r in recs])
def y(r,a): return np.mean([A[f'y_{r}_{a}_s{s}'] for s in range(3)],axis=0)
def fit(yy,cols,names,show):
    X=np.column_stack([np.ones(len(yy))]+cols); r=sm.OLS(yy,X).fit(cov_type='cluster',cov_kwds={'groups':g})
    return ' '.join(f'{n}={r.params[i+1]:+.4f}(t{r.tvalues[i+1]:+.1f})' for i,n in enumerate(names) if n in show)
base=[l1,lR,ind,s1,sR,H,m]; bn=['i4_r1','i4_r1R','ind','s1','sR','H','lm']
show={'i4_r1','i4_r1R','ind'}
for arm in ('primary','secondary'):
  for rung in ('r1','r1R'):
    yy=y(rung,arm)
    print(rung,arm,'F      ',fit(yy,base,bn,show))
    print(rung,arm,'F+lastFE',fit(yy,base+[dummies(last)],bn,show))
    print(rung,arm,'F+pairFE',fit(yy,base+[dummies(lastpair)],bn,show))
  d=y('r1',arm)-y('r1R',arm)
  print('PAIRED',arm,'F       ',fit(d,base,bn,show))
  print('PAIRED',arm,'F+pairFE',fit(d,base+[dummies(lastpair)],bn,show))
