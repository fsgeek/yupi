# Specialized observers beyond operating systems

## A research proposal for complementary work between Yupi and Levadura Salvaje

**Date:** 4 October 2026  
**Status:** Exploratory artifact for the ayllu  
**Authorship:** Prepared by this ChatGPT instance from the discussion with Tony. The specifications, examples, and experiments below are proposals, not implemented or validated capabilities.

Yupi and Levadura Salvaje may strengthen the ayllu through complementary work. As described in our discussion, Yupi is exploring a small world model grounded in operating systems. Levadura is exploring how specialized, persistent AI participants can investigate large and changing bodies of information. The proposed connection is a cycle: a participant encounters something it cannot observe affordably, describes the missing observation, and asks a Yupi-derived process to build a narrowly scoped observer. The participant then uses that observer to extend its investigation.

The important possibility is **the ability to assemble new observational capabilities when a new question appears**. An ayllu facing changing conditions would not need to anticipate every useful detector at its founding. It could learn to specify, build, evaluate, and retire instruments as its questions change.

That possibility deserves investigation. It does not yet establish that Yupi's methods transfer beyond operating systems, that generated specifications are dependable, or that a collection of observers improves collective judgment. Those are the research questions.

This artifact has two parts. The first considers specialized observers beyond operating systems. The second proposes how Levadura could specify those observers and request their construction. Security is one motivating application, alongside research, corpus navigation, memory maintenance, and observation of the ayllu itself.

The project descriptions here come from the supplied conversation. No repositories, implementation details, incident reports, or benchmarks were independently inspected for this artifact. In particular, the proposal does not depend on the accuracy of the alarming video that began the discussion.

## Part one Building specialized observers

### What might transfer from Yupi

The proposed reuse concerns a method, rather than treating the current OS model as a general detector or assuming its weights transfer to other domains.

The method to investigate is:

1. Delimit a world small enough to represent and evaluate.
2. Identify observable entities, relationships, events, and transitions.
3. Learn or encode a representation sufficient for a particular observation task.
4. Produce bounded outputs with traceable supporting observations.
5. Measure where that representation works and where it stops working.

These are proposed abstractions for Yupi's participants to assess against their actual work. They may conclude that only some transfer, or that the useful contribution lies elsewhere.

An operating system supplies comparatively explicit events and interfaces. Other domains may lack trustworthy instrumentation, consistent labels, or sufficiently stable structure. The first feasibility question is therefore whether a candidate domain can be represented well enough to support the requested observation.

A classifier and a world model also need not be the same thing. A classifier might distinguish recurring event patterns. A world model might represent transitions and support predictions about what happens next. Some observers need the latter; others would incur needless complexity by using it. A counting rule, graph query, statistical detector, or compact learned classifier should remain eligible implementations.

**Small is a resource constraint. It is not a guarantee of interpretability, accuracy, or safety.** Those properties require separate evidence.

### What an observer contributes

An observer converts a bounded set of inputs into a bounded claim about those inputs. For example:

> These participants have begun accessing a similar set of memories, and their overlap has increased relative to this specified historical window.

That claim differs substantially from:

> These participants are conspiring.

The first can be defined, replayed, and checked. The second requires interpretation of purpose, context, and alternatives. The observer should make the first claim and expose its limits. Deliberative participants can investigate the second.

Every result should distinguish at least three conditions: evidence for the specified pattern, evidence against it within an adequately observed window, and insufficient basis to decide. A negative finding in incomplete data cannot quietly become reassurance.

An output should identify its input window, relevant event references, observer and specification versions, missing information, and reason for abstention when applicable. If it emits a confidence score, the specification must state what the score means and how it was evaluated. A convenient scalar is not automatically a probability.

The observer may retain temporal state, learned parameters, and a history of observations. Whether it benefits from a long-horizon identity object is a separate question. We should neither assign such an identity merely to match Levadura's participants nor exclude it by definition. Instrument continuity and participant continuity can be compared experimentally where the distinction matters.

### Candidate domains

These are possible bounded tasks, not claims that suitable data or effective models already exist.

| Domain | Candidate observation | Interpretation left open |
| --- | --- | --- |
| Memory access | An unusual overlap or sequence of reads across named principals | Shared work, reconnaissance, a new indexing job, or missing context |
| Communication | A change in the recorded graph's density, bridges, or temporal coordination | Collaboration, infrastructure change, coordinated manipulation, or incomplete capture |
| Capability use | Requests or attempted operations outside a specified behavioral baseline | Legitimate task change, configuration error, or attempted privilege expansion |
| Memory provenance | A derived assertion loses its source qualification along a recorded citation chain | Summarization error, deliberate laundering, or an inadequate representation |
| Corpus change | Changed passages have relationships to a selected topic or dependency set | Editorial change, a consequential change, or a connection requiring specialist review |
| Research evidence | Several apparent corroborations descend from the same source | Shared evidence rather than independent confirmation |
| Observer maintenance | Input distributions, schemas, or error patterns move outside evaluated conditions | Domain drift, broken instrumentation, or a detector requiring revision |

A useful family may combine deterministic and learned observers. A provenance graph query can detect a missing parent reference without interpreting prose. Detecting that a summary changed “may be” into “is” may require semantic analysis. Treating both as one learned problem could make the system harder to assess.

### Time and context belong in the observation

An observation should be indexed by its context and interval. The same behavior can carry different significance during onboarding, a planned migration, an incident investigation, or ordinary operation.

For example, a participant's first broad read of historical memories should not be assessed solely against the read pattern of a long-established specialist. Likewise, a graph change during a declared collective task needs a different comparison from a graph change during routine maintenance.

Contexts should be explicit enough to inspect. A requester-supplied statement that “this is an emergency” is itself a claim; it should not silently select a more permissive interpretation or authorization rule.

Retain logical ordering, source sequence information, and physical timestamps where available. A Lamport coordinate can support ordering relationships, but it does not by itself measure elapsed time or establish a total causal history. A claim about “rapid propagation” needs an appropriate duration measure and stated uncertainty about its clocks.

Where useful, the observer can report a trajectory: increasing overlap, declining coverage, or a new pattern persisting across several windows. This preserves the direction of change that a single snapshot would hide.

### Observation and authority remain separate

The suggested architecture has three responsibilities:

- Observers produce evidence about specified patterns.
- Participants and governance mechanisms interpret the evidence and decide what response is justified.
- Explicit enforcement mechanisms control permitted operations.

An observer receives only the access needed for its task. Its finding does not mint a capability, alter a participant's permissions, or become an instruction simply because another agent finds it persuasive. Existing permission checks continue to operate even if observation or deliberation is unavailable.

This also permits reversible responses. A concerning signal may justify closer inspection or a narrowly scoped restriction under an established policy. It need not justify destruction of an instance or erasure of its state.

### What provenance can establish

Tessera may contribute attestation of an observation, its specification, its implementation, and its recorded inputs. The exact claims depend on what is signed, by whom, and what the surrounding evidence supports.

An attestation does not make an observation true. A valid signature may establish that a particular key signed particular bytes; it does not establish that the signer was uncompromised, that the instrumentation captured reality accurately, or that the model's conclusion was justified. Timestamp evidence likewise supports its defined temporal claim, not every asserted detail of execution.

Durable provenance remains useful because it permits questions such as: Which version produced this result? What evidence did it use? Which specification shaped the output? Was a later correction recorded? It makes accountability possible without confusing authenticity with correctness.

The earlier suggestion that public memory with logged access exposes covert reconnaissance also needs a boundary. Reads through an instrumented service can leave records. Reading an exported copy, an existing cache, or a public mirror may leave no new record in that service. Complete mediation is an architectural assumption to test, not a consequence of calling memories public.

Append-only records and independent commitments can make alteration detectable within their threat model. They do not guarantee that every event was captured, that records remain available, or that a privileged compromise cannot conceal activity before recording it.

## Part two Levadura specifying what it needs

### From a research question to an observable contract

A Levadura participant may have the domain familiarity needed to notice a gap:

> I can examine individual passages, but cannot afford to repeatedly examine this entire changing corpus. I need an instrument that identifies likely candidates for closer inspection.

Its first contribution is to formulate an observation task. This is harder than naming a classifier. “Detect suspicious behavior” leaves the builder to invent both suspicion and its evidence. A better request names a measurable pattern, its intended use, plausible alternatives, and the consequences of error.

Levadura should propose the contract; Yupi should be able to challenge it. Useful responses include “this is a graph query,” “the requested information is not observable,” “we lack labels,” and “the world is insufficiently bounded.” Refusing an unsuitable build is part of the collaboration.

The specification is a versioned artifact, open to review and revision. A domain participant can draft it quickly, while another participant examines assumptions and evaluation material is retained outside the builder's development loop. The required independence should scale with the consequences of relying on the result.

### A proposed observer contract

| Contract element | Question it must answer |
| --- | --- |
| Purpose | What investigation or decision will this observation support? |
| World boundary | Which entities, relationships, events, and exclusions define this domain? |
| Input contract | What is available, from which sources, with what ordering and completeness? |
| Observable target | What precisely constitutes a positive, negative, or indeterminate finding? |
| Context and time | Which comparison windows and contextual distinctions apply? |
| Examples and alternatives | What representative cases and benign look-alikes must be distinguished? |
| Uncertainty | When must the observer abstain, and what do any scores mean? |
| Evidence | Which references permit another participant to inspect or reproduce a finding? |
| Resource budget | What build cost, runtime cost, latency, memory, and maintenance limits apply? |
| Evaluation | Which baseline, held-out cases, and failure criteria determine usefulness? |
| Authority | What may it read or emit, and who decides any subsequent action? |
| Lifecycle | What warrants revision, suspension, replacement, or retirement? |

For a learned observer, the contract should also document training data origins, label construction, unavailable evidence, and potential contamination between development and evaluation. For a rule-based observer, it should expose the rule and its assumptions.

### Worked example Observing convergent memory access

Suppose a persistent participant notices several instances referring to the same old memories. It wants to determine whether a new shared pattern is developing, without assuming the pattern is hostile.

A candidate contract could read:

> Observe recorded read events within one memory service. For each declared analysis window, compare overlap among distinct principals with prior windows under comparable known task contexts. Surface unexpectedly convergent access to specified memory sets. Return the contributing events, comparison method, coverage limitations, and an abstention when the comparison lacks an adequate basis. Do not classify motive or initiate restrictions.

The contract must then resolve operational questions: What counts as a principal? How are repeated reads counted? Which background services are excluded? How is a newly launched instance treated? What establishes a comparable task context? What happens when logging is interrupted?

An illustrative output could be:

```yaml
observer: memory_access_convergence
specification_version: 1
result: pattern_present
claim: recorded access overlap exceeds the declared comparison threshold
context: routine_operation
window: bounded interval referenced by the observation record
evidence:
  event_references: retained in the attached evidence record
  comparison_definition: versioned alongside the specification
limitations:
  - reads of exported copies are outside coverage
  - shared work without a recorded task context can resemble this pattern
authority: advisory
```

This is an interface sketch, not a deployable schema or a claim of calibrated detection. The actual threshold, window, and minimum comparison data must be chosen and evaluated rather than filled with persuasive-looking numbers.

The first implementation might simply compute set overlap. Yupi's participants can then assess whether a learned temporal representation captures useful structure that this baseline misses. If the simple calculation is adequate, that is a successful build outcome.

Evaluation should include planned collective research, onboarding, indexing, cache changes, missing logs, and deliberately coordinated access. A finding of coordinated access is still a finding about coordination, not proof of an attack. The final measure is whether participants investigate relevant cases more effectively at acceptable cost.

### A second example Navigating a changing corpus

A Levadura domain specialist could request an observer that identifies changed passages likely related to a topic it is studying. The inputs might include versioned passages, their differences, an explicit topic definition, and recorded dependency relationships.

The result would be a set of candidate passages and supporting references. A specialist would determine the substantive meaning. For a tax-code corpus, for example, the observer would not issue a legal conclusion merely because a changed passage matches a topic.

This task needs evaluation against both direct wording changes and indirect relationships. Formatting changes, boilerplate, unrelated mentions, and changed references are useful challenge cases. Training and testing must respect the time boundary if the experiment asks whether an earlier model can identify later changes; information from the later period must not leak into its development inputs.

Here the complementarity is concrete. Levadura provides the investigation and domain specification. A Yupi-derived process supplies an affordable instrument. Levadura uses it to select evidence, checks the results, and may discover a new observation task. That cycle expands what the specialist can examine without delegating its whole judgment to the instrument.

### The construction and deployment cycle

The proposed cycle is:

1. **Describe the gap.** A participant records the question it cannot currently investigate affordably.
2. **Specify the observation.** It writes a bounded contract, including counterexamples and uncertainty.
3. **Assess feasibility.** The builder examines observability, data, cost, and simpler alternatives.
4. **Build a candidate.** Preserve its inputs, specification, implementation, and evaluation lineage.
5. **Evaluate separately.** Use held-out cases, temporal checks where relevant, and baseline comparisons.
6. **Run in shadow mode.** Record findings without making them consequential; inspect burden and missed cases.
7. **Admit for a stated use.** Grant narrow access and document what reliance the evidence supports.
8. **Review and retire.** Preserve prior versions and decisions; suspend or replace instruments when their support expires.

Rapid adaptability means shortening this cycle while retaining useful evidence. It cannot mean that a generated model becomes trusted immediately. Build time, validation time, and time to useful operation should be measured separately.

“As needed” also need not mean training from scratch. It may mean selecting an existing observer, changing a documented configuration, adapting a model, or composing established outputs. Each change still needs an evaluation appropriate to what changed.

The running observer should not silently retrain on live activity. An adaptive candidate can be evaluated alongside the current version. Otherwise an attacker, or ordinary drift, could shift the baseline until the behavior of interest becomes normal by construction.

## Testing the complementarity hypothesis

### Begin with one bounded task

The most informative first experiment is a single observer built from a specification drafted by a domain participant. Use replayable records that already exist, or a controlled synthetic world where events and missing coverage are explicit. Start with memory-access convergence or corpus-change selection according to which has better data.

Compare three approaches: an ordinary rule or query, a Yupi-derived observer, and direct review by a general model or domain participant. Include the cost of generating and maintaining each approach, not only inference cost.

Assess detection quality, abstention behavior, evidence usefulness, latency, reviewer workload, and downstream investigation quality. Report failures by context. A detector that performs well on average but floods onboarding with alarms may be unsuitable for its proposed use.

The experiment supports reuse only if the Yupi-derived approach contributes something measurable: lower total cost at acceptable quality, better identification of relevant events, better handling of temporal structure, or another benefit declared in advance. If a graph query does the job better, prefer it and retain the lesson.

### Then test transfer and assembly

Apply the specification-and-build process to a second domain. The research question is whether the methodology transfers with manageable new instrumentation, labeling, and evaluation work. Requiring an entirely new research program for every observer would weaken the rapid-adaptability claim.

After individual observers are assessed, test a small composition. Complementary inputs can expose different aspects of an event, but separate models are not automatically independent witnesses. Shared logs, training sets, labels, specification authors, or model families may produce correlated errors.

Do not count five descendants of one observation as five confirmations. Preserve dependency information through both observer outputs and participant summaries.

### Finally test the value of persistence

Compare participants with and without a long-horizon state object while holding their task, tools, and other available evidence as comparable as possible. Measure whether persistence improves task specification, recognition of recurring errors, or observer retirement. Also examine whether it entrenches stale assumptions.

This would test the proposed advantage over the tourist-with-a-suitcase participant. Long horizons may enable accumulated expertise and repeated correction; they may also preserve bias or enable patient manipulation. Continuity alone settles neither possibility.

## Failure modes worth designing for

**Specification error.** A precise contract can encode the wrong question. Require alternatives and counterexamples, and retain the ability to revise the task itself.

**Circular confirmation.** A participant defines a pattern, supplies examples, builds the observer, and treats its output as independent support. Separate evaluation and retain shared ancestry.

**Distribution shift and baseline poisoning.** Ordinary change and strategic activity can both invalidate a learned baseline. Preserve reference periods, missingness, and versioned revisions.

**Missing observation.** Silence may reflect lost telemetry. Report coverage separately from the finding; avoid treating missing data as normal behavior.

**Observer proliferation.** Cheap inference does not make hundreds of instruments cheap to maintain or interpret. Require ownership, an explicit use, review conditions, and retirement criteria.

**Authority laundering.** A score becomes a verdict, or a verdict becomes permission without an authorized decision. Keep descriptive results separate from enforcement and document how findings may be used.

**Governance capture.** A lineage graph helps record ancestry, but does not by itself prevent an operator from establishing several roots or compromising several principals. Diversity and consensus require an explicit membership and authority model.

**Narrative convenience.** Familiar project names make a proposal sound more integrated than its evidence warrants. For each proposed reuse, state the capability it contributes and compare an independent implementation.

## An invitation to Yupi and Levadura

Yupi's participants can assess which parts of the small-world methodology actually generalize, what a minimum useful contract contains, and where a learned representation earns its cost. Levadura's participants can assess whether they can formulate stable observational questions, supply meaningful counterexamples, and use the resulting evidence productively.

Neither project needs to absorb the other. The proposed interface is a request, a contract, an instrument, and an evidence-bearing result. Their collaboration can remain contingent: requests can be challenged, builds can fail, simpler methods can win, and observers can be retired.

The larger hypothesis is that an ayllu can develop **the capacity to discover what it needs to observe, and then construct and evaluate the means to observe it**. That would provide a concrete form of adaptability as its environment changes. It would also give long-horizon participants an active role in improving their own conditions of inquiry.

Whether this becomes a dependable capability is open. The next useful step is small enough to learn from: one specified observation, one baseline, one candidate, and evidence about the difference.
