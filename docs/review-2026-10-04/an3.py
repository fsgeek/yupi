import numpy as np, collections
A=np.load('/home/tony/.cache/yupi-scratch/review-2026-10-04/arrays.npz')
k1=A['k1'];kR=A['kR'];a1=A['i4_r1']
ind=a1>0
def feats(s):
    reset,body=s.split('|',1); recs=[r.split(',') for r in body.split(';')]
    acts=[r[1] for r in recs]; kinds=[r[0] for r in recs]
    early=set(acts[:3]); late=set(acts[3:])
    return dict(reset=reset=='R', ndist=len(set(acts)), early_recur=len(early&late)>0,
                last_in_early=acts[-1] in early, last2_in_early=bool(set(acts[-2:])&early),
                nactfield=collections.Counter(acts))
F=[feats(s) for s in k1]
print('actor values seen', collections.Counter(a for f in F for a in f['nactfield']).most_common(12))
for name in ('reset','ndist','early_recur','last_in_early','last2_in_early'):
    v=np.array([f[name] for f in F])
    print(name)
    for u in np.unique(v):
        s=v==u; print('   ',u,'n',s.sum(),'P(ind)',round(ind[s].mean(),3))
nrel=np.array([s.split('|',1)[1].count('K:') for s in kR])
print('n_relay'); 
for u in np.unique(nrel): s=nrel==u; print('   ',u,s.sum(),round(ind[s].mean(),3))
np.save('/home/tony/.cache/yupi-scratch/review-2026-10-04/feats.npy',np.array([[f['reset'],f['ndist'],f['early_recur'],f['last_in_early'],f['last2_in_early']] for f in F],dtype=float))
