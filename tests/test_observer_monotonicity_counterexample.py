"""Witness for the divergent-grid open question 1 refutation.

Observer-monotonicity (divergent mass non-decreasing as the observer
partition refines) is NOT a consequence of partition refinement: since
P-next and the tau functionals are linear in the belief, a coarse window's
mixture can coincide with another's while no piece-pair coincides. This
test pins the counterexample so the refutation cannot silently rot.

Structure mirrors the measured quantities exactly (see
docs/c1-observer-monotonicity-note-v0.1.md).
"""

from fractions import Fraction as F

# x and y share a next-record law (so P-next cannot separate them) but
# carry different tau values; refinement separates them inside window A.
NEXT_LAW = {"x": "p", "y": "p", "z": "q"}
TAU = {"x": F(0), "y": F(1), "z": F(5)}


def pnext(belief):
    out = {}
    for s, w in belief.items():
        out[NEXT_LAW[s]] = out.get(NEXT_LAW[s], F(0)) + w
    return tuple(sorted(out.items()))


def tau(belief):
    return sum(w * TAU[s] for s, w in belief.items())


def divergent_mass(windows):
    """windows: [(name, mass, belief)]; pair weight 2*m_a*m_b, delta=0 corner."""
    total = F(0)
    for i in range(len(windows)):
        for j in range(i + 1, len(windows)):
            (_, ma, ba), (_, mb, bb) = windows[i], windows[j]
            if pnext(ba) == pnext(bb) and tau(ba) != tau(bb):
                total += 2 * ma * mb
    return total


def test_refinement_can_destroy_divergent_mass():
    mA, mB = F(1, 10), F(9, 10)
    coarse = [("A", mA, {"x": F(1, 2), "y": F(1, 2)}),
              ("B", mB, {"x": F(1)})]
    fine = [("A1", mA / 2, {"x": F(1)}),
            ("A2", mA / 2, {"y": F(1)}),
            ("B", mB, {"x": F(1)})]

    # the refinement is consistent: A's belief is the mass-weighted mixture
    # of its pieces' beliefs, as path aggregation forces
    mixed = {}
    for _, m, b in fine[:2]:
        for s, w in b.items():
            mixed[s] = mixed.get(s, F(0)) + m * w / mA
    assert mixed == coarse[0][2]

    coarse_mass = divergent_mass(coarse)
    fine_mass = divergent_mass(fine)
    assert coarse_mass == F(9, 50)
    assert fine_mass == F(19, 200)
    assert fine_mass < coarse_mass, "refinement must be able to lose mass"


def test_loss_mechanism_is_the_mass_asymmetry():
    """The destroyed cross-pair is weighted by the OTHER window's mass; the
    created within-pair only by its own. So any mA < mB gives a decrease."""
    mA, mB = F(1, 10), F(9, 10)
    destroyed = 2 * (mA / 2) * mB          # (A1, B): identical beliefs, tau ties
    created = 2 * (mA / 2) * (mA / 2)      # (A1, A2): new sibling pair
    assert destroyed > created
