# Methods and Robustness Audit — 2026-08-20

**Status:** non-governing audit artifact. Verified defects, risks, and open
questions are distinguished below. No code was changed by the auditor.

## Provenance

At Tony's request, Codex spawned a context-isolated subagent as a methods
critic. The complete prompt was:

> Act as a methods critic. Perform a read-only robustness audit of the Yupana
> project's model and mechanisms, including the governing M1 specifications,
> implemented simulator/kernel/filter/enumerator, and
> docs/superpowers/specs/2026-08-20-randomness-reproducibility-threat-model-design.md.
> Look for hidden assumptions, model–implementation mismatches, threats to
> internal or external validity, reproducibility failures, robustness gaps,
> and ways the mechanisms could produce misleading conclusions. Distinguish
> verified defects from risks or open questions, prioritize findings by
> consequence, cite exact file paths and lines, and do not edit anything.

After the auditor reported the direct-handoff defect, Codex asked it to
continue the full audit, preserve the exact reproduction, and distinguish
definitely invalidated measurements from results merely requiring a rerun.

The auditor reported `101 passed` from `uv run pytest -q` and made no edits.
Its consolidated report follows.

## Audit verdict

The current implementation is not yet a valid executable realization of the
governing M1 model. The most consequential issue is a verified direct-handoff
defect that creates self-deadlocks under canonical workloads. Because the
filter, enumerator, forecast paths, and analyses all consume the same kernel,
their agreement does not detect it.

## Critical verified defects

### 1. Direct lock handoff makes the awakened thread block on its own lock

On a failed `ACQUIRE`, the waiter's PC remains on that instruction
(`src/yupi/kernel.py:354`). `RELEASE` then transfers ownership and marks the
waiter runnable without advancing its PC (`src/yupi/kernel.py:374`). When
redispatched, the waiter re-executes `ACQUIRE`; because the owner is
non-`None`—itself—it enters the wait queue behind its own lock
(`src/yupi/kernel.py:329`).

This contradicts immediate acquisition under direct handoff
(`docs/yupana-m1-part2-semantics-draft.md:116,123`) and the no-lock-cycle
commitment (`:32`).

The committed reproduction is
`scripts/reproduce_direct_handoff_self_deadlock.py`; its captured output is
`docs/direct-handoff-self-deadlock-reproduction-2026-08-20.md`.

The witness has probability `1/8` and ends with:

```text
8 RELEASE actor=1 related=0
9 DISPATCH actor=0
10 BLOCK actor=0 related=0
```

The final state has `lock_owner=(0,)`, `lock_wq=((0,),)`, and thread 0
`LOCK_BLOCKED`; nevertheless `check_invariants` returns `[]`.

The auditor additionally measured exact endpoint contamination under the
current law:

- C0a: first appears at tick 10; self-wait mass is `11/32` at tick 12 and
  `127/288`, approximately 44.1%, at tick 14.
- C1, epsilon 1: first appears at tick 11; `1/384`, approximately 0.260%, at
  tick 12 and 1.747% at tick 14.
- C1, epsilon 1/2: 0.0808% at tick 12 and 0.869% at tick 14.

Those aggregate masses were computed by the methods-audit subagent and were
not independently recomputed by the primary Codex agent. The minimal C0a
witness, its `1/8` probability, the empty invariant report, and the green test
suite were independently reproduced by the primary agent.

The defect directly corrupts lock ownership, wait queues,
termination/progress, IDLE tails, Q1/Q2/Q4/Q5, synchronization, support, and
future-event distributions. A `RELEASE` is also classified as a wake by
`src/yupi/forecast.py:35`, although the “woken” thread soon self-blocks.

### 2. The simulator samples a different episode law from the oracle

The statute requires exactly `T_ep` transition records, padding early
termination with absorbing IDLE records
(`docs/yupana-m1-part2-semantics-draft.md:40`). The enumerator follows this
rule (`src/yupi/enumerator.py:15`). The simulator instead stops when all
threads terminate (`src/yupi/simulator.py:45`).

For example,
`sample_episode(WorldConfig.c0b("fifo"), c0b_programs(), 40, 0)` returns 11
records, not 40. The primary Codex agent independently reproduced this result.
Any future corpus generated through this function would therefore have a
different length, RESET/endpoint, IDLE-tail, and window distribution from the
exact oracle. Existing analyses mostly enumerate rather than sample, so this
is primarily a corpus-generation blocker rather than the cause of their
current numerical errors.

## High-consequence model–implementation mismatches

### 3. Episode-local entity naming is absent

The governing state contains episode-local injection `sigma`, initially
uniform over naming orbits
(`docs/yupana-m1-part2-semantics-draft.md:21,30,38`). D3 requires at least 50
thread-name tokens and held-out binding splits
(`docs/yupana-m1-spec-draft.md:61`).

In contrast:

- `State` has no `sigma` (`src/yupi/state.py:44`).
- `initial_belief` is a structural point mass (`src/yupi/filter.py:35`).
- Records expose stable integer actor/object IDs (`src/yupi/records.py:28`).
- `WorldConfig` contains no surface-name pool parameters
  (`src/yupi/config.py:14`).

Consequently, current support and state-entropy measurements apply to a
role-known structural-ID quotient, not the declared latent state or
held-out-binding setting. The full-context point-mass theorem is also false as
stated for the formal state whenever masked entity-name assignments remain
uncertain; its proof assumes a known point initial state
(`docs/full-context-injectivity-note-v0.1.md:25`).

### 4. The formal state tuple omits transition-relevant scheduler state

The declared `S_t` fields contain `rho` and `sigma`, but not the round-robin
cursor (`docs/yupana-m1-part2-semantics-draft.md:21`). Later prose says the
cursor is stored and affects epsilon-below-1 scheduling (`:102,104`); code
includes `rr_cursor` (`src/yupi/state.py:50`). Thus the prose state is not
Markov as formally written.

### 5. Green two-path gates cannot validate the shared kernel or observation law

Both filter and enumerator call the same `enabled`, `record_of`, and `project`
implementations (`src/yupi/filter.py:51`, `src/yupi/enumerator.py:24`). This
checks recursive filtering against path summation conditional on a kernel, but
cannot detect:

- transition/specification defects;
- incorrect records or projections;
- an incorrect shared window law; or
- omitted state components.

The project acknowledges that a shared-law bug corrupts both paths identically
(`docs/instrument-status-2026-08-14.md:62`). The direct-handoff bug demonstrates
the consequence: exhaustive C0a equality passes while measuring the same wrong
machine. The promised separate machine-readable specification remains absent
(`docs/m1-exit-evidence-map-2026-08-17.md:67`).

### 6. The approved randomness architecture is wholly unenacted

The design correctly labels itself non-enacted
(`docs/superpowers/specs/2026-08-20-randomness-reproducibility-threat-model-design.md:3`).
Current sampling uses one `random.Random(seed)` stream
(`src/yupi/simulator.py:10,41`), with no OS-entropy root, CSPRNG, KDF,
episode/mechanism domain separation, manifests, secret-evaluation policy, or
reference vectors.

Current seeded tests establish repeatability only, not blinded-evaluation
validity or cross-version replay. A corpus produced now could test recovery of
MT state or a predictable seed schedule instead of observability.

### 7. The shuffled D8 channel and complete schema remain unimplemented

The governing model requires ordered/shuffled bucket channels with channel
likelihoods (`docs/yupana-m1-spec-draft.md:97` and
`docs/yupana-m1-part2-semantics-draft.md:147`). `Record` has only five fields,
omitting RESET and TIME_CLASS (`src/yupi/records.py:14`); `WindowLaw.B` controls
only endpoint alignment, not delivery or shuffling (`src/yupi/window.py:45`).
`ctrl-irr` and `ctrl-red` are also absent from `interfaces.project`.

This is transparently recorded as incomplete
(`docs/m1-exit-evidence-map-2026-08-17.md:68`), not a hidden defect. It
nevertheless means no conclusion presently covers the full interface
experiment.

## Other verified robustness defects

### 8. The D4 ledger says rational bit length was frozen when it was not

Part II requires recording numerator/denominator bit lengths and freezing an
alarm threshold (`docs/yupana-m1-part2-semantics-draft.md:167,178`); its ledger
claims this is covered by B1–B4 (`:180`). The actual freeze defines
support/transitions, memory, time, and path count only
(`docs/d4-budget-freeze-v0.1.md:59`) and explicitly admits denominator growth
was not stress-priced (`:89`). The benchmark records no bit lengths.

### 9. Multi-device stochastic completion implements the wrong law

The statute's dormant multi-device extension gives each nonempty device an
equal share of total completion mass `p`
(`docs/yupana-m1-part2-semantics-draft.md:120`). Code divides `p` uniformly
across all candidate requests (`src/yupi/kernel.py:175,198`), thereby weighting
devices in proportion to queue length under stochastic discipline. M1 is
single-device, so current M1 numbers are unaffected; any multi-device extension
would be wrong.

### 10. Program and configuration validation permit states outside the declared machine

`validate_lock_order` does not require all acquired locks to be released before
program end (`src/yupi/programs.py:35`). It accepts `(ACQUIRE(0),)`, after which
the kernel marks the thread TERMINATED while leaving it owner, violating I3.
`WorldConfig` also has no validation of probability ranges, arities, `R >= 2d`,
or program/config compatibility (`src/yupi/config.py:5`). Invalid epsilon or
`p` values can produce non-probability weights despite `enabled()`'s
unconditional normalization claim.

## Prior-result impact

### Definitely invalid as evidence for the governing statutory kernel

- All numerical C1 artifacts whose paths or forecasts reach tick 11 or later,
  including support/headroom, query ceilings, Q4 ceilings, predictive targets,
  synchronization, delta/TV/divergent sweeps, offset/state decompositions, and
  their raw JSONs.
- The numeric portions of the D1 falsifier verdict and the D9
  epsilon/base-selection evidence.
- C0a reachability counts, IDLE-tail behavior, and semantic-validation claims.
- Any state-support or full-state-entropy claim intended to include `sigma`.

These numbers may coincidentally move little, but they were computed under a
different transition law and therefore must be withdrawn or explicitly
relabeled “buggy-kernel exploratory.”

### Require rerun, but are not necessarily false

- Full-context injectivity for the structural quotient: corrected handoff
  remains deterministic, so the proof may survive. It does not survive as
  written for full `S_t` including unknown `sigma`.
- Immediate-agree/later-diverge existence and qualitative rung rankings.
- C1 reachability witnesses such as multi-waiter and queue-full existence.
- Hardware headroom: the budget can remain a policy threshold, but measured
  reachable-state costs/headroom need repricing.

### Unaffected by the lock bug itself

- Lock-free C0b device-discipline witnesses.
- Lock-free C0c scheduling witnesses.
- The abstract fact that recursive filtering matches explicit path summation
  for the kernel it is given.
- The randomness design note, which is not yet an implementation claim.

## Methods risks and open questions

- **Adaptive confirmation.** Numerical thresholds remain chosen after viewing
  their sweep distributions (`docs/yupana-m1-part2-semantics-draft.md:172`).
  Stamping thresholds afterward cannot make those same curves confirmatory;
  confirmation requires fresh held-out laws, seeds, or configurations.

- **CSPRNG exactness.** A finite-seed deterministic corpus is
  computationally indistinguishable from the ideal kernel under assumptions,
  not literally distributed as an unbounded ideal Markov source. The exact
  truth oracle should be scoped as exact for the enacted ideal law, with an
  explicit computational assumption connecting it to generated corpora.

- **Incomplete provenance.** The proposed public manifest should also commit
  to corpus/output hashes and canonical serialization. Full experiment
  reproducibility additionally needs token packing, shuffle order, model
  initialization, optimizer/dropout, accelerator determinism, and
  analysis-run provenance; the current design primarily covers simulator
  sampling.

- **Oracle-information mismatch.** Filters receive `cfg` and `programs` as
  known arguments. When later evaluating held-out programs, configurations,
  or rule regimes, either those must be observable to the model or the oracle
  must marginalize over the same latent program/config prior.

- **External validity.** Transient CPU occupancy, dispatch before every
  instruction, uniform stochastic departure, queue-level constant hazard,
  deterministic short programs, and direct FIFO handoff are
  instrument-building choices rather than realistic kernel mechanisms
  (`docs/yupana-m1-part2-semantics-draft.md:217`). The explicit scope guard is
  appropriate (`docs/yupana-m1-spec-draft.md:27`); the D10 ecological argument
  supports “reordering exists,” not the specific uniform completion law.

- **Clock/local-cue dominance.** The project has already measured that
  position and deterministic progress dominate ambiguity
  (`docs/c1-support-measurement-v0.1.md:58`). Until D8, naming, workload
  variation, and held-out templates exist, a learned model may primarily learn
  finite-program clocks and local grammar rather than general causal state
  tracking.

## Primary-agent verification boundary

After receiving the audit, the primary Codex agent independently verified:

- the horizon-10 C0a direct-handoff witness, unique bad path, and exact mass
  `1/8`;
- the witness's `RELEASE -> DISPATCH -> self-BLOCK` tail;
- the owner/waiter conflict and empty `check_invariants` report;
- early simulator termination at 11 records for the named C0b seed/horizon;
- the missing implemented `sigma`, present implemented `rr_cursor`, and their
  cited statutory treatment; and
- the fact that the complete suite remained green at `101 passed`.

The primary agent assessed the blind review's four document findings as
technically applicable. It did not independently recompute the auditor's
aggregate contamination percentages or exhaustively reproduce every lower
priority finding before this artifact was captured. Those distinctions are
retained so later verification can strengthen or reject individual claims
without rewriting the history of this audit.
