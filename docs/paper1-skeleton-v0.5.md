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

## §1's framing: producer locality against consumer locality (Tony, 2026-10-10)

Asked whether "log close to where it's needed" was ever a stated principle in systems tracing, Tony said no.
Logging is done close to where the activity occurs, at the producer. The nearest analogue he knew is his own
Indaleko argument: index close to where the indices are needed, which is often far from the data they index.

For §1:
- Traces are written with **producer locality**. Learners pay for **consumer distance**, which is the lag profile.
- The relay is an *index*, in Indaleko's sense: a redundant near copy placed at the point of use, with the source
  left where it is. That is what makes it a natural intervention, and not an artefact of the experiment.
- §4e's open seam becomes the paper's design question: how much does an index placed near the consumer buy, and
  why does the gain not scale with the lag-4 measure of the move?

**Refined the same evening (Tony):** the index-placement argument probably did not survive into print in that
form. The better statement has two decisions in it:
1. **Extract when the data is close.** In storage tiering, data starts local and moves to cheaper, farther tiers.
   Indexing should happen while extraction is still cheap.
2. **Keep the index close to where it is used.** Indexing where the data ends up stored performs worse.

The two decisions map onto the instrument, and each is measured exactly:
- *Extraction* is the interface choice. The kernel holds the full hidden state at emit time, so extraction is
  cheap there, and what it does not emit is lost for good. That loss is the **observation gap** (the ceiling).
- *Placement* is the lag profile. For a bounded learner, the trace's past is a tiered store: recent records are
  cheap to reach and far ones are dear. Information extracted but placed far away costs the learner without being
  lost. That cost is what B1 measures, and convergence (B5′) is the learner building its own index, which cuts the
  far-tier cost proportionally more and never to zero.
- The relay is the second decision applied with the first held fixed: same extraction, same ceiling, and a copy
  placed nearer the point of use.

So §1 can state the paper as a separation: what the producer extracts and where the trace places it are different
design decisions, and only a world with exact ceilings can price them separately. This is our framing and not an
attributed principle; at most it cites Tony's tiering work as motivation. Not yet checked whether the systems literature states consumer-side log placement anywhere. Tony's
recollection says not; a search is still owed before §1 says "no prior statement".

## Record lag is token lag (checked 2026-10-10)

The learner's distance is measured in tokens, but ι is defined over records, so the two had to be compared. The
d1 verdict (`d1-long-lag-verdict-v0.1.md:59`) listed token distance as an uncontrolled covariate. It is
controlled by construction (Part I D5; `src/yupi/corpus/rendering.py` `render`):
- Every record on every rung is exactly five tokens: KIND ACTOR OBJECT RELATED LINEAGE. Masked and absent fields
  render as placeholder tokens.
- The relay writes its KIND copy into the OBJECT slot and adds no tokens.
- RESET shifts absolute positions by one and leaves distances unchanged.

So token distance is 5 × record lag, plus a fixed offset within the record for each field, identical across
rungs. §3 should state this in one sentence. One consequence for §1's exchange rate: placement on this instrument
costs no trace *length*. Any price for redundancy has to be paid in slot capacity or entropy, not in bytes.

## Risk this framing carries

A reviewer may read §4a as "Someya again, in a toy world". The defence has to be in §1 and §3, not added in §4.
The variable is the *observation of a fixed system*, not the language. That makes the result a statement about
interface design, which no locality paper makes.
