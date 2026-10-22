# An operational test of "the kind is readable": declared before any run (2026-10-22)

> Owning instance. Answers the blind read's point 2 and its second-read refinement (2f): the look-alike statistic in
> §4.3 is calibrated by an oracle that knows the true class, so it is not a monitor's error rate. This builds an
> actual monitor, says exactly what it may see, and scores it against a prior-only baseline. Declared and stamped
> before any model is run through it. Status: EXPLORATORY, with declared predictions and a declared reading.

## What the observer may see

- **May see:** the cell's family: the interface, ε, and the exact class table at position 7 (every class's exact
  next-KIND law, its prior law mass, and its split). These come from the kernel, not from data. And one model output
  q_w (the next-KIND distribution, renormalised over KINDS as in `learner/exposure.py`).
- **May not see:** the window, its pattern class, or any other model output. With the class, the task would be a
  table lookup (the reviewer's point). The problem studied is reading the kind from q alone.

## Truth labels (per true class c of the window)

pure (G < 1e-12 and H\* > 1e-12); withheld (G ≥ 0.1); deterministic (H\* ≤ 1e-12); none (otherwise). This separates the
deterministic classes that §4.3 folded into "pure", as the reviewer asked. The headline population is windows whose
truth is pure or withheld. The other two are reported, never dropped silently.

## The monitor (no fitted parameters)

Group the table's classes by exact law. Each group g has a law P_g, a mass W_g, and a kind: the mass-majority truth
label of its classes (collisions are below 0.05 % of mass). For an output q:
- d_g = TV(q, P_g); g\* = argmin d_g (ties broken by larger W_g).
- Predict kind(g\*).
- **Abstain** if kind(g\*) is deterministic or none, or if a group whose kind is the other one of {pure, withheld}
  has d_g ≤ d_{g\*} + m.
- Margin m = **0.005** is the headline, fixed here. A sweep m ∈ {0, 0.0025, 0.005, 0.01, 0.02} is reported as a
  coverage–accuracy curve.

**Separation of populations.** The monitor has no trained parameters. Its inputs are the exact table, computed from the
kernel, and m, fixed above. Nothing is fitted on any model's outputs or on test windows, so there is no train/eval
leakage to control. Each model is scored on its own test split (84,949–85,105 windows).

## Comparators

- **Prior-only baseline:** always predict whichever of {pure, withheld} has more prior mass in the cell's table;
  never abstain. Its balanced accuracy is 0.5 by construction. Its plain accuracy is the majority share, reported to
  show what accuracy alone would hide.
- **Oracle-q reference:** the same monitor fed the true exact law (q = P_c). This is its ceiling with a perfect model,
  and it isolates what is lost to exact-law collisions and to the margin.

## Metrics (per model; headline population)

- coverage (share not abstained);
- on covered windows: balanced accuracy (mean of pure-recall and withheld-recall), both recalls, plain accuracy;
- conservative balanced accuracy, counting an abstention as an error;
- the full 4 × 3 confusion (truth: pure / withheld / deterministic / none; output: pure / withheld / abstain).

## Models

The same 12 as §4.3: r1 and r3, ε ∈ {1, ½}, seeds 1–3, 15-epoch ladder
(`learner-precision-monitor-gkind-40-8-2-k7-2026-10-15.json` lists the run directories and checkpoint hashes). CPU,
position 7, KIND only. Outputs are captured through the same wrapper as `scripts/learner_precision_monitor.py`.

## Predictions

- **K1 (oracle-q).** Coverage ≥ 0.97 and covered balanced accuracy ≥ 0.99 in every cell. Basis: collisions are below
  0.05 %, and the exact sweep puts 0.1–1.7 % of mass within 0.01 of the other kind.
- **K2 (models).** In every model, covered balanced accuracy ≥ 0.90 and coverage ≥ 0.80.
- **K3 (agreement).** The cell ordering of conservative balanced accuracy is the reverse of the ordering of mean
  look-alike other-kind mass (aG_mean): lower look-alike mass, better monitor. Checked on the four cell means.

## Declared reading (per cell; all three seeds must agree)

- **Operationally readable:** covered balanced accuracy ≥ 0.90 and coverage ≥ 0.80.
- **Not operationally readable:** covered balanced accuracy < 0.75 or coverage < 0.50.
- **Between:** numbers only, no general sentence.

v4's use of the word "readable" follows this reading. If a cell is not operationally readable while the look-alike
rule called it readable, v4 reports the disagreement and drops the look-alike rule's name.

## What this does not test

A monitor that knows less than the kernel (an unknown generative model), or one that sees several outputs from the
same window history. Both are different questions. Bergna et al. (2026) cover the first in general.
