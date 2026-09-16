# Exemplos sintéticos

Conteúdo FABRICADO, claramente separado do benchmark real (`data/`). Útil apenas
para (1) entender os formatos e (2) rodar um smoke test BM25-only **depois** que
você instalar as dependências — nunca como resultado experimental.

**Atenção:** os `chunk_id` em `qrels.yaml` e `evidence_groups.yaml` são
preenchidos APÓS rodar `rag-ptbr chunk` (os IDs dependem da numeração de blocos).
Este diretório NÃO é um corpus e NÃO deve ser misturado com os artigos reais.

Para um smoke test sem PDFs nem modelos:
1. Copie `examples/synthetic/extracted/art-syn-001.md` para `data/processed/extracted/`.
2. Crie `data/metadata/articles.yaml` a partir de `examples/synthetic/articles.yaml`.
3. Rode `rag-ptbr chunk`, depois preencha os chunk_ids nos qrels/grupos.
4. Rode `rag-ptbr index` e `rag-ptbr retrieve` (somente `bm25`/`bm25_rerank`,
   via `experiments.select: [bm25]`, para não carregar modelos).
