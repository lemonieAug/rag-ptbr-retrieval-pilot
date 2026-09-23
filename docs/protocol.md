# Protocolo do piloto

Este protocolo fixa, **antes da execução**, as decisões metodológicas do piloto.
As métricas primárias e os defaults aqui declarados devem ser respeitados na
análise; mudanças exigem registrar uma nova versão do protocolo e invalidar
resultados anteriores.

## 1. Pergunta e hipóteses

**Pergunta:** Como a recuperação híbrida e o reranking afetam a cobertura e o
ordenamento de evidências para RAG em artigos científicos em PT-BR?

Hipóteses exploratórias (não presumidas como confirmadas):

- H1: a recuperação híbrida pode aumentar a cobertura em relação à densa isolada.
- H2: o reranker pode melhorar o posicionamento das evidências disponíveis.
- H3: ganhos de recuperação podem ajudar a resposta final (medidos separadamente).

O reranker não recupera evidência ausente dos candidatos recebidos.

## 2. Corpus e benchmark

- 3–5 PDFs de artigos predominantemente em PT-BR (fornecidos pelo usuário).
- Texto e tabelas convertidos para Markdown, com contexto e proveniência.
- ~25–40 perguntas (meta inicial flexível): factuais e multi-evidência.
- **Toda consulta busca o corpus inteiro.** `origin_doc_id` é só anotação.
- Relevância = suporte efetivo à resposta (não basta artigo/página).
- Revisão humana de 100% das perguntas/respostas/evidências usadas nas métricas.
- Todo o corpus é de desenvolvimento; o estudo posterior usará teste separado.

## 3. Matriz experimental (14 configurações)

A execução offline fixa os snapshots registrados em `artifacts/models/revisions.json`.
Índices compatíveis são reutilizados; corpus, parâmetros, templates, precisão,
dimensões e revisões divergentes bloqueiam a reutilização. Consultas são codificadas
por um embedding de cada vez e os modelos são descarregados antes do reranker.
O tempo de codificação compartilhado fica em `parameters.query_encoding_seconds`
no manifesto; `timings.dense` mede a busca exata com vetor já codificado.
O relatório apresenta ambos separadamente, sem confundir busca com inferência.

`2 + 3×4` com 3 embeddings (colibri, qwen_embedding, e5 — embeddinggemma
removido por ser gated). Baselines centrais e ablações:

| Recuperação inicial | Sem reranker | Com reranker |
| --- | --- | --- |
| BM25 | `bm25` | `bm25_rerank` |
| Densa | `dense_<e>` | `dense_<e>_rerank` |
| Híbrida (RRF) | `hybrid_<e>` | `hybrid_<e>_rerank` |

Comparações (por embedding):

1. `hybrid_<e>_rerank` vs `dense_<e>` — efeito total do pipeline.
2. `hybrid_<e>` vs `dense_<e>` — efeito da hibridização.
3. `dense_<e>_rerank` vs `dense_<e>` — efeito do reranking na densa.
4. `hybrid_<e>_rerank` vs `hybrid_<e>` — efeito do reranking na híbrida.
5. `hybrid_<e>_rerank` vs `dense_<e>_rerank` — hibridização com reranker fixo.

`bm25`/`bm25_rerank` ajudam a interpretar o ganho sobre a base lexical.

## 4. Recuperação e reranking

- BM25: `k1 = 1.2`, `b = 0.75`; tokenização lexical fixa (Unicode/PT-BR), caixa
  baixa, acentos preservados (sem stemming/stopwords/accentos como ablações).
- Densa: dimensão nativa, vetores normalizados, cosseno (produto interno).
- `N = 50` candidatos por recuperador; `RRF` com `c = 60` e pesos iguais.
- RRF: une por `chunk_id`, acumula `1/(c+rank)` (ranks 1-based), ordena com
  desempate determinístico (score desc, depois `chunk_id`), top-N da fusão.
- Variante com reranker recebe **exatamente os mesmos N candidatos** da variante
  sem reranker; o reranker só reordena.
- Registram-se listas originais, união, ranking RRF, candidatos ao reranker e
  ranking final. Cobertura é medida antes e depois da seleção top-N da fusão.

## 5. Modelos

| Nome config | Checkpoint | Template/pooling |
| --- | --- | --- |
| colibri | `tardellirs/colibri-embed-ptbr` | ST prompt_name query/document |
| qwen_embedding | `Qwen/Qwen3-Embedding-4B` | instruction na consulta + last-token pool |
| e5 | `intfloat/multilingual-e5-large-instruct` | instruction na consulta + mean pool; 512 tokens |

Reranker fixo: `Qwen/Qwen3-Reranker-0.6B` (P("yes") por softmax yes/no).
Gerador opcional: Qwen3 14B via Ollama (temperatura 0, sem promessa de
determinismo absoluto). Revisões/hashes reais são gravados no manifesto ao executar.

## 6. Avaliação

- **Métrica primária (ordenamento): nDCG@10.**
- **Cobertura: Recall@5 e Recall@10** (reportados junto).
- Adicionais: Recall@1, MRR@10, Hit@k, Precision@k (secundária), recall do
  conjunto candidato por etapa, fração de grupos obrigatórios cobertos,
  proporção de perguntas com todos os grupos cobertos, e latências separadas.
- `Recall@k` usa o total de relevantes anotados como denominador.
- `Hit@k` = presença de ≥1 relevante (não é sinônimo de Recall).
- `MRR@10` = 1/posição do 1º relevante até a posição 10; 0 se ausente.
- `nDCG` usa qrels binários e IDCG com a relevância anotada (não só recuperados).
- Pergunta sem gold válido é **bloqueada** (não zerada).
- `Precision@k` explicita o denominador `min(k, nº de resultados)`.
- Resultados por pergunta, médias por pergunta e por artigo; deltas pareados
  sobre as mesmas perguntas. Sem teste de significância automático.

## 7. Geração (opcional, separada)

Prompt fixo, top-5, orçamento fixo, mesma montagem para todos os métodos; pede
resposta apoiada, citações por ID e indicação de "Evidência insuficiente".
Registra o contexto realmente enviado e as evidências excluídas pelo orçamento
(cobertura pós-montagem calculada separadamente). Avaliação humana cega
(correção, suporte, citações) — sem juiz automático como fonte principal.

## 8. Congelamento e reprodutibilidade

Congelar chunks e benchmark antes da anotação final; mudanças invalidam índices e
anotações afetadas. Cada execução registra hashes (corpus/chunks/qrels/config/
prompts), revisões, versões, seed, hardware e run id.
