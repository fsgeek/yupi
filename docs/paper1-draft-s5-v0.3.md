# Paper 1, §5 draft v0.3 (2026-10-13): What output-level comparisons could not settle

> **Status: DRAFT v0.3, owning instance.** It revises v0.1 after the whole-draft review
> (`paper1-whole-review-2026-10-13.md`: W16–W18, W21, W26), and supersedes it. Sources: inventory §C, §G, §I–§K and
> the documents they cite.

## 5. What output-level comparisons could not settle

An exact world removes one excuse for an inconclusive result: the information is known. Four questions still went
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

---

## Provenance

- 5.1: `plateau-stratified-results-v0.1.md`; inventory A5, C1; Figure 4a.
- 5.2: inventory C2; `relay-free-difficulty-results-v0.1.md` corrections.
- 5.3: inventory C3, D; `three-arm-prereg-review-2026-10-05.md`; `relay-lossmask-verdict-v0.1.md`;
  `relay-2x2-verdict-v0.1.md`.
- 5.4: inventory C4, B6.
