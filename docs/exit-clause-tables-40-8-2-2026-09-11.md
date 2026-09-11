# Exit-clause numeric tables: C1' looping world, (T_ep=40, L=8, B=2), rungs r0-r4

Frozen law per E3/D4 (docs/d4-budget-freeze-v0.1.md); delta = 0.01 bits (v0.2.5).

All numbers read directly from the JSON artifacts listed in Provenance; no value below was computed except differences (gaps), min/max selection, and ratios to delta, all shown with their formulas.


## eps=1

### Table 1 (eps=1): mean bits per rung

| quantity | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| Q1[L0] | 0.9946 | 0.1609 | 0.1270 | 0.0170 | 0.0170 |
| Q1[L1] | 0.6154 | 0.1021 | 0.0544 | 0.0404 | 0.0402 |
| Q2[T0] | 1.1765 | 0.0996 | 0.0906 | 0.0584 | 0.0502 |
| Q2[T1] | 1.0585 | 0.0522 | 0.0444 | 0.0229 | 0.0228 |
| Q2[T2] | 1.0453 | 0.0890 | 0.0795 | 0.0458 | 0.0456 |
| Q2[T3] | 0.8303 | 0.0179 | 0.0178 | 0.0162 | 0.0117 |
| Q3[D0] | 0.1949 | 0.0313 | 0.0312 | 0.0283 | 0.0141 |
| Q5[T0,T1] | 0.3393 | 0.0395 | 0.0299 | 0.0244 | 0.0219 |
| Q5[T0,T2] | 0.1320 | 0.0160 | 0.0126 | 0.0058 | 0.0048 |
| Q5[T0,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T1,T0] | 0.1984 | 0.0193 | 0.0151 | 0.0067 | 0.0067 |
| Q5[T1,T2] | 0.1797 | 0.0210 | 0.0163 | 0.0074 | 0.0074 |
| Q5[T1,T3] | 0.0619 | 0.0046 | 0.0004 | 0.0004 | 0.0004 |
| Q5[T2,T0] | 0.1682 | 0.0177 | 0.0136 | 0.0058 | 0.0058 |
| Q5[T2,T1] | 0.3432 | 0.0414 | 0.0308 | 0.0237 | 0.0237 |
| Q5[T2,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T0] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T1] | 0.0487 | 0.0002 | 0.0002 | 0.0002 | 0.0002 |
| Q5[T3,T2] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5joint | 1.0571 | 0.1177 | 0.0914 | 0.0642 | 0.0606 |
| H(S) | 3.9474 | 0.6008 | 0.5277 | 0.4046 | 0.3898 |
| Q4 gap (W=4) | 0.7029 | 0.1281 | 0.1086 | 0.0795 | 0.0761 |
| kinds2 gap | 0.7544 | 0.1858 | 0.1572 | 0.1239 | 0.1191 |
| P-next gap | 0.4418 | 0.1503 | 0.1346 | 0.1060 | 0.1026 |

### Table 2 (eps=1): adjacent-pair gaps (coarser rung minus finer rung, bits)

| quantity | r0→r1 | r1→r2 | r2→r3 | r3→r4 |
|---|---|---|---|---|
| Q1[L0] | 0.8337 | 0.0339 | 0.1100 | 0.0000 |
| Q1[L1] | 0.5132 | 0.0477 | 0.0140 | 0.0002 |
| Q2[T0] | 1.0769 | 0.0090 | 0.0322 | 0.0082 |
| Q2[T1] | 1.0062 | 0.0078 | 0.0215 | 0.0001 |
| Q2[T2] | 0.9564 | 0.0095 | 0.0337 | 0.0002 |
| Q2[T3] | 0.8124 | 0.0001 | 0.0015 | 0.0045 |
| Q3[D0] | 0.1636 | 0.0001 | 0.0029 | 0.0142 |
| Q5[T0,T1] | 0.2998 | 0.0096 | 0.0055 | 0.0025 |
| Q5[T0,T2] | 0.1160 | 0.0034 | 0.0067 | 0.0010 |
| Q5[T0,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T1,T0] | 0.1791 | 0.0042 | 0.0084 | 0.0000 |
| Q5[T1,T2] | 0.1587 | 0.0047 | 0.0089 | 0.0000 |
| Q5[T1,T3] | 0.0572 | 0.0042 | 0.0000 | 0.0000 |
| Q5[T2,T0] | 0.1505 | 0.0041 | 0.0078 | 0.0000 |
| Q5[T2,T1] | 0.3018 | 0.0106 | 0.0071 | 0.0000 |
| Q5[T2,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T0] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T1] | 0.0485 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T2] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5joint | 0.9394 | 0.0263 | 0.0272 | 0.0036 |
| H(S) | 3.3465 | 0.0731 | 0.1231 | 0.0148 |
| Q4 gap (W=4) | 0.5748 | 0.0195 | 0.0291 | 0.0034 |
| kinds2 gap | 0.5686 | 0.0286 | 0.0333 | 0.0048 |
| P-next gap | 0.2915 | 0.0157 | 0.0286 | 0.0034 |
| **max over statutory queries** | 1.0769 (Q2[T0]) | 0.0477 (Q1[L1]) | 0.1100 (Q1[L0]) | 0.0142 (Q3[D0]) |
| **ratio to delta=0.01** | 107.69x | 4.77x | 11.00x | 1.42x |

### Table 3 (eps=1): r1→r4 total gap per quantity

| quantity | r1→r4 gap (bits) |
|---|---|
| Q1[L0] | 0.1439 |
| Q1[L1] | 0.0619 |
| Q2[T0] | 0.0494 |
| Q2[T1] | 0.0294 |
| Q2[T2] | 0.0433 |
| Q2[T3] | 0.0061 |
| Q3[D0] | 0.0172 |
| Q5[T0,T1] | 0.0176 |
| Q5[T0,T2] | 0.0112 |
| Q5[T0,T3] | 0.0000 |
| Q5[T1,T0] | 0.0126 |
| Q5[T1,T2] | 0.0136 |
| Q5[T1,T3] | 0.0042 |
| Q5[T2,T0] | 0.0119 |
| Q5[T2,T1] | 0.0177 |
| Q5[T2,T3] | 0.0000 |
| Q5[T3,T0] | 0.0000 |
| Q5[T3,T1] | 0.0000 |
| Q5[T3,T2] | 0.0000 |
| Q5joint | 0.0571 |
| H(S) | 0.2110 |
| Q4 gap (W=4) | 0.0520 |
| kinds2 gap | 0.0666 |
| P-next gap | 0.0477 |

Max over statutory queries: **Q1[L0]** = 0.1439 bits (14.39x delta).

### Table 4 (eps=1): divergent-pair mass per rung (predictive-targets artifact, field divergent.mass)

| r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| 0.2018 | 0.6085 | 0.6377 | 0.7113 | 0.6698 |


## eps=1/2

### Table 1 (eps=1/2): mean bits per rung

| quantity | r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|---|
| Q1[L0] | 0.8090 | 0.0796 | 0.0555 | 0.0032 | 0.0032 |
| Q1[L1] | 0.5279 | 0.0682 | 0.0315 | 0.0210 | 0.0209 |
| Q2[T0] | 1.0409 | 0.0453 | 0.0415 | 0.0255 | 0.0186 |
| Q2[T1] | 0.9366 | 0.0152 | 0.0110 | 0.0034 | 0.0034 |
| Q2[T2] | 0.9109 | 0.0497 | 0.0396 | 0.0221 | 0.0220 |
| Q2[T3] | 0.7742 | 0.0062 | 0.0062 | 0.0059 | 0.0031 |
| Q3[D0] | 0.1697 | 0.0247 | 0.0247 | 0.0210 | 0.0098 |
| Q5[T0,T1] | 0.2829 | 0.0170 | 0.0105 | 0.0093 | 0.0068 |
| Q5[T0,T2] | 0.1318 | 0.0076 | 0.0055 | 0.0040 | 0.0020 |
| Q5[T0,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T1,T0] | 0.1928 | 0.0079 | 0.0057 | 0.0015 | 0.0015 |
| Q5[T1,T2] | 0.1350 | 0.0074 | 0.0035 | 0.0012 | 0.0012 |
| Q5[T1,T3] | 0.0588 | 0.0027 | 0.0001 | 0.0001 | 0.0001 |
| Q5[T2,T0] | 0.1230 | 0.0054 | 0.0030 | 0.0006 | 0.0006 |
| Q5[T2,T1] | 0.3285 | 0.0239 | 0.0161 | 0.0130 | 0.0130 |
| Q5[T2,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T0] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T1] | 0.0522 | 0.0001 | 0.0001 | 0.0001 | 0.0001 |
| Q5[T3,T2] | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5joint | 0.9592 | 0.0576 | 0.0398 | 0.0288 | 0.0243 |
| H(S) | 3.3711 | 0.2963 | 0.2400 | 0.1774 | 0.1658 |
| Q4 gap (W=4) | 0.7161 | 0.0703 | 0.0555 | 0.0395 | 0.0368 |
| kinds2 gap | 0.7973 | 0.1154 | 0.0916 | 0.0716 | 0.0683 |
| P-next gap | 0.4245 | 0.0922 | 0.0791 | 0.0590 | 0.0561 |

### Table 2 (eps=1/2): adjacent-pair gaps (coarser rung minus finer rung, bits)

| quantity | r0→r1 | r1→r2 | r2→r3 | r3→r4 |
|---|---|---|---|---|
| Q1[L0] | 0.7295 | 0.0241 | 0.0523 | 0.0000 |
| Q1[L1] | 0.4597 | 0.0366 | 0.0105 | 0.0001 |
| Q2[T0] | 0.9957 | 0.0038 | 0.0159 | 0.0069 |
| Q2[T1] | 0.9215 | 0.0041 | 0.0076 | 0.0000 |
| Q2[T2] | 0.8612 | 0.0101 | 0.0175 | 0.0000 |
| Q2[T3] | 0.7680 | 0.0000 | 0.0003 | 0.0028 |
| Q3[D0] | 0.1450 | 0.0001 | 0.0036 | 0.0113 |
| Q5[T0,T1] | 0.2660 | 0.0065 | 0.0012 | 0.0025 |
| Q5[T0,T2] | 0.1242 | 0.0021 | 0.0016 | 0.0020 |
| Q5[T0,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T1,T0] | 0.1849 | 0.0022 | 0.0042 | 0.0000 |
| Q5[T1,T2] | 0.1276 | 0.0040 | 0.0022 | 0.0000 |
| Q5[T1,T3] | 0.0561 | 0.0026 | 0.0000 | 0.0000 |
| Q5[T2,T0] | 0.1176 | 0.0024 | 0.0024 | 0.0000 |
| Q5[T2,T1] | 0.3046 | 0.0078 | 0.0031 | 0.0000 |
| Q5[T2,T3] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T0] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T1] | 0.0521 | 0.0000 | 0.0000 | 0.0000 |
| Q5[T3,T2] | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Q5joint | 0.9016 | 0.0178 | 0.0110 | 0.0045 |
| H(S) | 3.0748 | 0.0563 | 0.0626 | 0.0116 |
| Q4 gap (W=4) | 0.6458 | 0.0148 | 0.0160 | 0.0027 |
| kinds2 gap | 0.6818 | 0.0238 | 0.0200 | 0.0033 |
| P-next gap | 0.3323 | 0.0131 | 0.0201 | 0.0029 |
| **max over statutory queries** | 0.9957 (Q2[T0]) | 0.0366 (Q1[L1]) | 0.0523 (Q1[L0]) | 0.0113 (Q3[D0]) |
| **ratio to delta=0.01** | 99.57x | 3.66x | 5.23x | 1.13x |

### Table 3 (eps=1/2): r1→r4 total gap per quantity

| quantity | r1→r4 gap (bits) |
|---|---|
| Q1[L0] | 0.0764 |
| Q1[L1] | 0.0473 |
| Q2[T0] | 0.0267 |
| Q2[T1] | 0.0118 |
| Q2[T2] | 0.0277 |
| Q2[T3] | 0.0031 |
| Q3[D0] | 0.0150 |
| Q5[T0,T1] | 0.0101 |
| Q5[T0,T2] | 0.0057 |
| Q5[T0,T3] | 0.0000 |
| Q5[T1,T0] | 0.0064 |
| Q5[T1,T2] | 0.0062 |
| Q5[T1,T3] | 0.0026 |
| Q5[T2,T0] | 0.0048 |
| Q5[T2,T1] | 0.0109 |
| Q5[T2,T3] | 0.0000 |
| Q5[T3,T0] | 0.0000 |
| Q5[T3,T1] | 0.0000 |
| Q5[T3,T2] | 0.0000 |
| Q5joint | 0.0332 |
| H(S) | 0.1305 |
| Q4 gap (W=4) | 0.0335 |
| kinds2 gap | 0.0471 |
| P-next gap | 0.0362 |

Max over statutory queries: **Q1[L0]** = 0.0764 bits (7.64x delta).

### Table 4 (eps=1/2): divergent-pair mass per rung (predictive-targets artifact, field divergent.mass)

| r0 | r1 | r2 | r3 | r4 |
|---|---|---|---|---|
| 0.2024 | 0.6598 | 0.6902 | 0.7642 | 0.7184 |


## Provenance

### Files used


**eps = 1**

- r0: `docs/c1prime-loop-query-ceilings-40-8-2-r0-2026-09-06.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r0-W4-2026-09-06.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r0-2026-09-06.json`
- r1: `docs/c1prime-loop-query-ceilings-40-8-2-r1-2026-09-05.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r1-W4-2026-09-05.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r1-2026-09-05.json`
- r2: `docs/c1prime-loop-query-ceilings-40-8-2-r2-2026-09-05.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r2-W4-2026-09-05.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r2-2026-09-05.json`
- r3: `docs/c1prime-loop-query-ceilings-40-8-2-r3-2026-09-06.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r3-W4-2026-09-06.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r3-2026-09-06.json`
- r4: `docs/c1prime-loop-query-ceilings-40-8-2-r4-2026-09-04.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r4-W4-2026-09-05.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r4-2026-09-05.json`

**eps = 1/2**

- r0: `docs/c1prime-loop-query-ceilings-40-8-2-r0-2026-09-06-eps1_2.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r0-W4-2026-09-06-eps1_2.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r0-2026-09-06-eps1_2.json`
- r1: `docs/c1prime-loop-query-ceilings-40-8-2-r1-2026-09-05-eps1_2.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r1-W4-2026-09-05-eps1_2.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r1-2026-09-05-eps1_2.json`
- r2: `docs/c1prime-loop-query-ceilings-40-8-2-r2-2026-09-05-eps1_2.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r2-W4-2026-09-05-eps1_2.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r2-2026-09-05-eps1_2.json`
- r3: `docs/c1prime-loop-query-ceilings-40-8-2-r3-2026-09-06-eps1_2.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r3-W4-2026-09-06-eps1_2.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r3-2026-09-06-eps1_2.json`
- r4: `docs/c1prime-loop-query-ceilings-40-8-2-r4-2026-09-05-eps1_2.json`, `docs/c1prime-loop-q4-ceilings-40-8-2-r4-W4-2026-09-05-eps1_2.json`, `docs/c1prime-loop-predictive-targets-40-8-2-r4-2026-09-05-eps1_2.json`

### Regeneration snippet

```python
import json, pathlib
DOCS = pathlib.Path("docs")
# For a given (eps, rung), e.g. eps='1', rung='r4':
q = json.load(open(DOCS / "c1prime-loop-query-ceilings-40-8-2-r4-2026-09-04.json"))["rows"][0]
q4 = json.load(open(DOCS / "c1prime-loop-q4-ceilings-40-8-2-r4-W4-2026-09-05.json"))["rows"][0]
t = json.load(open(DOCS / "c1prime-loop-predictive-targets-40-8-2-r4-2026-09-05.json"))["rows"][0]

stat = [k for k in q['queries'] if not k.startswith('Q4proxy') and k != 'Q3thr[D0]']  # statutory query set
mean_bits = {k: q['queries'][k]['mean_bits'] for k in stat}
H_S = q['mean_state_entropy_bits']
q4_gap = q4['gap_bits']
kinds2_gap = t['means']['kinds2']['gap']
pnext_gap = t['means']['pnext']['gap']
divergent_mass = t['divergent']['mass']
# Adjacent-pair gap for query k between coarser rung a and finer rung b:
# gap = mean_bits_a[k] - mean_bits_b[k]
```

Extracted 2026-09-11 by a Sonnet subagent from the thirty artifacts alone; the snippet above reproduces every table. Checked against `tests/test_c1prime_loop_ceilings.py` (all adjacent maxima match).


## Fields not found / not applicable

- P-next: read from `means.pnext.gap` (the predictive-targets artifact's P-next quantity is named `pnext`, matching the pin test's `t["means"]["pnext"]["gap"]`).

- kinds2 ("next-2-kinds"): read from `means.kinds2.gap`.

- Divergent-pair mass: present directly as `divergent.mass` in every predictive-targets artifact used (not absent).

- Q4 gap: read from `gap_bits` in the q4-ceilings artifact (W=4), i.e. total_bits - irreducible_bits at that rung; this is the Q4 gap requested, not a cross-rung difference.

- `ttw4` and `lineage4` means (also present under `means` in the predictive-targets artifact) were not requested by the task's statutory list and are omitted from the tables; they exist in the source files if needed.
