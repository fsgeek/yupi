"""Design v0.1 §4: one vocabulary for every corpus of the world, ids pinned."""
import hashlib

from yupi.corpus import vocab as V


PINNED_SHA256 = "ed9a50c5029403554cfe34d8d29758cad172f4414c2fcd06fb687f949a789604"


def test_vocabulary_is_pinned():
    # 9 kinds (RESET included) + PAD + MASKED + NONE + 64 + 32 + 16 + 32 pool tokens
    assert len(V.VOCAB) == 156                       # design §4 wrote 157: RESET counted twice (ledger, 2026-09-15)
    assert hashlib.sha256("\n".join(V.VOCAB).encode()).hexdigest() == PINNED_SHA256
    assert V.VOCAB_SHA256 == PINNED_SHA256
    assert V.VOCAB_VERSION == 1


def test_ids_and_specials():
    assert V.TOKEN_ID[V.PAD] == 0                    # padding is id 0 so a zeroed buffer is all-PAD
    assert len(set(V.VOCAB)) == len(V.VOCAB)
    assert all(V.VOCAB[V.TOKEN_ID[t]] == t for t in V.VOCAB)
    assert set(V.KINDS) == {"ACQUIRE", "BLOCK", "DISPATCH", "IDLE", "IO_COMPLETE",
                            "IO_ISSUE", "RELEASE", "RESET", "STEP"}     # Part II §4 schema
    assert max(V.TOKEN_ID.values()) < 2 ** 16       # uint16 token files (design §5)


def test_pools_and_types():
    assert V.POOL_SIZES == {"thread": 64, "lock": 32, "device": 16, "request": 32}
    assert V.RESERVED == {"thread": 8, "lock": 4, "device": 2, "request": 4}
    for et in V.ENTITY_TYPES:
        toks = V.pool_tokens(et)
        assert len(toks) == V.POOL_SIZES[et] and all(V.token_type(t) == et for t in toks)
    assert V.token_type(V.PAD) == "pad"
    assert V.token_type(V.MASKED) == "special" and V.token_type(V.NONE) == "special"
    assert V.token_type("RESET") == "kind" and V.token_type("IDLE") == "kind"
