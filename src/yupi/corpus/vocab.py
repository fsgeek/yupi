"""Corpus vocabulary (design v0.1 §4; Part I D5: one schema, one vocabulary
across every rung and ε; a rung differs only in how many MASKED it emits).

Order is fixed and versioned: PAD (id 0), MASKED, NONE, the nine event kinds
of Part II §4 in sorted order (RESET among them — the RESET record is the
single token "RESET"), then the four pools. Pinned by tests/test_corpus_vocab.py.
"""
import hashlib

VOCAB_VERSION = 1

PAD, MASKED, NONE, RESET = "PAD", "MASKED", "NONE", "RESET"
KINDS = ("ACQUIRE", "BLOCK", "DISPATCH", "IDLE", "IO_COMPLETE", "IO_ISSUE",
         "RELEASE", "RESET", "STEP")                          # Part II §4, sorted

ENTITY_TYPES = ("thread", "lock", "device", "request")
POOL_SIZES = {"thread": 64, "lock": 32, "device": 16, "request": 32}   # design §3
RESERVED = {"thread": 8, "lock": 4, "device": 2, "request": 4}         # trailing slices, never drawn in training
_PREFIX = {"thread": "T", "lock": "L", "device": "D", "request": "R"}


def pool_tokens(entity_type: str) -> tuple:
    """The whole pool for an entity type, reserved slice last."""
    return tuple(f"{_PREFIX[entity_type]}{i:02d}" for i in range(POOL_SIZES[entity_type]))


def _build():
    toks = [PAD, MASKED, NONE, *KINDS]
    for et in ENTITY_TYPES:
        toks.extend(pool_tokens(et))
    return tuple(toks)


VOCAB = _build()
TOKEN_ID = {t: i for i, t in enumerate(VOCAB)}
VOCAB_SHA256 = hashlib.sha256("\n".join(VOCAB).encode()).hexdigest()

_TYPE = {PAD: "pad", MASKED: "special", NONE: "special"}
_TYPE.update({k: "kind" for k in KINDS})
for _et in ENTITY_TYPES:
    _TYPE.update({t: _et for t in pool_tokens(_et)})


def token_type(tok: str) -> str:
    """pad | special | kind | thread | lock | device | request. KeyError if unknown."""
    return _TYPE[tok]
