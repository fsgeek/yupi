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
- **Revision, disclosed.** The literal "clean revision" gate is **not met** for r1m, which records 1ed07c0 with
  `git_dirty: true`. All six processes launched together at 14:46:42 from the same tree. Each run reads the
  revision when it writes run.json: 14:47:26 for r1m, and 14:47:48–50 for r1Rs. That second time fell after the
  scorer commit at 14:47:42, which is why r1Rs records 4341134 as clean. So all six ran the same code. `git diff
  e170821..4341134 -- src` is empty. The trainer's dirty check covers `src/` and `scripts/` only, and the history
  is consistent with the uncommitted file being `scripts/relay_2x2_score.py`. That is an inference: run.json records
  no file list. The census raws for r1m seeds 1 and 3 and all three r1Rs seeds record `4341134+dirty`. The census's
  dirty check covers the whole tree, and parallel census jobs were writing their raws into docs/, which is the
  likely cause. (Reviewers: Claude finding 9; Codex finding 4.)
- **Census sha256** matches its JSONL for all five arms. The scorer checks this and refuses on a mismatch.

## 2. Did r1Rs learn the lookup? (prereg §5): yes

OBJECT cross-entropy against the relay values on r1 test inputs, over 20,000 windows (147,616 slots), in bits per
slot: 0.0000444, 0.0000424 and 0.0000467. The rule is ≤ 0.05. Raw: `relay-2x2-object-ce-r1Rs-2026-10-13.jsonl`.
For context, the pre-stamp reference values were measured on 4,000 windows for r1R seed 1 only: 0.006 on r1
inputs and 0.0001 on its own. Those are a different subset, so they are not a direct comparison. The check shows
r1Rs learned the lookup. It does not show that the lookup is what helped KIND (see §5).

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

## 5. Additional readings: POST HOC, not pre-registered (revised after both verdict reviews)

**ACTOR, under one standard for every contrast** (prereg §5 reports it alongside without scoring it). The same
decision rule and paired signs are applied to each:

| contrast | ACTOR d_s, seeds 1–3 | decision rule | paired signs |
|---|---|---|---|
| C1 r1Rm − r1m | −0.0018, −0.0075, −0.0064 | not resolved | (−,−,−) |
| C2 r1Rs − r1 | −0.0016, +0.0100, +0.0028 | not resolved | (−,+,+) |
| C3 r1R − r1Rs | −0.0018, −0.0138, −0.0034 | not resolved | (−,−,−) |
| C4 r1m − r1 | +0.0034, +0.0138, +0.0095 | **separated** (r1m worse) | (+,+,+) |

- On ACTOR the KIND-resolved contrasts do not resolve, and C1 *points the other way*: the unscored copy is
  better than the placeholder on ACTOR in every seed, though the ranges overlap. C3 points toward presence helping
  once the copy is supervised, also with overlapping ranges.
- The earlier draft suggested that C2's KIND gain might be a reallocation away from ACTOR. The seed pattern does
  not support that. Seed 1 has the largest KIND gain *and* improves ACTOR, while seed 2 has the smallest KIND gain
  and the largest ACTOR loss. A seed-level overall-quality factor fits better. ACTOR also responds strongly to any
  change in the OBJECT recipe (C4).

**C4 is not a noise floor.** It is completely separated on both fields: r1m is worse than r1 on KIND (minimum
0.01695 against maximum 0.01576) and on ACTOR. Removing OBJECT from the loss changes target scoring and loss
normalization together, so the cause is not isolated. Seed by seed, |C2| exceeds |C4| in two seeds of three
(1.70×, 0.08×, 1.35×). The seed-average magnitudes are 0.0018 against 0.0031. C2's complete separation rests on a
margin of 0.00049 bits (r1 seed 2 at 0.01464 against r1Rs's maximum of 0.01415).

**KIND + ACTOR summed, strict decision rule:**
- r1: 0.0469, 0.0445, 0.0471
- r1R: 0.0407, 0.0357, 0.0433
- r1Rs: 0.0420, 0.0541, 0.0483
- r1m: 0.0522, 0.0647, 0.0578
- r1Rm: 0.0609, 0.0774, 0.0652

Only r1R beats every r1 model (maximum 0.0433 < minimum 0.0445).

**Recovery.** r1Rs recovers about 48 % of r1R's seed-mean KIND gain over r1 (seed by seed: 118 %, 10 % and 50 %).

**Limits carried from the pre-registration.** C2 cannot tell lookup supervision from any nontrivial target in the
slot. C1 cannot tell an informative but unscored copy from a varying decoy field.

**Scorer deviations, disclosed** (Codex finding 7). The frozen scorer uses a 1e-15 tail tolerance, and it would
print a p for a resolved-against outcome. Neither affects this dataset, and the scorer is left frozen.

**Validation curves:** committed as `docs/relay-2x2-curves/` (r1m, r1Rs and r1Rm logs). They are not comparable
across arms, because the masks and targets differ.

## 6. Reading for paper 1 (POST HOC)

Pre-registered:
- On KIND, supervising the OBJECT slot with the relay value helped without the copy present (C2).
- An unscored copy in the input cost the learner, relative to a constant placeholder (C1).
- Whether showing the copy adds to supervision is not resolved (C3).

Post hoc:
- The C2 gain is small, comparable to the effect of a minor recipe change (C4), and it is not mirrored on ACTOR.
- C1's cost is on KIND only. On ACTOR the unscored copy, if anything, helped.
- Only the full relay beat r1 on KIND and ACTOR together under the strict rule.

None of this establishes that presence and supervision are each necessary, or that the placement hypothesis is
false. It does mean the relay gives that hypothesis no support in its simple form, "a near copy helps a learned
reader". Every number here is from three seeds, one world and one budget.
