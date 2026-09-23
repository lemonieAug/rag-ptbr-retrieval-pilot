# Auditoria técnica — Fase 2

> Estado após decisões humanas de Augusto Lemonie Gilioli: **122 aprovadas, três rejeitadas e nenhum draft**. Validação: zero erros e cinco avisos restritos às perguntas rejeitadas. **Retrieval liberado para as 122 aprovadas**: `ready_for_retrieval: true`, sem bloqueios, com quatro índices válidos e 14 configurações. Inventário atual: `gold_current_audit.json`; status: `status_after_human_review.json`. Nenhum retrieval ou avaliação oficial executado nesta revisão.

As primeiras 119 aprovações constam de `human_approval_20260923_142224/approval.json`. A q-001-t15 foi reformulada para perguntar pela conclusão declarada pelos autores, com aprovação explícita e divergência da Tabela 3 documentada nas notas; registro em `adjudication_q001t15/adjudication.json`.

A q-001-t20 foi rejeitada por decisão explícita: a contribuição declarada não tem suporte integral no texto indexado do corpus congelado, sem qrel positivo válido. ReviewRecord: `data/annotations/reviews/review-8b704a13508c4bde90c6506cf3bddfb6.yaml`.

A q-001-m05 foi rejeitada por decisão explícita: os chunks não preservam a associação inequívoca dos valores da tabela ao rótulo FLAIR, deixando um grupo obrigatório sem suporte. ReviewRecord: `data/annotations/reviews/review-fb2727fa1497457db7fa8948056edc76.yaml`.

A q-003-t17 foi reformulada e aprovada explicitamente para perguntar pelo nome e pela sigla atribuídos pelos autores à métrica. A resposta recebeu a ressalva aprovada "conforme denominado no artigo"; a inconsistência RMSE/MSE permanece nas notas. Registro: `adjudication_q003t17/adjudication.json`; ReviewRecord: `data/annotations/reviews/review-5e4575c5726641d298894e960ef788aa.yaml`.

A q-003-m03 foi rejeitada por decisão explícita: a atribuição dos resultados a Campo Verde e Maracaju depende das barras das Figuras 2 e 3, não preservadas nos chunks. A anotação `MANUAL_VISUAL_REVIEW_REQUIRED` permanece como justificativa histórica, sem afirmar inspeção visual. ReviewRecord: `data/annotations/reviews/review-35f076c4da834971aca2caca57375037.yaml`.

A q-004-t18 foi reformulada e aprovada explicitamente para atribuir à conclusão do artigo os ganhos de 25,35% em PBR e 24,87% em RDB. A resposta sobre baixa incidência de XT foi mantida, e a divergência do resumo (24,81%) permanece nas notas. Registro: `adjudication_q004t18/adjudication.json`; ReviewRecord: `data/annotations/reviews/review-a43132bdf8464e8dbb106eb4e1cf7a1c.yaml`.

Todas as 125 perguntas possuem exatamente um ReviewRecord correspondente ao status atual, em nome do revisor. Além das mudanças de status, somente as redações adjudicadas de q-001-t15, q-003-t17 e q-004-t18, suas notas e a ressalva da resposta de q-003-t17 foram alteradas nesta revisão humana. Evidências, qrels, grupos, corpus e índices foram preservados. Próximo comando: `rag-ptbr retrieve`. Os resultados abaixo documentam o fechamento técnico anterior às decisões.

Conferência final: 2026-09-23T14:07:27.239268.

Os quatro índices passaram pelos loaders atuais. Reranker local disponível e smoke de inferência concluído.
Único bloqueio para o experimento oficial: `HUMAN_GOLD_REVIEW_REQUIRED`.

## Processo antigo PID 12008

Encontrado em execução desde 10:00:20, com código anterior às correções, memória privada de 30,54 GB e sem artefatos Qwen/E5.
Às 11:48:14, `CloseMainWindow()` retornou falso (sem janela); foi necessário `Stop-Process -Id 12008 -Force`.
Ausência do PID confirmada após encerramento. Detalhes em `phase2_process_stop.json`.

## Indexação e integridade

Executado o handler atual `cli.cmd_index(SimpleNamespace(config=None))`, com instrumentação local em `phase2_index_run.py`.
BM25 e Colibri reutilizados, com hashes idênticos ao baseline. Qwen e E5 recalculados sequencialmente, com unload entre modelos.
Verificados corpus, IDs/ordem/unicidade, shape, dimensão, checkpoint/revision, fingerprint, encoding, dtype, finitude e normalização.

| Índice | Checkpoint | Revision | Dimensão | Shape | Fingerprint | Corpus version | Status |
|---|---|---|---|---|---|---|---|
| bm25 | — | — | — | [224] | 70f04c712b228d70a9106a52e2ab6a586e853bc7c61f97efb9c9a23ae48b6e2b | 8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743 | VALID |
| colibri | tardellirs/colibri-embed-ptbr | 95a4d4f3a1c056ac19e0da196d0ab2b4289e3b3b | 768 | [224, 768] | f4324759214c5801eec5c9e570463da3c8b792e3420cbe2d764e9cddca4a46dc | 8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743 | VALID |
| qwen_embedding | Qwen/Qwen3-Embedding-4B | 5cf2132abc99cad020ac570b19d031efec650f2b | 2560 | [224, 2560] | 689f2fe282ac056acc26c105287e2705f3c510bc84924a290af946a1eb847228 | 8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743 | VALID |
| e5 | intfloat/multilingual-e5-large-instruct | 274baa43b0e13e37fafa6428dbc7938e62e5c439 | 1024 | [224, 1024] | cdd660fc48aa8c3e26921406edf99e11a04cd5ccee0d9dfbd0d552c17eee9215 | 8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743 | VALID |

## Recursos e duração

Torch CPU; precisão e checkpoints preservados. As matrizes são persistidas em float32.
Memórias abaixo são máximos amostrados nos eventos, não uma medição contínua de pico.

| Modelo | Device | Dtype | Batch | Tempo total (s) | RSS máximo amostrado (GiB) | Privada máxima amostrada (GiB) |
|---|---|---|---|---|---|---|
| qwen_embedding | cpu | torch.float16 | [2] | 8019.63 | 6.99 | 11.64 |
| e5 | cpu | torch.float32 | [2] | 152.30 | 6.99 | 11.52 |

O tempo de Qwen inclui uma pausa de cerca de três minutos para um microbenchmark sintético isolado de threads.
O ensaio de 1/2 threads não mostrou ganho; os ensaios restantes foram cancelados e a indexação retomada com 12 threads, sem mudanças.
Registro: `phase2_cpu_threads_benchmark.json`. GPU RTX 3050 de 4096 MiB disponível no sistema, porém CUDA indisponível nesta instalação de torch.

## Smoke técnico

Três textos de perguntas reais foram codificados por cada embedding, sem uso de respostas esperadas ou origem para recuperar.
Cada busca retornou cinco chunks existentes com scores finitos; dimensões compatíveis. Reranker produziu dois scores finitos.
Rede bloqueada pelo runner; zero tentativas registradas. Rankings somente técnicos em `phase2_index_validation.json`, sem avaliação de qualidade.

## Testes e revisão

```text
........................................................................ [ 59%]
.................................................                        [100%]
121 passed in 8.01s
```

`rag-ptbr validate`: zero erros estruturais. `rag-ptbr matrix`: 14 configurações. `git diff --check`: código 0.
Cobertura inclui caches parciais/incompatíveis, reutilização sem inferência, Gemma rejeitado, confirmação humana e status com fingerprint incompatível.
`review-gold --question-id`, `--next` e `--summary` conferidos em modo de leitura. Aprovação exige ID explícito, reviewer e confirmação; testes de escrita usam fixtures sintéticas.

## Benchmark

125 perguntas draft, zero aprovadas; 119 prontas e seis pendentes. 157 qrels positivos para 124 perguntas; 176 evidências com quote/página, 174 com chunks; 62 grupos obrigatórios, 2 vazios.
Avisos: `{'empty_required_group': 2, 'draft': 125, 'missing_evidence_chunks': 2, 'missing_qrels': 1}`. Os seis casos completos estão em `phase2_gold_pending.md`; q-003-m03 preserva MANUAL_VISUAL_REVIEW_REQUIRED.
Invariantes conferidos diretamente nos YAMLs por `phase2_verify_gold.py`/`audit_gold`, incluindo referências, duplicatas, origem de evidências e justificativa de grupos factuais.

Também foram conferidas as 176 citações literais nas páginas indicadas do Markdown; as 125 respostas esperadas coincidem com HEAD. Registro: `phase2_gold_source_check.json`.

## Próxima ação

```powershell
rag-ptbr review-gold --next
```

Após decisões humanas, conferir `rag-ptbr status` e `rag-ptbr validate`; então executar retrieve → evaluate → report.
Nenhuma aprovação real, retrieval/avaliação oficial, commit ou push realizado. Corpus e índices reutilizados preservados; hashes em `phase2_results.json`.
A auditoria anterior permanece em `phase1_technical_audit.md` e `phase1_technical_results.json` como registro histórico.

## Conferência de reutilização após conclusão

`rag-ptbr index` executado diretamente após a conclusão: quatro mensagens `[reuse]`, código 0 e hashes dos sete arquivos de índices preservados. Saída em `phase2_all_indexes_reuse.txt`.

O monitor final separa 224 documentos por modelo das três consultas técnicas e registra `status: complete`; o PID 3164 já terminou.
