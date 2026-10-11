# Paper 1: skeleton v0.5 (2026-10-10)

> **Status: GOVERNING for paper 1's shape. It supersedes v0.4.** v0.4's centre paragraph still led with the relay
> claim that inventory §G withdrew, so the centre is rewritten here. The section content is otherwise v0.4's,
> reordered. Every claim keeps its inventory status (`docs/inventory-2026-10-09.md` v0.2, §F–§G). Written by the
> owning instance after Tony asked, on 2026-10-10, "You tell me: what's the story."

## The centre

**What a trace makes knowable does not settle what a learner will learn from it. Where the trace puts that
knowledge also matters, and that placement is a property of the interface.** We use a hidden system small enough
to count and vary only how it is observed. For each interface we compute the exact ceiling, and we also compute
the *lag profile*: at which distance in the trace the knowable information sits. Interfaces with equal ceilings can
place it differently. An intervention can hold the ceiling identical class by class and still move the
information. Small transformers' shortfall from the exact ceiling tracks the long-range end of the profile within
every interface. This holds for the next event's kind and for entity identity, on held-out models and at
convergence. Training longer shrinks the long-range cost proportionally more than the rest, and does not remove it.

**What is ours and what is not.** That learners pay for distance is Someya et al.'s locality bias (ACL 2025),
shown on languages and random automata. Our contribution is to make it a quantity of *observation design* for a
fixed hidden-state system. The world holds still, only the telemetry varies, the ceilings are exact per class, and
binding (actor identity under per-episode naming) is measured alongside kind. The classical figure of merit for an
interface is identifiability, and this paper argues that it is incomplete. The practical question is the systems
one: what should a trace record, and *how close to the moment it is needed*?

**Open seam, stated in the paper:** the relay adds a near copy and leaves the far source in place. It gives a
gain, but not in proportion to the lag-4 measure of the move. An exploratory full-profile reading favours locality,
and the question is open (inventory §G).

## Sections

| § | content | inventory items | status in the paper |
|---|---|---|---|
| 1 | Introduction: the observation-design question. Locality-bias prior work. The Mason & Anand relation as the adopted analogy paragraph only (`bridge-draft-2026-10-09.md` §0) | bridge | as reviewed |
| 2 | The instrument. Exact ceilings for a stated observer. The two-path gate validates the filter under one shared kernel, not the kernel. Interventions with ceilings identical class by class (gates A–C) | A1 (reworded), A4 | exact, shared-kernel limit stated |
| 3 | Exact observability is a profile, not only a number. Interface value exists only where the window hides history; four regimes at the frozen law, thin top rung. Lag profiles cross. Equal-ceiling interventions move information (relay, decoy), and self-copy moves nothing | A2, A3, A4, A5 | exact |
| 4a | Within-cell law: KIND and actor excess rise with ι_long, held-out and at convergence, under class-clustered errors. Positioned as locality bias measured against exact per-class ceilings in a hidden-state world | B1 | confirmatory |
| 4b | Convergence cuts the long-lag cost proportionally more than the overall excess, and not to zero | B5′ | confirmatory |
| 4c | Cross-interface ordering by ι holds at ε = 1 and fails at ε = ½, where the seed spread exceeds the ι gap | B2 | confirmatory, split |
| 4d | Far better than counting: every seed beats a Witten–Bell table over the ceiling's own classes, by 1.3–5.2× | B5 | exploratory, per seed |
| 4e | The relay: ceiling held, information moved closer, a gain, but not proportional to the lag-4 measure. Reported qualitatively per seed pairing, with the 10-05 CORRECTIONS. No gain where ι4 = 0, confounded with posterior shape | B3 (as revised in §G), B4 | rejection of lag-4 proportionality only; rest exploratory |
| 5 | What output-level comparisons across corpora could not settle, and the design that would settle each one | C1–C4, B6 | negative, as method |
| 6 | Limits and next studies: shared-kernel validation; one world and one scale; three seeds per cell; fixed-model, evaluation-time interventions; acquisition dynamics; exposure gap (paper 3) | B6, B7 | — |

## Cut from paper 1 (unchanged from v0.4)

Belief geometry (B7), the three-arm test, any mechanism claim, and any claim about epistemic honesty or text-only
supervision.

## Risk this framing carries

A reviewer may read §4a as "Someya again, in a toy world". The defence has to be in §1 and §3, not added in §4.
The variable is the *observation of a fixed system*, not the language. That makes the result a statement about
interface design, which no locality paper makes.
