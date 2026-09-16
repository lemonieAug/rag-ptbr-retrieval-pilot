# rag-ptbr-retrieval-pilot

Piloto de **retrieval para RAG** em artigos científicos em português brasileiro.
Este repositório implementa um pipeline controlado para comparar **recuperação
híbrida** e **reranking** sobre um corpus pequeno (3–5 artigos) com benchmark
anotado por humano.

> **Aviso importante:** o código e os testes desta entrega foram **escritos e
> revisados por leitura, mas NÃO executados**. Nenhuma validação de runtime,
> compatibilidade comprovada ou métrica foi obtida. A primeira execução e a
> validação empírica serão feitas por você, seguindo este README.

---

## 1. Pergunta de pesquisa, escopo e limites

> Como a recuperação híbrida e o reranking afetam a **cobertura** e o
> **ordenamento** de evidências para RAG em artigos científicos em PT-BR?

**Escopo do piloto:** verificar a viabilidade do pipeline, a qualidade das
anotações e os tipos de falha, antes de ampliar o estudo. Todo o corpus é de
desenvolvimento — não há ajuste em "teste" separado (isso fica para o estudo
posterior).

**Limites das conclusões:** o piloto é pequeno e exploratório. NÃO geramos
conclusões sobre todo o PT-BR, alegações de superioridade estatística nem
relatórios de significância. O reranker NÃO recupera uma evidência ausente dos
candidatos recebidos.

**Fora do escopo desta entrega:** treinamento de embedding, fine-tuning, knowledge
graph, nova arquitetura neural, múltiplos geradores, interface web e busca
adaptativa.

## 2. Componentes e matriz experimental

Componentes: extração de PDF → chunking (com validação de tokens) → BM25 local →
busca densa exata (NumPy) → fusão híbrida (RRF) → reranker → métricas/relatório
→ geração RAG opcional.

| Recuperação inicial | Sem reranker | Com o mesmo reranker |
| --- | --- | --- |
| BM25 | `bm25` | `bm25_rerank` |
| Densa | `dense_<e>` | `dense_<e>_rerank` |
| Híbrida (RRF) | `hybrid_<e>` | `hybrid_<e>_rerank` |

Com 4 embeddings (colibri, embeddinggemma, qwen_embedding, e5), a matriz completa
tem **18 configurações** (`2 + 4×4`). BM25 e BM25+reranker independem do
embedding. Use `rag-ptbr matrix` para listar e `experiments.select` no YAML para
escolher um subconjunto (por substring do id).

## 3. Preparação do ambiente

Requer **Python ≥ 3.10**. Recomendado: ambiente virtual.

```bash
# 1. Crie e ative um ambiente (exemplo com venv)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2. Instale o PyTorch compatível com seu hardware ANTES do resto.
#    GPU NVIDIA (A40, CUDA 12.x):
pip install torch --index-url https://download.pytorch.org/whl/cu121
#    CPU apenas:
# pip install torch --index-url https://download.pytorch.org/whl/cpu

# 3. Instale o pacote com os extras que for usar.
pip install -e ".[ingest,models,generate,dev]"
#    mínimo (sem modelos/PDFs): pip install -e ".[dev]"
```

Copie variáveis de ambiente (opcional, para credenciais/cache):

```bash
cp .env.example .env   # preencha HF_TOKEN para o EmbeddingGemma (gated)
```

## 4. Obtenção dos modelos (explícita)

Nenhuma etapa baixa modelo silenciosamente. Os checkpoints são obtidos uma única
vez, explicitamente:

```bash
rag-ptbr prepare-models
```

Isso baixa os 4 embeddings + o reranker para `artifacts/models/` e grava as
revisões reais em `artifacts/models/revisions.json`.

| Config | Checkpoint | Observação |
| --- | --- | --- |
| colibri | `tardellirs/colibri-embed-ptbr` | livre; derive de EmbeddingGemma |
| embeddinggemma | `google/embeddinggemma-300m` | **gated** — aceite os termos no model card e use `HF_TOKEN` |
| qwen_embedding | `Qwen/Qwen3-Embedding-4B` | livre |
| e5 | `intfloat/multilingual-e5-large-instruct` | livre |
| reranker | `Qwen/Qwen3-Reranker-0.6B` | livre |

Atenção ao **EmbeddingGemma**: (a) requer login/aceite de termos no Hugging Face
(licença Gemma); (b) ativações são incompatíveis com FP16 — o piloto usa BF16/FP32.

Gerador opcional: **Qwen3 14B via Ollama local** (instale o Ollama e rode
`ollama pull qwen3:14b`). Tag/digest/quantização reais são registrados no
manifesto na hora da execução.

## 5. Onde colocar os PDFs

Coloque os 3–5 PDFs em **`data/raw/articles/`**, com nomes estáveis, por exemplo:

```
data/raw/articles/art-001_anemia_ferropriva.pdf
data/raw/articles/art-002_vacina_covid.pdf
```

Use `doc_id` (ex.: `art-001`) nos metadados, nas evidências e nos chunks.

## 6. Metadados e verificação de extração/tabelas

1. Copie o template: `cp configs/templates/articles.yaml data/metadata/articles.yaml`.
2. Preencha um item por artigo (título, autores, ano, `pdf_filename`, etc.).
3. Extraia: `rag-ptbr extract` → gera `data/processed/extracted/<doc_id>.md` e
   `<doc_id>.provenance.json`.
4. **Revise** o Markdown (ordem de leitura, seções, tabelas com cabeçalho/linhas/
   legenda). Corrija diretamente no `.md`. PDF escaneado, extração vazia ou tabela
   mal extraída aparecem como `[revisar]` no log e em `provenance.json`.

## 7. Perguntas, evidências e aprovação do gold

1. `cp configs/templates/questions.yaml data/annotations/questions.yaml` e preencha
   (~25–40 perguntas no total; factuais e multi-evidência do mesmo artigo).
2. `cp configs/templates/qrels.yaml data/annotations/qrels.yaml`.
3. (multi-evidência) `cp configs/templates/evidence_groups.yaml data/annotations/evidence_groups.yaml`.
4. **Depois de congelar os chunks** (seção 8), preencha `chunk_ids` nos qrels e
   grupos. Relevância = **suporte efetivo à resposta** (não basta coincidir
   artigo/página).
5. Exija **revisão humana de 100%** das perguntas/respostas/evidências usadas nas
   métricas: marque `review_status: approved`. `draft` fica fora da avaliação.
6. Valide: `rag-ptbr validate` (sem carregar modelos).

> `origin_doc_id` é **somente** para anotação/avaliação — nunca é enviado aos
> métodos nem aparece no prompt de recuperação. Toda busca consulta o **corpus
> inteiro**.

## 8. Congelar chunks e benchmark

```bash
rag-ptbr chunk
```

Gera `data/processed/chunks/chunks.jsonl` + `corpus_manifest.json` (congelado).
O alvo é **350 tokens / 50 de sobreposição** (tokenizer de referência), validado
contra os tokenizers reais dos embeddings; blocos que estouram o limite mais
restritivo (E5 = 512) são **subdivididos uma única vez**. O `corpus_version`
(hash) vincula rankings, índices e métricas à versão exata do corpus.

## 9. Construir índices e executar as configurações

```bash
rag-ptbr index      # BM25 + índices densos (carrega modelos por etapas)
rag-ptbr retrieve   # roda as configurações selecionadas; imprime o RUN_ID
```

Os índices ficam em `artifacts/indexes/` e as listas ranqueadas em
`results/<run_id>/rankings/<config_id>.jsonl`. Para um subconjunto, edite
`experiments.select` no YAML (ex.: `select: [bm25, hybrid_e5]`).

## 10. Métricas, comparação e relatórios

```bash
rag-ptbr evaluate --run-id <RUN_ID>
```

Métrica primária (ordenamento): **nDCG@10**. Reportadas também: **Recall@5 e
Recall@10** (cobertura), Recall@1, MRR@10, Hit@k, Precision@k, recall do conjunto
candidato por etapa e cobertura de grupos obrigatórios. Saídas em
`results/<run_id>/metrics/`, `metrics_summary.json`, `comparison.json` (deltas
pareados) e `report.md`.

## 11. Geração opcional (Qwen3 14B via Ollama)

```bash
ollama pull qwen3:14b        # uma vez
rag-ptbr generate --run-id <RUN_ID>
```

Usa prompt fixo (`prompts/generation.txt`), top-5 inicial e orçamento de contexto
fixo para todos os métodos. Gera `results/<run_id>/generation/generations.jsonl`
e a planilha de avaliação humana `human_eval.csv` (+ `blind_mapping.json`), com
identificadores cegos e ordem embaralhada.

## 12. Testes (escritos; execute depois)

```bash
pytest
```

Os testes usam fixtures sintéticas e adaptadores mockados, e forçam modo offline
do Hugging Face (nunca baixam modelos). **Nesta entrega eles foram escritos, não
executados.**

## 13. Retomada, cache incompatível e erros comuns

- **Cache incompatível:** se você mudar texto, modelo, dimensão ou template, os
  índices/embeddings guardam um fingerprint e falham com mensagem clara — rode
  `rag-ptbr chunk` (e `index`) novamente.
- **Modelo ausente:** `prepare-models` resolve os checkpoints; os demais comandos
  usam cache local e falham com instrução útil.
- **Retomar etapas:** cada comando é independente; `evaluate`/`generate`/`report`
  usam `--run-id` (default: execução mais recente em `results/`).
- **Linux × Windows:** use caminhos relativos (já é o padrão); `HF_HOME`/cache são
  configuráveis; o tokenizer de referência e o BM25 são multiplataforma.

## 14. Arquivos a guardar para reproduzir

- `data/metadata/articles.yaml` e `data/annotations/*.yaml` (o gold).
- `data/processed/chunks/corpus_manifest.json` + `chunks.jsonl`.
- `configs/default.yaml` e `prompts/*`.
- `results/<run_id>/run_manifest.json` (hashes, revisões, versões, hardware, seed).

O `run_manifest.json` registra: hashes do corpus/chunks/qrels/config/prompts,
checkpoints/revisions, versões das bibliotecas, seed, hardware e parâmetros.

## 15. Aviso de não-execução

**Código gerado e revisado por leitura; não executado. Testes escritos, não
executados.** Nenhuma métrica foi obtida, nenhum modelo foi baixado/inferido e
nenhuma compatibilidade foi comprovada nesta entrega. A primeira execução é sua.

---

### Caminho principal (sequencial)

```bash
# 0) ambiente + modelos
python -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -e ".[ingest,models,generate,dev]"
cp .env.example .env        # HF_TOKEN para EmbeddingGemma
rag-ptbr prepare-models

# 1) inserir PDFs em data/raw/articles/  e preencher data/metadata/articles.yaml

# 2) extrair e revisar
rag-ptbr extract            # revise data/processed/extracted/<doc_id>.md

# 3) gerar e congelar chunks
rag-ptbr chunk

# 4) anotar e validar benchmark (preencher data/annotations/*.yaml)
rag-ptbr validate

# 5) indexar
rag-ptbr index

# 6) recuperar/reranquear
rag-ptbr retrieve           # anote o RUN_ID

# 7) avaliar
rag-ptbr evaluate --run-id <RUN_ID>

# 8) gerar (opcional)
rag-ptbr generate --run-id <RUN_ID>

# 9) relatório
rag-ptbr report --run-id <RUN_ID>
```

Todos os comandos são executados a partir da **raiz do repositório**
(`rag-ptbr-retrieval-pilot/`). Consulte `rag-ptbr <comando> --help` para detalhes.
