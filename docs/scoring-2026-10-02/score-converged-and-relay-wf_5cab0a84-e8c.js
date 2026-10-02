export const meta = {
  name: 'score-converged-and-relay',
  description: 'Mechanically score stamped preregs (converged ladder C1-C4, actor A4, relay R1-R4) with frozen scripts; two-family fidelity review; one fix round',
  phases: [
    { title: 'Score', detail: 'one runner executes frozen commands, builds scorecard' },
    { title: 'Review', detail: 'Claude + Codex independently try to refute every scored line' },
    { title: 'Fix', detail: 'runner answers each objection: fix or record disagreement' },
  ],
}

const COMMON = `
You are working in /home/tony/projects/yupi (project Yupi). Today is 2026-10-02. This is CONFIRMATORY scoring of
pre-registered, OTS-stamped predictions. The raw census/eval files were produced by frozen scripts and committed UNSCORED
at commit e3d1f06. Governing documents (read them in full, they are short):
  docs/converged-ladder-prereg-v0.1.md            (C1, C2, C3, C4)
  docs/actor-long-lag-design-prereg-v0.1.md       (A4 = A1 on every converged-ladder r1-r4 run)
  docs/relay-intervention-prereg-v0.1.md          (R1-R4)
  docs/relay-intervention-prereg-v0.1.1-addendum.md (resolves four ambiguities; it GOVERNS where it differs from the
     script's own help text — in particular R4's scored t is the quadrature t, which relay_paired.py labels "not scored")
Precedent verdicts for format/estimator reading: docs/d1-long-lag-verdict-v0.1.md, docs/actor-long-lag-verdict-v0.1.md.
HARD RULES: never edit any prereg; never modify scripts/implicit_info_bintest.py (sha256 must be
c73fab6b76180b6a3851bcea89369f958aab81987a7f39bdd2a49ad32dd7acfc), scripts/implicit_info_bintest_actor.py (sha256
09ba6f42d6303c49bb60fb05587c2ef962f4d468e6de9e82ce624ce3a40c4c09), scripts/relay_paired.py, learner_window_census.py,
learner_evaluate.py. Check those sha256s before use. Do NOT git commit anything (the owner commits). Do not reinterpret a
prediction to make it pass or fail: score the stamped wording literally; where wording is ambiguous, say so and give
both readings. Report failures plainly. Write any long-running output under ~/.cache/yupi-scratch (never /tmp only).
Never kill processes by pattern (pkill -f); the GPU is not needed and must not be touched.

New raws (all dated 2026-10-02, in docs/):
  censuses: learner-window-census-<cell>-2M-e15-seed{1,2,3}-2026-10-02.json for cells r0-eps1 r2-eps1 r3-eps1 r4-eps1
    r0-eps1_2 r1-eps1_2 r2-eps1_2 r3-eps1_2 r4-eps1_2 (27), plus r1-eps1-2M-e15-seed{1,2,3} (the 3 existing r1 eps=1 15-epoch
    models, newly censused), plus r1R-eps1-2M-e5-seed{1,2,3} and r1R-eps1-2M-e15-seed{1,2,3}.
  evaluations: learner-eval-<cell>-2M-d128-e15-seed{1,2,3}-2026-10-02.json (27 ladder runs, k=1..7).
  Each census raw records its per-window file (~/.cache/yupi-scratch/census/<run>-k7-test.jsonl) and its sha256.
Pre-existing inputs: 5-epoch r1 eps=1 censuses docs/learner-window-census-r1-eps1-2M-seed{1,2,3}-2026-09-21.json (relay
primary-arm controls); exact long-lag info table docs/implicit-info-lag-kind-40-8-2-k7-2026-09-28.json (C3's quoted values);
docs/relay-exact-side-2026-09-30.json.
`

const SCORE_TASK = `${COMMON}
YOUR ROLE: the single RUNNER. Execute exactly these, using \`uv run --extra learner python ...\` from the repo root:
 1. C1, C2: scripts/implicit_info_bintest.py --m-long 4 --glob 'docs/learner-window-census-r[1-4]-eps*-2M-e15-seed*-2026-10-02.json'
    --raw docs/converged-ladder-bintest-kind-2026-10-02.json   (must pick up exactly 24 raws: r1-r4 x eps{1,1/2} x 3 seeds;
    verify the count and that no r0 or r1R file is included). Score from the full_plus_log2_class_mass model (β_long = beta[1]).
    C1: per run β_long>0 and t>=3 (24 runs). C2: pooled per cell (8 cells) β_long in [0.01, 0.05].
 2. A4: scripts/implicit_info_bintest_actor.py --m-long 4, same glob, --raw docs/converged-ladder-bintest-actor-2026-10-02.json.
    Score as A1 is scored in docs/actor-long-lag-verdict-v0.1.md (same model row that verdict used; state which).
 3. C3, C4: the KIND-excess cell mean = the census's mean of by_field.kind over the k=7 test windows. Compute it per run from
    the per-window file (verify its sha256 against the raw first), then per cell mean over seeds, with between-seed spread.
    Cross-check each run's mean against the raw's class list (sum n*by_field.kind / total n) where possible. Write the small
    computation as a NEW script scripts/converged_ladder_c3c4.py that writes docs/converged-ladder-c3c4-2026-10-02.json.
    C3: eps=1/2: r2 > r1 > r3 (means); eps=1: r2 > r3 (r1 eps=1 excluded). Seed-resolution: every seed of the higher cell
    exceeds every seed of the lower one — report it beside each pairwise ordering. C4: r0 lowest KIND excess of every cell at
    its eps (compare r0 with r1..r4 at eps=1 — include r1 eps=1 e15 here, since C4 does not exclude it, but report both with
    and without it — and at eps=1/2). Also report r4 cell means (no prediction).
 4. Relay checkpoint provenance (addendum §3): for each arm, confirm from each census raw's run path / run.json / log that
    controls and r1R models match the arm recipe (primary: 5 epochs, final step 39065; secondary: 15 epochs, step 117195).
 5. R1, R2, R4 primary: scripts/relay_paired.py --arm primary --eps 1 --r1 docs/learner-window-census-r1-eps1-2M-seed{1,2,3}-2026-09-21.json
    --r1R docs/learner-window-census-r1R-eps1-2M-e5-seed{1,2,3}-2026-10-02.json --raw docs/relay-paired-primary-2026-10-02.json
    Secondary: --arm secondary --r1 docs/learner-window-census-r1-eps1-2M-e15-seed{1,2,3}-2026-10-02.json --r1R
    docs/learner-window-census-r1R-eps1-2M-e15-seed{1,2,3}-2026-10-02.json --raw docs/relay-paired-secondary-2026-10-02.json
    If a gate refuses, report the refusal verbatim; do not work around it.
    Score R4 with the quadrature t (addendum §2), and also report the set-mean-se t.
 6. R3: implicit_info_bintest.py --m-long 4 --glob 'docs/learner-window-census-r1R-eps1-2M-e5-seed*-2026-10-02.json'
    --raw docs/relay-r3-bintest-primary-2026-10-02.json (3 raws), and the e15 glob -> docs/relay-r3-bintest-secondary-2026-10-02.json.
    R3 per seed: full_plus_log2_class_mass β_long > 0 with t >= 3. Secondary arm: report without thresholds.
Keep each command's stdout in ~/.cache/yupi-scratch/census/scoring-2026-10-02-<step>.log.
Return the scorecard: one line per scored prediction instance, with the exact numbers, PASS/FAIL, and file+JSON path of
each number. Include anything surprising, any ambiguity, and the exact commands run.`

const SCORECARD = {
  type: 'object',
  properties: {
    lines: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string', description: 'e.g. C1/r2-eps1-s1, C2/r3-eps1_2, C3/eps1_2:r2>r1, R1/primary' },
      rule: { type: 'string' }, values: { type: 'string' },
      result: { type: 'string', enum: ['PASS', 'FAIL', 'REPORTED', 'REFUSED', 'AMBIGUOUS'] },
      source: { type: 'string' } }, required: ['id', 'rule', 'values', 'result', 'source'] } },
    summary: { type: 'string', description: 'per-prediction tallies, e.g. C1 24/24' },
    commands: { type: 'array', items: { type: 'string' } },
    files_written: { type: 'array', items: { type: 'string' } },
    sha_checks: { type: 'string' },
    notes: { type: 'string', description: 'ambiguities, surprises, deviations' },
  },
  required: ['lines', 'summary', 'commands', 'files_written', 'sha_checks', 'notes'],
}

const OBJECTIONS = {
  type: 'object',
  properties: {
    objections: { type: 'array', items: { type: 'object', properties: {
      line_id: { type: 'string' }, severity: { type: 'string', enum: ['changes-result', 'changes-number', 'wording/provenance'] },
      claim: { type: 'string' }, evidence: { type: 'string', description: 'your independent recomputation or the prereg text' } },
      required: ['line_id', 'severity', 'claim', 'evidence'] } },
    independently_confirmed: { type: 'array', items: { type: 'string' }, description: 'line ids you recomputed and agree with' },
    not_checked: { type: 'array', items: { type: 'string' }, description: 'line ids you could not check, and why' },
  },
  required: ['objections', 'independently_confirmed', 'not_checked'],
}

const reviewTask = (card, who) => `${COMMON}
YOUR ROLE: adversarial FIDELITY REVIEWER (${who}). A runner produced the scorecard below. Your job is to REFUTE it: for each
line, check (a) that the right inputs were used (globs, counts, arms, 5- vs 15-epoch controls, r1 eps=1 excluded from C3 only),
(b) that the right model row / estimator / standard error was scored (full_plus_log2_class_mass; R4 quadrature t per addendum;
R2 set-mean se alone), (c) that the threshold applied is the stamped one, and (d) the numbers themselves — recompute
independently from the raw JSONs and per-window files wherever feasible (write your own short code; do not just re-run the
runner's script). Also read scripts/converged_ladder_c3c4.py critically: is "mean of by_field.kind over k=7 test windows"
what it computes? Check the frozen-script sha256s. Look for anything the scorecard omits that the preregs require.
Do not modify any file in the repo (you may write scratch under ~/.cache/yupi-scratch/review-2026-10-02-${who}/). No commits.
Default to objecting when uncertain, but be precise about what would change.

SCORECARD:
${JSON.stringify(card, null, 1)}`

phase('Score')
const card = await agent(SCORE_TASK, { label: 'runner', phase: 'Score', schema: SCORECARD, effort: 'high' })
if (!card) { return { error: 'runner returned null' } }
log(`runner: ${card.summary}`)

phase('Review')
const [claudeRev, codexRev] = await parallel([
  () => agent(reviewTask(card, 'claude'), { label: 'review:claude', phase: 'Review', schema: OBJECTIONS, effort: 'high' }),
  () => agent(reviewTask(card, 'codex') + `\n\nYou are the cross-family reviewer: delegate the actual checking to Codex (a GPT model) via the codex
companion runtime with the full brief above, in read-only/investigation mode, and return Codex's findings faithfully in the
schema (do not substitute your own judgment for Codex's; if Codex is unavailable, say so in not_checked and return no
objections of your own).`, { label: 'review:codex', phase: 'Review', agentType: 'codex:codex-rescue', schema: OBJECTIONS }),
])
const objs = [
  ...((claudeRev && claudeRev.objections) || []).map(o => ({ ...o, by: 'claude' })),
  ...((codexRev && codexRev.objections) || []).map(o => ({ ...o, by: 'codex' })),
]
log(`objections: claude ${claudeRev ? claudeRev.objections.length : 'null'}, codex ${codexRev ? codexRev.objections.length : 'null'}`)

phase('Fix')
let fixed = null
if (objs.length) {
  fixed = await agent(`${COMMON}
YOUR ROLE: the RUNNER again, one fix round. Your scorecard and the reviewers' objections follow. For EACH objection: verify it
yourself; if correct, fix the computation (re-run the frozen command or correct scripts/converged_ladder_c3c4.py — never a frozen
script or prereg) and give the corrected line; if you believe it wrong, keep the line and state why, so the disagreement is
recorded. Return the full revised scorecard; in notes, list each objection id → accepted/rejected with reason.

ORIGINAL SCORECARD:
${JSON.stringify(card, null, 1)}

OBJECTIONS:
${JSON.stringify(objs, null, 1)}`, { label: 'runner:fix', phase: 'Fix', schema: SCORECARD, effort: 'high' })
}
return { card, claudeRev, codexRev, fixed }
