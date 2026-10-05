import numpy as np, statsmodels.api as sm
A=np.load('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz')
k1=A['k1'];_,g=np.unique(k1,return_inverse=True)
a1=A['i4_r1'];aR=A['i4_r1R'];m=A['lm'];x=A['dio'];z=A['zero'].astype(bool);ind=(a1>0).astype(float)
s1=A['i1_r1']-a1;sR=A['i1_r1R']-aR;H=A['H']
def y(r,a): return np.mean([A[f'y_{r}_{a}_s{s}'] for s in range(3)],axis=0)
print('mean i4_r1',a1.mean(),'mean i4_r1R',aR.mean(), 'nonzero mean i4_r1', a1[a1>0].mean())
e=np.quantile(x,np.linspace(0,1,11)); idx=np.clip(np.searchsorted(e,x,side='right')-1,0,9)
for arm in ('primary','secondary'):
    d=y('r1',arm)-y('r1R',arm)
    fits={}
    for nm,cols in (('M1',[a1,aR,m]),('M1+ind',[a1,aR,ind,m]),('Fpaired',[a1,aR,ind,s1,sR,H,m])):
        X=np.column_stack([np.ones(len(d))]+cols); fits[nm]=X@sm.OLS(d,X).fit().params
    print(arm,'dec  dIota  i4r1  i4r1R  obs   '+'  '.join(fits))
    for q in range(10):
        s=idx==q; print('  ',q,f'{x[s].mean():+.3f} {a1[s].mean():.3f} {aR[s].mean():.3f} {d[s].mean():+.4f} se{d[s].std()/np.sqrt(s.sum()):.4f} '+' '.join(f'{f[s].mean():+.4f}' for f in fits.values()))
    print('   zero set obs',d[z].mean(),'nonzero obs',d[~z].mean(), 'overall', d.mean())
