"""Tokenizer de referência fixo (sem dependências).

É uma aproximação determinística usada apenas como PONTO DE PARTIDA para o alvo
de tokens (default 350/50). NÃO é garantia de compatibilidade: a validação real
usa os tokenizers de todos os embeddings selecionados (``token_validation``).
"""

from __future__ import annotations

import re

# Token = sequência alfanumérica (Unicode) OU pontuação isolada.
_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class SimpleTokenizer:
    """Tokenizer de referência: aproximação sublexical determinística."""

    name = "simple"

    def tokenize(self, text: str) -> list[tuple[str, int, int]]:
        return [(m.group(), m.start(), m.end()) for m in _TOKEN_RE.finditer(text)]

    def count(self, text: str) -> int:
        return len(_TOKEN_RE.findall(text))

    def split(self, text: str, target: int, overlap: int) -> list[str]:
        """Divide o texto em trechos de ~``target`` tokens com ``overlap``.

        Corta nas fronteiras de tokens (preserva o texto original).
        """
        toks = self.tokenize(text)
        if not toks:
            return []
        if len(toks) <= target:
            return [text]

        chunks: list[str] = []
        start = 0
        while start < len(toks):
            end = min(start + target, len(toks))
            s = toks[start][1]
            e = toks[end - 1][2]
            chunk = text[s:e]
            if chunk.strip():
                chunks.append(chunk)
            if end >= len(toks):
                break
            start = max(start + 1, end - overlap)
            if start >= len(toks):
                break
        return chunks
