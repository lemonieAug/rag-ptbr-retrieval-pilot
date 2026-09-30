# Relatório de recuperação — run-20260930T165133+0000-8532bd1f

- Corpus: `8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743`
- Config hash: `ef19213dd59224d281621ce975923526359498656759e4288d28e77b83019cee`
- Configurações executadas: 14
- Métrica primária (ordenamento): **ndcg@10**

## Médias por configuração (sobre perguntas avaliadas)

| config | ndcg@10 | recall@1 | recall@5 | recall@10 | grupos_cobertos |
|---|---|---|---|---|---|
| bm25 | 0.5791 | 0.3975 | 0.6516 | 0.7418 | 0.7855 |
| bm25_rerank | 0.7610 | 0.5929 | 0.8210 | 0.8582 | 0.7855 |
| dense_colibri | 0.6703 | 0.4563 | 0.7391 | 0.8456 | 0.8783 |
| dense_colibri_rerank | 0.8207 | 0.6366 | 0.8866 | 0.9249 | 0.8783 |
| dense_e5 | 0.5926 | 0.3757 | 0.6462 | 0.8104 | 0.9391 |
| dense_e5_rerank | 0.8120 | 0.6284 | 0.8702 | 0.9167 | 0.9391 |
| dense_qwen_embedding | 0.7185 | 0.4973 | 0.8197 | 0.8784 | 0.9826 |
| dense_qwen_embedding_rerank | 0.8163 | 0.6284 | 0.8866 | 0.9262 | 0.9826 |
| hybrid_colibri | 0.6804 | 0.4986 | 0.7336 | 0.8238 | 0.8783 |
| hybrid_colibri_rerank | 0.8257 | 0.6366 | 0.8948 | 0.9372 | 0.8783 |
| hybrid_e5 | 0.6454 | 0.4180 | 0.7541 | 0.8213 | 0.8928 |
| hybrid_e5_rerank | 0.8278 | 0.6366 | 0.8948 | 0.9413 | 0.8928 |
| hybrid_qwen_embedding | 0.6728 | 0.4658 | 0.7582 | 0.8213 | 0.9826 |
| hybrid_qwen_embedding_rerank | 0.8344 | 0.6448 | 0.9030 | 0.9454 | 0.9826 |

## Latência média por etapa (segundos, quando medida)

A etapa dense mede busca exata com vetores de consulta já codificados. A codificação é compartilhada pelas variantes e medida separadamente abaixo; estes tempos não incluem carregamento dos modelos.

| config | bm25 | dense | rerank | rrf |
|---|---|---|---|---|
| bm25 | 0.004056 | — | — | — |
| bm25_rerank | 0.003916 | — | 1.253842 | — |
| dense_colibri | — | 0.000124 | — | — |
| dense_colibri_rerank | — | 0.000298 | 1.208514 | — |
| dense_e5 | — | 0.000165 | — | — |
| dense_e5_rerank | — | 0.000414 | 1.126858 | — |
| dense_qwen_embedding | — | 0.003088 | — | — |
| dense_qwen_embedding_rerank | — | 0.000997 | 1.331393 | — |
| hybrid_colibri | 0.004489 | 0.000163 | — | 0.000090 |
| hybrid_colibri_rerank | 0.004228 | 0.000345 | 1.265735 | 0.000106 |
| hybrid_e5 | 0.005172 | 0.000327 | — | 0.000134 |
| hybrid_e5_rerank | 0.004087 | 0.000343 | 1.228526 | 0.000104 |
| hybrid_qwen_embedding | 0.012123 | 0.015428 | — | 0.000819 |
| hybrid_qwen_embedding_rerank | 0.003876 | 0.000788 | 1.354974 | 0.000135 |

## Codificação das consultas (compartilhada entre variantes)

| embedding | consultas | média (s) | total (s) |
|---|---:|---:|---:|
| colibri | 122 | 0.037766 | 4.607495 |
| e5 | 122 | 0.010854 | 1.324134 |
| qwen_embedding | 122 | 0.035448 | 4.324666 |

## Deltas pareados (sobre as mesmas perguntas)

| comparação | A | B | n | Δ ndcg@10 |
|---|---|---|---|---|
| pipeline_total | hybrid_colibri_rerank | dense_colibri | 122 | 0.1554 |
| hibridizacao | hybrid_colibri | dense_colibri | 122 | 0.0101 |
| rerank_dense | dense_colibri_rerank | dense_colibri | 122 | 0.1504 |
| rerank_hybrid | hybrid_colibri_rerank | hybrid_colibri | 122 | 0.1453 |
| hibridizacao_com_rerank | hybrid_colibri_rerank | dense_colibri_rerank | 122 | 0.0050 |
| pipeline_total | hybrid_qwen_embedding_rerank | dense_qwen_embedding | 122 | 0.1159 |
| hibridizacao | hybrid_qwen_embedding | dense_qwen_embedding | 122 | -0.0457 |
| rerank_dense | dense_qwen_embedding_rerank | dense_qwen_embedding | 122 | 0.0978 |
| rerank_hybrid | hybrid_qwen_embedding_rerank | hybrid_qwen_embedding | 122 | 0.1616 |
| hibridizacao_com_rerank | hybrid_qwen_embedding_rerank | dense_qwen_embedding_rerank | 122 | 0.0181 |
| pipeline_total | hybrid_e5_rerank | dense_e5 | 122 | 0.2351 |
| hibridizacao | hybrid_e5 | dense_e5 | 122 | 0.0527 |
| rerank_dense | dense_e5_rerank | dense_e5 | 122 | 0.2194 |
| rerank_hybrid | hybrid_e5_rerank | hybrid_e5 | 122 | 0.1824 |
| hibridizacao_com_rerank | hybrid_e5_rerank | dense_e5_rerank | 122 | 0.0158 |

## Perguntas bloqueadas (sem gold válido)

Nenhuma.

> Piloto exploratório. Sem conclusões sobre todo o PT-BR, sem alegações de superioridade estatística. Veja `docs/review.md` para limitações.
