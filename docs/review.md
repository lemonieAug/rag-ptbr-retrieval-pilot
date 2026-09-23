# Relatório de revisão

> **Atualização de 23/09/2026:** Python 3.13.1, CLI, matriz, validação estrutural
> e suíte de testes executados localmente. Corpus de 224 chunks preservado;
> 125 perguntas continuam draft. Resultados e bloqueios operacionais constam
> de `artifacts/review/technical_audit.md`. As seções históricas abaixo descrevem
> a revisão inicial por leitura, anterior a esta auditoria de runtime.

## 0. Método da revisão

A revisão foi feita por **inspeção de código** (leitura dos módulos, schemas,
configurações e diferenças entre arquivos), complementada por uma segunda leitura
independente. O mecanismo de revisão do **Veramux** (pipeline com rodadas de
validação/correção que executam o código) **não foi acionado**, porque executaria
comandos proibidos nesta tarefa — conforme a cláusula de contingência do
enunciado ("se o mecanismo obrigar a executar comandos proibidos, revise por
leitura e registre a limitação"). Não contornamos a restrição nem alegamos
revisão de runtime que não aconteceu.

## 1. Inconsistências corrigidas (encontradas por leitura)

1. **`adapters/embeddings.py`** — `local_files_only`/`torch_dtype` eram passados
   como kwargs de topo do `SentenceTransformer` (que não os aceita → `TypeError`).
   Corrigido: movidos para `model_kwargs`/`tokenizer_kwargs`.
2. **`retrieval/pipeline.py`** — cronômetros com `stop()` duplo (medição
   incorreta de latência). Corrigido: um único `stop()` por etapa.
3. **`cli.py`** — conflito de argumento `--config` no subcomando `generate`
   (usado duas vezes). Renomeado para `--config-id`; corrigido o uso de
   `args.config` → `args.config_id`.
4. **`cli.py`** — `_load_bm25`/`_load_dense_index` chamavam
   `cfg.load_corpus_version()` (método inexistente). Agora recebem
   `corpus_version` do manifesto do corpus.
5. **`io_utils.py`** — `_default` usava `model_dump()` (enum não JSON-serializável
   → `"Modality.text"` em vez de `"text"`). Corrigido para `model_dump(mode="json")`.
6. **`chunking/md_parser.py`** — comentários HTML não reconhecidos (ex.: o aviso
   de extração) vazavam para o texto dos chunks; o primeiro cabeçalho (`# doc_id`)
   virava seção espúria. Corrigido: comentários ignorados; título não vira seção.
7. **`retrieval/results.py`** — faltavam `from_dict` para round-trip JSONL das
   listas ranqueadas. Adicionados.
8. **`generation/ollama_client.py`** — faltava o campo `context_text` no
   `GenerationResult` (usado pela planilha de avaliação humana). Adicionado.
9. **`ingest/extractor.py`** — usava `save_text` (não definido). Adicionado em
   `io_utils.py`.
10. **`cli.py`** — import não usado de `get_reranker_adapter` removido.

Correções adicionais após a **segunda leitura independente** (subagente de revisão):

11. **`cli.py`/`indexing/store.py`** — fingerprint do índice denso sempre usava
    `revision=None` (nova revisão de um mesmo checkpoint não invalidava o cache).
    Agora a revisão é lida de `artifacts/models/revisions.json` e entra no
    fingerprint (no `index` e no `_load_dense_index`).
12. **`cli.py`** — `main()` capturava só `ConfigError`/`ValidationError`;
    `MissingArtifactError` e demais `PilotError` viravam traceback. Agora captura
    `PilotError` (mensagem limpa + código 2).
13. **`cli.py`/`manifest.py`** — `prompts_hash` existia mas nunca era preenchido.
    Agora `cmd_retrieve` grava o hash do `prompts/generation.txt`.
14. **`cli.py`** — `OLLAMA_HOST` (documentada em `.env.example`) não era lida.
    Agora `cmd_generate` usa `OLLAMA_HOST` com fallback para `generator.host`.
15. **`adapters/reranker.py`/`adapters/tokenizers.py`** — contagem de tokens do par
    usava `add_special_tokens=False` (inconsistente com a tokenização real).
    Corrigido para `add_special_tokens=True` (conservador, sem off-by-one).
16. **`config.py`** — `config_to_dict` gravava `root` absoluto, tornando o
    `config_hash` dependente da máquina. Agora `root` é removido do hash.
17. **`metrics/ranking.py`** — `mrr@10` era reescrito dentro do loop de `k`.
    Agora calculado uma única vez fora do loop.
18. **`reporting/evaluation.py`** — `_mean([])` retornava `NaN` (JSON não-padrão).
    Agora retorna `None` (JSON válido; o relatório mostra "—").
19. **`adapters/embeddings.py`** — texto acima do limite levantava
    `MissingArtifactError` (semântica errada). Agora levanta `ConfigError`.

## 2. Correspondência CLI ↔ configuração ↔ README

Verificada por leitura, ponto a ponto:

- Comandos do README (`matrix`, `validate`, `extract`, `chunk`, `prepare-models`,
  `index`, `retrieve`, `evaluate`, `generate`, `report`) existem em `cli.py` com
  os mesmos nomes e flags (`-c/--config`, `--run-id`, `--config-id`).
- Caminhos citados no README (`data/raw/articles/`, `data/metadata/articles.yaml`,
  `data/annotations/*.yaml`, `data/processed/extracted/`, `artifacts/indexes/`,
  `results/<run_id>/...`) correspondem a `configs/default.yaml` e aos comandos.
- O `configs/default.yaml` satisfaz o schema Pydantic de `config.py` (campos e
  tipos conferidos: `retrieval.top_n=50`, `bm25.k1=1.2/b=0.75`, `rrf.c=60`,
  `metrics.primary=ndcg@10`, `k_values=[1,5,10]`, embeddings e dtype por modelo).

## 3. Suposições metodológicas e técnicas

- **Reranker só reordena**: a variante com reranker recebe exatamente os N
  candidatos da variante sem reranker (garantido em `RetrievalRunner.run_query` e
  coberto por teste dedicado).
- **Gold separado**: a API de recuperação recebe só `question_id`+`query_text`;
  `expected_answer`/`origin_doc_id`/qrels/grupos nunca entram nos métodos
  (`benchmark.leakage` + teste).
- **Cobertura antes/depois da seleção top-N**: `rrf_union` (fusão completa) e
  `rrf_topn` são registrados separadamente; a cobertura de cada etapa é calculada
  na avaliação.
- **Chunk único para todos os métodos**: um só chunking (referência 350/50),
  validado contra os tokenizers reais e subdividido uma única vez para caber no
  encoder mais restritivo (E5 = 512). Templates de consulta/documento ficam nos
  adaptadores.
- **IDs estáveis** dentro do corpus congelado (`<doc_id>-bNNNN-cNNN`); mudanças
  invalidam o `corpus_version`/fingerprints.
- **Dedup por `chunk_id`**, nunca por texto (RRF acumula contribuições por id).

## 4. Limitações da revisão inicial e validação posterior

- **Validado nesta auditoria**: imports leves, schemas, CLI e testes. A execução
  experimental oficial continua aguardando gold aprovado por humano.
- **Prompt/templates de colibri**: `prompt_name="query"/"document"` confirmados
  na documentação; conferir contra `model.prompts` no `prepare-models`.
- **Limite de entrada de colibri** marcado `None` (resolver no prep); o limite
  vinculante é o do E5 (512), então o chunking não depende dele.
- **EmbeddingGemma removido** do piloto (gated, exige `HF_TOKEN` + aceite de
  termos) — só embeddings de acesso livre são usados agora.
- **Extraçor de PDF em múltiplas colunas** é aproximado (marcado para revisão).
- **Contagem de tokens na geração** usa o tokenizer de referência (aproximação
  documentada); trocar por contador do tokenizer real do gerador se necessário.
- **Revisões/hashes** dos checkpoints não foram inventados; `prepare-models`
  grava os reais.
- **`split_block_to_limit`** depende de `return_offsets_mapping=True` do tokenizer
  (ok com tokenizers *fast*, padrão do `AutoTokenizer` — inclusive o XLM-R do E5);
  um tokenizer lento com offsets `(0,0)` corromperia a subdivisão. Risco
  condicional, não confirmado por leitura; validar na execução.

## 5. Verificações não executadas na revisão inicial (registro histórico)

- `pytest` (todos os testes escritos, nenhum executado).
- Instalação de dependências / resolução do PyTorch / import real dos módulos.
- `rag-ptbr` em qualquer comando (extract/chunk/index/retrieve/evaluate/generate).
- Carregamento de qualquer checkpoint/tokenizer; nenhuma inferência.
- Extração de PDF real; geração de chunks/embeddings/índices/resultados.
- Lint/formatação/type-check (`ruff`, `mypy`, `py_compile`).

Nenhuma métrica foi obtida e nenhum resultado experimental foi inventado.
