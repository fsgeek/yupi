import numpy as np, statsmodels.api as sm, sys
sys.path.insert(0,'/home/tony/projects/yupi/scripts')
import relay_v_diagnosis as dg
A=np.load('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz')
k1=A['k1']; kR=A['kR']
_,g=np.unique(k1,return_inverse=True)
def y(rung,arm): return np.mean([A[f'y_{rung}_{arm}_s{s}'] for s in range(3)],axis=0)
a1=A['i4_r1']; aR=A['i4_r1R']; lm=A['lm']; H=A['H']
nrel=np.array([s.split('|',1)[1].count('K:') for s in kR])
print('recon', np.abs(a1-aR-A['dio']).max())
# class keys in census match? check key ids consistent: census key -> k1 bijection
for arm in ('primary','secondary'):
    for rung in ('r1','r1R'):
        ck=A[f'key_{rung}_{arm}_s0']; kk=k1 if rung=='r1' else kR
        m={} ; bad=0
        for a,b in zip(ck,kk):
            if m.setdefault(a,b)!=b: bad+=1
        print(arm,rung,'census key->class conflicts',bad, 'n distinct',len(set(ck)),len(set(kk)))
# r1 class -> r1R class one-to-one?
print('r1 classes',len(set(k1)),'r1R classes',len(set(kR)),'pairs',len(set(zip(k1,kR))))
for arm in ('primary','secondary'):
    d=y('r1',arm)-y('r1R',arm)
    X=np.column_stack([np.ones(len(d)),a1,aR,lm])
    b,se,_=dg.ols_cr1(d,X,g)
    r=sm.OLS(d,X).fit(cov_type='cluster',cov_kwds={'groups':g})
    print(arm,'M1 mine',np.round(b,5),np.round(b/se,2)); print(arm,'M1 sm  ',np.round(r.params,5),np.round(r.tvalues,2))
    X=np.column_stack([np.ones(len(d)),nrel,lm]); r=sm.OLS(d,X).fit(cov_type='cluster',cov_kwds={'groups':g}); print(arm,'M2 sm',np.round(r.params,5),np.round(r.tvalues,2))
    X=np.column_stack([np.ones(len(d)),a1,aR,nrel,lm]); r=sm.OLS(d,X).fit(cov_type='cluster',cov_kwds={'groups':g}); print(arm,'M3 sm',np.round(r.params,5),np.round(r.tvalues,2))
    # sum test
    X=np.column_stack([np.ones(len(d)),a1,aR,lm]); r=sm.OLS(d,X).fit(cov_type='cluster',cov_kwds={'groups':g})
    print(arm,'sum', r.t_test([0,1,1,0]))
