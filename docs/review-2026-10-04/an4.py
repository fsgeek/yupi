import numpy as np, collections
A=np.load('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz')
k1=A['k1'];a1=A['i4_r1'];ind=a1>0;H=A['H']
recs=[[r.split(',') for r in s.split('|',1)[1].split(';')] for s in k1]
for pos in (6,5,0):
    v=np.array([r[pos][0] for r in recs]); print('kind at pos',pos)
    for u in np.unique(v): s=v==u; print('   ',u,s.sum(),round(ind[s].mean(),3))
print('H_kind by ind: mean', H[ind].mean(), H[~ind].mean(), ' H==0 share', (H[~ind]<1e-12).mean(), (H[ind]<1e-12).mean())
print('i1 (total info) by ind', A['i1_r1'][ind].mean(), A['i1_r1'][~ind].mean())
print('lm by ind', A['lm'][ind].mean(), A['lm'][~ind].mean())
