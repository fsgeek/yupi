# C1 Rung Separation Is Window Geometry — census, the (12,2,2) table, and the gap decomposition

**v0.2 — 2026-08-14 (same day, truthsayer round).** Codex's external audit
verified the census, the (12,2,2) table, the decomposition, and the
pricing — and refuted this note's headline: (12,6,2) was NOT an r3/r4
zero. The v0.2 section at the end REPLACES the "first measured r3/r4
separation" and "geometrically silent" claims wherever they appear below.
The mechanism findings, the census, the budget numbers, and the
multi-waiter geometric-impossibility claim survive unchanged.

**v0.1 — 2026-08-14 (day six).** Drafted by the day-six instance. Status:
**measured note advancing instrument-status open threads 1–2**; revises
finding 3 of `c1-support-measurement-v0.1.md` (v0.3) — the revision is of
a conjecture that note itself marked open, not an erratum to its numbers,
which are untouched (and were reproduced here as a regression, below).
Scripts: `scripts/c1_multiwaiter_census.py`,
`scripts/c1_support_at_law.py`, `scripts/c1_rung_gap_decomposition.py`,
`scripts/c1_support_12_2_2_crosscheck.py`. Raw JSON:
`docs/c1-multiwaiter-census-raw-2026-08-14.json`,
`docs/c1-support-12-2-2-raw-2026-08-14.json`,
`docs/c1-rung-gaps-12-2-2-raw-2026-08-14.json`.

**The question.** At WindowLaw(12,6,2), r3/r4 did not separate in exact
mean state support, and v0.3's finding 3 conjectured the missing
distinguishers (RELEASE.related under multi-waiter wake for r2/r3;
lineage for r3/r4) "plausibly require laws whose windows straddle
multi-waiter episodes." Before buying a support table at a larger law,
this note measures the habitat itself: where the conjectured events live,
whether any law window can straddle them, and — at a law where straddling
exists — which mechanisms actually carry each adjacent-rung gap.

## 1. The multi-waiter census (exact, exhaustive, with control)

Exhaustive annotated unroll of C1 over `kernel.enabled` (world definition
only), horizon 12, both ε. Control per the witness discipline: the
identical census on C0a reports zero events of either kind, as it provably
must (two threads cannot form a two-deep lock queue; a depth-1 device
queue cannot hold two requests).

- **Multi-waiter RELEASE (≥2 waiters at release).** Mass of episodes
  containing one: **11521/1259712 ≈ 0.91%** at ε=1;
  **634309/429981696 ≈ 0.15%** at ε=1/2. Every reachable event has
  waiters {0, 1} (thread 2's staggered arrival puts it elsewhere at these
  horizons — the design docstring's "threads 1 and 2" pair is not the one
  realized by t≤12), release at t ∈ {11, 12}, queue-forming BLOCKs at
  t ∈ {7, 9, 11}. **Both wait-queue orders are reachable — with exactly
  equal mass (11521/2519424 each) at ε=1; asymmetric (≈0.096% vs
  ≈0.051%) at ε=1/2.** The design claim of `c1_programs` is now a
  measured fact, with the ε=1/2 asymmetry as a bonus: structure in the
  dynamics prices the two orders differently.
- **Deep completions (≥2 requests in flight).** Mass ≈ 0.051% (ε=1),
  ≈ 0.002% (ε=1/2); only at t=12, issues at t ∈ {3,...,11}.
- **Straddle geometry.** Fully hiding a queue-forming BLOCK pair (both
  orders latent) requires offset U ≥ 9 with the release in-window. On
  T_ep=12's grid: **L=6 and L=4 admit no such window — zero straddles;
  the day-five law could not have witnessed the multi-waiter
  distinguisher at any mass.** Only L=2 straddles (the T=12 window over
  t ∈ {11,12}, blocks at 7,9 hidden). The r3/r4 non-separation at
  (12,6,2) was geometric impossibility, not a null result about C1.
- **Pricing the other door.** Path-tree leaves at horizons 12–16:
  69,162 / 149,744 / 307,362 / 621,482 / 1,293,762 (≈2.08×/tick).
  T_ep=16 exceeds B4's 10⁶-paths validation budget; **T_ep=14 with L=4
  straddles (U=10 ≥ 9 at T=14) at 307k paths, inside B4** — the priced
  next door if the multi-waiter witness is wanted at richer windows.

## 2. The exact support table at WindowLaw(12,2,2)

Same method as the cross-verified v0.3 table, law parameterized
(`c1_support_at_law.py`). Verification chain: (a) regression — at
(12,6,2) the script reproduces the v0.3 table in all 16 cells; (b)
two-path — every distinct (12,2,2) window recomputed through
`window_filter` (the recursive-mixture side of the firewall): all 971
windows match in support, both means match exactly, zero mismatches
(`c1_support_12_2_2_crosscheck.py`).

| ε | rung | windows | E[support] | max support |
|---|---|---|---|---|
| 1 | r1 | 186 | 27.5244 | 108 |
| 1 | r2 | 209 | 25.2335 | 108 |
| 1 | r3 | 283 | 23.9420 | 108 |
| 1 | r4 | 293 | 23.6254 | **104** |
| 1/2 | r1 | 186 | 25.4554 | 108 |
| 1/2 | r2 | 209 | 24.1147 | 108 |
| 1/2 | r3 | 283 | 22.9902 | 108 |
| 1/2 | r4 | 293 | 22.6695 | **104** |

**All four rungs separate — the first measured r3/r4 separation in the
project** (gap 0.3166 at ε=1, 0.3207 at ε=1/2), and lineage moves the
worst case too (max 108 → 104). The ε=1/2 direction of v0.3 persists at
every rung (lower levels); the r3/r4 *gap* is slightly larger at ε=1/2 —
recorded as an observation, no mechanism claimed.

D4 check at this law: worst per-component first-step expansion 462 (ε=1)
/ 809 (ε=1/2) transitions; summing a full resetless mixture bounds a
filter step at ≤948 / ≤1648 against B1's 70,000 (≈42× headroom); max
support 108 against 20,000. No budget pressure.

## 3. The decomposition — what actually carries each gap

A gap between adjacent rungs can come only from coarse-rung windows that
**split** at the finer rung (an unsplit window matches an identical path
set, hence an identical posterior). `c1_rung_gap_decomposition.py` finds
every split and asserts the contributions sum to the table gap exactly
(they do, all three pairs, both ε).

- **r1→r2 (gap 2.291 at ε=1, 23 splits):** dominated by `obj` on
  ACQUIRE — *which lock* is taken.
- **r2→r3 (gap 1.292, 56 splits):** windows containing a RELEASE carry
  **11.6%** of the gap at ε=1 (**5.1%** at ε=1/2). The rest —
  **88.4% / 94.9% — is `related` on BLOCK revealing the hidden owner of
  the contended lock** under ordinary single-waiter contention.
- **r3→r4 (gap 0.317, 10 splits):** every split differs **only in
  lineage fields**, every in-window IO_COMPLETE carries its in-window
  IO_ISSUE's id (both checked mechanically), so the discriminating
  information is exactly **the issue's request id**. Request ids are
  assigned lowest-free, so a visible id reveals the allocator's state —
  whether another request was already in flight before the window. The
  dominant split: a mass-0.047 (IO_ISSUE, IO_COMPLETE) window whose
  r3-support 108 resolves into a common id-0 child (support 104) and a
  rare id-1 child (support 4). **The completion-matching mechanism
  contributes exactly zero at this law.**

## Findings

1. **Adjacent-rung separation is a property of window geometry, not of
   rung content alone.** The same world, same rungs: at L=6 the r3/r4
   channels are geometrically silent; at L=2 all three gaps open. The
   enabling condition is antecedent-hiding — the window must contain a
   consequence whose cause lies before it.
2. **v0.3's finding-3 conjecture is revised.** The geometric intuition
   (straddle the antecedent) was right; the event class was wrong. The
   r2/r3 and r3/r4 gaps are carried by *ordinary* events — lock
   ownership on BLOCK, allocator state on IO_ISSUE — not by the rare
   multi-waiter/deep-completion episodes (≤11.6% and 0% of their gaps
   respectively). The multi-waiter wake-order witness and the
   completion-matching witness both remain **unwitnessed as support
   separators**; (14,4,2) is the priced door for the former.
3. **The lineage rung currently measures allocator leakage, not causal
   matching.** Lowest-free id assignment makes the identifier itself an
   information channel about hidden state — the same phenomenon the
   founding identifier-pool constraint (CLAUDE.md, "design constraints
   with teeth" (a)) exists to prevent in entity naming, appearing one
   level down in the record schema. If M1 wants r4 to isolate
   *request-matching* information, id assignment may need the same
   treatment as thread naming (per-episode draw from a large pool);
   flagged as a design question for the M1 characterization, not decided
   here.

## Caveats

1. Mean state support remains a coarse metric; none of this establishes
   the named-query or predictive-target witnesses M1's exit criteria
   require. Geometry that opens state-support gaps is a necessary
   precondition, measured here; sufficiency for the declared targets is
   open.
2. The L=2 observer is very poor in absolute terms (E[support] ≈ 23–28
   against full-context support 1). The M1-interesting regime is
   presumably richer windows over longer episodes — where, per §1's
   pricing, T_ep=14/L=4 is the next affordable straddling point.
3. One world (C1 as configured), one short horizon, ε ∈ {1, 1/2}; the
   terminating-dynamics caveat of the window-prior note applies
   unchanged (T=12 windows include absorbing-IDLE tails).
4. The census's straddle test is a necessary geometric condition, not
   sufficiency: pre-window evidence can still leak through visible
   in-window correlates; sufficiency claims here rest only on the exact
   posterior computations of §2–§3.

## v0.2 — headline erratum (same day; external finding, Codex truthsayer)

**The error.** v0.1 claimed that at (12,6,2) r3/r4 "did not separate in
exact mean state support," called the (12,2,2) result "the first measured
r3/r4 separation in the project," and wrote (finding 1) that "at L=6 the
r3/r4 channels are geometrically silent." All three are false. The v0.3
exact table already showed a nonzero r3/r4 gap (1.425970 vs 1.425243 at
ε=1 — its own text said "nearly identical," not zero), and this note's
own §2 regression reproduced those very numbers without subtracting them.

**The correction — verified by two paths.** Reapplying this note's own
decomposition to the old law (`c1_rung_gap_decomposition.py 12 6 2`)
reproduces Codex's independent computation exactly: six splits,

- ε=1: exact gap **5491/7558272 ≈ 7.3×10⁻⁴**
- ε=1/2: exact gap **1334375/61917364224 ≈ 2.2×10⁻⁵**

with every split differing only in lineage fields and every in-window
completion matching its in-window issue — **the same allocator channel,
already present at L=6.** The corrected claims:

- (12,2,2) is not the first r3/r4 separation; it **amplifies the
  pre-existing allocator-lineage channel ~436×** (0.316567 / 0.000726 at
  ε=1) and moves the worst-case support (108 → 104), which (12,6,2) did
  not.
- Finding 1's corrected form: **window geometry controls the magnitude
  and mechanism of adjacent-rung separation, not its mere existence.**
- What survives unchanged: the multi-waiter hidden-antecedent witness
  specifically was geometrically impossible at L ∈ {4, 6} on T_ep=12
  (zero straddling windows — that claim was about the multi-waiter
  mechanism and remains true); the census; the r2→r3 attribution; the
  budget and pricing numbers.

**The killer, named.** Reading v0.3's "remain nearly identical" as "do
not separate" — a stipulated-prior error held against evidence sitting in
this note's own regression output. Kutichiq's rule extends: re-reading
the governing document is not enough if you do not re-do its arithmetic.

**Three refinements from the same audit.**

1. The committed cross-check compared only support cardinalities — a
   weaker assertion than §2's prose implied (a wrong state with the right
   count would have passed). The script is now v2: full joint-posterior
   equality over (U, S_T), every window, exact Fractions — zero
   mismatches over all 971 windows × both ε, independently convergent
   with the truthsayer's own full-posterior check (1,942 comparisons).
2. "100% lineage-on-IO_ISSUE" is a causal statement, not a field census:
   ~60.6% (ε=1) / 62.2% (ε=1/2) of the r3→r4 gap sits in windows where
   issue and completion lineage co-vary. Every split contains an
   issue-id difference and the completion contributes no independent
   matching information; the mechanical checks in the decomposition
   script state exactly this.
3. Provenance debt paid: the §2 transition-expansion numbers
   (462/809 per component, 948/1648 per resetless mixture) now have a
   committed producer (`scripts/c1_budget_check_12_2_2.py`) and raw
   artifact (`docs/c1-budget-12-2-2-raw-2026-08-14.json`).

## v0.2.1 — budget-justification correction (same day; external finding, Codex truthsayer)

v0.2's budget script justified its first-step-only measurement with
"evidence only prunes, so the worst step is bounded by the first step
from the derived priors." **That argument is invalid in general**: a
kernel transition can re-expand a pruned support before the next
observation, so first-step expansion is not an a priori bound for longer
windows. The script is now v2: it measures **every step of every
distinct window at every rung** exhaustively. At this law the v0.2
numbers happen to be the true maxima — worst step 948 (ε=1) / 1648
(ε=1/2), occurring on the first step of a resetless r1 window; the
second step's maximum is 286 — as Codex's independent all-step
measurement also found. The D4 conclusion is unchanged; the *reasoning*
is repaired. Do not reuse the "evidence only prunes" bound at longer
laws: measure all steps.

## v0.3 — the (14,4,2) run: the habitat blooms, the RELEASE channel becomes material, the completion negative hardens (same day)

The priced door from §1 was opened: census at horizon 14, exact support
table and decomposition at WindowLaw(14,4,2), field-level attribution
added to the decomposition (script v2), all posterior-bearing numbers
two-path verified (full-joint crosscheck over all 16,694 distinct
windows, both ε: zero mismatches; `c1_support_crosscheck.py`,
parameterized successor of the (12,2,2) script). Raw:
`c1-multiwaiter-census-h14-raw-2026-08-14.json`,
`c1-support-14-4-2-raw-2026-08-14.json`,
`c1-rung-gaps-14-4-2-raw-2026-08-14.json`.

**Census at horizon 14.** The multi-waiter habitat grows ~7×: 6.24% of
episode mass at ε=1 (8.01% at ε=1/2), with events now at t=11–14. The
*designed* contender pair — threads 1 and 2 — appears for the first time
(t=13–14) and dominates the new mass, resolving §1's observation that
only {0,1} was reachable by t≤12: the design docstring's pair simply
lives later than horizon 12. Notably its two orders are asymmetric even
at ε=1 ((1,2): 0.0317 vs (2,1): 0.0139) while (0,1)/(1,0) remain exactly
equal — thread 2's staggered arrival prices the orders differently with
no help from ε. Several t=13–14 events are straddled by (14,4,2)'s T=14
window, confirming §1's grid arithmetic by direct measurement.

**Exact table at (14,4,2)** (all cells two-path verified):

| ε | rung | windows | E[support] | max support |
|---|---|---|---|---|
| 1 | r1 | 3497 | 6.8131 | 96 |
| 1 | r2 | 3922 | 6.0670 | 96 |
| 1 | r3 | 4577 | 5.4417 | 96 |
| 1 | r4 | 4698 | 5.3304 | **92** |
| 1/2 | r1 | 3497 | 5.0296 | 96 |
| 1/2 | r2 | 3922 | 4.5472 | 96 |
| 1/2 | r3 | 4577 | 4.0914 | 96 |
| 1/2 | r4 | 4698 | 4.0271 | **92** |

All four rungs separate; r3/r4 gap 0.111312 (ε=1) / 0.064265 (ε=1/2);
lineage again moves the worst case (96 → 92). ε=1/2 lowers every level,
consistent for the third law running.

**Field-level attribution of the r2/r3 gap** (v2 of the decomposition:
buckets splits by which record kind's `related` field actually differs
between children, replacing the coarser contains-a-RELEASE test; at
(12,2,2) the two coincide exactly):

| law | ε | BLOCK.related (owner) | RELEASE.related (woken) | both |
|---|---|---|---|---|
| (12,2,2) | 1 | 88.4% | 11.6% | — |
| (14,4,2) | 1 | 69.6% | **29.6%** | 0.8% |
| (12,2,2) | 1/2 | 94.9% | 5.1% | — |
| (14,4,2) | 1/2 | 79.9% | **19.9%** | 0.2% |

**The RELEASE.related channel becomes material — from 11.6% to 29.6% of
the gap — exactly when the window geometry begins straddling the wake
events.** The hidden-owner channel still dominates. Scope note, stated
before anyone asks: RELEASE.related ambiguity mixes *who was waiting*
(single-waiter releases with hidden BLOCKs) with *wake order* (the
multi-waiter distinguisher proper); isolating pure order ambiguity needs
a dedicated pass conditioning on the matched paths' waiter sets, which
is deliberately deferred — this measurement bounds the wake-order
channel above (≤29.6% + 0.8% at ε=1), it does not witness it in
isolation.

**The completion-matching negative hardens.** At L=4 a window *can*
contain an IO_COMPLETE without its IO_ISSUE, so the matching channel had
its first genuine geometric opportunity — and contributed exactly zero
again: 121 splits, every one differing only in lineage fields, every
in-window completion carrying its in-window issue's id, no
completion-only split windows (checked mechanically, both ε). Two laws,
two geometries, same exact zero. The structural explanation is the
allocator itself: a lone pre-window request always holds id 0 under
lowest-free assignment, so its completion cannot split anything;
matching ambiguity requires the deep-completion habitat (≥2 in flight),
whose mass (0.05–0.25%) never survives into a split at these laws. This
sharpens the §Findings-3 design question: under lowest-free ids, the r4
rung's information is allocator state at every law measured, and the
completion-matching concept lineage was meant to probe has yet to
contribute a single split.

**Budget.** All (14,4,2) computation inside the frozen envelope: 307,362
paths at the deepest endpoint (< B4's 10⁶), max support 96 (« B1), and
the all-step expansion discipline of v0.2.1 applies unchanged.
