# Does the ι4 > 0 step survive stratification? Results v0.1 (2026-10-05)

> **Status: EXPLORATORY.** Design `docs/plateau-stratified-design-v0.1.md` and script `scripts/plateau_stratified.py`
> were committed and stamped before the run (fc05734). Raws and log: `docs/plateau-stratified-2026-10-05.{json,log}`.
> Post-hoc diagnostic: `scripts/plateau_stratified_diag.py` and its log (d5d13c6). Reviewed before this note was
> written, per the 2026-10-04 lesson. Records are in §4. Written by the instance of 2026-10-05.

## 1. The pre-declared result

Spec D compares windows with ι4 in (0, 0.01] against windows with ι4 = 0. It uses only windows with ι4 ≤ 0.01 and
controls for S, H and M plus type-cell fixed effects (last kind × IO_ISSUE-in-window × reset). Applying the
declared rule:
- **count learner: survives** (β > 0 with t ≥ 3 in 6 of 8 cells);
- **transformer: mixed** (3 of 8 cells meet that bar, and 4 have |t| < 2).

The transformer's estimates are +0.001 to +0.012 bits; the count learner's are +0.018 to +0.051.

## 2. Why the verdict cannot be read as written: the low end is not identified

**Raw comparison.** Without controls, the near-zero vs zero difference within ι4 ≤ 0.01 is −0.010 to +0.007 for
the count learner and 0.000 to +0.004 for the transformer. A step appears only when controls are added, and its
size depends on how they are specified. The count learner's estimate ranges from −0.008 to +0.05 across
specifications (diagnostic log).

**The reason (reviewer finding, re-derived by the owner from the exact tables).** Within ι4 ≤ 0.01, the ι4 = 0
classes take **exactly three** next-KIND entropies: 0, H(⅓, ⅔) = 0.918, and one value near 1.5. No ι4 = 0 mass
lies in H ∈ (0.01, 0.7). That interval holds 73 % (r1 ε=1), 58 % (r3 ε=1), 48 % (r2 ε=½) and 39 % (r4 ε=½) of the
near-zero ι4 > 0 mass. The near-zero classes are also "easier" on the covariates: about 1.2 bits more mass, and
mean H 0.16–0.25 against 0.78.

Every adjusted step therefore extrapolates across a region with no comparison classes. The functional form fills
the gap:
- splines and local fits move the transformer between −0.0005 and +0.017;
- exact matching on type × mass × H bin covers only 26–64 % of treated windows.

This applies to the count learner's pre-declared "survives" too: spec D's linear H term bridges the same empty
region. Where the groups do overlap, the evidence is weak:
- **H < 0.01:** both learners show about 0, a floor effect that says nothing.
- **H ≥ 0.7:** the raw transformer difference is +0.005 to +0.016 in 7 of 8 cells. This hints at a real step,
  but matched coverage is only 1–34 %.

**Count learner, eps1 cells (reviewer, changes number).** The count learner's raw step sits in the bottom bin:
D0 for (0, 0.001] is +0.010 to +0.022, while D0 for (0.001, 0.01] is about 0. That bin has only 359–631 classes.
For the transformer the two bins are equal.

## 3. Reading

- **Withdrawn as a finding:** "the learner's cost tracks the *presence* of long-range dependence, not its
  quantity" (skeleton v0.2 D2′, exploratory). Its distinctive low end is **not identified** in these data. It is
  neither confirmed nor shown to be false. My first diagnosis, that the step is an artifact of global linear
  slopes, claimed more than the data support, and is withdrawn too.
- **Stands:** the rise in the top bin (ι4 > 0.6), the within-cell association (confirmatory), and the relay's
  rejection of the distance reading (confirmatory).
- **A structural fact worth keeping:** at the low end, "no long-range KIND information" coincides with
  deterministic or symmetric posteriors. Classes with ι4 = 0 are simple in a second way. Any learner comparison
  that conditions on ι4 = 0 is also conditioning on posterior shape.
- **For the confirmatory test:** no presence-step prediction as stated. A testable version needs ι4 = 0 and
  ι4 > 0 classes matched on posterior shape, for instance by design in the simulator, or a prediction stated only
  on the overlap region with its coverage reported. Without either, the prediction is dropped.

## 4. Review record

- **Claude reviewer (independent code, scratch `review-plateau/`):** reproduced spec A and D0 exactly, and checked
  joins, clustering and seeds. Found the H non-overlap (*changes conclusion*: "not identified", not "artifact"),
  the count learner's bottom-bin concentration (*changes number*), and two wording points. One was that the
  owner's quoted full-sample transformer range (0.006–0.017) is spec C′; plain spec A with merged bins gives
  0.008–0.026. All adopted. The overlap fact was re-derived by the owner from the exact tables (scratch `hgap.py`;
  numbers in §2).
- **Codex (GPT) reviewer (independent code, read-only).** Method: reweighting within type cells on log2 mass
  (0.5-bit bins) and H (0.05-bit bins, H = 0 kept separate), with class-level influence-function errors, in r1 ε=1
  and r2 ε=½. It reproduced the raw differences, spec D and the count-baseline low bins. Findings:
  - **Changes conclusion, adopted:** "largely an artifact" is not proven, since local regressions keep positive
    signals.
  - **Changes conclusion, adopted:** the overlap is almost entirely among deterministic (H = 0) classes.
    Restricted to H > 0, class effective sample sizes fall to 1.2–40, and nearest-neighbour matching finds 6 of
    592 and 7 of 729 pairs with H > 0 on both sides. Good balance says nothing outside that support.
  - **Changes number, adopted:** the reweighted count estimate swings from 0.0004 to 0.0145 with bin width and the
    H = 0 split. On the matched support the transformer is −0.0008 (se 0.0006) and −0.0003 (se 0.0002).
  - **No issue:** weighting choice and the zero threshold.

  Codex's wording, "a broad presence step is not robustly established; a step confined to classes outside the
  matched support (mainly H > 0) remains possible", agrees with §3.
- **Agreement between families.** The two reviewers used different methods (an exact overlap census vs
  reweighting by effective sample size) and reached the same correction to the owner's diagnosis. That was not
  arranged. They share the owner's prompt framing, so their independence is partial.
