export const meta = {
  name: 'paper1-skeleton',
  description: 'Map Yupi findings, adversarially verify support and novelty, and synthesize a paper-1 skeleton with readiness checklist',
  phases: [
    { title: 'Read', detail: 'charter reader + six partition readers extract findings' },
    { title: 'Verify', detail: 'per finding: evidence-support skeptic and novelty judge' },
    { title: 'Synthesize', detail: 'paper-1 skeleton with RQs, hypotheses, falsifiers, readiness list' },
    { title: 'Critique', detail: 'hostile external reviewer + completeness critic' },
  ],
}

const ROOT = '/home/tony/projects/yupi'
const COMMON = `You are working in the Yupi repository at ${ROOT} (read-only for you: do NOT edit, commit, or write any files). Yupi builds a finite OS-like stochastic simulator (Yupana) whose exact Bayesian posterior is computable, and compares small transformers trained on its traces against exact information-theoretic ceilings (observation gap / accessible-representation gap / exposure gap). Paper 1 under the committed cut = Milestones 1-3 (instrument, interface & context manipulations, learner vs exact ceilings) plus the belief-geometry slice of Milestone 5. Factorization/coupling is paper 2; exposure/causal-use (patching) is paper 3. Notes in docs/ are append-only: corrections are often placed at the TOP of a note or in later dated sections, and later notes can supersede earlier ones — always check for a status banner, correction block, or later superseding note before treating a claim as standing. House rules relevant to judging claims: a subset used to average a realized-record quantity must be a function of the prefix only; a summary that lands exactly on a boundary (e.g. a clean 0.000) must be rechecked at the finest grain; a variable the kernel never writes must not enter a state/identity quantity.`

const FINDINGS = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'short slug' },
          claim: { type: 'string', description: 'the finding stated precisely with its key numbers' },
          teaches: { type: 'string', description: 'what a reader would learn from it, in one or two sentences' },
          evidence: { type: 'array', items: { type: 'string' }, description: 'repo-relative doc/raw paths and section numbers' },
          status: { type: 'string', enum: ['established', 'exploratory', 'withdrawn', 'superseded', 'unclear'] },
          corrections: { type: 'string', description: 'any later correction, retraction, or caveat found, or "none found"' },
          gap: { type: 'string', enum: ['observation', 'representation', 'exposure', 'instrument', 'methodology', 'other'] },
          cut: { type: 'string', enum: ['paper1-core', 'paper1-supporting', 'paper2', 'paper3', 'out', 'unclear'] },
        },
        required: ['id', 'claim', 'teaches', 'evidence', 'status', 'corrections', 'gap', 'cut'],
      },
    },
    omitted: { type: 'string', description: 'what you saw but left out (so nothing is silently dropped)' },
  },
  required: ['findings', 'omitted'],
}

const CHARTER = {
  type: 'object',
  properties: {
    contribution: { type: 'string' },
    rqs: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, text: { type: 'string' }, source: { type: 'string' }, status_now: { type: 'string' } }, required: ['id', 'text', 'source', 'status_now'] } },
    hypotheses: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, text: { type: 'string' }, falsifier: { type: 'string' }, source: { type: 'string' }, status_now: { type: 'string' } }, required: ['id', 'text', 'falsifier', 'source', 'status_now'] } },
    cut_commitments: { type: 'array', items: { type: 'string' } },
    prior_art: { type: 'array', items: { type: 'object', properties: { ref: { type: 'string' }, what_it_already_shows: { type: 'string' } }, required: ['ref', 'what_it_already_shows'] } },
    drift_from_charter: { type: 'string', description: 'where the work as done departs from the proposal/spec, and whether that departure is recorded' },
  },
  required: ['contribution', 'rqs', 'hypotheses', 'cut_commitments', 'prior_art', 'drift_from_charter'],
}

const PARTS = [
  { key: 'exact-ceilings', files: 'docs/c1-support-measurement-v0.1.md, docs/c1-q4-ceilings-v0.1.md, docs/c1-query-ceilings-v0.1.md, docs/c1-predictive-targets-v0.1.md, docs/c1-offset-vs-state-v0.1.md, docs/c1-observer-monotonicity-note-v0.1.md, docs/c1-rung-separation-geometry-v0.1.md, docs/c1-residual-ambiguity-census-v0.1.md, docs/r0-ladder-census-v0.1.md, docs/full-context-injectivity-note-v0.1.md, docs/partition-identity-note-v0.1.md, docs/exposure-gap-note-v0.1.md' },
  { key: 'exact-sweeps-falsifiers', files: 'docs/c1-delta-sweep-v0.1.md, docs/c1-divergent-grid-v0.1.md, docs/c1-sync-sweep-v0.1.md, docs/c1-tv-sweep-v0.1.md, docs/d1-falsifier-verdict-v0.1.md, docs/d10-lineage-search-prereg-v0.1.md, docs/d10-lineage-verdict-v0.1.md, docs/held-out-laws-proposal-v0.1.md, docs/held-out-confirmation-v0.1.md, docs/w11-heldout-prereg-v0.1.md, docs/w11-heldout-confirmation-v0.1.md, docs/w11-predictive-rung-search-v0.1.md, docs/sweep-rerun-comparison-2026-08-21.md, docs/corrected-kernel-rerun-v0.1.md, docs/audit-adjudication-2026-08-20.md, docs/methods-robustness-audit-2026-08-20.md' },
  { key: 'attribution-truncation-window', files: 'docs/d8-attribution-prereg-v0.1.md, docs/d8-attribution-c0b-note-v0.1.md, docs/d8-attribution-c1-note-v0.1.md, docs/d8-attribution-c1-truthsayer-review-2026-08-29.md, docs/d8-shuffled-channel-note-v0.1.md, docs/d8-attribution-grid-freeze-c1-v0.3.md, docs/deep-truncation-census-v0.1.md, docs/window-prior-experiment-note-v0.1.md, docs/window-process-enumerator-v0.1.md, docs/window-process-interning-note-v0.1.md, docs/c1-prime-live-census-v0.1.md, docs/c1-prime-pilot-note-v0.1.md' },
  { key: 'law-freeze-corpus-contract', files: 'docs/looping-exit-law-freeze-v0.1.md, docs/exit-clause-40-8-2-note-v0.1.md, docs/exit-clause-tables-40-8-2-2026-09-11.md, docs/corpus-track-40-8-2-note-v0.1.md, docs/d4-budget-freeze-v0.1.md, docs/part2-threshold-freeze-proposal-v0.3.1.md, docs/part2-amendment-proposal-v0.2.9.md, docs/learner-corpus-generator-design-v0.1.md, docs/learner-model-vs-ceiling-contract-v0.1.md, docs/request-id-design-question-v0.1.md' },
  { key: 'learner-1-12', files: 'docs/learner-first-results-40-8-2-2026-09-18.md sections 1 through 12 (lines 1-404), docs/superpowers/specs/2026-09-18-learner-trainer-design.md' },
  { key: 'learner-13-22', files: 'docs/learner-first-results-40-8-2-2026-09-18.md sections 13 through 22 (lines 405-1490), docs/superpowers/specs/2026-09-23-probe-lock-owner-design.md, docs/superpowers/specs/2026-09-24-belief-geometry-design.md' },
]

phase('Read')
const charterP = agent(`${COMMON}

Your job: extract the CHARTER of paper 1. Read docs/what-the-trace-surrenders-proposal-v0.2.md, docs/yupana-m1-spec-draft.md, docs/yupana-m1-part2-semantics-draft.md, docs/instrument-status-2026-08-14.md, docs/founding-context-2026-08-21.md, docs/the-kingdom-small-enough-to-count.md, docs/m1-exit-evidence-map-2026-09-01.md, docs/literature-review-2026-08-11.md, docs/literature-check-2026-09-18.md. Return: the one-sentence contribution; every research question (RQ) and hypothesis the charter names that falls in paper 1's cut, each with its stated or implied falsifier and its source; the cut commitments; and prior art with exactly what each already shows (so a later judge can decide novelty). For status_now, say what you can infer from these files about whether it has been answered (you will not read the learner note; say 'see learner note' where relevant). Also report drift between the charter and the work as recorded.`, { label: 'charter', phase: 'Read', schema: CHARTER })

const verifySupport = (f, key) => agent(`${COMMON}

You are an adversarial skeptic. A reader extracted this finding from the ${key} part of the docs:
${JSON.stringify(f, null, 1)}

Try to REFUTE it as stated. Open the cited evidence (notes AND the committed raw JSONs where cited or findable in docs/), and search docs/ for later corrections, retractions, superseding notes, or status banners (grep for the finding's key terms and section numbers). Check the numbers against the source. Check whether it violates the house rules (prefix-only subsets, boundary-value recheck, inert variables). Default to 'not supported' only if you find a concrete problem; say exactly what. Report the corrected statement if the claim is roughly right but misstated.`, {
  label: `support:${f.id}`, phase: 'Verify',
  schema: { type: 'object', properties: {
    verdict: { type: 'string', enum: ['supported', 'supported-with-correction', 'not-supported', 'withdrawn-in-docs'] },
    problems: { type: 'string' }, corrected_claim: { type: 'string' }, checked: { type: 'array', items: { type: 'string' } },
  }, required: ['verdict', 'problems', 'corrected_claim', 'checked'] },
})

const judgeNovelty = async (f) => {
  const charter = await charterP
  const prior = charter ? JSON.stringify(charter.prior_art) : '(charter unavailable)'
  return agent(`${COMMON}

You are a novelty judge for a machine-learning / interpretability audience (the likely reader of paper 1: someone who knows Othello-GPT, Shai et al. belief-state geometry arXiv:2405.15943, computational mechanics, linear probing, and scaling-law practice). The criterion from the PI: a result belongs in the paper only if it teaches something most readers won't already know. Prior art recorded by the project:
${prior}

Finding:
${JSON.stringify(f, null, 1)}

Judge: would a knowledgeable reader already know or trivially expect this? Is it novel in itself, novel only as an instance of the instrument working, or novel only to the project? You may use web search sparingly to check a specific novelty doubt. Be hard: default 'expected' when the result is what the standard view predicts, unless the exactness itself is the lesson.`, {
    label: `novelty:${f.id}`, phase: 'Verify',
    schema: { type: 'object', properties: {
      novelty: { type: 'string', enum: ['novel', 'novel-as-instrument-demo', 'expected', 'project-internal'] },
      reason: { type: 'string' }, nearest_prior: { type: 'string' },
    }, required: ['novelty', 'reason', 'nearest_prior'] },
  })
}

const results = await pipeline(PARTS,
  p => agent(`${COMMON}

Read these files in full: ${p.files}. Extract the findings they establish, attempt, or withdraw — up to 15, ranked by importance to paper 1. Include withdrawn/superseded findings (marked so) when they are instructive. Numbers must be copied from the text, not paraphrased. Put anything you saw but did not include in 'omitted'.`, { label: `read:${p.key}`, phase: 'Read', schema: FINDINGS }),
  (r, p) => {
    if (!r) return null
    if (r.omitted) log(`${p.key} omitted: ${r.omitted.slice(0, 300)}`)
    return parallel(r.findings.map(f => async () => {
      const [s, n] = await Promise.all([verifySupport(f, p.key), judgeNovelty(f)])
      return { part: p.key, ...f, support: s, novelty: n }
    }))
  })

const findings = results.filter(Boolean).flat().filter(Boolean)
const charter = await charterP
log(`${findings.length} findings verified`)

phase('Synthesize')
const skeleton = await agent(`${COMMON}

You are drafting the SKELETON of paper 1 (not the prose). The PI's bar: "ready" means ready for external review; a result belongs only if it teaches something most readers won't already know. The project owner will decide; your job is a strong proposal.

Charter extracted from the proposal/specs:
${JSON.stringify(charter, null, 1)}

Every finding, each with an adversarial support verdict and a novelty verdict:
${JSON.stringify(findings, null, 1)}

Produce a markdown document with:
1. Working title and a one-paragraph abstract draft (claims only as strong as the verified findings allow).
2. The paper's research questions (3-5), each with its hypothesis, the falsification experiment, and its current status (answered/partly/owed) citing finding ids and evidence paths.
3. Section outline: for each section, which findings it carries and the one thing it teaches.
4. The cut list: findings that stay in the notes only, with a one-line reason each (expected / project-internal / paper 2 / paper 3 / not supported).
5. Readiness checklist: every experiment, reanalysis, figure, or check owed before external review, ordered by what blocks most. Be concrete (which runs, which seeds, which estimator). Note that a size-axis follow-up is currently running (seeds 2-3 at 15 epochs for d=64/128/256, and d=256 at 45 epochs).
6. Risks: where a reviewer would attack, and which claims are fragile (seed spread, undertraining, estimator bias).
Do not invent numbers; every number must come from a finding above.`, { label: 'skeleton', phase: 'Synthesize' })

phase('Critique')
const [reviewer, critic] = await parallel([
  () => agent(`${COMMON}

You are a hostile but fair external reviewer at a top ML venue (interpretability / learning theory track). Here is a proposed paper-1 skeleton built from the project's verified findings:
${skeleton}

You may open any file in docs/ to check claims. Write the review you would write if this were submitted as outlined: summary, the three strongest objections, what would change your score, and which claims you do not believe and why. Be specific.`, { label: 'reviewer', phase: 'Critique' }),
  () => agent(`${COMMON}

You are a completeness critic. Proposed paper-1 skeleton:
${skeleton}

Findings it was built from (ids and verdicts): ${JSON.stringify(findings.map(f => ({ id: f.id, part: f.part, cut: f.cut, support: f.support && f.support.verdict, novelty: f.novelty && f.novelty.novelty })))}

Check docs/ for anything the skeleton missed: a note or result not represented, a charter RQ silently dropped, a withdrawn claim that slipped back in, an owed item not on the readiness list, a claim whose support verdict was not-supported but still appears. List concrete gaps with file paths.`, { label: 'completeness', phase: 'Critique' }),
])

return { charter, findings, skeleton, reviewer, critic }
