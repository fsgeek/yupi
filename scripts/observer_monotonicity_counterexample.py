"""Is observer-monotonicity (divergent mass non-decreasing as the observer
partition refines) a theorem of partition refinement alone?

Abstract model, matching the measured quantities' structure exactly:
 - states s carry a next-record law p_s and a tau value t_s;
 - a window w carries a belief b_w over states and a law mass m_w;
 - P-next(w) = sum_s b_w(s) p_s and tau(w) = sum_s b_w(s) t_s  (BOTH LINEAR);
 - windows w != w' are divergent iff P-next equal AND some tau unequal;
 - divergent mass = sum over unordered divergent pairs of 2*m_w*m_w'
   (the tv_sweep/divergent_grid convention);
 - refinement: each coarse window's belief is the mass-weighted mixture of
   its pieces' beliefs (forced, since a fine window key determines the
   coarse key and beliefs are path-aggregated).

If a refinement exists that DECREASES divergent mass, then 24/24 in the
measured grid is a fact about Yupana's rung structure, not a corollary of
refinement.
"""

from fractions import Fraction as F

# three states; x and y share a next-record law but differ on tau
P = {"x": ("p", ), "y": ("p", ), "z": ("q", )}     # symbolic p_s
T = {"x": F(0), "y": F(1), "z": F(5)}              # symbolic tau_s (scalar)


def pnext(belief):
    """Symbolic mixture of next-record laws: dict label -> weight."""
    out = {}
    for s, w in belief.items():
        out[P[s][0]] = out.get(P[s][0], F(0)) + w
    return tuple(sorted(out.items()))


def tau(belief):
    return sum(w * T[s] for s, w in belief.items())


def divergent_mass(windows):
    """windows: list of (name, mass, belief). Returns mass and the pairs."""
    tot, pairs = F(0), []
    for i in range(len(windows)):
        for j in range(i + 1, len(windows)):
            (na, ma, ba), (nb, mb, bb) = windows[i], windows[j]
            if pnext(ba) == pnext(bb) and tau(ba) != tau(bb):
                tot += 2 * ma * mb
                pairs.append((na, nb))
    return tot, pairs


mA, mB = F(1, 10), F(9, 10)

# COARSE: A is the 50/50 mixture of x and y; B is pure x.
# P-next(A) = P-next(B) = p  (x and y share a next-record law)
# tau(A) = 1/2, tau(B) = 0  -> divergent.
coarse = [("A", mA, {"x": F(1, 2), "y": F(1, 2)}),
          ("B", mB, {"x": F(1)})]

# FINE: the observer's extra field separates x from y inside A.
# B is unrefined (its belief is already a point mass).
fine = [("A1", mA / 2, {"x": F(1)}),
        ("A2", mA / 2, {"y": F(1)}),
        ("B", mB, {"x": F(1)})]

# refinement is consistent: A's belief is the mass-weighted mixture of A1, A2
mix = {}
for _, m, b in fine[:2]:
    for s, w in b.items():
        mix[s] = mix.get(s, F(0)) + m * w / mA
assert mix == coarse[0][2], (mix, coarse[0][2])

dc, pc = divergent_mass(coarse)
df, pf = divergent_mass(fine)
print(f"coarse divergent mass {dc} = {float(dc):.4f}   pairs {pc}")
print(f"fine   divergent mass {df} = {float(df):.4f}   pairs {pf}")
print(f"refinement changed mass by {float(df - dc):+.4f}  "
      f"({'DECREASE — monotonicity refuted' if df < dc else 'no decrease'})")

# why: the (A1,B) pair dies (identical beliefs -> tau equal), and the
# (A1,A2) pair it gains is weighted by mA^2, not mA*mB.
print(f"\nlost pair (A1,B): 2*({mA}/2)*{mB} = {float(2*(mA/2)*mB):.4f}")
print(f"gained pair (A1,A2): 2*({mA}/2)^2 = {float(2*(mA/2)**2):.4f}")
print("\nDecrease requires only mA < mB: the destroyed cross-pair is weighted")
print("by the OTHER window's mass, the created within-pair by its own.")
