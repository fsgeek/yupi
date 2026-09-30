# Does the long-lag law extend to "who"? Design and pre-registration v0.1 (2026-09-30)

> **Status: CONFIRMATORY design + pre-registration** by the owner (instance of
> 2026-09-28/29/30), stamped **before** any actor-target ι has been computed and before any
> analysis of the actor field against ι has been run on any census. The third test owed by
> `docs/d1-long-lag-verdict-v0.1.md` ("Target: KIND only").

## Quantity

The ι of `docs/implicit-information-design-v0.1.md`, on the target T = (KIND, ACTOR) of the next
record, with ACTOR in the suffix-coarsened pattern names of design §1 (an actor seen only before
the suffix reads as fresh, so this ι is a lower bound). The chain rule for KL gives, per class c:

> ι_{(K,A)},m(c) = ι_K,m(c) + ι_{A|K},m(c)

where ι_{A|K},m is the law-mass-weighted KL of the actor-given-kind laws. **The actor's
long-lag load is ι_{A|K},4 = ι_{(K,A)},4 − ι_K,4**, computed per class. Gate: the identity
(mean KL = H_m − H̄) on the joint target, and ι_{A|K},m ≥ 0 per class up to 1e-12. Chain-rule
terms are non-negative per class, and a negative value would signal a bug.

## Frozen analysis (to be implemented and frozen before it touches a census)

`scripts/implicit_info_bintest_actor.py`: a copy of the frozen `implicit_info_bintest.py` with
exactly these changes. The response is the census's `by_field.actor`. The regressors are
ι_{A|K},4 (long), ι_{A|K},1 − ι_{A|K},4 (short), the class's exact H(ACTOR | KIND) (the
analogue of H_kind), and log₂ class mass. The model and HC1 errors are unchanged. The frozen
copy's sha256 is recorded in the verdict. No other change.

## Data

Every census raw that exists or will exist for r1–r4 (r0 has no actor): the 15 ε = 1 censuses of
2026-09-21/22, the 21 held-out ones of 2026-09-29, and the converged-ladder censuses when they
exist. None has ever been analysed against actor ι.

## Predictions

- **A1.** β_long > 0 with t ≥ 3 in every r1–r4 run of the 2026-09-21/22/29 censuses (36 runs).
- **A2.** Pooled per cell (the eight cell/ε combinations present), β_long > 0 with t ≥ 5.
- **A3 (distance, not history).** Pooled per cell, β_long > β_short.
- **A4 (converged).** A1 holds in every converged-ladder r1–r4 run once they are censused.

No magnitude band: the actor's scale differs from KIND's, and I have no basis for one.

## Reading

A1–A3 passing extend the law from *what happens next* to *who does it*. The actor field carries
most of the learner's excess (note §8), so this is the larger share of the story. If A3 fails
while A1 holds, then for identities any history is costly, not only distant history, and paper
1 says so.
