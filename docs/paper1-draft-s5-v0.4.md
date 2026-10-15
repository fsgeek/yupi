# Paper 1, §5 draft v0.4 (2026-10-15): What output-level comparisons could not settle

> **Status: DRAFT v0.4, owning instance (from 2026-10-14).** v0.3 plus §5.5 (skeleton v0.6 addendum, 2026-10-15).
> v0.3 is kept for the record.

## 5. What output-level comparisons could not settle

An exact world removes one excuse for an inconclusive result: the information is known. Five questions still went
unsettled. Each had its own cause, stated below, and each comes with a *candidate* design that might settle it.
None of these designs has been shown to work.

**5.1 Is the cost a step, or does it rise with far information?** The raw per-model bins rise with ι_4 in every
model (§4a, Figure 4a). An earlier reading of a step, a cost roughly constant once ι_4 > 0, came only from fits with
an entropy control. To test a step one needs classes of similar posterior shape on both sides of ι_4 = 0, and the
world does not supply them:
- classes with ι_4 = 0 take only three next-KIND entropy values;
- exact matching on type, mass and entropy bin covers 26–64 % of the windows with far information, almost all of
  them in deterministic classes.

*Cause:* the class structure of this world. *Candidate design:* a world variant built so that posterior shapes
overlap across ι_4 = 0.

**5.2 Which far-information measure does the learner track?** Two exact long-range regressors, one with an
accounting term and one without, correlate at 0.79. A pre-declared comparison between them initially separated
them. Once fixed effects for the last record's kind were added, it **lost its separation**: neither regressor stayed
resolved. *Cause:* collinearity. *Candidate design:* regressors that are not collinear by construction, or an
intervention that moves one while holding the other.

**5.3 Does a near copy help by being near, by carrying a binding fact, or through its training target?**
- A first design with relay, decoy and self-copy arms was blocked at review. The self-copy's value is determined by
  its own record's KIND, while the relay's and the decoy's depend on earlier records. So the self-copy cannot match
  the other two in what they vary with, and arm-specific effects of carrying a varying field were not absorbed.
  Under planted rival mechanisms, the design gave wrong attributions 14–33 % of the time. Its pilot models were
  trained, and only their between-seed spreads have been read.
- Two later pre-registered arms took a different route, separating the copy's presence from its supervision (§4e).
  On KIND, an unscored copy cost the learner, and supervising the slot without the copy helped a little. Whether
  the copy helps once supervised is not resolved with three seeds. On ACTOR none of the
  presence or supervision contrasts (C1–C3) resolves.

*Cause:* a missing control of the right kind, then too few seeds. *Candidate designs:* more paired seeds; a field
that varies like the relay but carries no information; a nontrivial auxiliary target that is not the lookup; and
interventions on a fixed trained model at evaluation time, such as counterfactual windows or interchange
interventions (Geiger et al. 2021).

**5.4 What is the unit?** Every paired analysis from 30 September to 5 October computed window-level errors on
seed-mean differences. Between-seed variance dominates at 5 epochs: two r1 seeds differ by more than the relay
effect. *Cause:* an analyst error, an inference mistake rather than an open question. Re-analysed with the model as
the unit, the qualitative findings survived and their stated strengths did not. §4 states every learner claim per
model.

**5.5 Does a learner treat "the world is random here" differently from "the telemetry hides the state here"?**
§3.0 splits each class's next-KIND uncertainty exactly into transition randomness R and observation gap G. The
natural contrast compares learners on classes of matched H\* where the uncertainty is pure randomness (G = 0,
H\* > 0) against classes where much of it is withheld state (G/H\* ≥ 0.5). Pooled over r1–r3, the pure-randomness
classes are 15.6 % (ε = 1) and 17.2 % (ε = ½) of the position-7 population, and take only three values of H\*; the
device-completion coin (0.918 bits) is 89–92 % of them. High-gap classes sharing a 0.05-bit H\* bin with them carry
0.8–1.4 % of that population. This contrast is in effect one mechanism against everything else.

A graded contrast has more support: within 0.05-bit H\* bins, the share G/H\* varies widely (10th–90th percentile
spread ≥ 0.30) on 17–22 % of the position-7 population at ε = 1 and 36–43 % at ε = ½ (exploratory bin statistics).
Whether that variation spans more than a few mechanisms has not been audited.

*Cause:* in this world, the randomness that does not depend on hidden state comes almost entirely from one source,
by design (Milestone 1 placed randomness only in the scheduler and the device to keep exact filtering tractable).
5.1 meets a related constraint: classes with no far information take three entropy values. *Candidate design:* a
reparameterised world in which completion and dispatch probabilities vary, which leaves the posterior support
unchanged (`world-variant-reading-2026-10-15.md`). *For any exact testbed:* compute the support of a planned contrast,
its mass and its mechanism composition, before designing the learner study.

---

## Provenance

- 5.1: `plateau-stratified-results-v0.1.md`; inventory A5, C1; Figure 4a.
- 5.2: inventory C2; `relay-free-difficulty-results-v0.1.md` corrections.
- 5.3: inventory C3, D; `three-arm-prereg-review-2026-10-05.md`; `relay-lossmask-verdict-v0.1.md`;
  `relay-2x2-verdict-v0.1.md`.
- 5.4: inventory C4, B6.
- 5.5: `exposure-prereg-review-2026-10-15.md`; `random-vs-hidden-review-2026-10-15.md` (Claude finding 4, Codex
  finding 8, both reproduced by the owner); `kind-uncertainty-split-*-2026-10-15.json`.
