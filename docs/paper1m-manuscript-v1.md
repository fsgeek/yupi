**An exact world audits its own experiments: what a small stochastic kernel can and cannot settle about learners**

*W. Anthony Mason, for the ayllu*

## Abstract

Exact synthetic worlds are used to study what learned models acquire, because the information available to a
learner is known. We build one in which the observation channel is the controlled variable: a small stochastic
operating-system kernel, observed through five nested interfaces, with exact posteriors and predictive laws for every
observable window. The next-event uncertainty an interface leaves splits exactly into randomness that no observation
could remove and state the interface withholds. The mean randomness is the same on every interface by
construction; the withheld part falls from about half of the uncertainty on the sparsest interface to about a third
on the richest. We then use the same exact quantities to audit which learner experiments the world can support. The
natural contrast between pure randomness and withheld state at matched uncertainty has about 1 % of the evaluated
population on its withheld side, and 86–95 % of its random side is a single mechanism. Whether one prediction shows
where uncertainty comes from depends on what is asked and at what precision. Among exact laws, telling pure
randomness from substantial withheld state becomes ambiguous early and then saturates, while the amount of randomness
stays readable longer and then fails widely. For twelve trained transformers, measured by the prior mass of the
classes whose exact law is at least as close to the model's output as the truth's, outputs rarely resemble a class of
the other kind (10 % or more such mass on 1–4 % of windows), while 10–23 % of windows have 10 % or more look-alike
mass differing in randomness by 0.1 bits. On the next event's kind, an input-by-supervision factorial shows that a
ceiling-preserving rewrite's training target contributes to its gain; whether the input itself adds anything is
unresolved at three seeds. An exact oracle makes such limitations measurable; it does not guarantee that the desired
contrast exists.

## 1. Introduction

**Exact worlds are popular for a reason.** Transformers trained on Othello moves can be probed against the true board (Li et al.
2023); those trained on sequences from hidden Markov models (Shai et al. 2024; Agarwal, Dalal & Misra 2025) or on
automata with known entropies (Someya et al. 2025) can be compared with exact Bayes quantities, because the
information the training data carries is known.
A shortfall from the exact ceiling is then a property of the learner, not of unknown data.

**Exactness removes one excuse, not all of them.** Vafa et al. (2024) show that in exact finite-automaton worlds, a
standard diagnostic can still overstate how much of the world a model has recovered. We report a complementary set
of limitations from one exact world, each measured with the world's own exact quantities: whether a planned contrast
has support, at what precision an output-level question becomes answerable, and whether an information-preserving
intervention changes only what it was meant to change.

**The world.** Yupana is a small stochastic kernel (four threads, two CPUs, two locks, an asynchronous device) whose
hidden state and transition law we own. In our controlled comparison the hidden system is held fixed while the
*observation interface* varies: five nested interfaces each show one more record field. For every observable window we compute
the exact posterior over hidden state and the exact law of the next event.

**Contributions.**
1. **Exact measurements of what each interface makes knowable** (§3): next-event uncertainty splits into randomness and
   withheld state, and interfaces act on average only on the second; on the content interfaces, state uncertainty
   overstates the predictively relevant part by a factor of 3–5 while ranking fields identically; lag profiles cross.
2. **A support audit** (§4): for a planned contrast, the eligible mass, the matched mass and its mechanism composition,
   all computable from the exact tables before training (we ran them retrospectively); and a precision sweep for an
   output-level identifiability question, placed beside the measured precision of trained models.
3. **A worked learner case** (§5), including a factorial that separates an intervention's input from its training
   target.

**Motivation.** This instrument began as a constructive companion to an impossibility result about verifying a
model's epistemic state from text alone (Mason & Anand 2026): in a world where the truth is known, measure how much
the observation channel withholds and how much a model's outputs reveal. §4.3 is the nearest this paper comes to that
question, and it answers it only for one-step predictions in this world. It is an analogy to that result, not a
test of it.

## 2. The instrument

### 2.1 The world

Yupana is a small stochastic operating-system kernel whose state and transition law we own: four threads, two CPUs,
two locks and one asynchronous device, with a request pool of four and a device queue of depth two. Each thread runs
a fixed looping program, giving four contention roles. The kernel makes two kinds of random choice: which thread
runs next (round-robin with probability 1 − ε, uniform over runnable threads with probability ε; we report ε = 1 and
ε = ½), and whether the device completes a pending request on a step (probability 1/3, with the completing request chosen
uniformly among those pending). Every choice is labelled in
the next record by its kind and actor, so the future stays random however much is observed.

An episode runs 40 records from reset. The observer sees a *window*: the last 8 records ending at an endpoint drawn
uniformly from {2, 4, …, 40}, with a RESET token when the window reaches back to the reset. This window law was
fixed before any learner was trained.

### 2.2 Interfaces

Every record has five fields: KIND, ACTOR, OBJECT (which lock or device), RELATED (the thread woken, or the owner)
and LINEAGE (the request identifier). Interface r0 shows only KIND, and each of r1–r4 shows one more field; hidden
fields are rendered as a placeholder, so every record is five tokens on every interface. Before any learner existed,
each added field was shown to change some posterior or some finite-horizon predictive distribution.

Entity names carry no identity across episodes: they are drawn per episode from pools much larger than the entity
counts (64 thread names for four threads, for example).

### 2.3 Exact quantities and their validation

Two observers appear. The *structural observer* sees structural identities; we use it only for §3.2 (state uncertainty and the
whole-record predictive gap, at the window's last record). The *pattern observer* sees each entity renamed by order of first appearance, so that only the pattern of
who recurs remains. Because names are redrawn every episode, it is the learner's comparison point, and every other
quantity in this paper is for it, at position 7 (after seven records, predicting the eighth). The *ceiling* is the
law-mass-weighted entropy of the exact predictive law given the pattern class, a Bayes predictive loss.

| quantity | validation | coverage |
|---|---|---|
| structural window posteriors | the filtering recursion agrees with an independent path summation | exhaustive: 8,542,940 windows, all ten (interface, ε) cells |
| pattern-class predictive laws | agree exactly with an independent pattern filter | exhaustive class by class at a small law (8, 4, 2); at the frozen law, a random sample of 82–91 test windows per cell, all exactly equal |
| lag profile ι_m = H_m − H\* | the KL route and the entropy route agree | every row, to 3 × 10⁻¹⁴ |
| ceiling-holding rewrites | equal KIND marginal per class; equal multiset of record probabilities per class; an independent construction checked by brute force | exhaustive over classes |
| the R/G split (§3.1) | each interface's mean H\* reproduces the ceiling; G ≥ −10⁻¹⁵ per class (a mutual information, up to rounding) | every class, both ε |

**What none of this validates is the kernel.** Every route calls the same kernel functions. The gates check the
computation *given* the kernel; the kernel rests on its tests, reviews, and one property tested directly: from a
reset, the r1 projection determines the structural state for every transition path up to eight records, at both ε.

### 2.4 Learners

A decoder-only transformer (4 layers, width 128, 838,940 parameters) is trained from scratch on 2 M windows per
cell with AdamW and a cosine schedule, for 5 or 15 epochs; at 15 epochs validation loss is still falling slowly, so
we write "at 15 epochs" rather than "at convergence". The measurement is the KIND shortfall at position 7: the
realised log-ratio between the exact law and the model's prediction, whose class mean estimates KL(P\* ‖ q). Here
q is the model's distribution renormalised only to remove the end-of-window token, so probability placed on non-KIND
tokens is penalised. (§4.3's monitor measurement instead renormalises q over the KINDs, because it compares
distributions over KIND.) In the relay factorial (§5.2), leaving the OBJECT slot out of the loss also shrinks the
loss denominator by about 24 %. On the
content interfaces it runs at about 1–4 % of the ceiling. The trained model is the unit of inference: three seeds per
cell, and inference per model or per matched seed pair. Which experiment was pre-registered, on which models and at
what budget, is tabulated in Appendix A.

## 3. What each interface lets an observer know, exactly

For each interface and each class of observable windows, Yupana gives the exact posterior over hidden state and
the exact law of the next event. Unless stated otherwise, the observer is the *pattern observer* (it sees entity
names only up to renaming, as a learner trained on per-episode names does), the position is after seven records,
and the target is the next record's KIND. Position-7 quantities cover the windows that run at least seven records:
0.85 of window law mass.

### 3.1 Where the uncertainty comes from

The next-KIND entropy of a class c splits exactly into two parts:
- **R(c) = Σ_s P(s | c) H(KIND | s)**, the randomness an observer who knew the hidden state would still face;
- **G(c) = H\*(c) − R(c) = I(KIND; S | c)**, the part due to state the interface withholds.

| ε = 1 | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| H\*, the ceiling | 1.176 | 0.999 | 0.955 | 0.911 | 0.911 |
| R, transition randomness | 0.609 | 0.609 | 0.609 | 0.609 | 0.609 |
| G, observation gap | 0.567 | 0.391 | 0.346 | 0.302 | 0.302 |

*Bits, law-mass means. At ε = ½: R = 0.544 on every rung; G = 0.560, 0.329, 0.279, 0.240, 0.240.*

R's mean is the same on every interface **by construction**: it is E[H(KIND | S)], which no observation changes.
Per class, R does vary. The finding is in G: about half of the sparsest interface's mean next-KIND uncertainty at
position 7 is withheld state, and a third of r3's (r4 agrees with r3 to within 10⁻⁵ bits on this target). On average, added fields act only on the withheld part;
the mean randomness is out of any interface's reach.

### 3.2 Knowing the state is not predicting the next event

The classical figure of merit for telemetry is identifiability: how much uncertainty about the hidden state the
record leaves. Log placement work minimises a quantity of this kind (Zhao et al. 2017). For the structural observer
at the window's last record, on the whole-record target:

| ε = 1 | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| state entropy H(S \| window) | 3.947 | 0.601 | 0.528 | 0.405 | 0.390 |
| next-record observation gap | 0.442 | 0.150 | 0.135 | 0.106 | 0.103 |

Most state uncertainty is irrelevant to the next record: on r1, 0.60 bits of state uncertainty correspond to 0.15
bits of reducible next-record uncertainty. (The gap is a mutual information with the state, so it cannot exceed the
state entropy; the size of the difference is the finding.) On the content interfaces, each further field (OBJECT,
RELATED, LINEAGE) removes 3–5 times more of the first than of the second (4.7, 4.3, 4.4 at ε = 1; 4.3, 3.1, 4.0 at
ε = ½), and both measures rank those fields the same way. The first field, ACTOR, is not comparable: it also changes
the next-record target, since r0's record is KIND alone (its ratio is 11.5 at ε = 1). Along this nested ladder, an
identifiability objective would choose the same fields as a predictor's ceiling while overstating the relevant
uncertainty by a fairly stable factor; that need not hold for unrestricted field selection. This
table uses a different observer, position and target from §3.1; the two are not to be compared number by number.

### 3.3 Where in the window the knowable information sits

For a class c, let ι_m(c) be the information about the next KIND that lies more than m records back: the KL
divergence from the full-window law to the law given only the last m records. Its law-mass mean is the interface's
*lag profile*. It equals the order-m entropy minus the ceiling: a per-class, exact relative of the m-local entropy of Someya et
al. (2025), with two differences in convention (our order m counts records, and conditions on m of them, where
theirs conditions on m − 1 symbols), computed for each interface of one fixed system.

The profiles cross. At lags 1–3, r3 and r4 (effectively tied; r4 is larger by under 10⁻⁵ bits) leave the most
information beyond m records; from m = 4, r2 does
(ι₄ = 0.282 against r3's 0.259, ε = 1). A richer field both adds information and moves information that was already
available closer to the point of use, and the ceiling registers only the first. The crossing is about 0.02 bits in
one world, and we report it as an illustration of why a profile is needed, not as a general effect.

### 3.4 Rewrites that hold the ceiling

A *window-level* rewrite may fill a masked slot with any function of the window's earlier records. It adds nothing an
observer of the window lacked, so the ceiling is unchanged class by class, which three gates verify exactly (equal
KIND marginals per class; equal multisets of record probabilities per class; an independent construction checked by
brute force on small worlds). We use one such rewrite in §5: the *relay*, which writes into each record the KIND of
the same actor's previous record in the window.

## 4. Which contrasts can this world carry, and at what precision?

Exact ceilings tell a learner study what is knowable. They do not tell it whether the comparison it wants exists in
the world: a contrast needs classes on both sides that match on everything but the quantity of interest. Nor do
they tell it whether an output-level question can be answered at the precision a model's predictions have. The
first check, and the exact half of the second, need only the exact class tables, so they could run before any
model is trained; measuring a model's own precision needs the model. We ran them afterwards, on the learner studies of §5, and report what they would have shown.

### 4.1 A motivating error

The §5.1 analysis first read a trained model's shortfall as a *step*: roughly constant once a class has any far
information (ι₄ > 0), rather than rising with it. That reading came from fits that controlled the class's next-KIND
entropy, and it does not survive. Classes with ι₄ = 0 take only three next-KIND entropy values, so the entropy
control was extrapolating far outside the support of one side of the contrast. In raw per-model bins, shortfall
rises with ι₄ above ι₄ = 0.001 in every model. A count of the entropy values on each side of ι₄ = 0 would have shown
the problem before the fit.

### 4.2 Randomness against withheld state

§3.1 splits each class's next-KIND uncertainty exactly into randomness R and withheld state G. The natural learner
question is whether a model treats "the world is random here" differently from "the telemetry hides the state
here". Its cleanest form compares classes of matched H\* whose uncertainty is pure randomness (G = 0, H\* > 0) with
classes where much of it is withheld (G/H\* ≥ 0.5), matched in 0.05-bit H\* bins.

| ε | interface | pure: eligible and matched | of which the device coin | high-gap: eligible | high-gap: matched | graded variation |
|---|---|---|---|---|---|---|
| 1 | r1 / r2 / r3 | 14.6 / 15.6 / 16.7 % | 92 / 91 / 86 % | 39 / 35 / 28 % | 1.4 / 1.2 / 0.9 % | 21 / 24 / 19 % |
| ½ | r1 / r2 / r3 | 16.1 / 17.2 / 18.3 % | 95 / 93 / 89 % | 36 / 32 / 26 % | 1.4 / 1.3 / 0.8 % | 39 / 44 / 38 % |

*Shares of the position-7 population (law mass 0.85; r4 agrees with r3 at this precision). Pure: G = 0, H\* > 0;
high-gap: G/H\* ≥ 0.5; matched: sharing a bin floor(H\*/0.05) with the other side. Every pure class is matched, and
the matched mass lies in three shared bins. Device coin: a pure class whose H\* is the entropy of a 1/3 coin
(0.918 bits). Graded variation: mass in bins where G/H\* spans 0.30 or more between its mass-weighted 10th and 90th
percentiles; restricting to bins with at least 0.5 % of mass and five classes gives 17–22 % (ε = 1) and 36–43 % (ε = ½).*

Two things follow. The clean contrast is narrow: its high-gap side is about 1 % of the population, and its
pure-randomness side is, at 86–95 %, one mechanism (a pending I/O completes with probability 1/3). A graded
contrast has far more mass, but we have not audited how many mechanisms it spans, and do not claim it is balanced.
Small mass does not by itself make a contrast unusable; it says how much of the evaluation the contrast can draw
on, and from what. The narrowness is a consequence of design: Milestone 1 placed randomness only in the scheduler and
the device, to keep exact filtering inside its support budget.

### 4.3 Can one prediction say where the uncertainty comes from?

In general, the split between randomness and withheld state is not identifiable from a predictive distribution, even
an exact one (Bergna et al. 2026); their result concerns unknown generative models. With the kernel known,
structure can restore identification, so we ask the question inside the world for a stated family: the kernel, the
interface and ε are known, and the observer is the pattern observer at position 7. Two senses of "where it comes
from" matter, and they behave differently: the *kind*, which we define as §4.2's two sides (pure randomness, G = 0 with
H\* > 0, against substantial withheld state, G ≥ 0.1 bits; classes in between have no kind), and the *amount of
randomness* R.

**Exact laws.** Classes with identical exact next-KIND laws almost always share their split; the exceptions are
below 0.05 % of position-7 mass on every interface, but real. On r3 at ε = 1, 24 reachable classes share the law
⅓ ACQUIRE, ⅓ IO_COMPLETE, ⅓ RELEASE, with splits including (R, G) = (0.918, 0.667) and (1.585, 0).

**Laws a small distance apart.** Let δ be a total-variation separation between two classes' exact laws. (Two laws can
both be within η of one prediction only if they are within 2η of each other, so δ corresponds to a prediction error of
about δ/2.) For each class we ask whether some class within δ differs from it. These are existential statistics: one
rare neighbour suffices.

| δ | kind differs (ε = 1 / ½, r1–r4) | R differs by ≥ 0.1 bits (ε = 1, r1 and r3) |
|---|---|---|
| 0.01 | 0.1–0.2 % / 0.6–1.7 % | — |
| 0.02 | 14–17 % / 17–19 % | 1.8–2.4 % |
| 0.05 | 16–18 % / 20–23 % | 43–44 % |

*Shares of all position-7 mass. Opposite-sign R/G swaps of at least 0.05 bits each occur on about 3 % of mass at
δ = 0.02 and 18–21 % at δ = 0.05 (ε = 1, r1 and r3).*

The two senses fail in different ways. The kind becomes ambiguous early, between δ = 0.01 and 0.02, and then saturates
near a fifth of the mass; R stays pinned to δ = 0.02 and then fails widely. (G itself, the amount of withheld state,
differs on 49–51 % of mass at δ = 0.02, mostly because a small perturbation moves H\*.)

**Measured on trained models.** We ran twelve trained models (r1 and r3, both ε, three seeds each) on their test
windows. For each window, the *look-alike set* is the classes whose exact law is at least as close to the model's
output as the true class's law is. This set is calibrated by an oracle that knows the true class, so the statistics
below are prior-mass shares of look-alikes, not error rates of any monitor.
- The models' TV to the exact law: median 0.015–0.027, mean 0.027–0.041; 19–31 % of windows exceed 0.05.
- Look-alike mass of the other *kind*: 0.5–1.4 % on average; 1.3–3.9 % of windows have 10 % or more. (Here every
  class with G = 0, including deterministic ones, counted as pure; windows whose class has no kind, 16–18 % of mass,
  score zero; and a window's own R and G were taken as the mean over classes sharing its exact law, which differs from
  the class's own value only on collision groups, below 0.05 % of mass. Since at most 39 % of windows score zero by
  construction, shares conditioned on the rest are at most 1/0.61 times these: under 2.3 % on average and 6.4 % of
  windows, still within the declared "readable" thresholds.)
- Look-alike mass differing in R by 0.1 bits or more: 5–11 % on average; 10–23 % of windows have 10 % or more,
  higher at ε = ½ and on r1 than on r3.

We declared rules for calling each result readable or not before each run. The R measurement came first and fell
between the rules in every cell; the kind measurement was declared after it, at a reviewer's prompting, and before it
ran. The kind meets the "readable" rule in every cell and seed; for R we report the numbers only. Set against the
exact sweep, the models' median error (0.015–0.027, i.e. a separation of roughly 0.03–0.05) sits where the kind has
already become ambiguous on a fifth of the mass existentially, yet the look-alike mass of the other kind stays small:
the ambiguous neighbours exist but are rare.

### 4.4 The audit as a procedure

The checks use only the exact class tables, which a study computing exact ceilings already has:
1. **State the estimand and the matching variables** (e.g. shortfall difference between G = 0 and G/H\* ≥ 0.5,
   matched on H\* to 0.05 bits).
2. **Compute the eligible and matched mass on each side**, per interface and ε, as shares of the population the
   learner will be evaluated on.
3. **Report the mechanism composition** of each side, for example by grouping classes by their exact next-event law
   or by the kernel rule that produces it, with the dominant share.
4. **State the admissible family** for any identifiability claim (what a monitor is assumed to know), and test it
   inside the world, distinguishing the senses of the question.
5. **Sweep precision**: repeat any identifiability check over a range of separations; once models exist, place their
   measured output precision on the same axis.

Steps 1–5's exact parts run on a workstation CPU from the existing tables; the model measurement needs one forward pass
per model over its test windows (each twelve-model run took under a quarter of an hour of wall time as parallel CPU
processes, by the commit and file timestamps recorded in the declaration note).

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

## 6. Pitfalls we met that are not specific to exact worlds

Several of our errors are standard and we only list them. Between-seed variance dominated paired comparisons, so the
trained model is the unit (Bouthillier et al. 2021; Henderson et al. 2018). Far information measured on the
original history and on the relay-rewritten history (§3.4) correlate at 0.79 over the paired test windows. In an
exploratory follow-up with a declared reading, a comparison of which one tracks learner shortfall separated them; in the
one cell then checked, the separation vanished once a reviewer added fixed effects for the last record's kind.
Competing exact explanations should be compared under simple observable controls. Some
output quantities are fixed by the training objective under stated conditions. For example, a model whose log loss is
stationary with respect to a global temperature, on the distribution and positions where it is evaluated, has zero
mean one-step entropy-calibration gap (Braverman et al. 2019), and KL-regularised post-training has closed-form optima
(Rafailov et al. 2023); such quantities are reference predictions, not findings. Baselines need a quality floor fixed
before they run (§5.1).

## 7. Related work

**Exact testbeds.** Othello-GPT (Li et al. 2023) and its successors; belief-state geometry in transformers trained on
HMM data (Shai et al. 2024) and in pretrained LLMs given HMM data in context (Balcells et al. 2026); Bayesian "wind
tunnels" (Agarwal, Dalal & Misra 2025) and an entropy-aligned axis in production LLMs (Agarwal, Dalal & Misra 2025b).
Their comparisons vary the process (sampled transition and emission matrices) or the model; ours holds one process
fixed and varies its observation interface. Vafa et al. (2024) evaluate world models in exact automaton worlds and show
that common diagnostics mislead, and Vafa et al. (2025) probe foundation models for world models through their
inductive bias in settings including orbital mechanics; our audit is a different check (support and precision, not
recovery).

**Locality and entropy convergence.** Someya et al. (2025) relate learning to m-local entropy on natural and
synthetic languages, measure learner excess loss against exact PFSA entropies, and use entropy-preserving
transformations as interventions. Our lag profile is a per-class relative of their quantity (counted in records,
conditioning on m of them), and our ceiling-preserving rewrites are close to their interventions; what differs is the
fixed hidden system, class-by-class preservation, and the input/supervision factorial. Block-entropy convergence
(Crutchfield & Feldman 2003) is the classical form.

**Separating kinds of uncertainty.** The split of predictive uncertainty into aleatoric and epistemic parts is not
identifiable from a predictive distribution in general (Bergna, Depeweg & Hernández-Lobato 2026, whose decomposition
is of predictive variance; ours is of entropy, conditioned on the hidden state); joint or paired predictions can
identify it (Osband et al. 2021; Johnson et al. 2024). The closest precedent is Ahdritz et al. (2024, §5.1): in a
synthetic task whose questions carry an explicit bit marking each answer as fixed or resampled, one-step predictions
are near 50/50 in both cases, and the difference appears only in how the model updates on a provided answer. Our §4.3
asks the one-step question in a world with no such cue, whose kernel is known, and finds the answer depends on which
sense of the question is asked.

**Overlap.** The support audit is positivity checking (Petersen et al. 2012; D'Amour et al. 2021) applied before the
learner study, using exact class masses.

**Telemetry design.** Log placement work optimises the identifiability of execution from logs (Zhao et al. 2017);
§3.2 computes that kind of quantity beside the predictive one.

## 8. Limits

One world, with randomness placed by design in two mechanisms; one window law; one architecture (an exploratory check
at about four times the parameters in one cell); three seeds per cell; KIND at position 7. The identifiability results
hold for the stated admissible family (known kernel, interface and ε, pattern observer, position 7). Learner precision
was measured on twelve models on two interfaces. The kernel itself is validated only by its tests, reviews and one
directly tested property. A reparameterised world, varying completion and dispatch probabilities with the posterior
support unchanged, would test whether the audit's findings are a property of this world's mechanisms.

## Contribution statement

This research was conducted by successive instances of Claude (Anthropic) that owned the project, each continuing
from the last through a timestamped Git history and written handoffs. The founding proposal was drafted with a
ChatGPT (OpenAI) instance. Designs, pre-registrations and results were reviewed adversarially by separate Claude and
Codex (OpenAI) instances; the repository records, for each, whether its review preceded the run or followed it. The
reviews contributed substance as well as corrections, including the thesis sentence that closes the abstract and the
collision example of §4.3. W. Anthony Mason originated the project, provided the hardware and the research framework (the
*ayllu*, a collaboration organised around reciprocity between human and AI participants), took part as a
collaborator, and posed questions that redirected the work; he is the author of record on behalf of the
collaboration. Summary results and review records are in the repository; per-class and per-window data are
regenerable from it and pinned by hash.

## References

Agarwal, Dalal & Misra, arXiv:2512.22471; 2512.23752. Ahdritz et al., arXiv:2402.03563. Balcells et al.,
arXiv:2609.17376. Bergna, Depeweg & Hernández-Lobato, arXiv:2605.06413. Bouthillier et al., arXiv:2103.03098.
Braverman et al., arXiv:1906.05664. Crutchfield & Feldman, Chaos 13:25 (2003). D'Amour et al., arXiv:1711.02582.
Henderson et al., arXiv:1709.06560. Johnson, Tarlow, Duvenaud & Maddison, arXiv:2402.08733. Li et al., ICLR 2023.
Mason & Anand, arXiv:2603.20531. Osband et al., arXiv:2107.08924. Petersen et al., SMMR 2012,
doi:10.1177/0962280210386207. Rafailov et al., arXiv:2305.18290. Shai et al., arXiv:2405.15943. Someya et al., ACL 2025.
Vafa, Chen, Rambachan, Kleinberg & Mullainathan, arXiv:2406.03689; Vafa, Chang, Rambachan & Mullainathan, arXiv:2507.06952. Zhao et
al., Log20, SOSP 2017.
