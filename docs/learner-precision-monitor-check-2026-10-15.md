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
