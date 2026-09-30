# rag-ptbr-retrieval-pilot

Piloto de **retrieval para RAG** em artigos científicos em português brasileiro.
Este repositório implementa um pipeline controlado para comparar **recuperação
híbrida** e **reranking** sobre um corpus pequeno (3–5 artigos) com benchmark
anotado por humano.

> **Estado local verificado em 30/09/2026:** 5 documentos, corpus congelado de
> 224 chunks, 125 perguntas (122 aprovadas, 3 rejeitadas, 0 drafts), 14
> configurações e `ready_for_retrieval = true`. O retrieval oficial ainda não
> foi executado e nenhuma métrica oficial foi produzida. Evidências:
> `artifacts/review/` e `rag-ptbr status`.

## RunPod / GPU execution

Para executar em RunPod Pod com GPU NVIDIA e volume persistente em `/workspace`,
veja o [guia RunPod](docs/runpod.md). A imagem, o `uv.lock`, os snapshots
pinados, o setup e o smoke test estão descritos lá.

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

Com 3 embeddings (colibri, qwen_embedding, e5), a matriz completa tem **14
configurações** (`2 + 3×4`). BM25 e BM25+reranker independem do embedding. Use
`rag-ptbr matrix` para listar e `experiments.select` no YAML para escolher um
subconjunto (por substring do id).

> **EmbeddingGemma removido do piloto:** o modelo é *gated* (exige `HF_TOKEN` +
> aceite dos termos de licença) e essa dependência de autenticação externa
> quebrou a reprodução offline. O piloto usa apenas embeddings de acesso livre,
> sem necessidade de token/API para baixar ou carregar os checkpoints.

## 3. Preparação do ambiente

Requer **Python ≥ 3.11 e < 3.14**. O ambiente científico RunPod fixa Python
3.11.16, PyTorch CUDA 12.4 e todas as dependências em `uv.lock`. Use o
[setup RunPod](docs/runpod.md) para instalá-lo no Pod.

```bash
# Ambiente leve local para testes sem modelos
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Copie variáveis de ambiente (opcional, para credenciais/cache):

```bash
cp .env.example .env   # HF_TOKEN não é necessário (nenhum checkpoint usado é gated)
```

## 4. Obtenção dos modelos (explícita)

Nenhuma etapa baixa modelo silenciosamente. Os checkpoints são obtidos uma única
vez, explicitamente:

```bash
rag-ptbr prepare-models
```

Isso baixa os 3 embeddings + o reranker para `artifacts/models/` nas revisões
fixadas em `configs/model_revisions.yaml`, confere os snapshots e grava
`artifacts/models/revisions.json`.

| Config | Checkpoint | Observação |
| --- | --- | --- |
| colibri | `tardellirs/colibri-embed-ptbr` | livre; derive de EmbeddingGemma |
| qwen_embedding | `Qwen/Qwen3-Embedding-4B` | livre |
| e5 | `intfloat/multilingual-e5-large-instruct` | livre |
| reranker | `Qwen/Qwen3-Reranker-0.6B` | livre |

> `google/embeddinggemma-300m` **não é usado** neste piloto: é um checkpoint
> *gated* (exige login/aceite de termos + `HF_TOKEN`) e essa dependência de
> autenticação externa não é confiável para reprodução offline. Todos os
> checkpoints usados aqui são de acesso livre.

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

Consulte `rag-ptbr status` para verificar corpus, snapshots locais, índices e
estado do benchmark sem carregar modelos. `rag-ptbr status --json` inclui
o inventário de evidências/qrels/grupos e os erros/avisos da validação. O estado
`ready_for_retrieval` exige decisões humanas para todos os drafts e pelo menos
uma pergunta aprovada, além de corpus, modelos e índices válidos.

O gold desta edição já foi revisado: 122 perguntas aprovadas, 3 rejeitadas,
nenhum draft. Os arquivos em `data/annotations/` são a referência oficial;
consulte `rag-ptbr review-gold --summary` para o histórico e rode
`rag-ptbr validate` para conferir a estrutura. O
[guia de anotação](docs/annotation_guide.md) documenta o processo para edições
futuras do benchmark.

> `origin_doc_id` é **somente** para anotação/avaliação — nunca é enviado aos
> métodos nem aparece no prompt de recuperação. Toda busca consulta o **corpus
> inteiro**.

## 8. Congelar chunks e benchmark

```bash
python scripts/check_artifacts.py
```

Esta edição já tem `data/processed/chunks/chunks.jsonl` e
`corpus_manifest.json` congelados; transfira os arquivos auditados ao Pod.
O comando `rag-ptbr chunk` criaria uma nova versão do corpus e não faz parte
da reprodução oficial. Se a transferência do corpus congelado for impossível,
use somente o procedimento explícito de reconstrução com PDFs canônicos e
Markdown revisado descrito em [docs/runpod.md](docs/runpod.md).
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

## 12. Testes

```bash
pytest
```

Os testes usam fixtures sintéticas e adaptadores mockados, e forçam modo offline
do Hugging Face (nunca baixam modelos). A suíte foi executada nesta auditoria;
o resultado detalhado está em `artifacts/review/technical_audit.md`.

## 13. Retomada, cache incompatível e erros comuns

- **Cache incompatível:** se você mudar texto, modelo, dimensão ou template, os
  índices/embeddings guardam um fingerprint e falham com mensagem clara — rode
  `rag-ptbr index` para reconstruir apenas índices incompatíveis. Não regenere
  o corpus congelado sem uma decisão explícita de criar outra versão.
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

## 15. Estado de execução

Os testes e a validação estrutural foram executados localmente, com checkpoints
existentes preservados. O carregamento fixa snapshots de `revisions.json` e usa
somente arquivos locais. `retrieve` requer aprovação humana; `evaluate`, `report`
e `generate` recusam resultados de corpus, configuração ou benchmark diferentes.
Veja `artifacts/review/` para o histórico de auditoria e revisão do gold.

---

### Caminho principal (corpus oficial já congelado)

```bash
python scripts/check_artifacts.py
rag-ptbr validate
rag-ptbr index
rag-ptbr retrieve           # anote o RUN_ID emitido
rag-ptbr evaluate --run-id <RUN_ID>
rag-ptbr report --run-id <RUN_ID>
# geração opcional separada: rag-ptbr generate --run-id <RUN_ID>
```

Todos os comandos são executados a partir da **raiz do repositório**
(`rag-ptbr-retrieval-pilot/`). Consulte `rag-ptbr <comando> --help` para detalhes.
