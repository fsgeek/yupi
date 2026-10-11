# Paper 1, §3 draft v0.1 (2026-10-11): Exact observability is a profile, not a number

> **Status: DRAFT, owning instance. Not reviewed.** Written from skeleton v0.5. Every number below was re-read from
> the raw named in the provenance list at the end. None was copied from a summary. Claims carry their inventory
> status (`inventory-2026-10-09.md` v0.2) in square brackets for review, to be removed in the paper. §2 (the
> instrument, rungs, the law (40, 8, 2) and the shared-kernel limit) is assumed and still to be written.

## 3. Exact observability is a profile, not a number

The usual figure of merit for a telemetry interface is how much of the hidden state it lets an observer recover.
For a fixed window, Yupana gives that figure exactly, as the ceiling: the entropy of the next record (here, the
next event's KIND) given everything the interface shows. This section shows that the ceiling is only half of what
an interface decides. The other half is *where* in the trace the knowable information sits. Both are computed
exactly, and they come apart.

### 3.1 The ceiling ladder

Each rung adds one field to the record: r0 shows only the event's KIND, r1 adds the ACTOR, r2 the OBJECT, r3 the
RELATED entity, and r4 the LINEAGE. At the frozen law, with an 8-record window, the ceiling on the next KIND falls
as fields are added:

| ε | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| 1 | 1.176 | 0.999 | 0.955 | 0.911 | 0.911 |
| ½ | 1.104 | 0.873 | 0.823 | 0.784 | 0.784 |

*Bits; the law-mass-weighted conditional entropy H\* of the next KIND given the first seven records of the window
(position k = 7, predicting record 8). Position-k quantities cover only windows that run at least k records,
which is 0.85 of window law mass at k = 7; windows that start too close to the episode's beginning drop out.* [EXACT;
re-derived 2026-10-11: H\* × 0.85 reproduces the pattern-ceiling raw to ≤ 10⁻¹⁵ on r0]

Three properties of this ladder matter later:
- **Interface value exists only where the window hides history.** From a reset, every content rung r1–r4 is
  injective on trajectories, so a richer field adds nothing the shorter interface could not reconstruct. r0 stays
  non-injective even from a reset. Rungs separate because the window cuts history off. [EXACT, A2]
- **Four regimes, and a thin top rung.** r4 − r3 is non-negative and at most 4 × 10⁻⁴ bits. LINEAGE is nearly
  derivable from what r3 already shows, and on the KIND target r3 and r4 agree to 10⁻⁴ at every lag. [EXACT, A2]
- **The ceiling is monotone.** A richer rung never leaves an observer knowing less. The next subsection shows that
  this monotonicity does not extend to where the knowledge sits.

### 3.2 The lag profile

For a prefix class c, let ι_m(c) be the information about the next KIND that lies more than m records back:
the KL divergence, in bits, from the exact predictive law given the whole window to the exact predictive law
given only the last m records, read through the suffix's own entity names. ι_m is a function of the prefix alone.
Its law-mass mean over classes is the interface's *lag profile*. ι_1 is the information an order-1 observer
misses; ι_6 is what lies further back than six records.

| m | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| 1 | 0.535 | 0.712 | 0.756 | **0.800** | 0.800 |
| 2 | 0.384 | 0.525 | 0.569 | **0.578** | 0.578 |
| 3 | 0.257 | 0.379 | 0.420 | **0.424** | 0.424 |
| 4 | 0.176 | 0.257 | **0.282** | 0.259 | 0.259 |
| 5 | 0.107 | 0.168 | **0.184** | 0.172 | 0.172 |
| 6 | 0.061 | 0.080 | **0.086** | 0.078 | 0.078 |

*ε = 1, bits, next-KIND target. Bold marks the largest value in each row. Every row passes the identity gate
(≤ 10⁻¹⁵) and the cross-check against the ceiling raw.* [EXACT, A3]

**The profiles cross.** At short lags r3 carries the most history information about the next KIND. From m = 4,
r2 carries the most, and r3 falls to r1's level. The RELATED field turns information that r2 must carry across
four or more records into information within the last few. At ε = ½ the crossing is sharper: r3 drops below r1
from m = 4 (0.305 against 0.338).

So two interfaces can be ordered one way by the ceiling (r3 lets an observer know more than r2) and the other way
by distance (r2 leaves more of what is knowable far back). A richer field does two separate things: it adds
information, and it can relocate information that was already available. The ceiling sees only the first.

**What the profile is not.** Every record on every rung is exactly five tokens (masked fields render as
placeholders), so a lag of m records is a lag of 5m tokens on every interface. The crossing is not an artefact of
record length. [EXACT, by construction]

### 3.3 Moving information while holding the ceiling

The crossing compares different interfaces, which also differ in their ceilings. A cleaner demonstration holds the
ceiling fixed. We built three interventions on r1, each of which writes into the OBJECT slot that r1 masks.
Each writes only a function of the window itself, so it adds nothing an observer of the whole window did not
already have, and the ceiling stays identical *class by class*. Gates A–C verify this exactly:
- the **relay** (r1R): record t's OBJECT holds the KIND of the most recent earlier record in the window with the
  same actor as t. It is an index in the sense of §1: a copy placed at the point of use, with the source left in
  place;
- the **decoy** (r1D): record t's OBJECT holds the KIND of record t − 1;
- the **self-copy** (r1S): record t's OBJECT holds record t's own KIND.

Write Δι_4 = ι_4(r1) − ι_4(intervention): the drop in next-KIND information lying more than four records back.
At ε = 1 the relay's mean Δι_4 is 0.094 bits and the decoy's 0.068, but they act in different classes: across
classes the two correlate only 0.29. The self-copy's lag profile equals r1's at every lag, so it moves nothing.
[EXACT, A4; re-read 2026-10-11 from `decoy-iota-check-2026-10-05.json` and the r1S exact-side log]

The means hide a mix. On about a quarter of law mass, *each* intervention raises ι_4 (relay 27.8 %, decoy 27.1 %).
A rise in ι_4 does not mean information moved further back overall. Where the relay raises ι_4, it still moves
information closer at lags 1–2, and over lags 1–6 it moves information closer on net (inventory §G). Δι_4 is one
point on a profile. Comparisons in this paper use the full profile wherever the claim is about distance.
[EXACT; sign fractions from `decoy-sign-fractions-2026-10-11.json`]

With the ceiling identical, any difference a learner shows between r1 and r1R is a difference in where the
information sits, and not in how much is available. §4e uses this.

### 3.4 What the profile predicts, and what it is not yet known to predict

The rest of the paper asks whether a learner's shortfall from the ceiling follows the profile. One cross-interface
fact belongs here. At ε = 1, r3 lets an observer know more than r2 (ceiling 0.911 against 0.955 bits) *and* leaves
less of it far back (ι_4 0.259 against 0.282). Converged learners have a larger KIND shortfall on r2 than on r3
(0.0189 against 0.0134 bits), with every seed separated, as the profile predicted. [CONFIRMATORY, B2 ε = 1] The
shortfall is measured above each interface's own ceiling, so the ceiling difference is already netted out. But
this pair does not set the ceiling against the profile, because both favour r3. In the pair where they disagree,
r1 against r2, r2 knows more and leaves more far back. That pair was tested only at ε = ½, as part of the
three-way ordering r2 > r1 > r3. There r2 sits above r1 on the means, but no seed separates them. (At ε = 1 the
pre-registration left r1 out of the ordering.)

This is one pair at one ε. At ε = ½ the predicted cross-cell ordering fails, because the ι gaps there are smaller
than the spread between seeds. The paper therefore does **not** claim that the profile ranks interfaces by learner
shortfall. Its learner claim is within interfaces (§4a): class by class, shortfall rises with the far end of the
profile. [B2 split; B1]

One more caution. A richer interface still helps the learner in absolute terms. The learner's total loss on r2
(ceiling plus shortfall) is lower than on r1. What the profile prices is the share of the knowable that the learner
fails to capture, not whether richer telemetry is worth having.

<!-- TODO before review: confirm the absolute-loss sentence with converged r1 ε=1 numbers. The converged prereg
excluded r1 at ε = 1, and the 5-epoch means (r1 0.021, r2 0.029) are under-converged. If no clean source exists,
cut the sentence. -->

---

## Provenance (every number above)

- Ceilings H\* and the lag profiles at both ε: `implicit-info-lag-kind-40-8-2-k7-2026-09-28.json` (60 rows; every
  gate true). Re-tabulated 2026-10-11 by the owner. The values match `implicit-information-first-results-v0.1.md` §1.
- Thin top rung: **re-audited 2026-10-11** from `pattern-ceilings-40-8-2-k{1..7}-2026-09-18.json`. r4 − r3 lies
  in [5e-6, 3.9e-4] bits on every k and both ε, and every gate holds. Injectivity from reset and the "four
  regimes" wording are **still not re-audited** (inventory A2).
- Relay and decoy Δι_4 and the 0.29 correlation: **re-read 2026-10-11** from `decoy-iota-check-2026-10-05.json`.
  Self-copy: `three-arm-exact-side-r1S-2026-10-05.log` (ι_m equals r1's). The 27 % had **no committed source**. It
  was recomputed (`scripts/decoy_sign_fractions.py` → `decoy-sign-fractions-2026-10-11.json`): the decoy's
  fraction is 27.1 %, and the relay's is 27.8 %. The inventory used the figure to set the decoy apart from the
  relay, which it does not.
- The converged r2 > r3 at ε = 1, and the C3 failure at ε = ½: `converged-ladder-verdict-v0.1.md` C3 (C3/C4 from
  `scripts/converged_ladder_c3c4.py`, reproduced by both reviewers).
- Five-token records: `src/yupi/corpus/rendering.py` `render`; `windows.py` `max_tokens`.
