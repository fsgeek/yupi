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
  structural_by_field  the five terms of that sum, reported per field (kind, actor, obj, related, lineage);
                   at the relay rung r1ʀ ("r1R") the OBJECT slot carries the relay (a KIND
                   literal, interfaces.Lit) and its term is reported as "relay", never as "obj"
                   and never inside "kind" (relay pre-registration v0.1, frozen analysis); at the
                   decoy r1ᴅ ("r1D") and self-copy r1ꜱ ("r1S") rungs it is reported as "decoy" and
                   "self" (three-arm design v0.1 §3)
  naming_bits      Σ_{fresh j} [ −log2 n_unused_j − (log2 P_M(tok_j) − log2 P̃_M(ρ_j)) ]
  token_bits       model token cost − ceiling token cost over the five fields (given
                   continuation) == structural_bits + naming_bits, algebraically
  kind_kl_bits     the exact Σ_kind P*(kind) log2 P*(kind)/P_M(kind | non-PAD)
  end_bits         at the record boundary after k records: −log2 P_M(continue) + log2 P*(continue),
                   with P*(end | k, RESET) from pattern_end_probability — ONE branch of the
                   end-of-window process, so its mean alone may be negative;
  end_total_bits   per window, the sum over every boundary (continue at k = 1..n−1, end at n):
                   its mean is the KL of the end-of-window process and is ≥ 0 in expectation

The rung is the corpus manifest's (`evaluate` reads it); a caller may pass it, and a
disagreement is refused. At a window-level rung (interfaces.WINDOW_RUNGS: r1R, r1D, r1S)
a KIND token in the OBJECT slot is a Lit; at every other rung it is an error.

Means over windows are estimates of the corresponding expected KLs (the
realized record is a sample from P*(· | Πw)); standard deviations and
standard errors are reported with every mean (contract §2.4).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from fractions import Fraction
from typing import Sequence, Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np

from yupi.corpus.vocab import ENTITY_TYPES, KINDS, MASKED, NONE, PAD, POOL_SIZES, RESERVED, RESET, TOKEN_ID, VOCAB, pool_tokens, token_type
from yupi.corpus.writer import read_split
from yupi.interfaces import MASKED as REC_MASKED, RELAY_RUNGS, WINDOW_RUNGS, Lit  # noqa: F401
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
RELAY_FIELDS = ("kind", "actor", "relay", "related", "lineage")     # reported names at a relay rung
# the OBJECT slot's reported name at each window-level rung (three-arm design v0.1 §3)
WINDOW_FIELD = {"r1R": "relay", "r1D": "decoy", "r1S": "self"}
assert set(WINDOW_FIELD) == set(WINDOW_RUNGS), "every window-level rung needs a reported field name"
KIND_TOKENS = frozenset(KINDS)


def field_names(rung: Optional[str]) -> Tuple[str, ...]:
    """The five reported field names at a rung: FIELDS, RELAY_FIELDS at the relay rung,
    and at any window-level rung the OBJECT slot under that rung's WINDOW_FIELD name."""
    if rung not in WINDOW_RUNGS:
        return FIELDS
    if rung == "r1R":
        return RELAY_FIELDS
    return FIELDS[:2] + (WINDOW_FIELD[rung],) + FIELDS[3:]


def manifest_rung(corpus_dir) -> str:
    """The rung recorded in a corpus directory's manifest.json."""
    return json.loads((Path(corpus_dir) / "manifest.json").read_text())["rung"]


class MissingClass(KeyError):
    """A test window's pattern class is absent from the ceiling table — a finding."""


# ---- surface tokens -> records with token-valued entity fields ----------------------

def _entity(tok: str):
    if tok == MASKED:
        return REC_MASKED
    if tok == NONE:
        return None
    return tok


def surface_records(tokens: Iterable[str], rung: Optional[str] = None) -> Tuple[bool, Tuple[Record, ...]]:
    """(reset flag, records) from a window's surface tokens; entity fields hold
    the surface TOKENS, so `pattern_all` yields the window's Π directly.

    `rung` (the corpus manifest's) decides the OBJECT slot's reading: at a
    window-level rung (r1R, r1D, r1S) it must be a KIND token (-> interfaces.Lit) or NONE; at any other
    given rung a KIND token there is an error. With no rung (callers that predate
    the relay, among them the frozen scripts/implicit_info_bintest.py, which cannot
    pass one) a KIND token in the OBJECT slot is read as a Lit: that is the only
    reading it has in any corpus, and no r0–r4 corpus contains one, so their
    records are unchanged."""
    relay = rung in WINDOW_RUNGS
    toks = list(tokens)
    reset = bool(toks) and toks[0] == RESET
    if reset:
        toks = toks[1:]
    if len(toks) % 5:
        raise ValueError("a window body is a whole number of five-token records")
    out = []
    for i in range(0, len(toks), 5):
        kind, a, o, rel, lin = toks[i:i + 5]
        if o in KIND_TOKENS:
            if rung is not None and not relay:
                raise ValueError(f"a KIND token {o!r} in the OBJECT slot at rung {rung!r}")
            obj = Lit(o)
        elif relay and o != NONE:
            raise ValueError(f"the relay slot at rung {rung!r} holds {o!r}, not a KIND or NONE")
        elif o == MASKED:
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


def actor_pattern_dist(star: Dict[Record, Fraction], kind: str, n_seen: int) -> Dict:
    """P*(actor | kind, prefix) over pattern actor classes: the seen threads' pattern
    indices 0..n_seen−1 and "fresh" (an actor not yet seen; its pattern index is
    n_seen). {} if P*(kind) = 0."""
    acc: Dict = {}
    for r, m in star.items():
        if r.kind == kind and r.actor is not None:
            key = "fresh" if r.actor >= n_seen else int(r.actor)
            acc[key] = acc.get(key, Fraction(0)) + m
    tot = sum(acc.values(), Fraction(0))
    return {k: q / tot for k, q in acc.items()} if tot else {}


def model_actor_dist(lp_row: np.ndarray, seen_tokens: Sequence[str]) -> Tuple[Dict, float]:
    """The model's distribution over the same classes from one natural-log softmax
    row: mass on each seen thread token by its pattern index, the summed mass on
    every unused thread token as "fresh", renormalized over thread tokens; second
    value is the mass the model put outside thread tokens."""
    p = np.exp(lp_row)
    thread_ids = [TOKEN_ID[t] for t in VOCAB if token_type(t) == "thread"]
    seen_ids = [TOKEN_ID[t] for t in seen_tokens]
    on_threads = float(p[thread_ids].sum())
    out: Dict = {i: float(p[tid]) for i, tid in enumerate(seen_ids)}
    out["fresh"] = float(p[[tid for tid in thread_ids if tid not in set(seen_ids)]].sum())
    return {k: v / on_threads for k, v in out.items()} if on_threads > 0 else out, 1.0 - on_threads


def kind_belief(star: Dict[Record, Fraction]) -> np.ndarray:
    """P*(kind_{k+1} | prefix) as a vector over KINDS (the exact next-kind belief; the
    belief-geometry target of docs/superpowers/specs/2026-09-24-belief-geometry-design.md)."""
    km = kind_marginal(star)
    return np.array([float(km.get(k, Fraction(0))) for k in KINDS], dtype=np.float64)


def kind_output(lp_row: np.ndarray) -> Tuple[np.ndarray, float]:
    """The model's next-kind distribution at a boundary row: P_M(kind | non-PAD) over
    KINDS (the evaluator's kind_kl convention: renormalized over non-PAD only, so mass
    on non-kind tokens is not redistributed) and the mass it put on non-kind tokens."""
    lp = lp_row - _logsumexp(np.delete(lp_row, PAD_ID))
    p = np.exp(np.array([lp[TOKEN_ID[k]] for k in KINDS]))
    return p, float(1.0 - p.sum())


def kl_bits_vec(p: np.ndarray, q: np.ndarray) -> float:
    """Σ_i p_i log2(p_i / q_i) over the support of p (q floored at 1e-300)."""
    m = p > 0
    return float((p[m] * (np.log2(p[m]) - np.log2(np.maximum(q[m], 1e-300)))).sum())


# ---- the model side ----------------------------------------------------------------

def _consistent_ids(field: str, tok: str, used: Dict[str, set],
                    relay: bool = False) -> Tuple[np.ndarray, Optional[int], Optional[str]]:
    """(token ids consistent with the field's pattern value, n_unused if fresh else None, entity type or None).
    With `relay`, the OBJECT slot's KIND token is a literal: its one token."""
    if field == "kind" or tok in (MASKED, NONE) or (relay and field == "obj" and tok in KIND_TOKENS):
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
                  star: Dict[Record, Fraction], rho: Record, rung: Optional[str] = None) -> dict:
    """The five-field excesses for one realized next record. `lp5` is [5, 156]
    natural-log softmax at the five positions predicting `next_tokens`;
    `used` is mutated: the record's fresh tokens are added as they occur.
    At a window-level rung the OBJECT slot is the rung's literal, reported under
    field_names(rung) ("relay" at r1R)."""
    relay = rung in WINDOW_RUNGS
    names = field_names(rung)
    ceil = field_ceiling(star, rho)
    structural = naming = ceiling_tok = model_tok = 0.0
    by_field = {}
    for j, (f, name, tok) in enumerate(zip(FIELDS, names, next_tokens)):
        lp = lp5[j]
        if f == "kind":                                  # given continuation: renormalize over non-PAD
            cont = _logsumexp(np.delete(lp, PAD_ID))
            lp = lp - cont
        ids, n_unused, et = _consistent_ids(f, tok, used, relay)
        lp_pat = _logsumexp(lp[ids])                     # log P̃_M(pattern value)
        lp_tok = float(lp[TOKEN_ID[tok]])                # log P_M(realized token)
        c = math.log2(float(ceil[j]))
        by_field[name] = c - lp_pat / LOG2
        structural += by_field[name]
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
             on_window: Optional[Callable[[int, int, tuple, dict], None]] = None,
             rung: Optional[str] = None) -> dict:
    """Per k: statistics of the per-window excesses over the split's windows
    that have at least k + 1 records. `logprobs_fn(inputs[N, seq_len]) ->
    [N, seq_len, 156]` natural-log softmax; position p predicts window
    token p (inputs are BOS + window). Missing classes are counted, never
    coerced; the window is skipped for that k. `on_window(i, k, key, ex)`,
    if given, is called once per scored (window index, k) with the window's
    ceiling-table key and its per-window excess dict (structural_by_field
    included) — the aggregates below are built from exactly these values.
    The rung is the corpus manifest's; a `rung` argument that disagrees with it
    is refused (ValueError)."""
    m_rung = manifest_rung(corpus_dir)
    if rung is not None and rung != m_rung:
        raise ValueError(f"rung {rung!r} disagrees with the corpus manifest's {m_rung!r}")
    rung = m_rung
    names = field_names(rung)
    rows = read_split(corpus_dir, split)
    if n is not None:
        rows = rows[:n]
    windows = [tuple(VOCAB[t] for t in w) for w, _ in rows]
    per_k = {k: {key: [] for key in ("structural_bits", "naming_bits", "token_bits", "kind_kl_bits",
                                     "ceiling_token_bits", "model_token_bits", "end_bits")} for k in k_list}
    by_field = {k: {f: [] for f in names} for k in k_list}
    missing = {k: 0 for k in k_list}
    too_short = {k: 0 for k in k_list}
    final_end, end_total = [], []
    for b0 in range(0, len(windows), batch):
        chunk = windows[b0:b0 + batch]
        x, _, _ = frame([tuple(TOKEN_ID[t] for t in w) for w in chunk], seq_len)
        lp = logprobs_fn(x)
        for i, toks in enumerate(chunk):
            reset, recs = surface_records(toks, rung)
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
                ex = window_excess(lp[i, p0:p0 + 5], tuple(toks[p0:p0 + 5]), used, star, rho, rung)
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
