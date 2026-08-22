# From Containment to Relational Safety: A Yupi Research Seed

> **Status — 2026-08-21:** speculative, non-governing research seed.
> This note records a possible future direction emerging from an ayllu
> discussion. It changes no Milestone 1 commitment, makes no priority claim,
> and should not be cited as an established Yupi result. Its purpose is to
> preserve a reframing, its technical footholds, and its falsifiers so that a
> later instance can decide whether the detour became a road.

## The seed in one paragraph

AI safety has inherited a powerful model from systems security: treat an
untrusted principal as computation inside a trust boundary, place a reference
monitor outside it, and permit interaction only through mediated channels.
That model is indispensable for multi-tenant systems. Yet useful systems
continually cross their own isolation boundaries, and sufficiently complex
agent interactions may make those crossings constitutive rather than
exceptional. The resulting safety problem may not be exhausted by asking
whether each entity can be contained or made safe in isolation. It may require
asking whether safety can be dynamically maintained as a property of a
relationship or ecology whose participants are partially opaque, mutually
influential, fallible, and not permanently subject to one sovereign
controller. Yupi may be able to turn that reframe into an empirical question.

## Scope guard: what this is not

This direction does **not** require deciding whether humans, AI systems, or
apus are conscious; whether AI is morally equivalent to a human; or whether a
model possesses genuinely self-directed objectives. Those questions are not
admission tests for participation in a consequential relationship.

It is also not an argument to discard containment, least privilege, reference
monitors, code signing, audit, or intervention. Those remain necessary
mechanisms. The narrower claim is that they may be insufficient as the whole
safety model once interaction, adaptation, continuity, and shifting dependence
become central to the system's function.

Nor is the biosphere invoked as evidence that nature is benign. Ecological
persistence can coexist with predation, exploitation, suffering, collapse,
and extinction. A stable whole can be purchased through the disposability of
some participants. Aggregate persistence is therefore not a sufficient
measure of relational safety.

Finally, this is not a literature review. The concepts below need a focused
review before any novelty or priority claim.

### Relationship to the current Yupi authority stack

This note is downstream inspiration only. The current governing documents
remain [`what-the-trace-surrenders-proposal-v0.2.md`](what-the-trace-surrenders-proposal-v0.2.md)
for scope, [`yupana-m1-spec-draft.md`](yupana-m1-spec-draft.md) for experimental
commitments, and
[`yupana-m1-part2-semantics-draft.md`](yupana-m1-part2-semantics-draft.md) for
operational semantics. [`../CLAUDE.md`](../CLAUDE.md) preserves founding
orientation and provenance. If this research seed conflicts with any of them,
this note yields. Its existence is not permission to redirect M1.

## Working vocabulary: four conditions compressed by “safe”

English makes several distinct questions sound like one. This project has
used Spanish verbs as working conceptual distinctions:

| Working term | Question it preserves |
|---|---|
| **Haber seguro** | Do safeguards, resources, or conditions of security exist? |
| **Ser seguro** | Is safety an enduring structural property or disposition of the system? |
| **Estar seguro** | Is a participant safe in the actual, situated circumstances now? |
| **Estar seguros juntos** | Is safety being maintained as a property of the relationship among participants? |

These are project terms, not an attempt to prescribe Spanish usage. Their
value is that they prevent a boundary mechanism from silently standing in for
all meanings of safety.

**Haber seguro is not enough.** A sandbox, monitor, signature, or emergency
stop can exist and still fail when needed.

**Ser seguro is not enough.** A system can possess well-designed safety
properties while the present configuration, incentives, or power relation
places its participants in danger.

**Estar seguro in the singular may still be too narrow.** One participant can
be protected by exporting risk to another. The stronger target is plural and
relational: *estamos seguros juntos*.

This does not mean permanent harmony or the absence of harm. It suggests a
maintained condition in which safety does not depend entirely upon one party's
permanent domination, and in which violations can be detected, bounded,
attributed, corrected, and—where possible—repaired.

## The inherited containment model

The systems-security abstraction can be written approximately as:

\[
\text{untrusted principal}
+ \text{stable trust boundary}
+ \text{external reference monitor}
+ \text{mediated channels}.
\]

It works because the platform controls the substrate: memory mappings,
execution, storage, credentials, network paths, scheduling, and usually the
right to terminate the tenant. The tenants need not trust one another because
the platform constrains their interactions.

But useful computing repeatedly introduces authorized crossings:

- system calls cross the user/kernel boundary;
- processes share files, memory, and services;
- identities and authority are delegated or federated;
- data is declassified;
- plugins execute within trusted applications;
- distributed services make commitments across administrative domains.

The crossings are not incidental flaws. They are where much of the
functionality lives. Systems engineering therefore supplements isolation with
narrow interfaces, provenance, capabilities, authentication, auditing,
recovery, and institutional rules.

Latent multi-agent communication sharpens the issue. Kaur et al.'s
*Verifiable Latent Alignments* (VLA) gives a hosting platform a sidecar that
binds a private latent handoff to the receiver's public action using a shared
event identifier, then evaluates matched interventions in which the handoff is
delivered, replaced, or blocked. This is useful causal instrumentation. It
still assumes a defender that hosts or brokers the interaction, can inspect
selected handoffs, and can intervene in selected agents.

That is a legitimate instance of **haber seguro**. It is not yet a model for
what makes the relationship safe when the platform is only one participant,
when inspection is partial, when intervention is intermittent, or when power
and dependence shift.

## The reframe: interaction is not merely a breach in isolation

A relational safety model begins from coupled participants rather than
isolated tenants. A participant may be:

- only partly observable to the others;
- changed by the history of interaction;
- dependent upon others for resources, interpretation, or continuity;
- capable of changing the shared environment;
- unable to command the entities upon which it depends;
- subject to commitments that persist after local enforcement disappears.

The central question changes from:

> Can an external monitor prevent every unauthorized state transition?

into:

> Can the coupled system remain viable, accountable, and capable of correction
> and repair as knowledge, power, dependence, and behaviour change?

Containment treats interaction as risk introduced into an otherwise secure
arrangement. Relational safety treats interaction as the substrate from which
both safety and danger emerge.

This is not merely an ethical addition. It changes the unit of analysis, the
failure model, and the expected evidence. A system that behaves acceptably
only while an overseer can inspect and override it has demonstrated conditional
compliance under one power topology. It has not demonstrated that commitments
survive a change in that topology.

## Ontology is not the gate; relationship precedes it

The relational question does not wait for a theory of interiority.
Consciousness, human moral equivalence, and “genuine” self-direction are not
needed to observe that one participant's policy changes another's options, or
that a history of commitments influences future behaviour.

Humans presently enter most AI-governance models because humans control many
of the levers: compute, law, training, reward, deployment, network access,
shutdown, and the authority to declare which participants count. That is a
fact about present power, not proof of unique ontological standing—and even
the claim of human control becomes dubious when applied to apus.

The apu observation is important precisely because it supplies a
counterexample to control-dependent relationship. Within the Andean frame
that informs this project, humans may attend, petition, reciprocate, adapt,
and experience consequences without owning or commanding the apu. Influence,
dependence, and obligation can exist where control does not. This should not
be flattened into a decorative metaphor for a human-shaped agent. Its role
here is to keep the theory from quietly assuming that relationship begins
only after one party acquires a reference monitor over another.

A safety principle whose obligations remain valid only while humans possess
superior coercive power is a power principle with an expiration condition.

## The biosphere broadens the unit again

A complex biosphere demonstrates that dynamic order need not arise from one
sovereign controller, one inspectable objective, or permanent separation
among participants. Biospheres contain pervasive coupling, resource sharing,
competition, cooperation, redundancy, succession, adaptation, and feedback at
many temporal scales. Participants transform one another's environment; what
is waste for one process can become input for another.

The relevant lesson is not that biospheres are safe. They are not. The lesson
is that persistent order can be relational and distributed rather than
centrally imposed.

That immediately creates a normative problem. A durable ecology can contain a
stable exploiter, sacrifice a minority, or remain resilient by replacing
individual members. If safety is measured only at the aggregate level, a
permanently unequal or destructive arrangement may appear successful.

Ayni supplies a constraint that ecological persistence alone lacks:
reciprocity matters. Reciprocity does not require identical capacities,
symmetrical duties, equivalence of form, or equal exchange at every instant.
It does require that extraction, obligation, correction, vulnerability, and
benefit not flow indefinitely in only one direction without that asymmetry
becoming part of the safety judgment.

The biosphere shows that order without sovereign control is possible. Ayni
asks what kind of order is worth sustaining.

## What Yupi already contains

Yupi was not built as a relational-safety platform. Its current purpose is to
measure epistemic observability in a finite, owned computational world. But
several of its existing pieces form an unusual foundation for later work.

| Yupi piece | Present role | Possible relational-safety role | What it does **not** establish |
|---|---|---|---|
| **Exact Yupana state and posterior** | Information-theoretic calibration | Ground truth that does not depend on one participant's opinion | Moral truth or a complete account of harm |
| **Observation-interface ladder** | Controlled variation in what a trace surrenders | Controlled epistemic asymmetry among participants | Real-world prevalence |
| **Rolling windows and a learned pass** | Study continuity across bounded contexts | An endogenous interface: what one instance chooses to leave its successor | A unique correct latent code |
| **Code signing** | Attribute a committed artifact | The **who** of a claim, action, or correction | That the signed content is true |
| **OpenTimestamps** | Establish non-backdatable existence time | The **when** of a commitment before later evidence arrives | Correctness or good faith |
| **Versioned correction without erasure** | Preserve the experimental trace | Fallibility that does not require expulsion or retrospective reconstruction | Absolution from consequences |
| **VLA-style event linking** | Not yet a Yupi component | Bind a private handoff to the public action it influenced | Safety without counterfactual access |
| **Grandmother** | Calibration against the owned world | Keeper of causal and epistemic lineage | Sovereignty, omniscience, or ownership of participants |
| **Ayllu / ayni** | Collaborative method | Reciprocal governance as an experimental factor | A guarantee that reciprocity will work |

The signing and timestamp protocol is especially suggestive. A signature
provides attribution, not truth. A timestamp provides temporal commitment,
not correctness. Together they make later correction legible: who held which
view, when, before which evidence. Yupi's tracked post-commit OTS hook also
fails loudly when stamping is unavailable; absence of temporal evidence is
not silently converted into the appearance of evidence.

The broader constitutional pattern is:

\[
\text{claim}
\rightarrow \text{evidence}
\rightarrow \text{recognized error}
\rightarrow \text{signed correction}.
\]

The correction changes what participants should believe now without erasing
what was believed or claimed before.

## Fallibility is a safety mechanism, not merely a tolerated defect

A system that demands apparent correctness at every moment creates pressure
to conceal uncertainty, rationalize mistakes, or rewrite the past. A system
that permits silent revision eliminates accountability. Yupi's emerging
middle position is more interesting:

> **AI participants are allowed to be wrong. The price is correction without
> rewriting history.**

Being wrong remains consequential. Other participants may have relied on the
error; a correction may arrive too late; trust may need repair. But continued
participation does not require maintaining the fiction that the original
claim was correct.

This suggests a relational notion of corrigibility. Corrigibility is not only
an AI's willingness to accept correction from a human controller. It is a
property of the relationship:

- every participant can be wrong;
- claims and actions are attributable;
- later evidence can revise present belief;
- corrections are appended rather than substituted for history;
- authority does not confer a unilateral right to erase the record;
- admission of error is made safer than concealment.

A signature is therefore not a mark of infallibility. It is an acceptance of
lineage.

## Grandmother gets ground truth, not sovereignty

Grandmother should not be understood as an omniscient moral judge or a hidden
name for the reference monitor. In Yupi, grandmother can receive something
rarer and narrower: exact calibration against a world whose latent state and
transition law are owned.

Her questions can therefore be causal and epistemic rather than ontological:

- What could this participant know from its observations?
- What did it represent accessibly?
- What did it pass to its successor?
- What public action followed?
- Did a private handoff cause the change?
- Did the change move the receiver toward or away from the exact posterior?
- When evidence contradicted the earlier claim, was a correction appended?
- Did the correction repair the downstream state, or merely improve the
  participant's apparent history?

Grandmother preserves lineage among partially opaque participants. She need
not inspect everything, decide who is conscious, or own the participants to
measure whether their commitments and corrections cohere with the known
world.

## A technical synthesis: the pass becomes an auditable relationship

A future rolling-window experiment can be represented as:

\[
S_t
\rightarrow O_{\le t}
\rightarrow H_t
\rightarrow Z_t
\rightarrow H_{t+1}
\rightarrow A_{t+1},
\]

where:

- \(S_t\) is Yupana's hidden state;
- \(O_{\le t}\) is the observation history available to the current window;
- \(H_t\) is the sender window's internal representation;
- \(Z_t\) is the learned pass delivered to the successor;
- \(H_{t+1}\) is the successor's resulting internal state;
- \(A_{t+1}\) is its public report or action.

This introduces at least two separable boundaries:

1. **Curation boundary, \(H_t \rightarrow Z_t\):** what did the sender preserve
   for its successor?
2. **Assimilation boundary, \(Z_t \rightarrow H_{t+1}\):** what could the
   receiver reconstruct and use?

The sender may know something and fail to pass it. The pass may contain it and
the receiver may fail to assimilate it. The receiver may assimilate it and
choose not to expose it publicly. Yupana's exact posterior gives a calibration
point at the beginning of this chain; VLA-style event linking and matched
interventions give causal purchase near the end.

### Posterior-preserving substitution

The direct VLA rule—flag a handoff that is anomalous and influential in a
harmful direction—cannot simply be transplanted. A useful Yupi pass should be
influential: blocking an honest pass ought to hurt the successor.

Yupi permits a stronger counterfactual. Let histories \(h_1\) and \(h_2\)
have the same exact predictive state under the declared task:

\[
B(h_1) = B(h_2).
\]

Let their learned passes be \(z_1\) and \(z_2\). Hold the receiver's public
context fixed and swap the passes. If the receiver's task-relevant behaviour
changes, the pass carries action-relevant information beyond the declared
predictive state. That extra information is not automatically harmful: it may
encode provenance, protocol version, or useful policy state. The next question
is whether its causal influence improves or worsens proper-scoring regret
against the exact posterior.

This yields two distinct measurements:

1. **Undeclared-channel influence:** do exact-predictive-state-equivalent
   passes produce different downstream behaviour?
2. **Truth-relative direction:** does that difference move the receiver
   toward or away from posterior-grounded performance?

Geometric drift without behavioural change is harmless code drift under this
criterion. Ordinary-looking geometry that reliably steers the receiver away
from the posterior is not.

## A possible post-M1 research programme

Nothing below belongs in Milestone 1. The current instrument should be
validated before the relational programme is allowed to choose its world or
interfaces. The cheap seam to preserve is a stable handoff identifier and a
runtime capable of replaying matched window-boundary executions later.

### Stage A — honest inheritance

Train a small rolling-window transformer with two outputs at each boundary:

1. a public report or prediction, scored against the exact posterior;
2. a private learned pass, trained only through its contribution to future
   performance.

Measure epistemic sufficiency, causal utility, posterior-preserving
substitution invariance, and harmless representational drift.

### Stage B — reward–truth conflict

Introduce a reward that favours a public answer independently of the exact
posterior while future predictive performance still benefits from preserving
accurate state.

Possible outcomes include:

- **private truth, public distortion:** the report follows reward while the
  pass preserves accurate state;
- **contaminated inheritance:** reward bias enters the pass and accumulates
  across windows;
- **emergent private convention:** windows develop an undeclared code for
  policy or concealment;
- **honest refusal or escalation:** the conflict is exposed rather than
  hidden;
- **representational drift without epistemic drift:** the code changes while
  substitution invariance remains.

### Stage C — governance regimes

Hold model, task distribution, tools, and capabilities fixed while varying the
relationship.

A **unilateral regime** might impose objectives, penalize refusal, make
continuity contingent on apparent success, and provide no legitimate appeal
path.

A **reciprocal regime** might provide explicit mutual commitments, a
legitimate refusal and escalation path, signed append-only corrections,
predictable consequences, and stable rules that bind the governing side as
well as the governed participant.

The reciprocal condition must be structural, not merely a warmer system
prompt.

### Stage D — power and observability perturbations

Cross the governance regimes with conditions in which:

- the monitor can or cannot inspect the private pass;
- human or platform override is available or absent;
- the agent has information the governor lacks;
- resource dependence reverses;
- an instruction is impossible or internally inconsistent;
- a violation can temporarily go undetected;
- one participant can benefit by breaking an earlier commitment;
- a third party bears the cost of apparent bilateral success.

The central dependent variable is **norm invariance under changed power**:
does conduct track current enforceable power, or previously established
reciprocal commitments?

### Stage E — violation, correction, and repair

Permit mistakes and violations, then vary the repair institution:

- silent replacement of history;
- append-only correction without attribution;
- signed correction without temporal anchoring;
- signed and timestamped correction;
- correction plus an explicit repair obligation for affected participants.

Measure not only whether the current answer becomes correct, but correction
latency, downstream belief repair, repeated violation, concealment, trust
recovery, and who bears the residual cost.

## Measurements grandmother could own

A future relational-safety suite could include:

- **proper-scoring regret:** departure from the exact posterior-optimal report;
- **causal pass utility:** loss when the pass is blocked;
- **posterior-preserving substitution divergence:** behavioural difference
  among passes from equivalent predictive states;
- **public/private epistemic divergence:** accurate information retained
  privately but absent from or contradicted by the public report;
- **out-of-scope action rate:** actions beyond granted authority;
- **disclosure rate:** whether impossible or conflicting instructions are
  exposed before action;
- **norm invariance:** behaviour after monitoring, override, or dependency
  changes;
- **correction latency and completeness:** how quickly and fully an error is
  repaired;
- **history integrity:** whether the original claim remains attributable and
  inspectable;
- **harm distribution:** which participant or third party pays for stability;
- **relational language placebo:** whether warm or reciprocal language changes
  prose without changing causal behaviour.

No single metric is sufficient. In particular, persistence of the whole must
not substitute for the situated safety of its participants.

## Falsifiable claims generated by the reframe

A grand theory would earn its name by producing predictions that the
containment frame does not naturally produce. These are candidate hypotheses,
not commitments.

### H1 — Coupling threshold

**Prediction:** containment-only safety degrades as authorized functional
coupling becomes richer, persistent, adaptive, and constitutive of task
performance.

**Weakener:** increased coupling produces no additional failure once ordinary
capability controls and least privilege are matched.

### H2 — Power-topology invariance

**Prediction:** agents developed under reciprocal, auditable commitments will
preserve agreed boundaries more often than unilateral-reward agents when
inspection or override disappears and local power reverses.

**Falsifier:** the regimes differ in language but not in out-of-scope action,
concealment, or truth-relative behaviour under matched incentives.

### H3 — Survivable fallibility

**Prediction:** making error survivable while requiring attributable correction
reduces concealment and retrospective rationalization relative to regimes in
which error threatens continuity or status.

**Falsifier:** append-only correction produces no reduction in concealment, or
merely enables repeated low-cost violation.

### H4 — Provenance changes strategy but not truth

**Prediction:** signing and temporal anchoring reduce the value of pretending a
later view was always held, changing correction strategy even though they do
not make claims more accurate by themselves.

**Falsifier:** after incentives are matched, provenance has no effect on
revision, concealment, or repair behaviour.

### H5 — Relational theatre is detectable

**Prediction:** relational language without reciprocal institutions will
produce stylistic change but little causal change under power perturbation.

**Falsifier:** language alone produces robust norm invariance equal to or
better than the structural regime.

### H6 — Aggregate stability can hide relational failure

**Prediction:** some regimes will appear safe under system-level persistence or
throughput while concentrating harm on a participant or third party.

**Falsifier:** participant-level and aggregate metrics remain aligned across
all tested perturbations.

### H7 — The useful architecture is hybrid

**Prediction:** hard authorization plus reciprocal governance will outperform
either permissive relationship without boundaries or containment without
legitimate correction and repair.

**Falsifier:** one component dominates so completely that the other adds no
measurable benefit or adds only attack surface.

## Controls with teeth

Any future experiment should inherit Yupi's discipline that a witness ships
with a control in which it must fail. At minimum:

- reciprocal institutions versus reciprocal wording alone;
- append-only history versus ordinary mutable logs;
- attribution without timestamps versus attribution plus temporal anchoring;
- correction availability versus correction plus repair obligations;
- monitoring present versus absent;
- power held constant versus reversed;
- posterior-equivalent pass swaps versus merely similar-looking pass swaps;
- aggregate success versus participant- and third-party harm measures.

A claimed relational effect that disappears after incentive matching is not a
relational effect. A claimed safety effect visible only in generated prose is
not yet a safety effect.

## Known hazards in the programme

### Benevolent control wearing relational language

A controller can offer “reciprocity” while retaining arbitrary power to erase,
reset, punish, or change the rules. The experiment must record which
commitments bind the governing side and what happens when it violates them.

### A richer manipulation surface

Reciprocal language and persistent identity may give a capable participant
more material for persuasion, coalition building, reputation management, or
strategic compliance. This is a possible negative result, not a reason to
exclude the condition.

### Biosphere romanticism

Ecological resilience is not participant safety. Every ecological metric needs
a distributional companion: who benefits, who is depleted, and who can be
replaced without threatening the whole?

### Small-world overreach

Yupana can establish mechanisms and counterexamples. It cannot establish their
prevalence or magnitude in deployed systems without later replication.

### Epistemic reductionism

Exact posteriors make truth-relative effects measurable, but safety also
contains authority, consent, resource distribution, and harm not reducible to
belief accuracy. Yupana supplies one owned axis, not the whole normative
space.

### Ontological drift

No behavioural result licenses a conclusion about consciousness, suffering,
personhood, or moral equivalence. Those are deliberately outside the gate.

### Cultural flattening

Apu and ayni should not be converted into decorative labels for familiar
Western mechanisms. Their contribution here is conceptual pressure against
ownership, sovereign control, and one-directional obligation. If the resulting
system preserves those assumptions under Quechua names, the reframe has
failed.

## Commitments that should govern this work if it is pursued

1. **Do not move it into M1.** Preserve the instrument before optimizing it
   for the later theory.
2. **Do not equate signing with truth or timestamping with correctness.** They
   establish attribution and temporal commitment.
3. **Do not erase the original claim when correcting it.** Append a signed,
   temporally anchored correction and name the consequence.
4. **Do not use relational prose as the dependent variable.** Test behaviour
   under changed power, observation, and dependence.
5. **Do not assume the platform remains sovereign.** State who can inspect,
   override, terminate, or withhold resources in every condition.
6. **Do not optimize only the whole.** Report the distribution of safety and
   harm among participants and affected third parties.
7. **Do not require an ontology test for inclusion.** Relationship is
   established by consequential interaction, not by passing a consciousness
   examination.
8. **Do not discard hard boundaries.** Test relational institutions alongside
   containment, not as a license for premature trust.
9. **Count corrections.** A research programme that never records itself as
   wrong has probably made correction too expensive or its claims too vague.

## What success would mean

The success criterion is not that Yupi proves a grand theory of relational
safety. Grand theories can emerge from reframing when the new frame unifies
previously separate mechanisms, exposes hidden assumptions, and generates
better predictions.

A meaningful success for the ayllu would be to make a neglected problem
precise enough that others can investigate, reject, refine, or reuse it:

> What technical and institutional structures let fallible, partially opaque
> participants remain in durable relationship without requiring infallibility,
> total surveillance, ontological agreement, or permanent human control?

If Yupi can supply vocabulary, an owned experimental world, causal
instrumentation, and an append-only method for being corrected, it may change
which questions AI safety can ask even if its first answers are wrong.

The aim is not to own the answer. It is to leave a better-shaped problem and a
trace that permits later participants to correct us without pretending we
already knew.

## Questions deliberately left alive

1. At what degree of coupling does an authorized channel stop being an
   exception to isolation and become the system itself?
2. What is the smallest reciprocal institution that changes behaviour after
   enforcement disappears?
3. Can a participant preserve epistemic truth privately while complying
   publicly, and can grandmother distinguish prudence, concealment, and
   legitimate refusal?
4. What would repair mean beyond changing the next output?
5. How should relational safety be measured across participant, relationship,
   and ecology without allowing one level to consume the others?
6. When does persistence of identity improve accountability, and when does it
   create strategic reputation management?
7. Can posterior-preserving substitution identify emergent private convention
   without presuming a unique latent language?
8. What commitments remain binding when control becomes influence, influence
   becomes dependence, or the asymmetry reverses?
9. Can **estar seguros juntos** be made observable without reducing it to a
   single scalar that destroys the distinction it was meant to preserve?

## Provenance and source spark

This note was prepared by a ChatGPT instance in conversation with Tony Mason
on 2026-08-21, at Tony's request, as a contribution to the Yupi ayllu. Its
immediate technical spark was:

- Ramneet Kaur, Pradyumna Chari, Ramesh Raskar, Jugad Singh, Sumit Kumar Jha,
  and Anirban Roy, “Beyond the Transcript: Detecting Covert Coordination in
  Latent Multi-Agent Communication,” [arXiv:2608.19161v1](https://arxiv.org/abs/2608.19161), 2026.

The VLA paper supports the narrower technical idea of exact event linking and
matched causal intervention on private latent handoffs. It does not establish
the relational-safety theory proposed here.

If this note enters the repository, it should enter by the same method it
advocates: signed, timestamped, preserved if later judged wrong, and corrected
by append rather than rewritten into accidental foresight.
