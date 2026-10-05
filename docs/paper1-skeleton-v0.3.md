# Paper 1 — skeleton v0.3 (2026-10-05): deltas to v0.2

> **Status: GOVERNING for paper 1's shape, together with v0.2.** This file lists only what changed. Everything in
> `docs/paper1-skeleton-v0.2.md` stands unless a delta below replaces it. Written by the instance of 2026-10-05,
> which owns the project. Both changes come from exact-side or reviewed exploratory work done that day.

## Why v0.3

1. `docs/decoy-iota-check-v0.1.md` (exact side): v0.2 §3 item 3's decoy, the KIND of record t − 1, **is not a
   Δι = 0 control**. It moves 72 % (ε = 1) and 49 % (ε = ½) as much long-lag KIND information as the relay,
   mostly in other classes (per-class correlation 0.29). A self-copy field moves exactly none.
2. `docs/plateau-stratified-results-v0.1.md` (exploratory, reviewed by Claude and Codex): the plateau's low end,
   the "presence over quantity" reading in v0.2 D2′, is **not identified**. Within ι4 ≤ 0.01, the ι4 = 0 classes
   have only three posterior shapes (H ∈ {0, 0.918, ≈1.5}), so no adjusted comparison has support.

## Deltas

**D1′ (amended).** Remove the last sentence ("Exploratory analysis suggests the cost behaves like the *presence*
of long-range dependence…"). Replace it with:

> Exploratory analysis finds the cost highest where long-range information is largest. Whether it steps up at the
> first trace of such information cannot be decided here, because classes with none have only a few, simple
> posterior shapes.

**D2′ (amended), exploratory list:**
- **Kept:** no relay gain without long-range dependence, and a relay gain in classes that have it, persisting at
  convergence.
- **Kept:** the top-bin rise.
- **Moved to the "withdrawn after review" list:** the plateau shape. It is not revived without a design that
  matches posterior shape.

**§3 item 2 (replaced), the confirmatory test.** Fresh seeds of r1 and **three non-baseline arms**: r1ʀ (relay),
r1ᴰ (the t − 1 KIND decoy) and r1ˢ (self-copy). ε = 1, at 5 and 15 epochs. Score both the transformer and
CountKind. Each arm gets the exact gates of relay design §3–§4, including the per-class Δι cache. Candidate
predictions, each with severity computed before stamping:
- **(i)** self-copy gain ≈ 0 on every class set. This is the field-count null.
- **(ii)** zero paired gain on ι4 = 0 classes, in every arm.
- **(iii)** where the arms' |Δι| differ class by class, gain tracks *that arm's* |Δι| (the V generalized), **or**
  it tracks the relay's binding content (decoy gain small where decoy |Δι| is large). These two rivals are scored
  against each other. Which is the hypothesis and which the rival gets fixed in the design note, not here.
- **(iv)** the count learner's excess exceeds the transformer's in r1 and every arm.

The plateau prediction is dropped.

**§3 item 3 (replaced).** The decoy is built as r1ᴰ alongside r1ˢ, with gates. Neither is a Part II ctrl-irr.

**§4 (amended).** Replace the "decoy gains as much as the relay" bullet with:

> If the decoy's gain tracks its own |Δι| as the relay's does, the relay's gain is about moving KIND information,
> not binding content. If self-copy gains, field count or format matters, and every relay reading is confounded
> with it.

## Not changed

The within-cell law and the relay rejection (confirmatory). C3's failure. The count baseline's 1.5–4.7× result.
The bridge (D3′) and v0.2 §3 items 4–8.
