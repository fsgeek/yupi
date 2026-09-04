# Part II amendment proposal — v0.2.7 (a kind-only rung r0 below the ladder)

> **REVISED (2026-09-04): superseded by `part2-amendment-proposal-v0.2.7.1.md`
> after the Codex review `part2-v0.2.7-v0.2.8-codex-review-2026-09-04.md`
> (verdict AMEND BEFORE ENACTMENT). Retained verbatim. Known errors in this
> version: "no frozen decision changes" (D2, D4, the exit clause and three
> note-level theorems are touched in meaning); "D4 is not touched" (r0 was
> never priced under an admitting rule; the census process reached 4.4 GB);
> statement 3's "the same object" (random-naming r1 and r0 are analogous
> mixtures, not equal); the ladder-collapse sentence lacks its from-reset
> qualifier; §6's synchronization formula is wrong for a non-injective rung.

> **Status (2026-09-03): PROPOSED — awaiting cross-family review, then PI
> enactment.** Written by the instance that ran the r0 census
> (`r0-ladder-census-v0.1.md`) on the day it was run. One clause. No
> transition rule, threshold, frozen decision, or committed number changes;
> every existing rung keeps its name and definition. What changes is what
> the interface variable ranges over.

## Clause 1 — r0 (EVENT_KIND only) joins the content ladder

§4's projection table gains a rung below r1:

| rung | visible | masked |
|---|---|---|
| **r0 (kind-only)** | EVENT_KIND | ACTOR, OBJECT, RELATED, LINEAGE |
| r1 (actor-only) | EVENT_KIND, ACTOR | OBJECT, RELATED, LINEAGE |
| r2 … r4 | as now | as now |

Refinement is preserved (r1 determines r0), so every monotonicity
assertion in the producers holds with r0 prepended. `interfaces.project`
already implements it (committed with the census, marked exploratory).

**Statements that enter §4 with the rung, verbatim from the census:**

1. r0 is **not injective at full context**. The full-context injectivity
   theorem (`full-context-injectivity-note-v0.1.md`) rests on ACTOR and
   applies to r1–r4 only. At (14, 14, 2) the r0 posterior from reset has
   mean entropy 2.577 bits (ε = 1) / 2.375 (ε = ½). Part I's "truncation
   is the only door" is a statement about r1 and above.
2. r0's residual is **thread identity**: at kind-only the observer cannot
   bind actions to structural threads, and threads whose programs are
   kind-permutations of one another stay confounded for the whole episode.
   Every thread-naming query (Q1, Q2, Q5) inherits this; Q3 (ids) and Q4
   partly do not.
3. Consequently r0 is the rung at which the **canonical-naming track's
   caveat (v0.2.6 Clause 2′) bites hardest**: an r0 ceiling on a
   thread-naming query is the observer's own mixture over role bindings,
   the same object the random-naming corpus process produces at r1 without
   a bridge. r0 numbers are structural-characterization quantities under
   σ₀ like every other committed number, and the bridge requirement
   applies to them unchanged. The proposal does not claim r0 resolves or
   replaces the bridge; it makes the bridge part of the interface variable.

**Why (the D2 argument, made against the measurements):**

- D2 requires each adjacent pair to change a fact posterior or a
  preregistered predictive distribution. r0 → r1 changes both by more than
  the whole r1 → r4 ladder at every measured context: 0.49–0.60 bits on
  next-2 kinds at L ≥ 4 against 0.08 at the ladder's widest, and it does
  not decay with L (the ladder is gone by L = 12; r0 → r1 is 0.49 at
  L = 14).
- M1's exit condition asks for measurably distinct regimes across rungs.
  With r0 the interface axis has one at every context; without it the
  axis has none past ten visible records in C1
  (`c1-residual-ambiguity-census-v0.1.md` §7).
- The founding design constraint (b) — the sparsest interface is the most
  computationally hostile — is what this rung tests, and it fails to bite
  here: r0 supports are at most 282 states and shrink with L; the two-path
  filter sample passed at every L in under four seconds. The D4 budget is
  not touched by adding r0 at C1 scale. (It may be at M1 scale; that is
  priced when M1 scale is.)

**What the rung does not do:** it does not restore range to r1–r4. The
object / owner / lineage information the ladder was designed to measure
still collapses by eight to ten visible records in C1; the Part C
intervention question is unchanged by this clause and remains the PI's.

## Considered and declined

- **Adding r0 as an "exploratory interface" outside the statute.** Declined
  because the paper's variable is the ladder; a rung the paper's central
  figure uses must be in the statute or the figure is unregistered.
- **Masking ACTOR only on some kinds** (e.g. DISPATCH), to break the
  fieldless-prefix identity without giving up thread identity everywhere.
  Declined for now: it is a designed interface rather than a monotone
  ladder step, and the ladder's monotonicity is what the producers assert.
  Recorded as a possible r0′ if the identity residual proves to be a
  confound rather than an instrument.
- **Waiting for the naming bridge before adding r0.** Declined: the census
  is the strongest evidence yet that the bridge matters to the interface
  variable itself, and the rung's numbers carry the same caveat every
  committed number already carries.

## Review request

Cross-family review before enactment, as for every version bump. The
specific questions: (i) whether statement 2's identification of the r0
residual with thread identity is adequately evidenced by the support
sizes (modal 6, then 12 and 18) and the split-by-r1 census, or needs an
explicit permutation-orbit computation before entering §4; (ii) whether
r0 should be excluded from the D1 falsifier's rung-collapse criterion
(it never collapses, by construction) or included with that noted; (iii)
whether the Part I exit clause "three rungs distinct" should count r0.
