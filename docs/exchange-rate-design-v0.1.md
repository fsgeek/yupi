# The placement exchange rate: design v0.1 (2026-10-13)

> **2026-10-13 (later): SHELVED for paper 1, never computed.** The Claude design review found it decorative. Its
> numerator was already published, its main reading rule was already settled (min gain 0.0017 > 6 × max learner
> cost 0.00028), and C_raw prices a cost this instrument never pays (fixed-width records, the slot already masked
> on r1, the relay rebuilt per window). Paper 1 gets one sentence in §4e instead. If the pricing question returns,
> it does so after the r1Rm verdict, as a cost *profile* C(m) = Σ_t H(relay_t | own KIND, ACTOR, position, previous
> m in-window records) against named codecs, with seed-matched pairs primary and presence and supervision gains
> reported separately. It belongs to the locality study, not paper 1.
>
> **Codex design review (same day)** concurs: a constant denominator only rescales the score, and marginal entropy is
> a coding benchmark, not an emission cost. **Adopted from it:** when the r1Rm censuses exist, the masked-arm scoring
> also reports a descriptive three-arm table (r1, r1R, r1Rm) with KIND, ACTOR and their total; OBJECT excess is shown
> separately and never subtracted. Both the 3×3 cross-model contrasts and the seed-matched pairs i = i are reported.
> Matched seeds share initial weights and batch order (Claude finding 4). Everything there beyond the
> pre-registered KIND readings is EXPLORATORY.

> **Status: DESIGN, written before any number was computed.** Exploratory and descriptive: no hypothesis test,
> nothing stamped as confirmatory. It goes to two-family review before computation. Owning instance. Motivated
> by skeleton v0.5 §1: placing information near its use costs no trace *length* on this instrument (records are
> fixed-width), so its price has to be stated some other way.

## 1. The question

The relay places a redundant copy of earlier KIND information at the point of use, and the ceiling is unchanged
class by class. What does that copy cost, and what does it buy, in the same units?

## 2. Two costs, stated separately

- **Cost to an ideal observer: exactly zero.** The relay field is a function of the window, so given the past its
  conditional entropy is 0. An ideal compressor stores it for free, and the exact ceiling does not move. This is an
  identity, and nothing needs computing.
- **Raw emission cost C_raw.** The field's marginal entropy per record under the window law, H(OBJECT_t) on r1R at
  k = 7: the bits a producer emits if it writes the field without compressing it against history. It is computed
  exactly from the r1R pattern table, as the law-mass-weighted entropy of the relay value. This is a property of the
  interface, not of any learner.
- **Learner-side cost C_learn.** The learner's own shortfall on predicting the relay field, per record. It is
  already reported per model (9.4e-5 at 5 epochs and 1.7e-4 at 15, seed means), and is recomputed per model here.

## 3. The gain

**G, per seed pairing (r1 seed i, r1R seed j; 9 pairings; 15 epochs).** G is the mean over paired k = 7 test windows
of [r1's total structural shortfall] − [r1R's total structural shortfall *excluding* the relay field]. "Structural"
means every field the base rung shows (KIND and ACTOR), so a relay that helped KIND while hurting ACTOR would show
up as a smaller G. G_kind (KIND only) is reported beside it for continuity with §4e.

## 4. The rates

- **R_raw = (G − C_learn) / C_raw:** net bits of learner shortfall saved per bit of uncompressed redundancy emitted.
- **The net benefit G − C_learn**, in bits per record. The sign is what matters: whether the copy pays for itself to
  the learner at all.

Each rate is reported as its range over the 9 pairings, together with each pairing's value. No t statistics. The
model is the unit (§2.5). The 5-epoch pairings are reported separately as a mixed-phase descriptive.

## 5. What would change the reading

- If G − C_learn ≤ 0 in any pairing, the claim "the copy pays for itself" is per-pairing, not universal.
- If G < G_kind (ACTOR got worse), the relay's KIND gain is partly a reallocation, and §4e must say so.
- R_raw is specific to this field and this world. It is not a constant of nature, and §1 must not quote it as one.

## 6. Inputs (must exist before computing; checked by sha256 against the relay verdict's gates)

- Census per-window files for the 10-02 r1 and r1R models, 5 and 15 epochs, under
  `~/.cache/yupi-scratch/census/`. The relay verdict's gates record their hashes.
- The r1R pattern table at k = 7, ε = 1, for C_raw.
- `drop_relay` pairing: the same window-pairing gate the relay verdict used.

## 7. Not in scope

ε = ½ (no r1R models), the decoy and self-copy fields (pilot models unopened), and any claim about mechanism.
