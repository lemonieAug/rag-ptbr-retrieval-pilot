"""Limites de tokens (referência + subdivisão) e invalidação de caches."""

import pytest

from rag_ptbr_pilot.adapters.specs import get_embedding_spec
from rag_ptbr_pilot.chunking.token_validation import compute_binding, split_block_to_limit
from rag_ptbr_pilot.chunking.tokenizer_ref import SimpleTokenizer
from rag_ptbr_pilot.indexing.store import (
    bm25_fingerprint,
    dense_fingerprint,
    ensure_compatible,
)


def test_binding_limit_is_e5_512():
    specs = [get_embedding_spec(n) for n in
             ["colibri", "embeddinggemma", "qwen_embedding", "e5"]]
    name, limit = compute_binding(specs)
    assert name == "e5"
    assert limit == 512


def test_simple_tokenizer_split_below_target():
    st = SimpleTokenizer()
    text = " ".join(str(i) for i in range(20))
    pieces = st.split(text, target=7, overlap=2)
    assert len(pieces) > 1
    for p in pieces:
        assert st.count(p) <= 7


def test_simple_tokenizer_short_text_unsplit():
    st = SimpleTokenizer()
    assert st.split("um dois", target=10, overlap=2) == ["um dois"]


class _FakeTokenizer:
    """Tokenizer fictício por palavras com offsets de caracteres."""

    def __call__(self, text, add_special_tokens=False, return_offsets_mapping=False):
        words = text.split()
        offsets = []
        idx = 0
        for w in words:
            s = text.index(w, idx)
            offsets.append((s, s + len(w)))
            idx = s + len(w)
        return {"input_ids": list(range(len(words))), "offset_mapping": offsets}

    def encode(self, text, add_special_tokens=True):
        base = text.split()
        return (["<s>"] + base + ["</s>"]) if add_special_tokens else base


def test_split_block_to_limit_subdivides_once():
    spec = get_embedding_spec("e5")  # document_template = "{text}"
    tok = _FakeTokenizer()
    text = " ".join(f"w{i}" for i in range(10))
    pieces = split_block_to_limit(tok, spec, text, limit=5, overlap=0)
    # overhead = encode("") = 2 tokens -> available = 3 -> 10 palavras => 4 trechos
    assert len(pieces) == 4
    for p in pieces:
        assert len(p.split()) <= 3


def test_dense_fingerprint_invalidates_on_change():
    f1 = dense_fingerprint("cv1", "e5", "cp", None, 1024)
    f2 = dense_fingerprint("cv2", "e5", "cp", None, 1024)
    f3 = dense_fingerprint("cv1", "e5", "cp", None, 512)
    assert f1 != f2
    assert f1 != f3


def test_ensure_compatible_raises_on_mismatch():
    with pytest.raises(RuntimeError):
        ensure_compatible("stale", bm25_fingerprint("cv1", 1.2, 0.75, {}), "bm25")
    # compatível não levanta
    expected = bm25_fingerprint("cv1", 1.2, 0.75, {})
    ensure_compatible(expected, expected, "bm25")
