# Decisões técnicas

Registro das decisões de implementação e das fontes primárias consultadas.
Revisões/hashes de checkpoints NÃO foram inventados — ficam como `None` e são
resolvidos em `rag-ptbr prepare-models` e gravados no manifesto de execução.

## 1. Modelos: formatos oficiais implementados

### Colibri — `tardellirs/colibri-embed-ptbr`
- SentenceTransformer sem adaptadores; `prompt_name="query"` →
  `task: search result | query: ` e `prompt_name="document"` →
  `title: none | text: `.
- 768-dim, FP32 por padrão (há branch fp16/ONNX, NÃO usados — decisão: não criar
  outra variável experimental).
- Fonte: [model card](https://huggingface.co/tardellirs/colibri-embed-ptbr).

### EmbeddingGemma — `google/embeddinggemma-300m` (REMOVIDO do piloto)
- **Decisão revertida na primeira execução:** o modelo é **gated** (licença
  Gemma, requer `HF_TOKEN` + aceite dos termos), e essa dependência de
  autenticação externa se mostrou pouco confiável para reprodução offline —
  o download inicial baixou só o `README.md` do repo e falhou silenciosamente
  nos arquivos reais do modelo (erro 401 só apareceu depois, na etapa de
  `index`). Trocado por usar apenas os 3 embeddings de acesso livre
  (colibri, qwen_embedding, e5); ver `configs/default.yaml`.
- Registro do formato original (não usado em execução): mesma convenção de
  prompts do Colibri (query/document) — confirmada na doc oficial do Google:
  `query: "task: search result | query: "` e `document: "title: none | text: "`.
  FP32 ou BF16 (ativações incompatíveis com FP16).
- Fontes: [model card](https://huggingface.co/google/embeddinggemma-300m) e
  [doc Google EmbeddingGemma + Sentence Transformers](https://ai.google.dev/gemma/docs/embeddinggemma/inference-embeddinggemma-with-sentence-transformers).

### E5 instruct — `intfloat/multilingual-e5-large-instruct`
- Instruction na consulta: `Instruct: {task}\nQuery: {query}`; documento sem
  instruction. Average pooling + normalize. Limite **512 tokens** (documentado).
- `task = "Given a web search query, retrieve relevant passages that answer the query"`.
- Fonte: [model card](https://huggingface.co/intfloat/multilingual-e5-large-instruct).

### Qwen3 Embedding — `Qwen/Qwen3-Embedding-4B`
- Instruction na consulta: `Instruct: {task}\nQuery:{query}` (sem espaço após
  `Query:`); documento sem instruction. **Last-token pooling** (pooling oficial) +
  normalize. 2560-dim. `padding_side="left"`.
- Fonte: [model card](https://huggingface.co/Qwen/Qwen3-Embedding-4B).

### Reranker — `Qwen/Qwen3-Reranker-0.6B`
- Formato: `<Instruct>: {instruction}\n<Query>: {query}\n<Document>: {doc}`, com
  prefixo/sufixo do chat template (`system` com "Judge whether the Document meets
  the requirements..."; sufixo `<think>...`).
- Score = **P("yes")** por softmax dos logits dos tokens `yes`/`no` na última
  posição (código oficial do card). NÃO é similaridade de embeddings.
- `max_length` 8192 (contexto nominal 32k). Fonte:
  [model card](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B).

### Gerador — Qwen3 14B via Ollama
- `ollama pull qwen3:14b`; temperatura 0; `num_ctx` 8192; tag/digest/quantização
  reais registrados no manifesto ao executar (não inventados).
- Fonte: [Ollama qwen3:14b](https://ollama.com/library/qwen3:14b).

## 2. Arquitetura e recuperação

- **BM25 local** (`k1=1.2, b=0.75`) e **busca densa exata em NumPy** (sem banco
  vetorial): corpus pequeno não justifica infraestrutura distribuída.
- Vetores **normalizados** + cosseno via produto interno; dimensões **nativas**
  (sem redução/quantização como experimento).
- **Fusão RRF**: une por `chunk_id`, acumula `peso/(c+rank)` com ranks 1-based,
  `c=60`, pesos iguais; desempate determinístico (score desc, `chunk_id` asc).
  NÃO soma scores brutos (escalas incompatíveis).
- **Normalização lexical** idêntica para docs/consultas: Unicode NFKC + caixa
  baixa; **acentos preservados**, sem stemming/stopwords (evitar ablações).
- `N=50` candidatos; cobertura medida antes/depois da seleção top-N da fusão.

## 3. Ingestão e chunking

- **pdfplumber** (MIT, documentada) para texto+tabelas; **pypdf** para metadados.
  Páginas com tabelas reconstroem o texto do corpo excluindo as bboxes das
  tabelas (evita duplicação); tabelas viram blocos Markdown com cabeçalho/linhas/
  legenda/página.
- **Limitação conhecida:** reconstrução em múltiplas colunas é aproximada; páginas
  complexas são marcadas para revisão humana. PDF escaneado/extração vazia gera
  item de revisão (não fingimos sucesso).
- **Tokenizer de referência** = "simple" (regex `\w+|[^\w\s]`, determinístico,
  sem dependências). Alvo 350/50 é só ponto de partida; a validação real usa os
  tokenizers de todos os embeddings (template + tokens especiais). Blocos que
  estouram o limite mais restritivo (E5 = 512) são **subdivididos uma única vez**.
- **IDs**: `chunk_id = <block_id>-c<NNN>`, `block_id = <doc_id>-b<NNNN>` (índice
  sequencial estável dentro do corpus congelado). Mudanças no Markdown alteram os
  IDs/hashes — o congelamento garante consistência entre anotação e índices.

## 4. Prevenção de vazamento e avaliação

- A API de recuperação recebe apenas `question_id` + `query_text`; qrels/gold/
  grupos/`origin_doc_id` são exclusivos da avaliação. `benchmark.leakage` valida.
- `Recall@k` usa total de relevantes anotados; `nDCG` com IDCG da anotação;
  pergunta sem gold é **bloqueada**. Métricas primárias declaradas **antes** da
  execução (`docs/protocol.md`).

## 5. Preparação e pendências

- Revisões dos quatro checkpoints ativos já registradas localmente em
  `artifacts/models/revisions.json` e fixadas no carregamento offline. A auditoria
  de 23/09/2026 preservou os arquivos existentes; não executou downloads.
- Limite de entrada do colibri (marcado `None`); o limite vinculante é o do E5
  (512), então o chunking não depende dele.
- Contagem exata de tokens na geração: o padrão usa o tokenizer de referência
  (aproximação documentada); troque por um contador com o tokenizer real do
  gerador se precisar de precisão.

## 6. Escolhas que NÃO foram feitas de propósito

- Sem treinamento/fine-tuning, sem knowledge graph, sem nova arquitetura, sem
  múltiplos geradores, sem interface web, sem busca adaptativa.
- Sem reduzir/quantizar dimensões nem testar prompts alternativos como experimento.
- Sem herdar grafo/métricas/chunking da reprodução anterior (RAG multimodal em
  manuais): o piloto é independente.
