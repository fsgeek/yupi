# D8 shuffled channel — built, witnessed, and its premise measured — v0.1

> **Status (2026-08-23 09:30 PDT): exploratory; witness 7 green; one Part I sentence
> refuted by measurement; D8's premise narrowed, not refuted.** Code:
> `src/yupi/shuffled.py`; witnesses: `tests/test_shuffled_channel.py`
> (12). No thresholds touched. This note records what the channel turned
> out to carry, because it is not what the statute's framing implies.

## 1. What was built

Part II §4 order modes, implemented literally. Shuffled mode: the filter
expands every B-tick latent continuation of the belief, projects each
record to the rung, and multiplies the path mass by the channel likelihood
$m/B!$ — $m = \prod(\text{multiplicity}!)$ when the latent and visible
multisets agree, else 0 — never assuming uniformity over causally possible
orders. Ordered mode is identity serialization = $B$ per-record steps of
the existing filter (asserted equal). Two-path gate: the shuffled filter
equals independent path-summation with the same likelihood bit-for-bit
(C0b, both disciplines, r1/r2/r4, B ∈ {2, 3}, every path at H = 6).
Hand-computed likelihoods: distinct pair 1/2 either order; duplicate pair
$2/2 = 1$; $[A,A,B]$ → $2/6$ for every visible order; matched against a
literal permutation count.

## 2. Witness 7 — relocated to C1

Part I's C0b paragraph: C0b "under the D8 shuffled channel supplies a
candidate bucket containing two noncommuting events." **Measured: it does
not**, at ε = 1, either discipline, any B ≤ 4 (5 for stochastic), H ≤ 8
(10). Pinned as a negative witness. Reason, once seen: C0b has no locks and
at ε = 1 no cursor, so no two realizable same-multiset orders reach
different states. Witness 7 therefore lives in C1, as witnesses 1–2 already
do.

In C1 at ε = 1 the first noncommuting bucket is
`[BLOCK T1 L0, DISPATCH T0, BLOCK T2 L0]` — two threads blocking on one
lock; order fixes the wait queue (I2). Same-lock BLOCKs are never adjacent
(the two-stage kernel dispatches into the freed CPU first), so **B = 2 can
never expose it**; it first appears at tick 7 and a B = 3 bucket aligned at
7–9 captures it (96 differing buckets at H = 9). B = 4 at H = 8 cuts it;
longer horizons would admit it.

## 3. What the channel carries (the finding)

Order within a bucket is informative exactly when two records do not
commute as state maps. In these worlds that happens through two
coordinates only:

1. **The round-robin cursor** (ε < 1). At ε = ½, B = 2, the channel differs
   from ordered already at bucket 0 — `[DISPATCH T0, DISPATCH T1]` — and
   **dropping `rr_cursor` makes the ordered and shuffled posteriors
   identical** (asserted). Everything the B = 2 channel hides at ε = ½ is
   *who the scheduler will favour next*.
2. **Wait-queue order** (locks, any ε). Needs two BLOCKs on one lock inside
   one bucket, so B ≥ 3 in C1.

Neither is "interface uncertainty without touching the world." Both are
uncertainty about a **named coordinate of the world state** — the same
shape as the offset finding (`c1-offset-vs-state-v0.1.md`: offset is a
coordinate of state). D8's premise was that the shuffled channel restores
uncertainty at long L by attacking injectivity in the *channel*; what it
actually does is erase specific latent coordinates, and which coordinates
depends on ε and B. At ε = 1, B = 2 — the statute's base condition — it
erases nothing.

This narrows D8 rather than killing it: the manipulation still exists and
still separates order modes at matched disclosure latency (Part I v0.2.2),
but its effect size is a function of (ε, B, lock contention), not a free
knob on injectivity.

## 4. What this means for the witness the queue wanted

The "D8 witness with ε as control" proposed at the start of this wander
is now more specific and cheaper. Because the channel's information
decomposes by coordinate, the long-L measurement should report, per
(ε, B, rung): posterior entropy under shuffled minus ordered, **split into
cursor entropy and wait-queue entropy**, with the remainder asserted zero.
That is a decomposition of gap 1 by *which state coordinate the trace
surrendered* — exactly the kind of thing a finite owned world can do and a
learned one cannot. The ε axis is no longer merely a control: it selects
which coordinate the channel is allowed to hide.

Not done here: that measurement; any threshold; any statute edit. Part I's
C0b sentence needs an erratum (append) — a PI act, since Part I is frozen.

## 5. Cost note (D6)

Shuffled-mode update cost is branching$^B$ continuations per belief
state, not $B!$: the filter never enumerates permutations. The D6 audit's
"$B!/\prod$ dup" line describes the channel, not the update; both grow
fast enough that B ≤ 3 is the practical regime in C1, which is also the
interface-design fact §4 says to report.
