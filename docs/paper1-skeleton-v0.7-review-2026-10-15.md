# Skeleton v0.7 review record (2026-10-15)

> Both families: **RESHAPE**, independently. Owning instance. Findings the owner relied on were reproduced.

## Converged (both reviewers)
- **The thesis "mechanism sparsity cuts both ways" is unearned.** Claude #1–#3, Codex #2. Exact tractability needs a
  small hidden state, not few mechanisms (HMM wind tunnels have continuous emission laws). The monitor edge holds
  only at exact rational precision: reproduced by the owner, mass with G span ≥ 0.1 bits rises from ≤ 0.04 % (exact)
  to 60–82 % at a 0.05 grid (`one-step-identifiability-check-2026-10-15.md`, Correction). Codex adds a real-kernel
  counterexample (deterministic ACQUIRE, deterministic IO_ISSUE, and a 50/50 ACQUIRE/IO_ISSUE state give equal
  predictives with R/G = 1/0 vs 0/1): identifiability depends on the reachable posterior family, not on counting
  laws. **Withdrawn.**
- **§4.1 mislabelled and overstated** (Claude #9, Codex #4): the temperature identity gives mean g ≈ 0 only under
  stationarity on the same distribution, positions and normalisation, which training does not guarantee. Becomes
  "objective-implied nulls", conditions stated, one paragraph with citations (Braverman et al. 2019).
- **§4.2 misnamed and over-generalised** (Claude #4–#5, Codex #5): G = 0 means the hidden state carries no extra
  information about the next KIND, not that the state is known; "~1 %" is a specific pure-random vs high-gap
  contrast, with its denominator (15–17 % of mass) to be stated.
- **§4.6 overstated** (Claude #7, Codex #6): "only as a training target" withdrawn. Supported: an unscored copy hurt
  on KIND; supervision without the copy helped a little; the copy's increment under supervision is unresolved;
  ACTOR resolves nothing.
- **§4.5 "effect" → "precision"** (Claude #8, Codex #7).
- **[PRE-RUN] as a tally reads as padding** (Claude #9, Codex #8); "two-family review" is provenance, not validation.
  Stopped designs enter only as self-contained analyses (a counterexample, a support census).
- **Checklist:** keep support tables (overlap with mass and mechanism composition), input-by-supervision factorials,
  objective-implied nulls, admissible-family identifiability with tolerance; drop items 4, 5, 7 as standard
  hygiene (Claude #11, Codex #9). Add: test whether competing exact explanations survive simple observable
  controls (Codex #9, from §4.4).
- **Better shape** (Claude #14, Codex #10): instrument first; exact results; an audit of which contrasts the
  instrument supports; the relay factorial as the substantive learner example; standard pitfalls compressed.
  Codex's thesis adopted: *an exact oracle makes experimental limitations measurable, but does not guarantee
  that the desired contrast exists.*

## Other
- Claude #6, Codex #3: Bergna et al. explicitly allow identification under structural assumptions; the lesson is to
  state the admissible family, not that a theorem "fails". Adopted. The original over-reading was the owner's.
- Claude #12: R's interface invariance is by construction; keep the label. The G numbers lead.
- Codex #1: the claim that the field "takes exactness to remove" these problems has no support; dropped.
- Claude #14: if a post-mortem framing were wanted, a negative-results workshop (ICBINB) fits; not adopted.
