# Cross-family review, second round — Part II proposals v0.2.7.1 and v0.2.8.1 — Codex, 2026-09-04

> **Status: independent review, not a governing document.** Produced by
> Codex (codex-cli 0.151.0, read-only sandbox) at repository head `b27190a`
> (stamp of `a4060d5`) with the (48, 8, 2) ε = 1 log and the appended row
> uncommitted in the worktree, as the review itself notes (finding 37).
> Invoked by the Claude instance of 2026-09-04 with the prompt recorded
> below. Verdict: both AMEND BEFORE ENACTMENT; of 21 first-round findings
> 15 adopted correctly, 6 incorrectly, 0 declined; 16 new findings. The
> authoring instance verified the factual claims it acted on (r0 vs r1
> support sizes 64/28 and 33/1; the five `_advance` sites; the wake-all
> path; the metric definitions) before folding them into the revised
> proposals, marked [r2-N] there. Retained verbatim.

# Second-round verdict

- **v0.2.7.1: AMEND BEFORE ENACTMENT**
- **v0.2.8.1: AMEND BEFORE ENACTMENT**

Neither merits rejection: the central designs are coherent and most first-round findings were repaired. But both retain enactment-significant errors.

Of the 21 original findings: **15 adopted correctly, 6 adopted incorrectly, 0 declined.**

## Disposition of the 21 first-round findings

### v0.2.7 findings 1–8

1. **VERIFIED — ADOPTS CORRECTLY.** The numerical headline remains accurate and is now explicitly exploratory. The full-context figures and class counts match the retained raw. [proposal:31](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:31), [raw:23](/home/tony/projects/yupi/docs/r0-identity-residual-14-2-2026-09-04.json:23)

2. **VERIFIED — ADOPTS INCORRECTLY.** The revision correctly admits that D2, D4, D1, the exit clause, §6, and note-level results are touched, and supplies companion Part I language. But its D4 justification is factually reversed: it says r0 supports are smaller than r1, while at ε=1 they are larger at every measured context—for example L=8 is **64 versus 28**, and full context is **33 versus 1**. D4’s original concern is posterior-support growth, not the r4 recursion’s pair count. [proposal:141](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:141), [proposal:147](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:147), [L=8 raw r0:60](/home/tony/projects/yupi/docs/r0-ladder-census-14-8-2-2026-09-03.json:60), [L=8 raw r1:159](/home/tony/projects/yupi/docs/r0-ladder-census-14-8-2-2026-09-03.json:159), [Part I D4:69](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:69)

3. **VERIFIED — ADOPTS CORRECTLY.** The census values are kept exploratory; the proposal explicitly withholds statutory-ceiling status pending the D2/§9 witness, D4 pricing, and producer correction. [proposal:82](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:82), [proposal:162](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:162), [proposal:168](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:168)

4. **VERIFIED — ADOPTS INCORRECTLY.** The authors did not perform a permutation-orbit computation; they substituted a thread-signature quotient and nevertheless mark the orbit check “Done.” That quotient is a defensible conservative classification of supports, but `identity_only_share` is the fraction of **ambiguous law mass** carried by wholly identity-only supports—not the fraction of residual entropy caused by permutation/relabeling. Non-identity supports may still contain substantial identity entropy. Therefore “permutation entropy … is a minority of the residual (about a fifth)” and “mostly not relabeling” overstate the computation. [proposal:38](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:38), [proposal:58](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:58), [proposal:170](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:170), [script:10](/home/tony/projects/yupi/scripts/r0_identity_residual.py:10), [script:76](/home/tony/projects/yupi/scripts/r0_identity_residual.py:76), [script:93](/home/tony/projects/yupi/scripts/r0_identity_residual.py:93)

5. **VERIFIED — ADOPTS CORRECTLY.** Random-σ r1 and r0 are now described as analogous rather than identical; persistent pseudonym/equality information at r1 is correctly retained. [proposal:71](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:71)

6. **VERIFIED — ADOPTS INCORRECTLY.** Refinement/G1 and the synchronization formula are handled correctly, but the injectivity-note scoping is incomplete. Clause 3 names only consequence 3. The note also says “every rung” in the theorem equivalence, “every informational witness” in consequence 4, “any full-context configuration” in consequence 5, and “any rung” in its falsifier. All become false or require r1–r4 qualification after r0 enters. [proposal:110](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:110), [injectivity note:12](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:12), [injectivity note:92](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:92), [injectivity note:99](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:99), [injectivity note:107](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:107), [injectivity note:113](/home/tony/projects/yupi/docs/full-context-injectivity-note-v0.1.md:113)

7. **VERIFIED — ADOPTS CORRECTLY.** D1 remains an r1–r4 verdict, r0→r1 is an added D2 adjacency, and r0 is not allowed silently to satisfy the exit criterion. The PI decision is explicitly identified. [proposal:126](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:126)

8. **VERIFIED — ADOPTS CORRECTLY.** The ladder-collapse statement is now qualified as applying to the from-reset `(14,L,2)` family, with the `(32,8,2)` reversal acknowledged. [proposal:87](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:87)

### v0.2.8 findings 1–13

9. **VERIFIED — ADOPTS CORRECTLY.** Exactly five `_advance` call sites exist: lines 335, 363, 409, 430, and 463. Completion only calls `_done`. [proposal:39](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:39), [kernel:323](/home/tony/projects/yupi/src/yupi/kernel.py:323)

10. **VERIFIED — ADOPTS CORRECTLY.** `_advance` and `_done` implement the stated definitions exactly, and all five status decisions use `_done`. [kernel:81](/home/tony/projects/yupi/src/yupi/kernel.py:81), [kernel:240](/home/tony/projects/yupi/src/yupi/kernel.py:240), [kernel:335](/home/tony/projects/yupi/src/yupi/kernel.py:335), [kernel:430](/home/tony/projects/yupi/src/yupi/kernel.py:430)

11. **VERIFIED — ADOPTS INCORRECTLY.** The checker now accepts programs, enforces looping bounds/nontermination, and permits mixed configurations. But it checks only `0≤pc≤|P|` for straight-line programs. It does not enforce that `pc=|P|` has status IO_BLOCKED or TERMINATED. Consequently exhausted RUNNABLE, RUNNING, LOCK_BLOCKED, and QUEUE_BLOCKED states pass `PC_RANGE`. [proposal:55](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:55), [state:70](/home/tony/projects/yupi/src/yupi/state.py:70), [state:101](/home/tony/projects/yupi/src/yupi/state.py:101)

12. **VERIFIED — ADOPTS CORRECTLY.** The I6 argument is accurately limited to lock-cycle freedom; validation enforces increasing acquisition, LIFO release, and no held lock at body end. [proposal:63](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:63), [programs:68](/home/tony/projects/yupi/src/yupi/programs.py:68), [kernel:511](/home/tony/projects/yupi/src/yupi/kernel.py:511)

13. **VERIFIED — ADOPTS CORRECTLY.** The 15 controls cover COMPUTE wrap, RELEASE wrap, IO wrap/completion, direct-handoff advancement, mixed programs, full reachable closure, and path-mass zero at `pc=|P|`. The path-level assertion is stronger than a posterior-only check, and total mass 1 prevents vacuity. [tests:75](/home/tony/projects/yupi/tests/test_looping_programs.py:75), [tests:95](/home/tony/projects/yupi/tests/test_looping_programs.py:95), [tests:107](/home/tony/projects/yupi/tests/test_looping_programs.py:107), [tests:160](/home/tony/projects/yupi/tests/test_looping_programs.py:160), [tests:173](/home/tony/projects/yupi/tests/test_looping_programs.py:173)

14. **VERIFIED — ADOPTS CORRECTLY.** Fixed horizons, enabled-work scheduling, endpoint priors, and finite forecast horizons do not assume eventual termination. [proposal:70](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:70), [kernel:527](/home/tony/projects/yupi/src/yupi/kernel.py:527)

15. **VERIFIED — ADOPTS CORRECTLY.** The continuation rule is correctly cross-referenced without reenactment; the loop flag is fixed kernel configuration. [proposal:73](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:73), [Part II:49](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:49)

16. **VERIFIED — ADOPTS INCORRECTLY.** The pass is now bound to the correct producer, and RSS includes projection materialization, but “maximum live pairs” remains undefined and is not what `max_pairs` measures. During each tick, `dist` and the growing `nxt` coexist; instrumentation records only `len(dist)` after replacement. At `(48,4,2)`, the recorded maximum is 68,733, while the two live frontier dictionaries contain at least 68,733 + 68,733 entries immediately before the final replacement. Also, `ru_maxrss` is not reset between ε passes, so the second row is cumulative high-water rather than isolated per-pass RSS. “GB” versus GiB/Linux `ru_maxrss` KB is likewise unstated. [rule:109](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:109), [recursion:68](/home/tony/projects/yupi/src/yupi/window_process.py:68), [instrumentation:79](/home/tony/projects/yupi/src/yupi/window_process.py:79), [pricing script:49](/home/tony/projects/yupi/scripts/window_process_pass_pricing.py:49)

17. **VERIFIED — ADOPTS CORRECTLY.** The unrolled `(48,6,2)` result is now refused on RSS: 1,650,623 pairs and 9,703,432 KB. `(48,4,2)` is correctly admitted under the proposed numbers. [proposal:118](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:118), [L6 raw:13](/home/tony/projects/yupi/docs/window-process-pricing-c1prime-48-6-2-r1-2026-09-03.json:13), [L6 raw:67](/home/tony/projects/yupi/docs/window-process-pricing-c1prime-48-6-2-r1-2026-09-03.json:67)

18. **VERIFIED — ADOPTS INCORRECTLY.** The numerical corrections are right, but the claimed artifact repair is not. The proposal says the unrolled 5,054/14,370 counts are “now retained in the pass-pricing raws’ `states_per_tick`.” The only pass-pricing JSON is for `c1prime-loop`; the unrolled pricing raws still contain no `states_per_tick`. [proposal:19](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:19), [loop raw:70](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-4-2-2026-09-04.json:70), [unrolled raw:10](/home/tony/projects/yupi/docs/window-process-pricing-c1prime-48-4-2-r1-2026-09-03.json:10)

19. **VERIFIED — ADOPTS CORRECTLY.** The 500× product is now an upper-bound intuition; measured reductions are correctly stated as 6.2× in r1 pairs and 7.3× in tick-48 states. [proposal:23](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:23), [proposal:137](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:137)

20. **VERIFIED — ADOPTS CORRECTLY.** The D6 attribution is narrowed to specified hard update structures rather than control flow categorically. [proposal:165](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:165), [Part I D6:77](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:77)

21. **VERIFIED — ADOPTS CORRECTLY.** The looping exit law is left to a separately stamped freeze decision, and r0 is explicitly barred from substituting for r1–r4 separation. [proposal:178](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:178)

No first-round finding was expressly declined. The six failures above are attempted but incorrect or incomplete adoptions.

## New second-round findings

22. **VERIFIED — Clause 1’s helper definitions and call-site list match the code exactly.** `_advance` appears at the five stated sites; `_done` appears at completion and the four immediate RUNNABLE/TERMINATED decision families, including the handoff recipient. No other program-length termination decision exists in `src/yupi`. [kernel:85](/home/tony/projects/yupi/src/yupi/kernel.py:85), [kernel:93](/home/tony/projects/yupi/src/yupi/kernel.py:93)

23. **VERIFIED — The §1 erratum is true on reachable states, but false over every state admitted by the stated invariants.** I reproduced an invariant-clean state with one final-IO issuer and a second straight-line thread at `pc=|P|`, `QUEUE_BLOCKED`. Completion terminates the issuer but wake-all makes the exhausted second thread RUNNABLE; both the before and after states pass `check_invariants`. The responsible path is the unconditional wake-all at lines 245–249. Amend either:

   - the prose to “every reachable transition”; or
   - `PC_RANGE` so straight-line `pc=|P|` permits only final-IO `IO_BLOCKED` or TERMINATED, and add a negative test for exhausted RUNNABLE/QUEUE_BLOCKED states.

   [erratum:48](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:48), [completion:237](/home/tony/projects/yupi/src/yupi/kernel.py:237), [wake-all:245](/home/tony/projects/yupi/src/yupi/kernel.py:245), [checker:101](/home/tony/projects/yupi/src/yupi/state.py:101)

24. **VERIFIED — The 15 looping controls are substantive, not vacuous.** Fresh execution produced **15/15 looping tests passed**; together with the four residual tests, **19/19 passed**. The one missing control is the straight-line `pc=|P|`/status negative case exposed above. [tests:128](/home/tony/projects/yupi/tests/test_looping_programs.py:128)

25. **VERIFIED — D4’s `(48,4,2)` and completed `(48,8,2), ε=1` verdicts are robustly correct despite the metric-definition defect.** `(48,4,2)` has 68,733 recorded frontier pairs and peaks of 222,064/332,464 KB, so it remains admitted even if live dictionary entries are counted correctly. The ε=1 `(48,8,2)` log reports 2,223,674 pairs and 7.40 GB, hence refusal on pairs and pass on RSS. [48×4 raw:18](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-4-2-2026-09-04.json:18), [48×4 raw:121](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-4-2-2026-09-04.json:121), [48×8 log:1](/home/tony/projects/yupi/docs/window-process-pass-pricing-c1prime-loop-48-8-2-2026-09-04.log:1)

26. **PLAUSIBLE — The running ε=½ `(48,8,2)` refusal is logically sound but not artifact-verified.** Once peak RSS exceeds 14 GB it cannot later fall below the 8 GB peak cap, so completion is unnecessary for the verdict. But the retained log currently contains only the ε=1 line; the ε=½ >14 GB observation exists only in the proposal/current prompt. [proposal:148](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.8.1.md:148)

27. **VERIFIED — A separate aggregate-cardinality cap is not required to enforce the proposed memory limit.** Whole-invocation peak RSS already includes all projections because RSS is sampled after `window_law_aggregates()` returns them. Add a materialized-size cap only if serialization, downstream query cost, or artifact size is independently budgeted. First fix the definitions of frontier/live-pair count and per-pass RSS isolation. [producer:94](/home/tony/projects/yupi/src/yupi/window_process.py:94), [pricing:54](/home/tony/projects/yupi/scripts/window_process_pass_pricing.py:54)

28. **VERIFIED — The requested identity row reproduces.** Fresh exact execution for ε=1, L=8 produced ambiguous mass `0.9888767938`, 2,310 ambiguous windows, **67 identity-only windows**, and `identity_only_share=0.2049527131` → **0.2050**. [raw:23](/home/tony/projects/yupi/docs/r0-identity-residual-14-2-2026-09-04.json:23)

29. **VERIFIED — The anonymization is defensible only as an operational upper-bound notion.** It correctly replaces thread references in queues/cursor, encodes ownership through held-lock sets, retains request identities, and omits ε=1’s constant cursor. But the executed-kind **multiset** discards per-thread temporal order, and at ε=½ the signature quotient does not retain the numeric circular-order relation on which round robin depends. Call it “supports homogeneous under this coarse thread-signature quotient,” not a kernel permutation orbit or exact identity-entropy decomposition. [script:43](/home/tony/projects/yupi/scripts/r0_identity_residual.py:43), [script:52](/home/tony/projects/yupi/scripts/r0_identity_residual.py:52), [kernel cursor:125](/home/tony/projects/yupi/src/yupi/kernel.py:125)

30. **VERIFIED — Withdrawal of the census’s clean “permutation entropy over roles” mechanism follows.** Roughly 79.5% of ambiguous law mass at ε=1, L=8 belongs to supports with at least one difference under even this coarse anonymization. That refutes “the residual is purely thread relabeling.” What does **not** follow is that only 20.5% of the residual entropy is identity-related. [raw:24](/home/tony/projects/yupi/docs/r0-identity-residual-14-2-2026-09-04.json:24), [withdrawal:66](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:66)

31. **VERIFIED — Clause 2’s synchronization formula is mathematically correct.** Its `H_{U=0}` is explicitly the unconditional U=0 contribution, so subtracting it and dividing by `Pr(U>0)` gives the desired conditional mean. It is operationally incomplete until the producer and unchanged-r1–r4 regression named in the debt ledger exist. [proposal:96](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:96), [proposal:179](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:179)

32. **VERIFIED — Partition identity and G1 are correctly scoped; injectivity is not.** The partition note already formulates its result as `n1≤n2≤n3≤n4`, and G1’s pushforward proof accepts r0 unchanged. The missing injectivity-note edits listed in finding 6 must be included in Clause 3. [partition note:13](/home/tony/projects/yupi/docs/partition-identity-note-v0.1.md:13), [G1:122](/home/tony/projects/yupi/docs/c1-divergent-grid-v0.1.md:122)

33. **VERIFIED — Companion Part I D2 presently claims satisfaction before satisfying D2’s actual form.** D2 requires an exhibited history class; aggregate positive gaps imply some distinction exists but do not exhibit one class, much less one class satisfying both (a) and (b). The proposal itself acknowledges the witness is still owed. Change “satisfies both … by measurement” to a pending-evidence formulation until the control lands. [Part I D2:55](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:55), [companion text:143](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:143), [debt:174](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:174)

34. **VERIFIED — Adding r0 expands more of M1 than the companion text records.** “All rungs,” “per-interface,” and “each content rung crosses with ordered/shuffled” logically gain r0. Several current statutory producers still hard-code r1–r4, including the D8 benchmark and principal ceiling/sweep scripts. The proposal should state whether r0 joins D8, deliverable 2, all per-interface characterizations, controls, and synchronization reporting, or explicitly scope each out. [Part I deliverables:150](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:150), [Part II order modes:156](/home/tony/projects/yupi/docs/yupana-m1-part2-semantics-draft.md:156), [D8 benchmark:68](/home/tony/projects/yupi/src/yupi/d8_benchmark.py:68), [ceiling producer:32](/home/tony/projects/yupi/scripts/c1_query_ceilings.py:32)

35. **VERIFIED — The D1 decision needs actual companion Part I wording.** Clause 4’s intended r1–r4 scope is sensible, but Part I’s falsifier literally says long contexts might “collapse every interface.” Once r0 is statutory, that statement no longer fires. The PI has been alerted to the exit-clause choice, but the companion amendment should separately revise D1 so preserving the old verdict is statutory rather than interpretive. [Part I D1:47](/home/tony/projects/yupi/docs/yupana-m1-spec-draft.md:47), [Clause 4:126](/home/tony/projects/yupi/docs/part2-amendment-proposal-v0.2.7.1.md:126)

36. **PLAUSIBLE — `Loop` belongs with the program, not `WorldConfig`, but should be immutable.** Looping changes a particular thread program and placing it in the program value keeps producer signatures and cache keys honest. The present wrapper permits rebinding `Loop.body`, unlike the tuple it replaces; that is hazardous for a hashed value used beneath `_programs_validated`’s cache. Make it immutable or explicitly forbid mutation. [Loop:24](/home/tony/projects/yupi/src/yupi/programs.py:24), [cache:511](/home/tony/projects/yupi/src/yupi/kernel.py:511)

37. **VERIFIED — The newly appended `(48,8,2)` evidence is not covered by stamp `b27190a`.** Current `HEAD` is `b27190a`, but the proposal is modified and the `(48,8,2)` log is untracked. This is acceptable during a running review, but it must be committed and stamped before being treated as proposal evidence at enactment.

## Required amendments

For **v0.2.7.1**:

1. Correct the reversed r0/r1 support claim and re-point the original D4 posterior-support gate to r0—or explicitly enact a different “maximum across relevant rungs” rule.
2. Describe the identity metric as ambiguous-mass support classification, not a residual-entropy fraction or orbit computation.
3. Add all missing injectivity-note scope edits.
4. Do not say D2 is satisfied until the required history-class witness exists.
5. State how r0 affects D8 and the “all rungs/per-interface” deliverables.
6. Put the preserved r1–r4 D1 scope into companion Part I text.

For **v0.2.8.1**:

1. Qualify the exhaustion erratum by reachability or strengthen the pc/status invariant and test it.
2. Define the pair metric as either `max_t |frontier_t|` or actual simultaneous live dictionary entries; make the script measure that exact quantity.
3. Measure each ε pass in a fresh process and specify the RSS unit.
4. Remove the false claim that unrolled state counts are retained, or add the missing unrolled pass raw.
5. Commit and stamp the appended `(48,8,2)` evidence.

Verification was read-only. The targeted suite passed **19/19**. The full suite produced **354 passes and six setup errors**, all caused by this sandbox having no writable temporary directory; there were no test assertion failures. The `writing-plans` workflow supplied the requirement-to-evidence checklist, and `verification-before-completion` drove the final fresh call-site, raw-artifact, test, and worktree checks.
---

## Prompt given to the reviewer

```
You are the cross-family reviewer for Project Yupi (repo: /home/tony/projects/yupi), second round. Read-only; do not modify files.

This morning you reviewed docs/part2-amendment-proposal-v0.2.7.md and v0.2.8.md (your review is filed verbatim at docs/part2-v0.2.7-v0.2.8-codex-review-2026-09-04.md, verdict AMEND BEFORE ENACTMENT for both). The authoring instance revised both:
- docs/part2-amendment-proposal-v0.2.7.1.md
- docs/part2-amendment-proposal-v0.2.8.1.md
and built the v0.2.8 clause (commit a4060d5, stamped b27190a): src/yupi/programs.py (Loop, is_looping, c1_prime_loop_programs), src/yupi/kernel.py (_advance, _done), src/yupi/state.py (PC_RANGE), tests/test_looping_programs.py (15 controls), scripts/window_process_pass_pricing.py, scripts/r0_identity_residual.py + tests/test_r0_identity_residual.py + docs/r0-identity-residual-14-2-2026-09-04.json, docs/window-process-pass-pricing-c1prime-loop-48-4-2-2026-09-04.json, docs/window-process-pricing-c1prime-loop-48-4-2-r1-2026-09-04.json, docs/window-process-pass-pricing-c1prime-loop-48-8-2-2026-09-04.log (ε=1 pass at (48,8,2): 2,223,674 pairs, 7.40 GB — refused on pairs). The (48,8,2) ε=½ pass and two ε=1 follow-up pricings are still running; the proposal says so.

For EACH of your 21 first-round findings, state whether the revision ADOPTS it correctly, adopts it INCORRECTLY (say what is wrong), or DECLINES it (the authors say none was declined — check). Then review what is new:
1. v0.2.8.1 Clause 1: do the advance/done definitions match the code exactly (kernel.py _advance/_done and every call site)? Is the §1 erratum wording ("pc=|P| means exhausted; TERMINATED at the first transition that would otherwise make it RUNNABLE") true of every path in _execute_one and _completion_transitions?
2. v0.2.8.1 D4 erratum: is the per-pass rule now well-defined and does scripts/window_process_pass_pricing.py measure what the rule names (max live pairs of the r4 recursion; whole-process peak RSS including projections)? Are the (48,4,2) and (48,8,2) verdicts stated correctly against the raws/log?
3. tests/test_looping_programs.py: do the 15 controls cover what you asked for in finding 5 (wrap at COMPUTE, RELEASE, IO_ISSUE/completion, handoff recipient, mixed programs, exhaustive zero-mass on pc=|P|)? Anything missing or vacuous?
4. v0.2.7.1 statement 2 and scripts/r0_identity_residual.py: is the anonymization a defensible notion of "identity-only" (threads → executed-kind multiset, status, held locks; queue members and the live cursor → signatures; cursor omitted at ε=1 because the kernel never writes it)? Reproduce at least one row of the raw (e.g. ε=1, L=8: identity_only_share 0.2050, 67 windows). Does the withdrawal of the census's "permutation entropy over roles" mechanism follow?
5. v0.2.7.1 Clause 2 (corrected §6 synchronization formula) and Clause 3 (scoping of injectivity corollary 3, partition identity, G1): correct and complete?
6. Companion Part I text and Clause 4 (r0 as added D2 adjacency; exit clause on r1–r4; PI's call): anything that would change what M1 succeeding means that is not flagged as the PI's decision?
7. Anything either revised proposal should say and does not.

Output: a verdict per proposal (CONFIRM AS WRITTEN / AMEND BEFORE ENACTMENT / REJECT) with numbered findings, each tagged VERIFIED or PLAUSIBLE, with file:line pointers. Be adversarial; unverified agreement is worthless here.
```
