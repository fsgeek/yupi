# Part II amendment proposal — v0.2.6 (cursor into the tuple; σ as an M1 condition)

> **Status (2026-08-24 13:59 PDT): PROPOSED — awaiting cross-family review, then PI
> enactment.** Process per the E-via-D decision (2026-08-24, this
> conversation's walk item 3): one small consolidated amendment, reviewed
> before enactment like every prior version bump, closing the two
> state-definition open items adjudicated 2026-08-20
> (`audit-adjudication-2026-08-20.md`, findings 3 and 4) so that the D8
> order-mode attribution measurement targets a defined statutory object.
> No transition rule, projection, threshold, or frozen decision changes.

## Clause 1 — the scheduler cursor joins S_t (erratum, owed since Aug 20)

§1's tuple omits the round-robin cursor while §3 uses it ("part of
scheduler metadata when ε < 1"), making the §1 prose non-Markov as written
for ε < 1. Amend the tuple to

$$S_t = (\mathbf{pc}, \mathbf{st}, \mathbf{run}, \rho, \mathbf{own}, \mathbf{wq}, \mathbf{dq}, \kappa, \sigma)$$

- $\kappa \in \{0..n_T-1\}$ — global round-robin cursor. Semantics
  unchanged from §3 (v0.2 cursor rule): advances past the selected thread
  on both mixture components, canonical mod $n_T$. **At ε = 1 the cursor
  is never written and stays at its initial value 0** — matching §3.1's
  "absent from the effective state" and the implementation
  (`kernel._epsilon_policy`); formally it is a constant coordinate there,
  so no ε = 1 quantity changes. At ε < 1 it is honest state: the D8
  channel measurably carries it (`d8-shuffled-channel-note-v0.1.md`,
  cursor-drop test).

No implementation change: `State.rr_cursor` already exists and behaves
exactly as above. This clause makes the statute describe the machine.

## Clause 2 — σ is pinned to identity as a condition of M1 characterization

§1 includes σ (episode naming); §2's μ₀ draws it uniformly from
injections. The implementation has never carried σ; every committed
posterior, ceiling, theorem, and witness is about the role-known
structural quotient (audit finding 3). Rather than leaving this as a
standing statute–implementation gap, amend:

**M1 characterization condition:** all M1 exact-characterization
quantities (posteriors, ceilings, query entropies, witness searches,
divergence classes, the D8 order-mode contrast) are computed **under the
condition σ ≡ id** (the identity naming). Under this condition, posteriors
over $S_t$ coincide exactly with posteriors over the structural quotient,
because σ is dynamically inert (no kernel rule reads it) and known. μ₀
conditioned on σ = id is the point mass on the structural initial state.

**What this does not change:** corpus generation draws σ per episode from
D3's ≥ 50-token pools, exactly as §2 states; held-out-binding evaluation
and every naming-dependent claim live at the corpus layer and are **not**
covered by the condition. The statute–implementation gap for *corpus*
work remains open and recorded; it closes at the corpus milestone, not
here. Any characterization quantity that ever needs σ uncertainty (none
in M1's query set does — no Q1–Q5 query reads names) would be computed
without the condition and labeled as such.

**Effect on the record:** retroactively, every committed exact
measurement is a statutory measurement under a stated condition, rather
than an exploratory measurement about an off-statute object. No number
changes.

## Considered and declined

- **Option A — implement σ now** (full statutory state before the D8
  measurement): pulls corpus-milestone work forward; σ would ride inert
  through a measurement that never reads it. Declined as cost without
  content.
- **Option C — relocate σ out of S_t to the emission/corpus layer**:
  defensible (σ is dynamically inert; naming is arguably an
  observation-layer property) and would close the gap by moving the
  statute to the implementation. Declined because it is the largest edit
  of the options, forecloses future worlds whose dynamics read names, and
  its benefits over Clause 2 are cosmetic while its review burden is not.
  Recorded here so the relocation option is on the record as examined,
  not overlooked.
- **Bare erratum without the σ clause** (the original option B): leaves
  every measurement labeled exploratory-relative-to-statute when one
  sentence makes it statutory-under-condition. Dominated.

## Review request

Cross-family review is asked to check: (i) Clause 1's ε = 1 constancy
convention against `kernel._epsilon_policy` and §3.1; (ii) whether σ ≡ id
conditioning could distort any *binding-theoretic* claim M1 exit relies
on (the proposer believes none — no M1 query reads names — but this is
exactly the blind spot a naming-focused reviewer would catch); (iii)
whether the invariants I1–I6 need κ mentioned (proposer: no — none
constrains it). Enactment after review is the PI's; the enacting commit's
stamp versions Part II to v0.2.6.
