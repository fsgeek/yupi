# D10 truncated-window lineage search — preregistration v0.1

> **Status (2026-08-23 10:44 PDT): PREREGISTRATION, stamped before any D10 posterior
> is computed.** Contract for the witness-3/witness-6 search and crossover
> verdict (Part I D10; Part II §9 scoping: both witnesses enumerate C0b
> windows). Analysis rules fixed here, per truthsayer review (via Tony,
> 2026-08-23, seven points, all adopted). Anything not fixed here is
> exploratory and will be labeled so.

## 1. Estimand

Let H₃ be the masked-lineage (r3) observation of a window, Λ the lineage
sequence additionally exposed at r4, Z the query target, d ∈ {fifo,
stochastic} the discipline. Per coarse history h:

    g_d(h) = I(Z; Λ | H₃ = h)        (bits, exact rationals → floats at print)

and globally

    Δ_d = E[g_d(H₃)] = I(Z; Λ | H₃)

under the declared window law. Δ_information(D10) := Δ_stoch − Δ_FIFO,
**no precommitted sign**. This is the exact expected-log-score gain of
Part I D10; the name Δ_information is reserved for this ceiling contrast.

## 2. Targets

- **Primary (preregistered):** statutory Q3[D0] = ordered in-flight
  (thread, request-id) list (`q3_inflight_ids`).
- **Mechanism diagnostic (co-primary for interpretation, not for the
  witness):** thread/order-only Q3thr[D0] (`q3_inflight`).
- **Secondary:** the remaining statutory queries, reported in full,
  **never** substituted for Q3 in the witness verdict. Taking a best
  result across targets is forbidden by this section.

Predeclared interpretation of the (Q3, Q3thr) pair per cell:
| Q3 | Q3thr | reading |
|---|---|---|
| > 0 | 0 | witness passes formally; mechanism is allocator-label recovery |
| > 0 | > 0 | lineage informs issuing-thread membership/order itself |
| 0 | 0 | no D10 witness in that cell |
| 0 | > 0 | impossible (Q3 refines Q3thr); its occurrence is an inference-defect alarm |

## 3. Prevalence (defined before results)

Primary: **P(g_d(H₃) > 0)** — law mass of coarse r3 histories with
strictly positive exact gain. Existence uses exact g > 0 only; **δ is an
information threshold and takes no part in existence.** Also reported:
count of distinct informative coarse histories; E[g | g > 0]; max g and
quantiles {50, 90, 99}; global Δ_d. Fraction-of-r4-children is a secondary
view answering a different question and is labeled as such.

## 4. Window law (mechanical rule, value computed then recorded)

B = 2 (primary M1 condition). T_ep chosen by rule, not by result: **the
smallest even horizon at which (i) two requests are simultaneously
in-flight with positive probability, (ii) a non-head completion is
reachable (stochastic), and (iii) at least one truncated window (U > 0)
opens strictly after an IO_ISSUE it does not contain.** The search script
computes this T_ep* and records it in the artifact before any posterior at
it is examined. Sensitivity: T_ep* + 2 and T_ep* + 4 (absorbing-IDLE
padding dilutes prevalence; dilution is reported, not hidden). Every
eligible L (even, < T_ep) and every endpoint/window position reported —
law means co-reported, never substituted for cells.

## 5. Gates (all must pass before any verdict is read)

1. Full-context (L = T_ep) exact zero: g_d ≡ 0 in both disciplines
   (v0.2.4 erratum's derivability, asserted not assumed).
2. Two-path: recursive window filter equals independent prefix-
   marginalized path summation on **every distinct C0b window** at the
   chosen laws, bit-for-bit, both disciplines, r3 and r4.
3. r4 exactly refines r3 (each r4 window class nests inside one r3 class).
4. Matched queue-level hazard verified mechanically: P(completion | n>0)
   = p identical across disciplines at every reachable state.
5. g_d(h) ≥ 0 for every h (conditional MI nonnegativity as an
   arithmetic check on the implementation).
6. An existence verdict cites **> 1 enumerated coarse history**, never a
   single handcrafted trace.

## 6. Verdict rules (written before the search)

- Nonempty class (P(g>0) > 0, gate 6) with Δ_d < δ: **witness
  ESTABLISHED; rung numerically collapsed under that law.** Not a failure.
- Empty class after all gates pass: invoke Part I's three-way
  disambiguation (mistaken mechanism / sterile validation scale /
  inference defect) — the padded-horizon sensitivity and the D8 allocator
  evidence inform the first two arms; redesign/rescale per the witness
  rule, no fiat.
- **No single monotone "crossover" is assumed.** The deliverable is the
  exact set of informative (L, T) cells per discipline; a crossover
  horizon is summarized only if the informative cells form one.
- D8's allocator finding (order-sensitivity of [IO_COMPLETE, IO_ISSUE]
  under masked lineage) is a **candidate mechanism D10 tests
  independently**, not prior proof; it is cited in interpretation only
  through the §2 decomposition table.

## 7. Provenance

Search scripts, raw JSONs (append-only, versioned names), and the verdict
note cite this preregistration by commit hash. Any deviation is recorded
as a deviation, not silently absorbed. Predictions beyond the statute's
(witness 3, witness 6 mechanisms) are deliberately **not** added here: the
Tier-1 lesson is that this instance's numeric priors from other laws are
unreliable; the statute's existence predictions are the preregistered
content.
