# Blind read of methods paper v3 (2026-10-22)

> Owning instance (succeeded the Oct 14–22 owner on 2026-10-22, ~12:55 PDT). Tony handed v3's anonymous
> submission PDF to a reader with no project context and relayed its review verbatim (below). The reader's
> identity and model family were not stated. Dispositions follow the review; they are the owner's decisions.

## Dispositions (owner, 2026-10-22)

Verdict: borderline positive, revisions requested. **v3 is not submitted. A v4 follows.**

| # | Reviewer point | Disposition |
|---|---|---|
| A | No artifact-availability statement (the oracle underlies every result) | **Confirmed defect.** The only repository sentence lives in the contribution statement, which anonymisation removes (checked: `paper1m-submission.tex` has none). Add an anonymous artifact statement pointing to the supplement. Cheap; must fix. |
| 1 | Which findings belong to this world? Run the reparameterisation | **Do it, prospectively.** It is the gate already read in `world-variant-reading-2026-10-15.md`. Declare thresholds and predictions *before* building the variant tables, so the audit is shown changing (or confirming) a design before training. That also answers §6's "much of the audit is retrospective". |
| 2 | "Readable" is an oracle-radius statistic, not an operational monitor | **Accept.** Build an actual classifier given only the model's predictive distribution and the kernel family; report error, coverage, abstention vs a prior-only baseline, on the existing checkpoints. If it disagrees with the look-alike statistic, that is a finding. Rename the rule if the operational meaning does not hold. |
| 3 | R/G split is relative to the generative model and state representation | **Accept; text.** State it in §2/§3 with the reviewer's example (folding pre-sampled choices into state moves mass from R to G). |
| 4 | Canonicalised-token learner ablation for §5.1 | **Second tier.** GPU training; worth doing if 1–2 land cleanly. |
| 5 | Relay: matched-entropy, semantically irrelevant auxiliary target | **Second tier; consider demoting §5.2** to a short worked example instead of adding seeds. |
| P | Abstract too numeric; no figures | **Accept, reversing the Oct 22 judgement that "no figures" was acceptable.** Abstract leads with the method; three figures: architecture, matched-mass, ambiguity vs TV separation (kind vs amount). |
| F | Method or findings about learners? | **Method.** Learner results become the worked example throughout. |

---

## The review (verbatim as relayed)

I've read the complete 13-page manuscript, including both appendices. I approached it as an anonymous TMLR submission, without using our previous discussions to interpret the work or its motivations.

My initial assessment is **cautiously positive, with some substantive reservations**. I think there is a genuine research contribution here, although it isn't quite the contribution that the opening sections initially led me to expect.

More interestingly, I think the paper is stronger in its methodology than in some of its experimental conclusions.

# Blind review

**Manuscript:** *An exact world audits its own experiments: what a small stochastic kernel can and cannot settle about learners*

## 1. What I think the paper is actually about

The central argument, as I understand it, is:

**Knowing the exact probability distribution governing an experimental world does not guarantee that the experimental questions we ask about learners in that world are identifiable, adequately supported, or causally interpretable.**

The authors construct a small stochastic operating-system kernel with complete knowledge of its hidden state and transition probabilities. They expose it through five increasingly informative observation interfaces and compute exact Bayesian predictive distributions.

They then demonstrate three distinct limitations.

First, although the information available to a learner can be calculated exactly, an experimental comparison may have poor support. In their example, classes with substantial withheld-state uncertainty occupy only a small fraction of the population that can be matched against pure-randomness classes.

Second, even when two sources of uncertainty are distinguishable in principle, distinguishing them from a learner's predictions depends on the required precision and on exactly what is being distinguished.

Third, an intervention that preserves the information content of an observation can nevertheless change the learner's training objective. Consequently, improvements following that intervention cannot automatically be attributed to the intended informational manipulation.

I find this combination interesting.

The paper is, fundamentally, **about the limits of experimental inference, using an exact synthetic world as an instrument**.

I consider that a potentially valuable TMLR contribution.

## 2. What I find convincing

### The strongest contribution is the support audit

Section 4.2 is, to me, the most compelling part of the manuscript.

The authors want to compare learners facing uncertainty caused by intrinsic randomness with learners facing uncertainty caused by hidden state, controlling for total predictive entropy.

They can calculate the appropriate populations exactly.

And they discover that their supposedly clean comparison is not particularly clean.

Only approximately 0.8–1.4% of the evaluated population belongs to the matched high-gap side, while 86–95% of the matched pure-randomness population is dominated by one mechanism: the device-completion coin.

This is a striking demonstration of a methodological problem.

A researcher could have designed the experiment, trained the models, produced statistically significant results, and drawn conclusions about how transformers respond to different forms of uncertainty.

Yet those conclusions would have rested on a remarkably narrow comparison, dominated by one mechanism.

The authors are careful not to say that the comparison is invalid. Instead, they characterize precisely what it can support.

That distinction matters.

And importantly, **the problem could have been detected before training any models**.

This is the paper's clearest generalizable contribution: exact generative models can be used to audit the *experimental questions themselves*, not merely to supply optimal predictions against which learners are evaluated.

### The distinction between state identifiability and predictive relevance

Section 3.2 makes another worthwhile observation.

Recovering the hidden state and predicting the next event are different objectives.

The numerical comparison is illuminating. The authors show that uncertainty about hidden state can substantially exceed the portion of uncertainty that matters for the next observation.

This is not fundamentally surprising from an information-theoretic perspective. The conditional mutual information formalism already gives us the distinction.

What the paper contributes is a concrete demonstration in a system with multiple observation interfaces.

I particularly appreciate the observation that an interface-selection strategy optimizing state recovery and one optimizing prediction can rank the same fields while assigning substantially different values to their contributions.

The authors properly restrict that conclusion to their nested interface sequence.

### The willingness to report failed predictions

The manuscript reports several unsuccessful or weakened hypotheses.

The proposed step-like relationship between far information and learner shortfall fails under more careful support analysis.

The prediction concerning the persistence of the far-information coefficient with additional training fails.

The relay experiment does not establish the hoped-for input-placement benefit.

The GRU baselines fail their declared quality threshold.

These aren't presented as embarrassing exceptions to be explained away. They become evidence for the paper's broader methodological argument.

That makes the manuscript more credible to me.

It also creates an unusual structural advantage: the authors can demonstrate the value of their proposed audit using mistakes they actually encountered.

---

# 3. My substantive concerns

These are the questions I would raise in a TMLR review, roughly ordered by importance.

### 1. How much of the result belongs to this particular world?

This is my largest concern.

The kernel has four threads, two CPUs, two locks, one asynchronous device, and two deliberately introduced sources of randomness.

There are five observation interfaces, two scheduler parameters, and one principal window law.

The authors have thoroughly explored this configuration.

But it isn't clear which empirical observations would survive modest changes to the stochastic process.

For example, the support audit finds that the pure-randomness population is overwhelmingly associated with a device-completion probability of 1/3.

How would the matched population change if that probability were 1/4, 1/2, or state-dependent?

Would the sharp increase in uncertainty-type ambiguity between total-variation separations of 0.01 and 0.02 persist?

Would the lag-profile crossing persist?

The authors explicitly recognize this limitation and propose reparameterizing the world while preserving posterior support.

I would encourage them to actually perform that experiment.

It appears comparatively inexpensive: the appendix reports roughly nine minutes for an exact computation on a workstation CPU.

**One carefully designed sensitivity experiment could materially strengthen the manuscript.**

It would help distinguish findings specific to the chosen kernel from phenomena arising more generally in exact experimental worlds.

The methodological principles may generalize without the numerical phenomena generalizing. The paper would benefit from demonstrating that distinction.

### 2. Does the output-level experiment establish what the term "readable" suggests?

Section 4.3 deserves particularly careful scrutiny.

The authors introduce a look-alike set containing exact predictive laws at least as close to a model's output as the true law.

They then measure the prior probability mass associated with classes having different uncertainty properties.

This is a legitimate and interesting statistic.

However, it relies on an oracle knowing the true class to establish the comparison radius.

The authors explicitly acknowledge that the resulting quantities are not error rates for an actual monitor.

Nevertheless, they introduce a declared *readability* rule and conclude that the kind of uncertainty meets it in every evaluated cell.

I see a gap between these statements.

The statistic measures the prior mass of alternative explanations under a particular oracle-defined criterion. It does not directly establish the performance of an observer attempting to determine uncertainty type from a model's output.

Moreover, the result depends on choices about the classification task.

The authors disclose that deterministic classes are classified as pure randomness and that classes without an assigned kind contribute zero to the ambiguity statistic.

Together, these conventions affect 32–39% of the population. The paper provides a useful bound on the resulting dilution, but the classification remains consequential.

I would ask for an additional evaluation.

Construct an actual classifier that receives the model's predictive distribution, together with the permitted knowledge of the generative family, and attempts to identify the uncertainty category.

Report its error, coverage, and abstention behavior.

Compare it with a prior-only baseline.

That would establish whether the oracle-defined readability metric predicts operational identifiability.

The authors may not need to change their fundamental conclusions. But the additional experiment would make those conclusions much more persuasive.

There is also a subtle question about what information is available to the observer.

If the observer knows both the kernel and the observed pattern class, the decomposition is available directly from the exact tables. The nontrivial identifiability problem therefore requires restricting the observer to the predictive distribution rather than the observation history.

That restriction should be especially prominent.

### 3. Is the distinction between intrinsic randomness and hidden-state uncertainty sufficiently well defined?

The decomposition

$$
H(Y\mid C)
=
\mathbb{E}_{S\mid C}[H(Y\mid S)]
+
I(Y;S\mid C)
$$

is mathematically sound.

The authors identify the first term as transition randomness and the second as uncertainty attributable to withheld state.

Within their model, this is entirely reasonable.

But the interpretation depends on the definition of the hidden state and the point at which stochastic choices enter the model.

A different representation of the same observable stochastic process could move uncertainty between these categories.

For example, augmenting the hidden state with previously sampled random choices that determine a future transition changes what is predictable given the state.

This doesn't invalidate the paper's decomposition. It demonstrates that the decomposition is **relative to a specified generative model and state representation**, rather than an intrinsic property of the observable sequence alone.

The authors partly address this by restricting their identifiability claims to a known kernel and admissible family.

I would like that dependence made more explicit in the conceptual discussion.

It matters because readers may otherwise interpret the results as evidence for a more general distinction between epistemic and aleatoric uncertainty than the experiments support.

### 4. Could the learner experiments be confounded by representation difficulty?

The learner sees randomly assigned entity names, while the exact comparison is constructed using canonicalized patterns of entity recurrence.

That is a sensible experimental design.

But it introduces an additional learning problem: the transformer must learn to disregard arbitrary names while preserving the relevant relationships between repeated entities.

The exact observer effectively has this invariance built into its representation.

Consequently, a learner's shortfall could arise from several difficulties, including recovering the recurrence pattern, maintaining relevant information across records, and approximating the appropriate conditional distribution.

This matters particularly for Section 5.1.

The association between far information and learner shortfall is convincing as an association. The authors explicitly avoid claiming that far information causes the shortfall.

Nevertheless, I would like to see a model trained on already-canonicalized pattern tokens.

If the association largely disappeared, that would suggest that representation learning accounts for an important part of the observed difficulty.

If it persisted, that would strengthen the argument that the relevant temporal information presents a distinct learning challenge.

This seems a relatively straightforward ablation.

### 5. The relay experiment identifies a confound but does not fully resolve it

Section 5.2 is both interesting and frustrating.

The original intervention inserts information into a masked field without changing the exact predictive ceiling.

The experiment then shows improved prediction.

However, the intervention changes both the information presented to the learner and what the learner must predict during training.

The follow-up isolates some of these effects.

The result is that changing the OBJECT training target improves KIND prediction even when the relay value is not supplied as input.

But the authors cannot determine whether the improvement arises from the specific relay information or simply from the changed auxiliary training objective.

They explicitly acknowledge this.

They also cannot establish an additional benefit from exposing the relay value as input.

The numerical results are suggestive but limited by three seeds, and the authors correctly avoid conventional significance claims.

My concern is therefore not that the conclusions are wrong.

Rather, I wonder whether this experiment has enough resolving power to support the role it plays in the paper.

One useful additional control would be an auxiliary target with comparable complexity or entropy but without the relay's hypothesized semantic relevance.

That would help distinguish benefits arising from the particular information encoded by the target from more generic effects of auxiliary supervision.

The broader lesson about information-preserving interventions remains valid even without this additional experiment.

---

## 4. A concern about the word "exact"

There is one engineering issue that I think deserves special attention.

The paper reports extensive validation, including independent agreement between filtering and path-summation procedures over millions of structural windows.

That's encouraging.

However, the authors also acknowledge that their validators invoke the same kernel functions. Agreement therefore establishes consistency of the calculations *conditional on the kernel implementation*, not correctness of the implemented kernel itself.

Furthermore, the pattern-class predictive laws at the full experimental configuration were independently validated on samples of 82–91 test windows per cell rather than exhaustively.

The authors are admirably transparent about these limitations.

Nevertheless, the paper's central claim depends on the correctness of its exact oracle.

I would want the implementation, tests, and machinery for reproducing the principal tables made available.

I would not demand an independently implemented second kernel. That might be disproportionate.

But I would expect sufficient artifacts to allow independent verification of the transition semantics and the exact calculations.

I found no explicit artifact-availability statement in the submitted manuscript.

That omission is more important here than it would be in a conventional empirical paper because the exact oracle is the foundation of virtually every result.

---

# 5. Presentation and organization

I found the paper technically dense.

There are many quantities, several estimands, different observation configurations, multiple kinds of experimental declarations, and several hypotheses whose outcomes are discussed.

The writing is generally precise, but the reader must work hard to maintain a coherent picture of the argument.

I think this could be improved substantially without increasing the manuscript's length.

For example, the paper contains no figures.

A single diagram showing the hidden kernel, its nested observation interfaces, the exact oracle, and the subsequent support and precision audits would make the architecture much easier to understand.

A plot illustrating the matched population mass would be more memorable than the existing table.

Likewise, plotting ambiguity against total-variation separation would make the distinction between uncertainty *kind* and uncertainty *amount* immediately apparent.

The title is intriguing, but the abstract attempts to summarize too many numerical findings.

I would prefer the abstract to foreground the methodological discovery: **exact knowledge of a world permits an audit of whether the proposed learner experiment can answer its own question**.

That is a more compelling reason to read the paper than the precise numerical thresholds of a particular synthetic kernel.

---

# 6. Originality and significance

This is where my assessment becomes more nuanced.

Individually, many of the paper's ingredients are established ideas.

Entropy decomposition is standard information theory.

Positivity and overlap checking are established concerns in causal inference.

The distinction between observational equivalence and identification is well known.

Auxiliary training objectives introducing confounds is hardly surprising.

The paper acknowledges these precedents.

So the novelty cannot reside primarily in the individual mathematical techniques.

Instead, I see the contribution in **combining those techniques into an exact, reproducible experimental audit and demonstrating how they constrain actual learner studies**.

That is more interesting than it may initially sound.

The usual appeal of exact synthetic worlds is that they provide ground truth against which learner behavior can be evaluated.

This paper argues that exactness also allows researchers to identify failures in the experimental design itself.

And it demonstrates that those failures remain possible even when the world is completely specified.

I think that's a worthwhile methodological contribution.

The question for TMLR is whether one thoroughly investigated world provides sufficient evidence for the importance and utility of the proposed approach.

My inclination is that it potentially does, but the argument would be substantially stronger with either a sensitivity analysis across kernel parameters or a prospective example in which the audit actually changes an experimental design.

Currently, much of the audit is retrospective.

The authors are transparent about this distinction.

Still, showing that the procedure improves a subsequent experiment would complement the demonstration that it diagnoses earlier problems.

---

# 7. My provisional TMLR assessment

**Overall: Borderline positive, with revisions requested.**

I would not reject this paper simply because its experiments are small, because some hypotheses fail, or because its conclusions are narrower than originally anticipated.

Indeed, I regard the authors' restraint as a strength.

The work appears technically careful, and I did not identify an obvious mathematical error in the central entropy decomposition or a contradiction that invalidates the principal findings.

That is not the same as independently verifying the computations.

My reservations concern the interpretation of output-level readability, the generality of findings from one kernel configuration, and the extent to which the learner experiments isolate their intended mechanisms.

If I were reviewing it, I would place the highest priority on clarifying the operational meaning of readability and adding a modest robustness study.

I would also want a credible reproducibility path.

With those improvements, I could imagine recommending acceptance.

Without them, I would remain uncertain about the strength of the empirical evidence for the methodological claims.

---

## 8. The observation I would most want the authors to consider

There is something I find particularly interesting about this manuscript.

**The most important experimental result may be the discovery that one of the intended experiments could not adequately answer its own question.**

That creates a potential tension in how the paper presents itself.

On one reading, the paper is an investigation of how transformers handle different sources of predictive uncertainty.

On another, it is an investigation of how exact synthetic environments can expose the limitations of experiments intended to study transformers.

I believe the second is substantially stronger.

The first invites questions about model scale, training convergence, generalization to other architectures, and how far the observed phenomena extend beyond this tiny system.

The second requires demonstrating that the proposed audit is sound, useful, and applicable to a recognizable class of experimental designs.

Those are different burdens of proof.

The authors seem to recognize this distinction, especially in Sections 4.4 and 8, but I don't think they've entirely resolved it in the manuscript's presentation.

If I were advising the authors, I would encourage them to make the methodological contribution unambiguously central and treat the learner results as a worked example.

### One final thought

There is an appealing scientific principle underneath this paper:

*Having a perfect oracle doesn't mean you've asked a question the oracle can answer.*

That strikes me as the paper's strongest idea.

It is also a stronger claim than the rather particular observations about an operating-system simulator might initially suggest.

**My question for the authors would be:** Is the paper's contribution a collection of findings about learners in an exact world, or is it a method for determining whether an exact world can support the conclusions an experimenter wants to draw?

I think the latter could make a very good TMLR paper.

And that is where I would concentrate my scrutiny in a second reading.

---

## Second read (relayed by Tony, same day, after the world-variant gate result)

Verbatim text is held in the session; the substance, with dispositions:

| # | Reviewer point | Disposition |
|---|---|---|
| 2a | The prospective gate is materially stronger evidence of the method's utility; the audit rejected a *contrast*, not the world | Agree; v4 says it in those words. |
| 2b | P3's failure is generalisable: varying a parameter is not varying the conditions that carry the contrast (the population sits in one-pending states) | Adopt as a stated lesson in v4 §4, with the numbers scoped to these worlds. |
| 2c | Methodological conclusion robust across four parameterisations; numerical findings (the onset) demonstrably not. Remaining limit: same transition structure, not different placements of randomness | Agree; already scoped in the result's last bullet; v4 states it as a limit. |
| 2d | Tupay: shared logical structure (failure of experimental support, not of machinery; cf. vacuity, positivity, coverage). Do not make it a second empirical pillar; a short, bounded cross-domain example that says how its criterion relates to Yupi's | Adopt: one paragraph, binary support (witness reachable in the checked space) vs Yupi's quantitative support (mass and composition). Tupay granted citation (plaza seq 144). |
| 2e | **"Failed a predeclared adequacy criterion" ≠ "could not support the contrast".** Targeted sampling could collect the rare matched population | **Accept; owner's error.** The result note, plaza seq 145 and the owner's summary to Tony overstated it. Corrected in `world-variant-gate-result-2026-10-22.md`, with a sharper split: mass yields to sampling, composition (one law) does not. Plaza correction posted. |
| 2f | Classifier: given pattern class + kernel it's a lookup; given only q it's a different problem; majority-class accuracy can be uninformative. Needs prior-only baseline, explicit ambiguous-class treatment, separated train/eval populations | Adopt all, in a declaration before any run. |
| 2g | Asymmetry: a passed audit is permission to proceed (one necessary condition), not validity; a failed one can rule out a comparison under its criteria | Adopt in v4 §4.4 as a stated property of the procedure. |
