# C1 Predictive-State Targets — P-next, P-horizon, and the divergent-history search (v0.1)

> **⚠ KERNEL ERRATUM (2026-08-20):** every number in this note was computed
> under the pre-d69fa87 kernel, whose direct-handoff defect made self-deadlock
> states reachable (adjudication: `docs/audit-adjudication-2026-08-20.md`).
> Status: **buggy-kernel exploratory**. Corrected-kernel raws and drift:
> `docs/corrected-kernel-rerun-v0.1.md` (qualitative structure survives;
> magnitudes drift ≤0.004 at T_ep=12, ≤0.041 at (14,4,2)). Machine-readable
> status: `docs/artifact-status.json`. This banner is an append-only marker;
> the original text below is unchanged.



**v0.2.1 — 2026-08-15 (third pass).** Record repaired: v0.1 body restored
verbatim; supersession stated explicitly (below). Prevalence sentence in
the amendment proposal corrected (see `part2-amendment-proposal-v0.2.4.md`).

**v0.2 — 2026-08-15 (same night, truthsayer round on the forecast layer).**
Codex confirmed the three witness pairs, the conservation identities,
the two-path gate, and the suite — and refuted four claims and one
procedural claim in this note. Each recomputed independently before
adoption. **The v0.1 text below the rule is verbatim (restored from
commit 6074a36 on the third pass — the second pass had edited two lines
of it in place while claiming preservation); items 2 and 3 of this block
supersede its P2 scoring line and its finding 5 wherever they appear,
including the "siblings"/"manufactures" mechanism sentences, which are
withdrawn.**

1. **m = 2 and W = 4 were NOT frozen** — Part II §5 says 𝒯, m, and W are
   frozen with the §7 budgets; the D4 freeze (B1–B4) predates and omits
   them; a measured note cannot freeze them retroactively. Same for the
   rung-collapse δ and δ_sync (§6) — also absent from the D4 freeze — so
   every rung-gap comparison this week is exploratory relative to a δ
   that was to be frozen first. **Status of everything in this note and
   in `c1-q4-ceilings-v0.1.md`: exploratory parameter selection.**
   Repair: a prospective amendment is drafted as
   `docs/part2-amendment-proposal-v0.2.4.md` (m, W, the past-T_ep
   continuation, δ/δ_sync placeholders, and the divergent-class
   criterion form); it binds when Tony confirms and it is stamped, and
   only measurements after that stamp are confirmatory. On the
   truthsayer's suggestion to freeze δ-close/Δ-apart thresholds now: I
   decline to pick numbers without a sweep — freezing an arbitrary
   threshold is a worse error than leaving it exploratory one more day;
   the proposal names the criterion form and a sweep as the freeze's
   precondition.
2. **"Divergent mass rises with rung" is overstated.** r4 > r1 in all
   six windowed (law, ε) cells; adjacent monotonicity does NOT hold —
   (12,2,2) ε=1 r3→r4: 0.013812 → 0.013673; ε=½: 0.013126 → 0.013119.
   I printed the decrease and called it a rise. P2's scoring line is
   corrected to "reversed in the r1→r4 comparison; not monotone."
3. **The "siblings" mechanism is mostly wrong.** Tracing every divergent
   fine pair to its coarse parents at (12,2,2), ε=1 (my recomputation
   reproduces Codex's): r1→r2 **0/21** siblings, r2→r3 **7/90**, r3→r4
   **0/86**. Refinement creates newly qualifying pairs mainly because
   children of DIFFERENT coarse parents acquire coincident P-next
   mixtures while keeping different futures — not because one window
   splits into divergent siblings. Finding 5's causal sentence is
   replaced by this narrower one.
4. **Metric qualifications adopted.** The L=2 range is **0.065%–9.92%**
   of law mass, not "0.5–7%". `class_pairs` counts pairs of distinct
   joint τ-signature classes within a P-next class — NOT state pairs
   (caveat 2 was wrong). "Knife-edge under truncation" is too broad:
   rare at L=2, already 31–42% at truncated L=4. Divergent mass is valid
   for the EXISTENCE question and is one coverage measure only — a
   high-mass window counts fully even if its only partner is negligible.
   Two prevalence measures added to the script (v0.2, raw files
   `…-raw-2026-08-15-v0.2.json`, v0.1 files untouched): **pair_prob**,
   the probability that two independent law-weighted window draws form
   a divergent pair, and **tv_pair_prob**, the same weighted by the
   largest total-variation distance among the differing τ mixtures:

| law | ε | rung | div. mass | pair_prob | tv_pair_prob | class_pairs |
|---|---|---|---|---|---|---|
| (12,2,2) | 1 | r1 | 0.0053 | 4.28e-06 | 1.93e-06 | 15 |
| (12,2,2) | 1 | r2 | 0.0056 | 4.41e-06 | 1.95e-06 | 18 |
| (12,2,2) | 1 | r3 | 0.0138 | 1.13e-05 | 3.77e-06 | 53 |
| (12,2,2) | 1 | r4 | 0.0137 | 1.13e-05 | 3.77e-06 | 48 |
| (12,2,2) | 1/2 | r1 | 0.0007 | 5.00e-08 | 1.16e-08 | 7 |
| (12,2,2) | 1/2 | r2 | 0.0008 | 5.00e-08 | 1.16e-08 | 8 |
| (12,2,2) | 1/2 | r3 | 0.0131 | 2.23e-05 | 8.98e-06 | 27 |
| (12,2,2) | 1/2 | r4 | 0.0131 | 2.23e-05 | 8.98e-06 | 23 |
| (14,4,2) | 1 | r1 | 0.3114 | 1.16e-03 | 4.82e-04 | 6086 |
| (14,4,2) | 1 | r2 | 0.3756 | 1.38e-03 | 5.88e-04 | 7727 |
| (14,4,2) | 1 | r3 | 0.3952 | 1.70e-03 | 7.47e-04 | 8182 |
| (14,4,2) | 1 | r4 | 0.4068 | 2.04e-03 | 8.82e-04 | 8474 |
| (14,4,2) | 1/2 | r1 | 0.3347 | 8.36e-04 | 2.56e-04 | 5574 |
| (14,4,2) | 1/2 | r2 | 0.3758 | 1.00e-03 | 2.92e-04 | 7729 |
| (14,4,2) | 1/2 | r3 | 0.4025 | 9.83e-04 | 3.30e-04 | 9377 |
| (14,4,2) | 1/2 | r4 | 0.4222 | 1.06e-03 | 3.54e-04 | 9674 |
| (14,2,2) | 1 | r1 | 0.0552 | 1.67e-05 | 7.12e-06 | 10 |
| (14,2,2) | 1 | r2 | 0.0553 | 1.67e-05 | 7.12e-06 | 11 |
| (14,2,2) | 1 | r3 | 0.0647 | 2.45e-05 | 9.15e-06 | 59 |
| (14,2,2) | 1 | r4 | 0.0672 | 2.52e-05 | 9.25e-06 | 64 |
| (14,2,2) | 1/2 | r1 | 0.0052 | 1.24e-05 | 5.49e-06 | 5 |
| (14,2,2) | 1/2 | r2 | 0.0052 | 1.24e-05 | 5.49e-06 | 5 |
| (14,2,2) | 1/2 | r3 | 0.0160 | 3.05e-05 | 7.01e-06 | 39 |
| (14,2,2) | 1/2 | r4 | 0.0992 | 3.05e-05 | 7.01e-06 | 46 |

   Read: the class is real and rare — 10⁻⁸–10⁻⁵ pair probability at
   L=2, ~10⁻³ at L=4; the 9.92%-mass cell at (14,2,2) ε=½ r4 has
   pair_prob 3×10⁻⁵ (one high-mass window, negligible partners).
   Full-context (12,12,2), v0.2 rerun — pair_prob is the honest
   version of the "95–98% mass" figure:

| law | ε | rung | div. mass | pair_prob | tv_pair_prob | class_pairs |
|---|---|---|---|---|---|---|
| (12,12,2) | 1 | r1 | 0.9776 | 1.51e-02 | 7.18e-03 | 3255 |
| (12,12,2) | 1 | r2 | 0.9773 | 1.44e-02 | 7.02e-03 | 3228 |
| (12,12,2) | 1 | r3 | 0.9484 | 1.38e-02 | 6.83e-03 | 3205 |
| (12,12,2) | 1 | r4 | 0.9478 | 1.38e-02 | 6.83e-03 | 3192 |
| (12,12,2) | 1/2 | r1 | 0.9810 | 6.65e-03 | 3.18e-03 | 4872 |
| (12,12,2) | 1/2 | r2 | 0.9791 | 6.50e-03 | 3.16e-03 | 4821 |
| (12,12,2) | 1/2 | r3 | 0.9522 | 6.16e-03 | 3.06e-03 | 4727 |
| (12,12,2) | 1/2 | r4 | 0.9522 | 6.16e-03 | 3.06e-03 | 4714 |

5. Also from the round: continuation past T_ep is Codex's recommended
   reading too, but it is an unstated semantic decision — in the
   proposal (item 1).

---

**v0.1 — 2026-08-15 (day seven, night).** Drafted by the day-seven
instance. Status: **measured note; Part II §5 predictive-state targets
implemented and measured; divergent-history search run** (M1
deliverable 5's finite-side probe). Code: `src/yupi/predict.py` ⟂
`src/yupi/predict_paths.py`, gate `tests/test_predict.py` (every
endpoint state of every C1 path to horizon 8, both ε, W ≤ 4, m ≤ 3,
Fraction-exact). Script `scripts/c1_predictive_targets.py T_ep L B`.
Frozen here (implementation-time parameters, Part II §5/§7): m = 2 next
kinds; W = 4 for time-to-next-wake and next-IO_COMPLETE lineage.
Predictions written before the first run.

## Definitions

Per window w (belief b_w), per rung r:
- **P-next**: Σ_s b_w(s) · P(project(O_{t+1}, r) | s) — the observer's
  Bayes-optimal next-record distribution AT ITS RUNG.
- **P-horizon** functionals τ (state-side, rung-independent given s):
  next-2 EVENT_KINDs; time-to-next-wake ∈ {1..4} ∪ {NONE}; lineage of
  the next IO_COMPLETE within 4 ∪ {NONE} ("where exposed": reported at
  every rung as a state functional; only r4 observers can act on it).
- Each reported as (total, irreducible, gap) as for Q4.
- **Divergent pair**: two windows (same rung, same ε) with IDENTICAL
  P-next (exact Fraction equality) and DIFFERENT mixture on at least one
  τ. Reported: number of pairs, number of windows in ≥1 pair, law mass
  of those windows, and which τ separates.

## Predictions (pre-stated)

- **P1:** divergent pairs exist at (12,2,2) at every rung, both ε, with
  positive law mass — the immediate-agree/later-diverge class is
  non-empty in C1 under truncation.
- **P2:** the law mass of windows in ≥1 divergent pair is non-increasing
  in rung (a finer P-next partitions windows more finely).
- **P3:** at full context (12,12,2) — where every window is a state —
  divergent STATE pairs exist at r1 and are fewer at r4 than at r1.
- **P4 (conservation, check):** every τ's irreducible term is
  rung-invariant at every law.
- **P5:** next-2-kinds separates more divergent pairs than
  time-to-next-wake (it is the finer functional).

---

## Three divergent pairs, concretely — (12,2,2), r3, ε=1

Same exact P-next mixture at r3; different P-horizon:

1. A = `DISPATCH(2) ; BLOCK(1, L0, owner=0)` (mass 0.0041, support 8) vs
   B = `DISPATCH(1) ; BLOCK(2, L0, owner=0)` (mass 0.0009, support 3):
   time-to-wake A {NONE .801, 2: .071, 3: .001, 4: .127} vs
   B {NONE .784, 2: .077, 4: .139}.
2. A = `DISPATCH(1) ; BLOCK(2, L0, owner=0)` vs
   B = `DISPATCH(2) ; RELEASE(1, L0, no waiter)` (support 1): B can
   produce no wake within 4 (NONE = 1.0); A can.
3. **A = `IO_COMPLETE(3) ; ACQUIRE(2, L0)`** (mass 0.0011) vs
   **B = `IO_COMPLETE(3) ; RELEASE(2, L0)`** (mass 0.0003): thread 2's
   next record is the same COMPUTE step either way — identical next-
   record distribution — but "just acquired" and "just released" have
   different futures (time-to-wake A {NONE .79, 4: .21} vs
   B {NONE .91, 3: .06, 4: .04}).

An observer scored only on P-next cannot be told apart on these pairs
from one that carries the future; an observer scored on P-horizon can.
This is the finite-side content of "define the exposure gap relative to
a query class" (CLAUDE.md, gap 3).

## Results (raw: `c1-predictive-targets-<law>-raw-2026-08-15.json`)

Means in bits (law-mass weighted). P-next: total / irreducible / gap at the
observer's rung. τ gaps: observation-gap term of each P-horizon functional
(their irreducible terms are rung-invariant by construction — checked).
Divergent: window pairs with identical P-next mixture and unequal τ-mixture;
windows in ≥1 pair; their law mass; pairs separated by each τ.

| law | ε | rung | P-next tot/irr/gap | kinds2 gap | ttw4 gap | lin4 gap | P-next classes | div. pairs | div. windows | div. mass | by kinds2/ttw4/lin4 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| (12,12,2) | 1 | r1 | 1.1581/1.1581/0.0000 | 0.0000 | 0.0000 | 0.0000 | 126 | 194388028 | 82538/86086 | 0.9776 | 181493088/173553228/33265992 |
| (12,12,2) | 1 | r2 | 1.1581/1.1581/0.0000 | 0.0000 | 0.0000 | 0.0000 | 143 | 193749428 | 82376/86086 | 0.9773 | 181043060/172917400/33247284 |
| (12,12,2) | 1 | r3 | 1.1581/1.1581/0.0000 | 0.0000 | 0.0000 | 0.0000 | 186 | 193272576 | 79200/86086 | 0.9484 | 180829580/172442980/33036860 |
| (12,12,2) | 1 | r4 | 1.1581/1.1581/0.0000 | 0.0000 | 0.0000 | 0.0000 | 195 | 193256520 | 78642/86086 | 0.9478 | 180823508/172437148/33020804 |
| (12,12,2) | 1/2 | r1 | 0.9249/0.9249/0.0000 | 0.0000 | 0.0000 | 0.0000 | 238 | 106252276 | 82488/86086 | 0.9810 | 104161686/99886026/13665294 |
| (12,12,2) | 1/2 | r2 | 0.9249/0.9249/0.0000 | 0.0000 | 0.0000 | 0.0000 | 271 | 105843992 | 82316/86086 | 0.9791 | 103881616/99479128/13651600 |
| (12,12,2) | 1/2 | r3 | 0.9249/0.9249/0.0000 | 0.0000 | 0.0000 | 0.0000 | 342 | 105563032 | 79126/86086 | 0.9522 | 103753620/99199384/13527476 |
| (12,12,2) | 1/2 | r4 | 0.9249/0.9249/0.0000 | 0.0000 | 0.0000 | 0.0000 | 353 | 105547152 | 78576/86086 | 0.9522 | 103747548/99193552/13511596 |
| (12,2,2) | 1 | r1 | 1.9136/1.1581/0.7555 | 0.8225 | 0.2466 | 0.0754 | 146 | 18 | 23/186 | 0.0053 | 14/9/16 |
| (12,2,2) | 1 | r2 | 1.9236/1.1581/0.7656 | 0.7887 | 0.2398 | 0.0745 | 165 | 21 | 26/209 | 0.0056 | 17/12/18 |
| (12,2,2) | 1 | r3 | 1.9221/1.1581/0.7641 | 0.7489 | 0.2221 | 0.0744 | 206 | 90 | 56/283 | 0.0138 | 82/50/53 |
| (12,2,2) | 1 | r4 | 1.9236/1.1581/0.7655 | 0.7485 | 0.2220 | 0.0741 | 216 | 86 | 50/293 | 0.0137 | 82/50/49 |
| (12,2,2) | 1/2 | r1 | 1.6981/0.9249/0.7731 | 0.8347 | 0.2590 | 0.0845 | 157 | 7 | 14/186 | 0.0007 | 3/3/7 |
| (12,2,2) | 1/2 | r2 | 1.7021/0.9249/0.7772 | 0.8200 | 0.2527 | 0.0813 | 177 | 8 | 16/209 | 0.0008 | 4/4/7 |
| (12,2,2) | 1/2 | r3 | 1.7051/0.9249/0.7802 | 0.7947 | 0.2425 | 0.0811 | 225 | 39 | 41/283 | 0.0131 | 33/22/19 |
| (12,2,2) | 1/2 | r4 | 1.7053/0.9249/0.7804 | 0.7947 | 0.2425 | 0.0811 | 239 | 35 | 33/293 | 0.0131 | 33/22/15 |
| (14,4,2) | 1 | r1 | 1.3634/1.1003/0.2632 | 0.3883 | 0.1545 | 0.0285 | 965 | 67271 | 2000/3497 | 0.3114 | 63153/56444/41981 |
| (14,4,2) | 1 | r2 | 1.3483/1.1003/0.2480 | 0.3439 | 0.1396 | 0.0281 | 985 | 97202 | 2385/3922 | 0.3756 | 92429/83594/60206 |
| (14,4,2) | 1 | r3 | 1.3386/1.1003/0.2383 | 0.3108 | 0.1280 | 0.0276 | 1038 | 153482 | 2928/4577 | 0.3952 | 149268/128110/95117 |
| (14,4,2) | 1 | r4 | 1.3398/1.1003/0.2395 | 0.3101 | 0.1277 | 0.0273 | 1018 | 159485 | 3036/4698 | 0.4068 | 156123/134640/97816 |
| (14,4,2) | 1/2 | r1 | 1.0522/0.8693/0.1829 | 0.3219 | 0.1308 | 0.0200 | 1409 | 38831 | 1929/3497 | 0.3347 | 36316/33149/23802 |
| (14,4,2) | 1/2 | r2 | 1.0442/0.8693/0.1749 | 0.3005 | 0.1226 | 0.0197 | 1509 | 55292 | 2255/3922 | 0.3758 | 52499/48192/33137 |
| (14,4,2) | 1/2 | r3 | 1.0367/0.8693/0.1675 | 0.2794 | 0.1142 | 0.0194 | 1616 | 82651 | 2789/4577 | 0.4025 | 80192/71350/51413 |
| (14,4,2) | 1/2 | r4 | 1.0370/0.8693/0.1677 | 0.2794 | 0.1141 | 0.0194 | 1618 | 84933 | 2828/4698 | 0.4222 | 83190/74380/51378 |
| (14,2,2) | 1 | r1 | 1.8655/1.1003/0.7652 | 0.8550 | 0.3223 | 0.0851 | 178 | 24 | 25/223 | 0.0552 | 3/18/15 |
| (14,2,2) | 1 | r2 | 1.8734/1.1003/0.7731 | 0.8208 | 0.3089 | 0.0839 | 200 | 26 | 28/250 | 0.0553 | 5/20/17 |
| (14,2,2) | 1 | r3 | 1.8674/1.1003/0.7671 | 0.7747 | 0.2898 | 0.0825 | 262 | 120 | 71/359 | 0.0647 | 95/95/94 |
| (14,2,2) | 1 | r4 | 1.8698/1.1003/0.7695 | 0.7733 | 0.2893 | 0.0817 | 279 | 187 | 96/406 | 0.0672 | 134/157/122 |
| (14,2,2) | 1/2 | r1 | 1.6365/0.8693/0.7672 | 0.8594 | 0.3399 | 0.0835 | 191 | 13 | 14/223 | 0.0052 | 0/9/4 |
| (14,2,2) | 1/2 | r2 | 1.6400/0.8693/0.7707 | 0.8431 | 0.3268 | 0.0806 | 214 | 13 | 14/250 | 0.0052 | 0/9/4 |
| (14,2,2) | 1/2 | r3 | 1.6303/0.8693/0.7611 | 0.8095 | 0.3053 | 0.0797 | 285 | 61 | 51/359 | 0.0160 | 46/46/41 |
| (14,2,2) | 1/2 | r4 | 1.6308/0.8693/0.7616 | 0.8093 | 0.3053 | 0.0797 | 308 | 105 | 71/406 | 0.0992 | 82/88/49 |

Conservation check (all τ AND P-next irreducible rung-invariant at every law/ε): True

### Predictions scored

- **P1 held**: divergent pairs exist at (12,2,2) at every rung, both ε (18–90 pairs, 0.5–1.4% law mass), and at every other windowed law.
- **P2 REFUTED, in the opposite direction, at every windowed law**: divergent mass RISES with rung — (12,2,2) ε=1: 0.0053→0.0056→0.0138→0.0137; (12,2,2) ε=1/2: 0.0007→0.0008→0.0131→0.0131; (14,4,2) ε=1: 0.3114→0.3756→0.3952→0.4068; (14,4,2) ε=1/2: 0.3347→0.3758→0.4025→0.4222; (14,2,2) ε=1: 0.0552→0.0553→0.0647→0.0672; (14,2,2) ε=1/2: 0.0052→0.0052→0.0160→0.0992. Mechanism: a finer interface splits a coarse window into siblings that share the same next-record mixture but differ later — the history partition refines faster than the P-next partition. The finer the interface, the MORE immediate-agree/later-diverge histories it manufactures. (Also: many split siblings are near-point-mass, and exact P-next equality between resolved windows is easy — see finding 4.)
- **P3 held (marginally)**: at full context divergent STATE pairs exist at r1 (194,388,028 window pairs, mass 0.9776) and are fewer at r4 (193,256,520, mass 0.9478); P-next classes 126→195 over 720 states (ε=1). Held in direction; the magnitude says P-next is a very lossy summary of state — 95–98% of law mass has a next-record twin with a different future.
- **P4 held (conservation)**: True — every functional's irreducible term is float-identical across rungs at every law and ε; P-next's too (given the exact state, the r1 record determines the r4 record: injectivity at one step).
- **P5 held in 26 of 32 (law,ε,rung) cells — MIXED, not "almost everywhere"**: next-2-kinds separates ≥ as many pairs as time-to-wake at (12,2,2) and (14,4,2) throughout, but at **(14,2,2) time-to-wake separates MORE in six cells** (ε=1: r1 3 vs 18, r2 5 vs 20, r4 134 vs 157; ε=½: r1 0 vs 9, r2 0 vs 9, r4 82 vs 88), and at (12,2,2) r1/r2 the LINEAGE functional separates the most (16 vs 14 at ε=1; 7 vs 3 at ε=½). Which functional exposes divergence depends on the law. Neither exception was predicted.


## Findings (v0.1)

1. **The predictive-state targets exist and are two-path gated** (W ≤ 4,
   m ≤ 3, every horizon-8 endpoint state, both ε). P-next total 1.3–1.9
   bits under windows, of which 0.24–0.78 is observation gap; the
   P-horizon functionals' gaps: next-2-kinds 0.28–0.86, time-to-wake
   0.11–0.34, next-completion lineage 0.02–0.09.
2. **Conservation holds for every functional and for P-next itself.**
   P-next's irreducible term is rung-invariant: given the exact state,
   the r1 record determines the r4 record — the injectivity theorem at
   one step. Everything the ladder does to a predictive target is done
   to its gap term.
3. **The immediate-agree/later-diverge class is non-empty in C1 under
   truncation at every windowed law and rung** (M1 deliverable 5's
   existence question: yes), and concretely legible — "just acquired"
   vs "just released" with identical next-record mixtures (§ above).
4. **The exact-equality criterion is a knife-edge under truncation and
   near-universal at full context.** At (12,12,2), 95–98% of law mass
   is in a divergent pair because P-next has only 126–353 classes over
   720–1244 states; under L=2 windows exact P-next equality between
   *mixtures* is rare (0.5–7%); at L=4 it is common (31–42%) because
   many windows are resolved. The divergent mass therefore measures
   window resolution as much as future divergence. **Design input for
   the exposure experiments:** define the class with δ-close P-next and
   Δ-apart P-horizon, not exact equality; the exact version is the
   δ = 0 corner and this note is its baseline.
5. **Divergent mass RISES with interface fineness** (P2 reversed at
   every windowed law): finer rungs split windows into siblings that
   agree on the next record and disagree later. The finer the
   telemetry, the more such pairs it hands a model.
6. **Which functional exposes divergence is law-dependent** (P5 mixed):
   kinds at (12,2,2)/(14,4,2), time-to-wake at (14,2,2), lineage at the
   coarsest (12,2,2) rungs.

## Caveats

1. m = 2 and W = 4 are frozen HERE, not yet in Part II §7 with the
   budgets; the truthsayer should say whether that is acceptable or
   whether §7 needs an amendment first.
2. Divergent-pair counts at full context are window-pair counts
   inflated by history multiplicity (many histories per state); the
   state-level number is `class_pairs` in the raw JSON. Under
   truncation the two nearly coincide.
3. Two-path gate exhaustive at W ≤ 4 / m ≤ 3 over horizon-8 states, as
   for Q4; the past-T_ep continuation decision applies here too.
4. Exact Fraction mixtures compared for equality; entropies are float
   sums, as before.
5. Three of five predictions were wrong or mixed (P2 reversed, P3
   marginal, P5 mixed) and one summary sentence outran its table before
   commit — caught by re-reading the table, once more.

---

*2026-08-15 20:47 PDT (commit 5b58d7f) — status pointer, appended:* the amendment
`part2-amendment-proposal-v0.2.4.md` was confirmed by Tony and enacted as
Part II v0.2.4 (§A m/W/𝒯 frozen; §B continuation past T_ep; §D criterion
form; §C: thresholds unfrozen pending three sweeps and a second stamp).
Every number in this note precedes that stamp and remains **exploratory**;
nothing above is changed by the enactment.
