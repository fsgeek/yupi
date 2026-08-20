# Adjudication of the 2026-08-20 Methods Audit (v0.1)

**Status: adjudication note; written 2026-08-20 12:21 PDT (`date` in the writing
command), ninth instance.** The audit
(`docs/methods-robustness-audit-2026-08-20.md`, commit 47b4019, external
— Codex-spawned methods critic, primary-agent partial verification) was
non-governing until adjudicated; this note adjudicates it. Per Tony: no
deference owed — every adopted claim below was re-verified in this
repository before adoption.

## Findings 1, 2, 10 — VERIFIED, FIXED (commit d69fa87)

**Finding 1 (direct-handoff self-deadlock): verified three ways.**
(i) Code: `RELEASE` set `lock_owner[l] = woken` without advancing the
woken thread's pc; `ACQUIRE` tests only `owner is None`, so the
redispatched head re-executed its completed ACQUIRE against itself and
enqueued behind its own lock. (ii) Statute: §3.3/§3.5 say the woken head
"acquires ownership immediately" — its pc must move at handoff; the code
contradicted the statute. (iii) Measurement: the audit's aggregate
contamination masses, which the primary agent had NOT independently
recomputed, were recomputed here from the enumerator and match **exactly**:
C0a 1/8 (T=10), 11/32 (T=12), 127/288 ≈ 44.10% (T=14); C1 ε=1 first at
T=11, 1/384 ≈ 0.260% (T=11 and 12), 1056353/60466176 ≈ 1.7470% (T=14);
C1 ε=½ 11443/14155776 ≈ 0.0808% (T=12), ≈ 0.8687% (T=14).
Fix: handoff advances the woken pc (termination edge mirrored from the
ACQUIRE branch). Post-fix: the committed reproduction reports 0 bad
paths, and exact enumeration shows zero self-wait mass at every tested
horizon. `check_invariants` gains **I6** (owner queued on its own lock)
— the audit's bad state passed I1–I5, which is why 101 tests stayed
green.

**Finding 2 (sampler episode law): verified** — `sample_episode(c0b,
40, seed 0)` returned 11 records. Fixed: the sampler no longer breaks at
all-TERMINATED; the kernel's absorbing IDLE self-loop pads to exactly
T_ep, the same law the enumerator follows. Corpus generation was blocked
on this; it no longer is (but see finding 6).

**Finding 10 (validator): verified, fixed** — `validate_lock_order` now
rejects programs ending while holding a lock. Config-range validation
remains open.

**Tests:** 7 new witnesses (written failing against the defective
kernel), suite 101 → 108 green. Two old tests encoded buggy-kernel
expectations and were corrected with history noted in-place: IDLE-kind
coverage needed horizon 15 (IDLE at 12 came from deadlocked paths); the
reachable C0a count is **58**, not 72 — **Part II §3.2a's "transient
gives 72 states" is a buggy-kernel measurement and needs a statute
erratum (PI action).**

## Prior-result impact — audit classification ADOPTED

All numerical artifacts whose paths or forecasts reach tick 11+ are
relabeled **buggy-kernel exploratory**: the week's C1 notes (support,
query/Q4 ceilings, predictive targets, sync sweep, δ/δ_sync/TV sweeps,
divergent grid + resolution, offset-vs-state), the D1 verdict's Part B
numbers, and the D9 base-ε evidence. The prior notes are NOT edited
(append-don't-overwrite); this note and the store are the relabel.
Contamination at the measured laws is small — (12,·) laws touch it only
at endpoint 12 (0.26% ε=1); (14,·) at 12 and 14 (0.26%, 1.75%) — and a
drift probe under the corrected kernel (predictive targets, (12,2,2))
moved means in the third decimal (windows 283 → 277 at r3/r4; divergent
mass 0.0138 → 0.0136 ε=1). Direction, not magnitude, is the point: the
numbers were computed under a different transition law. **Every
quantitative claim above awaits rerun before reuse; the qualitative
structure (rung ordering, conservation identities, decompositions) is
expected to survive and must be re-verified, not assumed.**
Full-context injectivity: the corrected kernel remains deterministic
given the dispatch/completion record content; the theorem is expected to
survive for the structural quotient but the note's exhaustive checks
must be rerun (and finding 3 already limits its scope to that quotient).

## Findings adopted as open items (no code changed here)

- **3 (σ / entity naming absent):** verified — `State` has no σ, D3's
  ≥50-token pools unimplemented. All support/entropy claims are about
  the role-known structural quotient; the injectivity theorem holds for
  that quotient only. Statute–implementation gap; needs a Part II
  amendment or an implementation milestone before corpus work.
- **4 (rr_cursor missing from the formal S_t tuple):** verified; §1
  erratum needed (prose non-Markov as written).
- **5 (shared-kernel blindness of the two-path gate):** correct, and
  the failure predicted by `instrument-status` §firewall occurred: both
  paths agreed on the same wrong machine. The audit's implicit
  recommendation — an independent executable spec (deliverable 1's
  "machine-checkable form") — moves up the priority list.
- **6 (randomness architecture unenacted):** correct; the design note is
  design only. Corpus generation stays blocked on enactment even though
  finding 2 is fixed.
- **8 (D4 bit-length not frozen):** verified against
  `d4-budget-freeze-v0.1.md` §"not stress-priced"; owed at repricing.
- **9 (multi-device completion law):** verified mismatch
  (per-request vs per-device split); M1 single-device unaffected;
  flagged — do not build multi-device without resolving.
- **Methods risks** (adaptive thresholds → fresh laws for confirmation;
  CSPRNG scoping; provenance beyond sampling; oracle-information
  matching on held-out programs; external validity; clock dominance):
  adopted as standing constraints for the M1 report and corpus design.

## Revised next actions (supersedes the evidence-map v3 ordering)

1. ~~D10 witness search~~ → **first rerun the measurement chain under
   the corrected kernel** (same scripts, new dated raws; diff against
   buggy-kernel values and record the drift table). The D10/witness
   work would otherwise be built on relabeled numbers.
2. Statute errata bundle for the PI: §3.2a count, §1 rr_cursor, §3.3
   handoff-pc wording (make "acquires immediately" explicit about pc),
   finding 9 choice. Bundle with the pending v0.2.5 stamp.
3. Then the previous queue: D10 (w3/w6/w5), witness suite, D1 Part B
   re-adjudication on corrected curves, D8 design note, σ/naming
   decision.
