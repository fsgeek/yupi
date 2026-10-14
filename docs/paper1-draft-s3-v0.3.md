# Paper 1, §3 draft v0.3 (2026-10-13): Exact observability is a profile, not a number

> **Status: DRAFT v0.3, owning instance.** It revises v0.2 after the whole-draft review (`paper1-whole-review-2026-10-13.md`:
> W3, W5, W17, W20, W23, W25, W26), and v0.2 revised v0.1 after the first review.
> Each finding's disposition is in `paper1-review-2026-10-13.md`, and the review numbers adopted here were
> reproduced by the owner where noted. Supersedes v0.1, which is kept for the record. Statuses are in square
> brackets.

## 3. Exact observability is a profile, not a number

For each interface and each class of observable windows, Yupana gives the exact predictive law of the next event.
Its entropy, averaged over the window law, is the interface's **ceiling**: the best expected log loss any observer
of that interface can achieve on the next event's KIND. The ceiling is a Bayes predictive loss, not a measure of
how well hidden state can be recovered. It includes randomness that no interface could remove: even a reset
window has a next-KIND entropy of 0.918 bits, the same in every state consistent with it, because the device completes with probability
1/3. [EXACT] What differs between interfaces is how much of the reducible part they leave. This section shows that
an interface decides a second thing as well: *where* in the window the knowable information sits.

### 3.0 Knowing the state is not the same as predicting the next event

The classical figure of merit for telemetry is identifiability: how much uncertainty about the hidden state the
record leaves. Log20 minimises a quantity of this kind, the entropy of the execution path given the log. A learned reader
faces a different quantity. Table 3.0 gives both, exactly, for the structural observer at the window's last record.
The table shows three quantities:
- the **state entropy** H(S | window);
- the next-record entropy, split into the part no interface could remove, H(next | S), and the observation gap
  (the decomposition fixed in the milestone specification);
- (on r1–r4 the irreducible part is the same, because the extra fields are determined given the state).

| ε = 1 | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| state entropy H(S \| window) | 3.947 | 0.601 | 0.528 | 0.405 | 0.390 |
| next-record entropy | 0.998 | 1.214 | 1.198 | 1.169 | 1.166 |
| … irreducible H(next \| S) | 0.557 | 1.063 | 1.063 | 1.063 | 1.063 |
| … observation gap | 0.442 | 0.150 | 0.135 | 0.106 | 0.103 |

*Bits. r0's record is KIND only, so its next-record target is smaller. At ε = ½ the pattern is the same: state
entropy 0.296 → 0.166, gap 0.092 → 0.056 across r1–r4.* [EXACT; `state-vs-predictive-40-8-2-2026-10-13.json`]

What the table shows:
- **Most of the state uncertainty is irrelevant to the next record.** On r1, an observer is uncertain about 0.60
  bits of state, but only 0.15 bits of it bears on the next record. The gap is the mutual information between the
  next record and the state, given the window, so it cannot exceed the state entropy. The size of the difference is
  the finding.
- **The two measures agree on ranking.** Each added field removes 3–5 times more state entropy than predictive gap
  (ε = 1: 4.7, 4.3 and 4.4 for OBJECT, RELATED and LINEAGE; ε = ½: 4.3, 3.1 and 4.0). Both rank RELATED first and
  LINEAGE last.
- So in this world an identifiability objective would pick the same fields as a predictor's ceiling, while
  overstating the remaining relevant uncertainty by a stable factor.

*Reconciliation.* Table 3.0 is for the structural observer, at the window's last record, over all windows
(short reset windows included). The rest of §3 is for the pattern observer at position 7, over the 0.85 of law mass
whose windows run at least seven records. On r0 the two observers coincide, but the numbers do not (0.998 here,
1.176 in §3.1). The difference is the position and the coverage, not the observer.

The rest of this section, and every learner comparison in §4, uses the predictive quantity for the pattern
observer.

### 3.1 The ceiling ladder

Each rung adds one field. r0 shows only KIND, r1 adds ACTOR, r2 OBJECT, r3 RELATED, and r4 LINEAGE. On the common
target, the next KIND, the ceiling falls as fields are added:

| ε | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| 1 | 1.176 | 0.999 | 0.955 | 0.911 | 0.911 |
| ½ | 1.104 | 0.873 | 0.823 | 0.784 | 0.784 |

*Bits; the law-mass-weighted entropy of the next KIND given the first seven records of the window (position
k = 7). Position-k quantities cover the windows that run at least seven records, which is 0.85 of window law
mass.* [EXACT]

- **The ladder is monotone on a common target.** Each rung refines the one below it, so it cannot raise the
  next-KIND entropy. The r3 → r4 step is the thinnest: 9 × 10⁻⁶ bits at ε = 1. On the whole-record target the
  rungs predict different fields and are not comparable this way. There, r4 − r3 lies in [5 × 10⁻⁶,
  3.9 × 10⁻⁴] bits at every position and both ε, because LINEAGE is nearly derivable from what r3 shows. [EXACT]
- **The observer matters.** From a reset, the structural observer's r1 prefix determines the state (tested
  exhaustively up to 8 records, §2.3). The pattern observer cannot do this, because it does not know *which* renamed
  thread is which. At ε = 1 the first dispatch is uniform over the four threads, so after one renamed DISPATCH the
  pattern observer gives four structural states equal weight (the structural r1 enumeration has four distinct
  prefixes at t = 1). All the ceilings below are for the
  pattern observer.

### 3.2 The lag profile

For a prefix class c, let ι_m(c) be the information about the next KIND that lies more than m records back:
KL(P\*(· | whole window) ‖ P\*(· | last m records)), in bits. The suffix is read through its own entity names, so
an entity seen only before the suffix is fresh to the order-m observer. ι_m is a function of the prefix alone. Its
law-mass mean is the interface's **lag profile**, and it equals H_m − H\*: the order-m entropy minus the ceiling.
This is the m-local entropy of Someya et al. (2025), less the full-window entropy, computed here exactly and class
by class for each interface of one fixed system.

| m | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| 1 | 0.535 | 0.712 | 0.756 | **0.800** | 0.800 |
| 2 | 0.384 | 0.525 | 0.569 | **0.578** | 0.578 |
| 3 | 0.257 | 0.379 | 0.420 | **0.424** | 0.424 |
| 4 | 0.176 | 0.257 | **0.282** | 0.259 | 0.259 |
| 5 | 0.107 | 0.168 | **0.184** | 0.172 | 0.172 |
| 6 | 0.061 | 0.080 | **0.086** | 0.078 | 0.078 |

*ε = 1, bits. Bold marks the largest value in each row (r3 and r4 are tied at this precision). The two computational routes for ι (KL and entropy
difference) agree to within 3 × 10⁻¹⁴ on every row, against a gate of 10⁻⁹. The cross-check against the
independent ceiling raw applies to r0 here, whose record is its KIND, and to every rung on the whole-record
target.* [EXACT]

**What holds by construction, and what was found.** Two properties are guaranteed:
- the ladder is monotone, since each rung refines the one below;
- a window-level rewrite leaves the ceiling unchanged (§3.3), by data processing.

What is found, in this world, is the crossing below: about 0.02 bits at lag 4. A second world variant is
paper 2's work.

**The profiles cross.** At lags 1–3, r3 (with r4, tied at the precision shown: r4 exceeds r3 by 2 × 10⁻⁶ to 9 × 10⁻⁶ at
every lag) leaves the most next-KIND information beyond m records. From m = 4, r2 carries
the most, and r3 falls to r1's level. RELATED makes local what r2 has to carry across four or more records. At
ε = ½, r3 drops below r1 from m = 4 (0.305 against 0.338).

So a richer field does two things: it adds information, and it relocates information that was already available.
The ceiling registers only the first. Interfaces can be ordered one way by the ceiling (r3 knows more than r2) and
the other way at a given lag (r2 leaves more beyond four records). At ε = 1, summed over lags 1–6, the order flips
back (r3 2.312, r2 2.297, from unrounded values). At ε = ½ it does not (r2 2.835, r3 2.763). So "farther" depends on
which lags one counts. This is why the paper reports profiles and not a
single distance number.

Every record is exactly five tokens on every rung, so a lag of m records is 5m tokens everywhere. The crossing is
not an artefact of record length. [EXACT, by construction]

### 3.3 Changing the presentation while holding the ceiling

The crossing compares interfaces that differ in their ceilings. A cleaner contrast holds the ceiling fixed. A
*window-level* rung may fill a slot its base rung masks, with any function of the window's records that precede
that slot in field order. Such a field adds nothing that an observer of the window lacked, so the ceiling is
unchanged class by class. Three gates verify this exactly: A, an equal KIND marginal per class; B, an equal multiset of
whole-record probabilities per class; C, an independent construction plus brute force on small worlds.
[EXACT] We built three such rungs on r1, each writing into the OBJECT slot:
- **relay (r1R):** the KIND of the most recent earlier record in the window with the same actor;
- **decoy (r1D):** the KIND of the previous record;
- **self-copy (r1S):** the record's own KIND. Given that KIND it carries nothing; marginally it varies, as the
  other two do.

These are transformations of a window a consumer already holds. The relay's lookup restarts at every window, so a
record's relay value depends on where the window begins. A producer could emit a similar back-reference field, but
that would be a different interface, and it was not built.

Write Δι_4 = ι_4(r1) − ι_4(rung). At ε = 1 the relay's mean Δι_4 is 0.094 bits and the decoy's 0.068. Across classes
the two correlate 0.29, and their signs agree on 65 % of law mass. The self-copy's profile equals r1's at every lag.
[EXACT]

Δι_4 is one point on a profile. Each of the relay and the decoy *raises* ι_4 on about a quarter of law mass (27.8 %
and 27.1 %). On the windows where the relay raises ι_4 by more than 0.05, its mean change at lags 1–2 still moves
information closer. That is a conditional mean, however. Pointwise, about half of that region's mass has a
negative summed change. [EXACT]

With the ceiling identical, any difference in learning between r1 and r1R happens despite identical available
information. What causes it is a separate question (§4e). One fact about the comparison matters here. In the original recipe
learners are trained on every position, so r1R models are also trained to *produce* the relay value. That
comparison changes the input and the training targets together, and §4e separates the two.

### 3.4 One cross-interface comparison, and its limits

At ε = 1, r3 lets an observer know more than r2 (ceiling 0.911 against 0.955) and leaves less beyond four records
(ι_4 0.259 against 0.282). At 15 epochs, learners' KIND shortfall is larger on r2 than on r3 (seed means 0.0156, 0.0172
and 0.0238 against 0.0122, 0.0140 and 0.0142), with every seed separated, as the pre-registration predicted from
ι_4. [CONFIRMATORY, B2 ε = 1; one r2 seed carries much of r2's spread]

The same data contain a counterexample, which the paper reports. At ε = 1, r1 and r3 have nearly equal ι_4 (0.257
and 0.259). Yet r1's shortfall (0.0146–0.0158) lies above r3's (0.0122–0.0142), with every seed separated. r1 at
ε = 1 was left out of the scored ordering because its models had been seen before the pre-registration. That
justifies excluding it from the test, but not from the description. [DESCRIPTIVE] At ε = ½ the pre-registered
ordering r2 > r1 > r3 fails, and no pair is seed-resolved. [CONFIRMATORY failure]

The other scored ordering also passed: r0, with the highest ceiling and the least far information, has the lowest
shortfall at both ε, with every seed separated [CONFIRMATORY, 15-epoch ladder C4]. r0 also has no entities to
carry and far fewer classes seen in the test split (3.5–3.7 k against 20–33 k; 5.5 k against 89–160 k classes in
all), so this ordering does not isolate far information either.

ι_4 therefore does not rank the content interfaces by learner shortfall, and the paper does not claim it does. Its learner
claims are within interfaces (§4).

A richer interface still helps in absolute terms. At 15 epochs, learners reach 1.015 bits per next KIND on r1 and 0.974
on r2 at ε = 1 (0.895 and 0.853 at ε = ½). The shortfall measures how much of the knowable the learner fails to
capture. It is not a judgment on whether richer telemetry is worth having.

---

## Provenance

- Ceilings and lag profiles: `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`, re-tabulated 2026-10-11. Identity
  tolerance: the largest |identity_diff| is 2.9 × 10⁻¹⁴ (Codex finding 14). The gate is 10⁻⁹
  (`scripts/implicit_info.py:64`).
- Reset class 0.918 bits: Codex finding 3 (r1 k = 7 table, first reset class, P(IO_COMPLETE) = 1/3).
- r3 → r4 on KIND: 0.910661 − 0.910652 from the same raw. Whole-record r4 − r3: `pattern-ceilings-40-8-2-k{1..7}`.
- Pattern-observer reset uncertainty: Codex finding 2; `src/yupi/pattern_filter.py:6`.
- Profile sums over m = 1..6: from the table (r2 2.297, r3 2.312, unrounded).
- Gates A–C: `three-arm-exact-side-r1S-2026-10-05.log` (derive A/B; brute force C). The slot rule: Claude finding 12.
- Δι_4, the correlation and the sign agreement: `decoy-iota-check-2026-10-05.json` (`mass_frac_sign_agree` 0.649).
  The sign fractions: `decoy-sign-fractions-2026-10-11.json`.
- 3.4 seed means: `converged-ladder-c3c4-2026-10-02.json`, re-read 2026-10-13. The r1 inversion: Claude finding 6,
  checked against the same raw.
- Table 3.0: `scripts/state_vs_predictive_table.py` → `state-vs-predictive-40-8-2-2026-10-13.json` (from the frozen-law
  query-ceiling and predictive-target raws of 2026-09-05/06; structural observer, window aggregation).
- Unrounded profile sums and the r4 − r3 gaps: recomputed 2026-10-13 from `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json`.
- r0 lowest (C4): `converged-ladder-verdict-v0.1.md`; class counts from `count-baseline-results-v0.1.md`.
