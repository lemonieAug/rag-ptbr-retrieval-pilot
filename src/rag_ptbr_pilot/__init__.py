"""rag_ptbr_pilot — piloto de retrieval para RAG em artigos científicos em PT-BR.

Importar este pacote não carrega modelos nem inicia downloads. Modelos de
embedding/reranker/geração são carregados sob demanda apenas pelos comandos que
realmente os utilizam (``index``, ``retrieve``, ``generate``).
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
