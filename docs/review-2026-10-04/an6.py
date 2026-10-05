import numpy as np, statsmodels.api as sm
A=np.load('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz')
k1=A['k1'];_,g=np.unique(k1,return_inverse=True)
l1=A['i4_r1'];lR=A['i4_r1R'];s1=A['i1_r1']-l1;sR=A['i1_r1R']-lR;H=A['H'];m=A['lm'];ind=(l1>0).astype(float)
def y(r,a): return np.mean([A[f'y_{r}_{a}_s{s}'] for s in range(3)],axis=0)
def ols(yy,cols):
    X=np.column_stack([np.ones(len(yy))]+cols); return sm.OLS(yy,X).fit(cov_type='cluster',cov_kwds={'groups':g})
edges=[0,1e-3,1e-2,0.05,0.15,0.3,0.6,10]
b=np.digitize(l1,edges,right=True)  # 0 => exactly 0
print('bin counts',np.bincount(b))
D=np.column_stack([(b==k).astype(float) for k in range(1,len(edges))])
for rung in ('r1','r1R'):
  for arm in ('primary','secondary'):
    yy=y(rung,arm)
    r=ols(yy,[D,s1,sR,H,m]); print(rung,arm,'bin effects vs zero:',' '.join(f'{edges[k]:.0e}-{edges[k+1]:g}:{r.params[k+1]:+.4f}(t{r.tvalues[k+1]:+.1f})' for k in range(D.shape[1])))
    for nm,cols in (('l1 only',[l1,ind]),('lR only',[lR,ind]),('lR only noind',[lR]),('l1 only noind',[l1])):
        r=ols(yy,cols+[s1,sR,H,m]); print('    ',nm,f'{r.params[1]:+.4f}(t{r.tvalues[1]:+.1f}) R2={r.rsquared:.5f}')
