# Completing the relay 2×2: verdict v0.1 (2026-10-13)

> **Status: VERDICT against `docs/relay-2x2-prereg-v0.1.md`** (frozen and stamped at e170821 after two-family
> pre-stamp review, before any model in it was trained). Exploratory in scale: three seeds per arm, with a paired p
> floor of 1/8. Scored by the frozen scorer `scripts/relay_2x2_score.py`, committed at 7ae7630 before any 2×2
> model had finished training. Raw: `docs/relay-2x2-score-2026-10-13.json`. Owning instance, which also wrote the
> pre-registration. Two-family review of this verdict is owed.

## 1. Gates (prereg §6)

- **The trainer reproduces 10-02: PASS.** HEAD trained r1 seed 1 for 1,000 steps on the GPU, and its step-1000
  losses equal the 10-02 log exactly (0.6791265606880188, 0.6846594339672173).
- **All six runs** reached 117,195 steps, exit status 0, and census step 117,195. Input manifest `457ec69a…` (the r1
  corpus `fd5da4c31e43d73d`); r1Rs target manifest `d8c23cab…` (r1R); `unscored_fields` is OBJECT for r1m and empty
  for r1Rs.
- **Revision, disclosed.** The r1Rs runs record 4341134, clean. The r1m runs record 1ed07c0 with `git_dirty: true`.
  At 14:47:26, when they wrote run.json, the only uncommitted file was `scripts/relay_2x2_score.py`, committed 16
  s later at 7ae7630. Between the freeze and 4341134 only `scripts/relay_2x2_census.sh` and that scorer changed.
  The learner code (`src/`) is identical for all six runs, so the flag is benign. The gate's literal "clean
  revision" is not met for r1m, and we say so.
- **Census sha256** matches its JSONL for all five arms. The scorer checks this and refuses on a mismatch.

## 2. Did r1Rs learn the lookup? (prereg §5): yes

OBJECT cross-entropy against the relay values on r1 test inputs, in bits per slot: 0.00004, 0.00004 and 0.00005,
against the ≤ 0.05 rule. That is better than r1R on r1 inputs (0.006) and close to r1R on its own (0.0001). Raw:
`relay-2x2-object-ce-r1Rs-2026-10-13.jsonl`. So C2 and C3 can be read as being about lookup supervision.

## 3. Results

KIND shortfall, seeds 1–3:

| arm | input at OBJECT | OBJECT target | seed 1 | seed 2 | seed 3 |
|---|---|---|---|---|---|
| r1 | MASKED | MASKED | 0.01570 | 0.01464 | 0.01576 |
| r1m | MASKED | none | 0.01760 | 0.02092 | 0.01695 |
| r1Rs | MASKED | relay | 0.01247 | 0.01414 | 0.01415 |
| r1R | relay | relay | 0.01296 | 0.00947 | 0.01252 |
| r1Rm | relay | none | 0.02809 | 0.04114 | 0.03072 |

| contrast | d_s, seeds 1–3 (bits) | decision (pre-registered direction) | paired p |
|---|---|---|---|
| **C1** r1Rm − r1m | +0.0105, +0.0202, +0.0138 | **resolved in the predicted direction** | 1/8 |
| **C2** r1Rs − r1 | −0.0032, −0.0005, −0.0016 | **resolved in the predicted direction** | 1/8 |
| **C3** r1R − r1Rs | +0.0005, −0.0047, −0.0016 | **not resolved with three seeds** | 1/4 |
| C4 r1m − r1 | +0.0019, +0.0063, +0.0012 | descriptive | — |
| I (difference-in-differences) | −0.0100, −0.0249, −0.0154 | no interaction claim, because C3 is not resolved | 1/4 (two-sided) |

## 4. The pre-registered sentences (prereg §4), as fixed

- C2 resolved: **"supervising the OBJECT slot with the relay value helped without the copy present"**.
- C2 resolved and C3 not resolved: **"whether showing the copy adds to that is not resolved"**.
- C1 resolved: **"an unscored copy in the input cost the learner, relative to a constant placeholder"**.

## 5. What else must be said

- **C4 was expected to be near-null, and it is not.** Removing the trivial MASKED target (r1m against r1) raised
  the shortfall in all three seeds, by 0.0012–0.0063 bits. The pre-registration named C4's |d_s| as a noise floor
  for near-identical recipes. On that floor, C2's effect (0.0005–0.0032) is *no larger* than what removing a trivial
  target does. C2 is resolved by its decision rule, with the mask and denominator fixed within the contrast. But its
  size sits inside the variation a minor recipe change produces, so it is a small effect. C4's consistent sign also
  means C4 is not pure noise: scoring the trivial OBJECT target itself appears to help a little.
- **ACTOR, reported alongside per prereg §5, qualifies C2.** ACTOR shortfall by seed:
  - r1: 0.0312, 0.0299, 0.0314
  - r1Rs: 0.0296, 0.0400, 0.0342
  - r1m: 0.0346, 0.0438, 0.0409
  - r1R: 0.0278, 0.0262, 0.0308
  - r1Rm: 0.0328, 0.0363, 0.0345

  r1Rs is worse than r1 on ACTOR in seeds 2 and 3. On KIND + ACTOR together it is worse in two seeds of three
  (r1 0.0469, 0.0445, 0.0472; r1Rs 0.0421, 0.0541, 0.0484). **C2's KIND gain is therefore not a gain on the
  record's other learned field.** It may be a reallocation. The pre-registered reading stands for KIND only, and
  paper 1 must give the ACTOR numbers beside it. By contrast, r1R is better than r1 on both fields in every seed.
- **C2's limit, stated in the pre-registration:** it cannot tell lookup supervision from *any* nontrivial
  predictable target in that slot. The lookup check shows r1Rs did learn the lookup. It does not show that the
  lookup is what helped.
- **C1's limit:** it cannot tell an informative but unscored copy from a varying decoy field.
- **Relation to r1R's gain over r1** (−0.0027, −0.0052, −0.0032, seed-paired): r1Rs recovers part of it without
  ever showing the copy. C3, the copy's increment once supervised, is not resolved.

## 6. Reading, for paper 1

Within these arms, three statements hold:
1. Training the learner to *produce* the back-reference helped KIND a little, even when the copy was never shown.
   It did not help ACTOR, which got worse in two seeds of three.
2. *Showing* the copy without supervising it hurt.
3. Showing it once it was supervised added nothing that three seeds resolve.

The relay was built to test whether placing information near its point of use helps a learned reader. Neither manipulation alone reproduced
the full relay's gain on both fields. Supervision without presence gave a small KIND gain, about as large as a
minor recipe change moves the shortfall, and it was offset on ACTOR. Only presence and supervision *together* (r1R)
beat r1 on both fields in every seed. C3 and the interaction are not resolved, so whether the pair is more than
the sum of its parts is open. This is exploratory: three seeds, one world and one budget.
