# Paper 1 (methods), §5 draft v0.2 (2026-10-15): The learner case

> **Status: DRAFT v0.2, owning instance.** v0.1 revised per `paper1m-draft-review-2026-10-15.md` (Claude #16). Governed by `paper1-skeleton-v0.9.md` §5. Compressed from
> `paper1-draft-s4-v0.3.md` (reviewed three times by both families); its numbers are carried unchanged. Not yet
> reviewed in this form.

## 5. The learner case

The learners and the shortfall measure are those of §2.4. This is a measured case, not a general account of
learners.

### 5.1 Shortfall is higher where far information is

Within each content interface, a pre-registered regression of per-window KIND shortfall on far information (ι₄), near
information, ceiling entropy and log class mass gives a positive far-information coefficient with t ≥ 3 in every
run: 21 of 21 held-out runs at 5 epochs and 24 of 24 at 15 epochs. It survives errors clustered by class, and fixed
effects for the last record's kind crossed with the number of distinct actors (lowest t 3.44), in all 45 of those
evaluations (runs, not independent seeds). An exploratory check at about four times the parameters, in one cell, keeps the
sign. The same analysis for the actor field passes its pre-registered test but is not robust to the fixed effects (9
of 24 runs keep t ≥ 3 at 15 epochs). The association is a correlation within cells: classes with more far
information may also be rarer or harder in ways the controls miss. A pre-registered prediction that the coefficient
would shrink no faster than overall shortfall with training failed in 8 of 8 cells.

**Baselines.** A Witten–Bell count table over the ceiling's own classes, trained on the same windows, is worse than
every transformer on every content interface, by 1.33–5.22 times. A parameter-matched GRU on the transformer's
untuned recipe was pre-registered with a floor, fixed before the models ran: each had to beat the count table
before its association could be read. All eight failed it (KIND 0.045–0.076 bits against the table's 0.039–0.064),
so their large, positive association statistics are uninformative under the declared rule.

### 5.2 A copy placed at the point of use, as an input-by-supervision factorial

The relay rewrite (§3.4) holds the ceiling identical class by class while putting the same actor's previous KIND in
each record. All three relay models had lower KIND shortfall than all three controls. But in the original recipe the
copy is both an input and a training target. Two pre-registered follow-ups separated the two by varying only the
OBJECT slot (KIND and ACTOR shortfall at 15 epochs, seeds 1–3):

| arm | OBJECT input | OBJECT target | KIND | ACTOR |
|---|---|---|---|---|
| r1 | placeholder | placeholder | 0.0157, 0.0146, 0.0158 | 0.0312, 0.0299, 0.0314 |
| r1m | placeholder | none | 0.0176, 0.0209, 0.0170 | 0.0346, 0.0438, 0.0409 |
| r1Rs | placeholder | relay value | 0.0125, 0.0141, 0.0142 | 0.0296, 0.0400, 0.0342 |
| r1Rm | relay copy | none | 0.0281, 0.0411, 0.0307 | 0.0328, 0.0363, 0.0345 |
| r1R | relay copy | relay value | 0.0130, 0.0095, 0.0125 | 0.0278, 0.0262, 0.0308 |

A contrast is "resolved" when every model of one arm lies beyond every model of the other in the pre-registered
direction. With three seeds a side, exact paired sign-flip p-values cannot fall below 1/8, and none is conventionally
significant. On KIND:
- **An unscored copy hurt** (r1Rm against r1m): showing the copy without training on it cost the learner, relative to
  a constant placeholder. This cannot distinguish an informative unscored copy from any varying field.
- **Changing the slot's target moved the shortfall** (r1Rs against r1): training the slot to produce the relay value,
  without ever showing it, gave a small resolved gain, with a margin of 0.0005 bits. Removing the slot from the loss
  altogether (r1m against r1) moved KIND by a comparable amount, and the contrast cannot tell lookup supervision from
  any nontrivial target in that slot.
- **Whether the copy adds to supervision is unresolved** (r1R against r1Rs).

On ACTOR, none of these contrasts resolves. The simple placement hypothesis, "a near copy helps a learned reader", finds
no support here. The original gain does not establish an input-placement benefit. The training target contributes,
and the input's increment remains open at three seeds.

For the audit of §4, this is the second kind of limitation an exact world leaves in place: holding the ceiling fixed
controls what is *knowable*. It does not control what the learner is *trained to produce*, and an
information-preserving rewrite of the input can change the training targets with it.

---

## Provenance

- 5.1: `paper1-draft-s4-v0.3.md` §4a–4b and its provenance (B1 raws; `b1-fe-coarse-robustness-2026-10-13.json` and
  `-actor-`; `b1-size-axis-d256-2026-10-13.jsonl`; `converged-ladder-*-2026-10-02.json`).
- Baselines: `count-baseline-comparison-2026-10-04.json`; `gru-baseline-verdict-v0.1.md`, `gru-baseline-score-2026-10-13.json`.
- 5.2: `relay-lossmask-verdict-v0.1.md`, `relay-2x2-verdict-v0.1.md`; table as in `paper1-draft-s4-v0.3.md` §4e.
