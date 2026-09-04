# Part II amendment proposal — v0.2.7.1 (a kind-only rung r0 below the ladder; revised after cross-family review)

> **Status (2026-09-04): PROPOSED — revised from v0.2.7 after the Codex
> review of 2026-09-04 (`part2-v0.2.7-v0.2.8-codex-review-2026-09-04.md`,
> verdict AMEND BEFORE ENACTMENT), and again the same day after the
> second round (`part2-v0.2.7.1-v0.2.8.1-codex-review-2-2026-09-04.md`:
> 15 of 21 first-round findings adopted correctly, 6 adopted incorrectly,
> 0 declined; the six and the new findings are folded in below, each marked
> [r2-N]); awaiting a third read, then PI enactment.** Written by the
> instance of 2026-09-04. v0.2.7 is retained
> unchanged with a pointer to this file. Every finding the review made
> against v0.2.7 is either adopted below or answered by an executable check
> named below; none was declined. No transition rule, threshold, or
> committed number changes. What changes relative to v0.2.7: the proposal
> now says which frozen *meanings* it touches (D2, D4, the exit clause,
> three note-level theorems, one §6 formula) instead of claiming to touch
> none.

## Clause 1 — r0 (EVENT_KIND only) joins the content ladder *(as v0.2.7)*

§4's projection table gains a rung below r1:

| rung | visible | masked |
|---|---|---|
| **r0 (kind-only)** | EVENT_KIND | ACTOR, OBJECT, RELATED, LINEAGE |
| r1 (actor-only) | EVENT_KIND, ACTOR | OBJECT, RELATED, LINEAGE |
| r2 … r4 | as now | as now |

Refinement is preserved (r1 determines r0). `interfaces.project` already
implements it (committed with the census, marked exploratory).

**Statements that enter §4 with the rung** (revised wording; the review's
finding number in brackets):

1. r0 is **not injective at full context**. The full-context injectivity
   theorem (`full-context-injectivity-note-v0.1.md`) rests on ACTOR and
   applies to r1–r4 only. At (14, 14, 2) the r0 posterior from reset has
   mean entropy 2.577 bits (ε = 1) / 2.375 (ε = ½) (raw
   `r0-ladder-census-14-14-2-2026-09-03.json`; 5,696 r0 classes against
   394,824 for each of r1–r4). Part I's "truncation is the only door" is a
   statement about r1 and above.
2. *(measured per [4], 2026-09-04; wording per [r2-4], [r2-29], [r2-30])*
   The r0 residual is **not a relabeling orbit**. A kernel permutation-orbit
   computation is trivial for C1 (no two threads run the same program), so
   the check run is a **coarse thread-signature quotient**: each support
   state is anonymized — threads replaced by (executed-kind *multiset*,
   status, held locks); queue members and the live cursor by those
   signatures — and a support is classed *identity-only* if all its states
   share one anonymized form. The metric is the share of **ambiguous law
   mass carried by identity-only supports**. It is a support
   classification, not a decomposition of the residual entropy: a
   non-identity-only support can still hold identity entropy, and the
   multiset discards per-thread order and (at ε = ½) the cursor's circular
   order, so the identity-only share is an operational figure under this
   quotient, not an exact identity fraction. Raw
   `r0-identity-residual-14-2-2026-09-04.json`, pinned in
   `tests/test_r0_identity_residual.py` (ε = 1, L = 8 row reproduced
   independently by the reviewer):

   | ε | L | ambiguous mass | identity-only share | largest non-identity class |
   |---|---|---|---|---|
   | 1 | 4 | 0.9996 | 0.179 | dev_q+lock_wq+threads 0.426 |
   | 1 | 8 | 0.9889 | 0.205 | threads 0.425 |
   | 1 | 12 = full | 0.9746 | 0.216 | threads 0.516 |
   | ½ | 4 | 0.9996 | 0.000 | cursor+dev_q+lock_wq+threads 0.460 |
   | ½ | 8 | 0.9864 | 0.002 | cursor+threads 0.435 |
   | ½ | 12 = full | 0.9708 | 0.005 | cursor+threads 0.553 |

   What follows: the census's clean mechanism — "the residual is a
   permutation entropy over kind-indistinguishable roles" — is
   **withdrawn**, because about four fifths of the ambiguous mass at ε = 1
   (and nearly all at ε = ½) sits in supports whose states differ even
   under this coarse quotient, typically in the anonymized `threads`
   multiset: which thread has executed which kinds. The observer saw an
   ACQUIRE and cannot say whether thread 0 or thread 1 issued it, and those
   threads do different things next; that is attribution of visible
   actions to role-asymmetric threads, and it carries object / owner /
   lineage consequences. What does **not** follow is that only a fifth of
   the residual *entropy* is identity-related; that decomposition has not
   been computed. The r0 census §3's separation "r0 measures identity, the
   ladder measures object / owner / lineage" is withdrawn as a clean split.
   Thread-naming queries (Q1, Q2, Q5) inherit the residual either way.
3. *(rewritten as analogy per [5])* r0 is the rung at which the
   canonical-naming caveat (v0.2.6 Clause 2′) bites hardest. An r0 ceiling
   on a thread-naming query is the observer's mixture over role bindings.
   The random-naming corpus process at r1 also produces a mixture over role
   bindings, **but not the same one**: random-σ r1 still exposes a
   persistent pseudonym and its equality pattern across the window, which
   updates the binding; r0 exposes no actor at all. The two objects are
   analogous, not equal, and the bridge requirement (joint inference over σ
   and state, or a per-metric equivariance proof) applies to r0 numbers
   unchanged.

**Why (the D2 argument, made against the measurements; all figures
exploratory per [3]):** r0 → r1 changes both a fact posterior and a
preregistered predictive distribution by more than the whole r1 → r4 ladder
at every measured context from reset: 0.49–0.60 bits on next-2 kinds at
L ≥ 4 against 0.08 at the ladder's widest, not decaying with L (0.49 at
L = 14). *(qualified per [8])* The r1–r4 ladder's collapse by eight to ten
visible records is a **from-reset** statement about the (14, L, 2) family;
at (32, 8, 2) mid-episode every adjacent r1–r4 pair is above δ
(`deep-truncation-census-v0.1.md`), so r0's case does not rest on the
ladder being dead — it rests on r0 → r1 being the largest step on the axis
wherever both have been measured (3.3 bits on the r0 → r1 step in the
live world, `c1-prime-live-census-v0.1.md` — attribution, per statement 2,
not identity alone).

## Clause 2 — §6 synchronization horizon: formula corrected for a non-injective rung *(new; per [6])*

§6's synchronization horizon evaluates the mean posterior entropy
conditional on truncation as $E[H \mid U > 0] = H_{law} / \Pr(U > 0)$. That
identity assumes the law-mass mean over $U = 0$ windows is zero, which is
the full-context injectivity theorem and holds for r1–r4 only. Amend to

$$E[H \mid U > 0] = \frac{H_{law} - H_{U=0}}{\Pr(U > 0)},\qquad
H_{U=0} = \sum_{\text{windows with } U = 0} P(\text{window})\, H(S \mid \text{window}),$$

which reduces to the current formula wherever $H_{U=0} = 0$. **No committed
synchronization horizon changes** (all are r1–r4). Producers that compute
the horizon must use the corrected form before any r0 horizon is reported.

## Clause 3 — scope of three note-level theorems *(new; per [6])*

Enactment applies the following scoping edits, each a correction placed
where the next reader meets the claim (no original text deleted):

- `full-context-injectivity-note-v0.1.md` *(list completed per [r2-6])*:
  the theorem statement's "every rung" (line 12), consequence 3 ("the
  interface axis is degenerate at full context, everywhere", line 92),
  consequence 4 ("every informational witness", line 99), consequence 5
  ("any full-context configuration", line 107) and the falsifier's "any
  rung" (line 113) — each true for r1–r4 and false or unqualified with r0
  on the axis. Add the r1–r4 qualifier at each.
- `partition-identity-note-v0.1.md` — the identity
  $n_r(T_{ep}, L, B)$ constant across rungs holds for r1–r4 (measured, every
  committed law); it fails for r0 (5,696 vs 394,824 at (14, 14, 2)). Add the
  scope line.
- `c1-divergent-grid-v0.1.md` G1 (divergent mass non-increasing in the
  predicted-record rung): the pushforward/nested-pair proof applies with r0
  prepended; no edit needed, recorded here so the check is on the trace.

## Clause 4 — D1 falsifier and the exit condition *(new; per [7]; PI's call)*

- **D1.** The over-synchronization falsifier's verdict
  (`d1-falsifier-verdict-v0.1.md`) is a statement about the r1–r4 content
  ladder and stays so. r0 → r1 enters D2 as an added adjacency and is
  reported alongside, never as a substitute: "r0 never collapses" is a
  property of C1's programs (four distinct programs whose actions are
  unattributable at kind-only), not of the rung. *(per [r2-35])* Part I's
  D1 text says long contexts might "collapse every interface"; with r0
  statutory that sentence can never fire. The companion Part I amendment
  therefore revises D1 to read "collapse every content rung r1–r4", so the
  preserved verdict is statutory, not interpretive.
- **Exit.** Part I's exit clause reads "measurably distinct observability
  regimes across rungs"; the "three rungs distinct" phrasing is a later
  gloss in the D1 verdict, not statute. The researcher's recommendation is
  that "across rungs" continues to mean r1–r4 as the clause was written,
  with r0 reported beside it. **Whether r0 counts toward the exit clause
  changes what M1 succeeding means and is the PI's decision at enactment.**

## Companion Part I amendment (text proposed; Part I is the PI's document) *(per [2])*

- **D2** *(per [r2-33])* — "Rungs: actor-only → +object → +related-entity
  → +lineage" becomes "Rungs: kind-only → actor-only → +object →
  +related-entity → +lineage. The r0 → r1 adjacency is **pending** D2's
  own form of evidence — an exhibited history class on which ACTOR changes
  a Q1–Q5 posterior and a preregistered predictive distribution (Owed item
  2 below); the census's aggregate gaps show such classes exist but do not
  exhibit one. The four-rung content ladder's requirements are unchanged."
- **D4** *(corrected per [r2-2]: the previous draft had the comparison
  reversed)* — D4's concern is posterior-support growth under the sparsest
  interface, and with r0 on the axis **r0 is the sparsest interface and its
  supports are larger than r1's** at every measured C1 context (ε = 1, max
  support: L = 8 r0 64 vs r1 28; full context r0 33 vs r1 1; raws
  `r0-ladder-census-14-{8,14}-2-2026-09-03.json`). The companion text
  therefore **re-points D4's support-bound requirement at r0**: "measure
  reachable-support growth of the exact filter under the kind-only
  interface (the sparsest rung) on the base configuration; if it exceeds
  the enumeration budget, the world shrinks — not the ladder." r0 is priced
  under that rule at M1 scale when M1 scale is priced, on the per-pass unit
  of v0.2.8.1's erratum. The claim "D4 is not touched" in v0.2.7 is
  **withdrawn**: the r0 census's process reached 4.4 GB at L = 14 on the
  recursion, and r0 has not been priced under any admitting rule.
- **Scope of r0 across the deliverables** *(per [r2-34]; researcher's
  decision, recorded here)* — r0 joins the ladder wherever the ladder is
  the variable: deliverable 4's per-interface characterization, the
  D8 order-mode cross (Part II §4 order modes), the §9 controls, and
  synchronization reporting (under Clause 2's corrected formula). Every
  producer that hard-codes r1–r4 today (`scripts/c1_query_ceilings.py`,
  `d8_benchmark.py`, the sweeps) is extended at the time it is next run
  under a stamped rule; **every committed r1–r4 artifact stays as
  measured and is labelled r1–r4**, and no committed D8 attribution number
  is re-derived. Nothing in deliverables 1–3 or 5 changes.
- **Exit clause** — wording unchanged; interpretive note per Clause 4,
  resolved by the PI.

## Considered and declined *(as v0.2.7, with one addition)*

- Adding r0 outside the statute; masking ACTOR on some kinds only (r0′);
  waiting for the naming bridge — declined as in v0.2.7.
- **Declaring r0's numbers statutory on the strength of the census.**
  Declined *(per [3])*: the census ran no full gate, its note says nothing
  in it is a statutory ceiling, and the D2/§9 witness for r0 → r1 has not
  been written as a control. The rung enters the statute; its numbers stay
  exploratory until the owed items land.

## Owed before the numbers can be cited as statutory

1. ~~Permutation-orbit check~~ **Run 2026-09-04 as a coarse
   thread-signature quotient** (statement 2's table;
   `scripts/r0_identity_residual.py`, 94 s for four contexts and both ε).
   It settles the mechanism question in the negative; it does not give an
   identity-entropy decomposition, which remains open. The census note
   `r0-ladder-census-v0.1.md` §2–3 needs a correction block at enactment:
   mechanism withdrawn, table inserted.
2. **r0 → r1 D2/§9 witness**: an executable control exhibiting a history
   class where ACTOR changes a Q1–Q5 posterior (D2(a)) and the next-2-kind
   distribution (D2(b)).
3. **D4 pricing of r0 on the per-pass unit** at the laws the paper will
   cite.
4. **Producer edits** for Clause 2 (the corrected horizon formula) with a
   regression pinning every committed r1–r4 horizon unchanged.

## Review request (second round)

(i) whether Clause 2's corrected formula is the right conditional (it
subtracts the $U = 0$ contribution from the law-mass mean; an alternative is
to define the horizon on $U > 0$ windows only and never mix); (ii) whether
the companion Part I text for D4 should instead re-point the support-bound
requirement at r0 as the new sparsest rung — the researcher's position is
no, because r0's supports are measured smaller and the requirement's point
is the binding constraint; (iii) anything in Clause 3's scoping list that
is missing; (iv) whether the anonymization in statement 2 is the right
notion of "identity-only" — it treats two states as the same situation iff
they agree after replacing every thread by (executed-kind multiset, status,
held locks); an alternative keeps the executed-kind *sequence*, which would
lower the identity-only share further.
