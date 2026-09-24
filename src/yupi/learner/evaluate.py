"""The contract's evaluator (learner-model-vs-ceiling-contract v0.1.2;
trainer spec §3; plan Task 6) — the ONLY learner module that imports the
exact side.

Per test window and per prefix length k (k records seen, record k+1
predicted), from ONE forward pass over the window:

  ceiling   P*(Πr | Πw_{≤k}) from the prefix-k ceiling table, looked up by
            the pattern of the first k surface records (Π is invariant
            under σ, so the surface tokens pattern to the structural class);
            its five field conditionals at the realized record's pattern
            values, by successive marginalization (product = P*(ρ)).
  model     the softmax at each of the five field positions, projected to
            the field's pattern value: a bound entity -> its token; a fresh
            entity -> the sum over the drawable tokens of its type not yet
            used in the window (reserved tokens never count); KIND, MASKED,
            NONE -> the one token. The KIND conditional is taken given
            continuation (renormalized over non-PAD), and the end-of-window
            event is scored separately.

  structural_bits  Σ_j log2 P*(ρ_j | ρ_<j) − log2 P̃_M(ρ_j | surface prefix)
  structural_by_field  the five terms of that sum, reported per field (kind, actor, obj, related, lineage)
  naming_bits      Σ_{fresh j} [ −log2 n_unused_j − (log2 P_M(tok_j) − log2 P̃_M(ρ_j)) ]
  token_bits       model token cost − ceiling token cost over the five fields (given
                   continuation) == structural_bits + naming_bits, algebraically
  kind_kl_bits     the exact Σ_kind P*(kind) log2 P*(kind)/P_M(kind | non-PAD)
  end_bits         at the record boundary after k records: −log2 P_M(continue) + log2 P*(continue),
                   with P*(end | k, RESET) from pattern_end_probability — ONE branch of the
                   end-of-window process, so its mean alone may be negative;
  end_total_bits   per window, the sum over every boundary (continue at k = 1..n−1, end at n):
                   its mean is the KL of the end-of-window process and is ≥ 0 in expectation

Means over windows are estimates of the corresponding expected KLs (the
realized record is a sample from P*(· | Πw)); standard deviations and
standard errors are reported with every mean (contract §2.4).
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np

from yupi.corpus.vocab import ENTITY_TYPES, KINDS, MASKED, NONE, PAD, POOL_SIZES, RESERVED, RESET, TOKEN_ID, VOCAB, pool_tokens, token_type
from yupi.corpus.writer import read_split
from yupi.interfaces import MASKED as REC_MASKED
from yupi.learner.data import BOS, frame
from yupi.naming import pattern_all
from yupi.pattern_ceiling import Table
from yupi.pattern_filter import pattern_end_probability
from yupi.records import Record
from yupi.window import WindowLaw

LOG2 = math.log(2.0)
DRAWABLE = {et: frozenset(pool_tokens(et)[:POOL_SIZES[et] - RESERVED[et]]) for et in ENTITY_TYPES}
DRAWABLE_IDS = {et: np.array(sorted(TOKEN_ID[t] for t in DRAWABLE[et])) for et in ENTITY_TYPES}
KIND_IDS = np.array([TOKEN_ID[k] for k in KINDS if k != RESET])
PAD_ID = TOKEN_ID[PAD]
FIELDS = ("kind", "actor", "obj", "related", "lineage")


class MissingClass(KeyError):
    """A test window's pattern class is absent from the ceiling table — a finding."""


# ---- surface tokens -> records with token-valued entity fields ----------------------

def _entity(tok: str):
    if tok == MASKED:
        return REC_MASKED
    if tok == NONE:
        return None
    return tok


def surface_records(tokens: Iterable[str]) -> Tuple[bool, Tuple[Record, ...]]:
    """(reset flag, records) from a window's surface tokens; entity fields hold
    the surface TOKENS, so `pattern_all` yields the window's Π directly."""
    toks = list(tokens)
    reset = bool(toks) and toks[0] == RESET
    if reset:
        toks = toks[1:]
    if len(toks) % 5:
        raise ValueError("a window body is a whole number of five-token records")
    out = []
    for i in range(0, len(toks), 5):
        kind, a, o, rel, lin = toks[i:i + 5]
        if o == MASKED:
            obj = REC_MASKED
        elif o == NONE:
            obj = None
        else:
            obj = ("LOCK" if token_type(o) == "lock" else "DEV", o)
        out.append(Record(kind, _entity(a), obj, _entity(rel), _entity(lin)))
    return reset, tuple(out)


# ---- the ceiling side --------------------------------------------------------------

def field_ceiling(star: Dict[Record, Fraction], rho: Record) -> List[Fraction]:
    """Five conditionals P*(ρ_j | ρ_<j) from P*(Πr); their product is P*(ρ)."""
    cands = list(star.items())
    out = []
    for f in FIELDS:
        v = getattr(rho, f)
        den = sum((m for _, m in cands), Fraction(0))
        cands = [(r, m) for r, m in cands if getattr(r, f) == v]
        num = sum((m for _, m in cands), Fraction(0))
        if num == 0:
            raise ValueError(f"realized record {rho} has zero ceiling probability at field {f}")
        out.append(num / den)
    return out


def kind_marginal(star: Dict[Record, Fraction]) -> Dict[str, Fraction]:
    out: Dict[str, Fraction] = {}
    for r, m in star.items():
        out[r.kind] = out.get(r.kind, Fraction(0)) + m
    return out


def actor_entropy_given_kind(star: Dict[Record, Fraction], kind: str) -> Optional[float]:
    """H*(actor | kind, prefix) in bits: the exact observer's residual uncertainty
    about who acts, given that the next record has this kind (the ceiling the
    ACTOR-field excess on such records is measured against). None if P*(kind) = 0."""
    acc: Dict = {}
    for r, m in star.items():
        if r.kind == kind:
            acc[r.actor] = acc.get(r.actor, Fraction(0)) + m
    tot = sum(acc.values(), Fraction(0))
    if tot == 0:
        return None
    return float(-sum(float(q / tot) * math.log2(float(q / tot)) for q in acc.values() if q > 0))


# ---- the model side ----------------------------------------------------------------

def _consistent_ids(field: str, tok: str, used: Dict[str, set]) -> Tuple[np.ndarray, Optional[int], Optional[str]]:
    """(token ids consistent with the field's pattern value, n_unused if fresh else None, entity type or None)."""
    if field == "kind" or tok in (MASKED, NONE):
        return np.array([TOKEN_ID[tok]]), None, None
    et = token_type(tok)
    if et not in ENTITY_TYPES:
        raise ValueError(f"token {tok!r} of type {et} in an entity field")
    if tok in used[et]:
        return np.array([TOKEN_ID[tok]]), None, et
    unused = sorted(TOKEN_ID[t] for t in DRAWABLE[et] - used[et])
    if TOKEN_ID[tok] not in unused:
        raise ValueError(f"realized fresh token {tok!r} is not a drawable unused token")
    return np.array(unused), len(unused), et


def _logsumexp(a: np.ndarray) -> float:
    m = float(np.max(a))
    return m + math.log(float(np.sum(np.exp(a - m))))


def window_excess(lp5: np.ndarray, next_tokens: Tuple[str, ...], used: Dict[str, set],
                  star: Dict[Record, Fraction], rho: Record) -> dict:
    """The five-field excesses for one realized next record. `lp5` is [5, 156]
    natural-log softmax at the five positions predicting `next_tokens`;
    `used` is mutated: the record's fresh tokens are added as they occur."""
    ceil = field_ceiling(star, rho)
    structural = naming = ceiling_tok = model_tok = 0.0
    by_field = {}
    for j, (f, tok) in enumerate(zip(FIELDS, next_tokens)):
        lp = lp5[j]
        if f == "kind":                                  # given continuation: renormalize over non-PAD
            cont = _logsumexp(np.delete(lp, PAD_ID))
            lp = lp - cont
        ids, n_unused, et = _consistent_ids(f, tok, used)
        lp_pat = _logsumexp(lp[ids])                     # log P̃_M(pattern value)
        lp_tok = float(lp[TOKEN_ID[tok]])                # log P_M(realized token)
        c = math.log2(float(ceil[j]))
        by_field[f] = c - lp_pat / LOG2
        structural += by_field[f]
        ceiling_tok += -c
        model_tok += -lp_tok / LOG2
        if n_unused is not None:
            naming += (-math.log2(n_unused)) - (lp_tok - lp_pat) / LOG2
            ceiling_tok += math.log2(n_unused)
        if et is not None:
            used[et].add(tok)
    km = kind_marginal(star)
    lp0 = lp5[0] - _logsumexp(np.delete(lp5[0], PAD_ID))
    kind_kl = sum(float(q) * (math.log2(float(q)) - float(lp0[TOKEN_ID[k]]) / LOG2) for k, q in km.items())
    return dict(structural_bits=structural, naming_bits=naming, token_bits=model_tok - ceiling_tok,
                kind_kl_bits=kind_kl, ceiling_token_bits=ceiling_tok, model_token_bits=model_tok,
                structural_by_field=by_field)


def end_excess(lp: np.ndarray, ended: bool, p_end: Fraction) -> float:
    """−log2 P_M(realized continue/end) + log2 P*(same) at a record boundary."""
    lp_pad = float(lp[PAD_ID])
    lp_event = lp_pad if ended else math.log1p(-math.exp(lp_pad)) if lp_pad < -1e-12 else -math.inf
    p = float(p_end) if ended else 1.0 - float(p_end)
    if p == 0.0:
        raise ValueError("realized end-of-window event has zero ceiling probability")
    return -lp_event / LOG2 + math.log2(p)


# ---- the loop over a split -----------------------------------------------------------

def _stats(xs: List[float]) -> dict:
    a = np.asarray(xs, dtype=np.float64)
    n = len(a)
    if n == 0:
        return dict(n=0, mean=None, sd=None, se=None)
    sd = float(a.std(ddof=1)) if n > 1 else 0.0
    return dict(n=n, mean=float(a.mean()), sd=sd, se=sd / math.sqrt(n))


def evaluate(logprobs_fn: Callable[[np.ndarray], np.ndarray], corpus_dir, law: WindowLaw,
             tables: Dict[int, Table], k_list: Iterable[int], seq_len: int, n: Optional[int] = None,
             batch: int = 512, split: str = "test",
             on_window: Optional[Callable[[int, int, tuple, dict], None]] = None) -> dict:
    """Per k: statistics of the per-window excesses over the split's windows
    that have at least k + 1 records. `logprobs_fn(inputs[N, seq_len]) ->
    [N, seq_len, 156]` natural-log softmax; position p predicts window
    token p (inputs are BOS + window). Missing classes are counted, never
    coerced; the window is skipped for that k. `on_window(i, k, key, ex)`,
    if given, is called once per scored (window index, k) with the window's
    ceiling-table key and its per-window excess dict (structural_by_field
    included) — the aggregates below are built from exactly these values."""
    rows = read_split(corpus_dir, split)
    if n is not None:
        rows = rows[:n]
    windows = [tuple(VOCAB[t] for t in w) for w, _ in rows]
    per_k = {k: {key: [] for key in ("structural_bits", "naming_bits", "token_bits", "kind_kl_bits",
                                     "ceiling_token_bits", "model_token_bits", "end_bits")} for k in k_list}
    by_field = {k: {f: [] for f in FIELDS} for k in k_list}
    missing = {k: 0 for k in k_list}
    too_short = {k: 0 for k in k_list}
    final_end, end_total = [], []
    for b0 in range(0, len(windows), batch):
        chunk = windows[b0:b0 + batch]
        x, _, _ = frame([tuple(TOKEN_ID[t] for t in w) for w in chunk], seq_len)
        lp = logprobs_fn(x)
        for i, toks in enumerate(chunk):
            reset, recs = surface_records(toks)
            off = 1 if reset else 0
            n_rec = len(recs)
            for k in k_list:
                if k + 1 > n_rec:
                    too_short[k] += 1
                    continue
                pw, _ = pattern_all(recs[:k])
                key = (reset, pw)
                if key not in tables[k]:
                    missing[k] += 1
                    continue
                _, star = tables[k][key]
                rho = pattern_all(recs[:k + 1])[0][-1]
                used = {et: set() for et in ENTITY_TYPES}
                for t in toks[off:off + 5 * k]:
                    tt = token_type(t)
                    if tt in ENTITY_TYPES:
                        used[tt].add(t)
                p0 = off + 5 * k
                ex = window_excess(lp[i, p0:p0 + 5], tuple(toks[p0:p0 + 5]), used, star, rho)
                ex["end_bits"] = end_excess(lp[i, p0], False, pattern_end_probability(law, k, reset))
                if on_window is not None:
                    on_window(b0 + i, k, key, dict(ex))
                for f, v in ex.pop("structural_by_field").items():
                    by_field[k][f].append(v)
                for key2, v in ex.items():
                    per_k[k][key2].append(v)
            # the final boundary: the window ended after n_rec records; and the whole end-of-window process
            fe = end_excess(lp[i, off + 5 * n_rec], True, pattern_end_probability(law, n_rec, reset))
            final_end.append(fe)
            end_total.append(fe + sum(end_excess(lp[i, off + 5 * kk], False, pattern_end_probability(law, kk, reset))
                                      for kk in range(1, n_rec)))
    out = {"n_windows": len(windows), "per_k": {}, "final_end_bits": _stats(final_end), "end_total_bits": _stats(end_total)}
    for k in k_list:
        out["per_k"][k] = {key: _stats(v) for key, v in per_k[k].items()}
        out["per_k"][k]["structural_by_field"] = {f: _stats(v) for f, v in by_field[k].items()}
        out["per_k"][k]["missing_classes"] = missing[k]
        out["per_k"][k]["too_short"] = too_short[k]
        if per_k[k]["structural_bits"]:
            ident = np.asarray(per_k[k]["token_bits"]) - np.asarray(per_k[k]["structural_bits"]) - np.asarray(per_k[k]["naming_bits"])
            out["per_k"][k]["identity_max_abs"] = float(np.max(np.abs(ident)))
    return out


def torch_logprobs_fn(model, device: str = "cpu", batch: int = 512) -> Callable[[np.ndarray], np.ndarray]:
    """Wrap a Decoder as the evaluator's model function (float64 log-softmax)."""
    import torch

    def fn(x: np.ndarray) -> np.ndarray:
        model.eval()
        out = []
        with torch.no_grad():
            for i in range(0, len(x), batch):
                ids = torch.from_numpy(x[i:i + batch]).to(device)
                out.append(torch.log_softmax(model(ids).double(), dim=-1).cpu().numpy())
        return np.concatenate(out, axis=0)
    return fn
