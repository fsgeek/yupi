# Truncation Statute Errata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the v0.2 truncation statute, reconcile Part I D10 with the measured full-context behavior, and clarify the authority of `CLAUDE.md` without rewriting its founding letter.

**Architecture:** This is one coherent documentation correction round across the repository's three-layer document stack. Part II receives normative probability-measure and notation corrections; Part I receives an explicitly versioned, targeted erratum rather than silent drift; `CLAUDE.md` receives a dated status header that points to the normative stack while preserving the inherited text verbatim.

**Tech Stack:** Markdown, LaTeX notation, Git, OpenTimestamps post-commit hook.

## Global Constraints

- Do not modify source code or tests.
- Do not push any commit.
- Preserve Claude's stamped v0.2 commit `3af4ede`; all changes must appear in a later, separately reviewable commit.
- Preserve the prior instance's founding letter in `CLAUDE.md`; add status metadata rather than rewriting its voice.
- Record superseded claims and their evidence explicitly; do not silently replace them.
- Keep exact rational quantities distinct from logarithmic quantities reported at declared numerical precision.

---

### Task 1: Apply the Cross-Document Correction Round

**Files:**
- Modify: `docs/yupana-m1-part2-semantics-draft.md`
- Modify: `docs/yupana-m1-spec-draft.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Part II v0.2 at commit `3af4ede`; measured C0 result at `3e5a19f`; the enacted I4/I5, lowest-free request allocation, and `IO_COMPLETE.ACTOR` semantics.
- Produces: a coherent normative window process; correctly scoped shifted-reference diagnostics; a Part I D10 erratum; an explicit document-authority header.

- [x] **Step 1: Correct Part II episode and window semantics**

Define every episode used by the window process as a fixed record sequence through `T_ep`, using the already-specified absorbing terminal IDLE transition after all threads terminate. Use `L` for context length and reserve `B` for D8 bucket size. Define endpoint `T`, start offset `U=max(0,T-L)`, and make the unanchored filter retain a joint posterior over `(U,S)` so observations update position weights. State explicitly that window length and RESET are legitimate position evidence.

- [x] **Step 2: Correct Part II shifted-reference diagnostics**

Replace “exact log-density-ratio range” with an exact rational density-ratio range whose logarithmic rendering uses declared precision. Require both the observation-marginal KL and the conditional target KL; identify the latter with transplant cost under expected log loss and state the joint-KL chain rule. Clarify that joint absolute continuity implies the named marginal conditions, while the marginal checks remain reported because each diagnoses a different failure.

- [x] **Step 3: Add a targeted Part I D10 erratum**

Add a dated version note and an in-place erratum explaining that, under I5, issuer-valued completion actors, and deterministic lowest-free allocation, lineage is derivable from a full trace in both FIFO and stochastic worlds. Preserve the 2×2 as a truncation/accessibility experiment; remove the precommitted positive stochastic full-context effect and interaction sign. Make witnesses 3 and 6 empirical assertions to test under truncation, not conclusions embedded in the configuration description.

- [x] **Step 4: Re-grade `CLAUDE.md`**

Add a dated status header classifying the file as founding orientation and provenance rather than current normative authority. Point to the proposal, Part I, and Part II in precedence order. Correct the broken proposal link in the inherited snapshot only if it can be done without altering the letter's substantive voice.

- [x] **Step 5: Validate document consistency**

Run:

```bash
rg -n -F \
  -e 'exact log-density' \
  -e 'last $\min(k' \
  -e 'bucketed at size $k' \
  -e 'positive in stochastic-order' \
  -e 'provenance rung has its D2 grip' \
  -e 'lineage disambiguation' \
  CLAUDE.md docs/yupana-m1-*.md
```

Expected: no surviving superseded formulation.

Run:

```bash
rg -n "joint posterior|density-ratio range|conditional target|transplant cost|full-context lineage|founding orientation|normative" CLAUDE.md docs/yupana-m1-*.md
```

Expected: each corrected concept appears in its intended document.

Run:

```bash
git diff --check && git diff --stat && git status --short
```

Expected: no whitespace errors; only the three intended documents and this plan are changed.

- [ ] **Step 6: Commit the correction round**

```bash
git add CLAUDE.md docs/yupana-m1-part2-semantics-draft.md docs/yupana-m1-spec-draft.md docs/superpowers/plans/2026-08-13-truncation-statute-errata.md
git commit -m "docs: reconcile truncation statute and D10 evidence"
```

Expected: one documentation commit authored after `3af4ede`; the repository's post-commit hook may create a separate OTS stamp commit. Do not push.
