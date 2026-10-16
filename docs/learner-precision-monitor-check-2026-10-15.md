# Can the kind of uncertainty be read from an actual learner's output? Declared check (2026-10-15)

> Owning instance. Declared before any model is run. Follows the corrected `identifiability-tolerance-check-2026-10-15.md`
> (Pinsker bounds learner TV only from above; at δ ≈ 0.02 R stays readable, by δ ≈ 0.05 it does not).

**Models.** 15-epoch ladder (`converged-ladder-c3c4-2026-10-02.json`), r1 and r3 at ε ∈ {1, ½}, seeds 1–3: 12 models,
evaluated on CPU on their test split at k = 7 (pattern observer), KIND only. Q is the model's KIND distribution
renormalised over the KINDS (`learner/exposure.py` convention).

**Measured per window w** (class c, exact law p_c, model output q_w):
- t_w = TV(p_c, q_w): the model's actual precision on that window;
- the *look-alike set* A_w = classes c′ of the same (rung, ε) table with TV(p_c′, q_w) ≤ t_w, i.e. classes the output
  resembles at least as much as the truth (always contains c);
- a_w = law-mass share of A_w with |R_c′ − R_c| ≥ 0.1 bits (prior-weighted: what a monitor that knows the kernel and
  the class prior would find ambiguous about the *randomness* part).

**Reported per model:** the distribution of t_w (mean, median, q90); mean a_w; the share of windows with a_w ≥ 0.10.
The model is the unit; seeds are reported separately.

**Declared reading** (per (rung, ε), all three seeds must agree):
- **Kind readable at learner precision:** mean a_w < 0.05 and windows with a_w ≥ 0.10 < 10 %.
- **Kind not readable:** mean a_w ≥ 0.20 or windows with a_w ≥ 0.10 ≥ 40 %.
- **Between:** report the numbers, no general sentence.
Validity: V1, each model's mean of kind_kl_eval equals its census-era `kind_kl_bits` within 10⁻⁶ where a learner-eval raw
exists; V2, mean t_w ≤ the Pinsker bound from the same model's mean KL (a consistency check, by Jensen).

## Result (owner, 2026-10-15): BETWEEN in every cell; numbers only, as declared

Raw: `learner-precision-monitor-40-8-2-k7-2026-10-15.json` (12 models, 84,949–85,105 test windows each, none
unmatched). V1 (KL equals the evaluator's) and V2 (mean TV ≤ Pinsker bound) hold for all 12.

| cell | TV median | TV mean | TV q90 | mean a_w | windows a_w ≥ 0.10 |
|---|---|---|---|---|---|
| r1, ε = 1 | 0.020–0.026 | 0.032–0.035 | 0.076–0.081 | 0.062–0.066 | 12.8–13.5 % |
| r3, ε = 1 | 0.015–0.018 | 0.027–0.030 | 0.070–0.076 | 0.047–0.055 | 9.6–11.5 % |
| r1, ε = ½ | 0.019–0.022 | 0.037–0.041 | 0.095–0.106 | 0.106–0.113 | 21.1–23.1 % |
| r3, ε = ½ | 0.019–0.027 | 0.036–0.039 | 0.094–0.100 | 0.096–0.099 | 19.5–20.5 % |

(Ranges are over seeds 1–3. r3 ε = 1 seeds 1–2 meet the "readable" rule and seed 3 does not, so the cell is Between
by the all-seeds condition.)

**What can be said without a general sentence:** trained learners' one-step outputs sit mostly near the boundary
the tolerance check located (median TV 0.015–0.027, against δ ≈ 0.02 where R stays readable). On average, 5–11 % of
the prior mass of the classes an output resembles at least as much as the truth differ from it in randomness by
≥ 0.1 bits; 10–23 % of windows carry ≥ 10 % such ambiguity. Ambiguity is higher at ε = ½ and on r1 than on r3.

## Second declared measurement (owner, 2026-10-15, after the whole-draft Claude review, before running)

The first measurement asked about R only. §4.2 frames the *kind* of uncertainty as pure randomness (G = 0) against
withheld state, and the two are different questions (Claude whole-draft review #1). Same 12 models, windows, Q and
look-alike set; a new disagreement test:
- a_w^G = law-mass share of the look-alike set A_w whose kind differs from the true class's, where kind is *pure*
  (G < 10⁻¹²) or *withheld* (G ≥ 0.1 bits), and a class with 0 < G < 0.1 has no kind and never disagrees.

The look-alike set is oracle-calibrated (its radius is the true class's own TV to the output), so a_w and a_w^G are
look-alike prior-mass shares, not monitor error rates. Reported beside the R version, with the TV tail (share of
windows with t_w > 0.05). The same declared reading thresholds apply. Rows pinned: `split-v2-rows-sha256-2026-10-15.txt`.
