# Auditoria técnica local — 23/09/2026

## Resultado e limite operacional

O corpus congelado e os índices existentes BM25/Colibri foram validados pelo
código de carregamento usado no retrieval. Os índices Qwen/E5 ainda estão
ausentes. Não foi iniciada uma segunda indexação: já havia um processo do usuário
`C:\Python313\python.exe ...\rag-ptbr.exe index`, PID 12008, pai 29648, iniciado
às 10:00:20 locais. Ele continuava usando CPU e cerca de 23–24 GB de memória
privada, com paginação. Nenhum processo preexistente foi encerrado nesta auditoria.

A instalação atual é Python 3.13.1 e torch 2.13.0+cpu. `nvidia-smi` mostra uma
RTX 3050 de 4096 MiB, mas `torch.cuda.is_available()` é falso. RAM física total
aproximadamente 15,7 GiB; leituras durante a auditoria mostraram apenas 3,5–3,8
GiB disponíveis. O Qwen 4B não cabe na GPU de 4 GiB mesmo numa futura instalação
CUDA com fp16. O checkpoint e a precisão foram preservados; nenhuma reinstalação,
redução de modelo, quantização ou alteração metodológica foi feita.

Os números de memória, status de índices, ambiente e hashes finais estão em
`technical_results.json`; a captura inicial está em `technical_baseline.json`.
`Get-CimInstance Win32_OperatingSystem` foi negado pelo ambiente, portanto a
memória foi lida com `psutil`. Não houve escalada de privilégios.

## Comandos efetivamente executados

- `python --version`: Python 3.13.1.
- `rag-ptbr --help`: CLI importada; inclui agora `review-gold`.
- `rag-ptbr matrix`: exatamente 14 configurações, três embeddings ativos.
- `pytest`: baseline 40 aprovados em 12,77 s; um `PytestCacheWarning` devido a
  permissão na `.pytest_cache` preexistente.
- `pytest -o cache_dir=artifacts/review/.pytest_cache`: 40 aprovados em 10,12 s
  após primeiras correções; depois 50 aprovados em 9,93 s. Cache local removeu
  o warning sem modificar dependências ou testes válidos.
- Testes focais novos de integridade/runtime/run: 24 aprovados em 2,09 s.
- Suíte final: `pytest -o cache_dir=artifacts/review/.pytest_cache` — **91 passed
  em 15,60 s**, sem warnings (inclui os 40 testes originais).
- `rag-ptbr review-gold --question-id q-001-t01`: saída completa, código 0,
  sem precisar configurar `PYTHONIOENCODING`.
- `rag-ptbr validate`: baseline 0 erros e 250 avisos (125 sem quote literal,
  125 drafts sem qrels); validação final abaixo.
- `python -m compileall -q src`: executado sem erros.
- `ollama list`: executável não encontrado no PATH. Nenhum download foi feito.

Não foram executados `extract`, `chunk`, `prepare-models`, retrieval oficial,
evaluate oficial, report oficial ou generate. O processo de indexação encontrado
já existia antes desta tarefa e não é registrado como execução iniciada pelo agente.

## Corpus

- Versão: `8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743`.
- 224 chunks, IDs únicos, texto não vazio, cinco documentos, `frozen=true`.
- Versão recalculada sobre os conteúdos coincide com `hashes.chunks` e manifesto.
- SHA-256 de `chunks.jsonl`: `bd025e6b5b1ce93f203fa1de10c25ccd20add4ef989ff35fa8388b118c1d4607`.
- SHA-256 de `corpus_manifest.json`: `6bdb44775e458c10e59c11568b57b9ab63ec63f9ddfe2f622bc2abc92a3a5780`.
- Os dois hashes foram preservados; não houve regeneração do corpus.

## Índices e modelos locais

| Artefato | Estado verificado |
|---|---|
| `artifacts/indexes/bm25.json` | Compatível; estatísticas, IDs, parâmetros e fingerprint conferidos |
| `artifacts/indexes/dense_colibri/` | Compatível; matriz 224×768, finita/normalizada, revisão, IDs e fingerprint conferidos |
| `artifacts/indexes/dense_qwen_embedding/` | Ausente; indexação concorrente não iniciada |
| `artifacts/indexes/dense_e5/` | Ausente; indexação concorrente não iniciada |

Snapshots dos quatro checkpoints ativos existem nos caminhos fixados por
`artifacts/models/revisions.json`: Colibri `95a4d4f3a1c056ac19e0da196d0ab2b4289e3b3b`,
Qwen embedding `5cf2132abc99cad020ac570b19d031efec650f2b`, E5
`274baa43b0e13e37fafa6428dbc7938e62e5c439`, reranker
`e61197ed45024b0ed8a2d74b80b4d909f1255473`.
O diretório residual do antigo EmbeddingGemma foi preservado e está inativo.
Os cinco arquivos safetensors dos quatro checkpoints foram conferidos por
existência, cabeçalhos, offsets e tamanho; os dois shards referenciados pelo
índice do Qwen estão presentes. Isso não substitui um teste de inferência.
Os hashes dos cinco PDFs e dos cinco Markdown também conferem com o manifesto
(o hash de Markdown usa o texto com finais de linha normalizados pelo Python,
conforme o código que congelou o corpus).

## Bugs corrigidos e garantias

1. `index` reconstruía índices válidos. Agora usa os loaders de retrieval para
   validar/reutilizar cada índice e reconstrói somente o ausente/incompatível.
2. O adapter HF codificava todos os documentos num lote único. Agora divide em
   lotes de dois, preservando ordem, modelo, precisão, pooling e normalização,
   e desativa KV cache desnecessário. `unload` remove referências diretamente,
   sem copiar pesos de volta para CPU antes de liberar memória.
3. `retrieve` carregava todos os embeddings e reranker simultaneamente. Agora
   codifica consultas com um embedding por vez e descarrega antes do próximo;
   o reranker só é carregado depois. Seeds são efetivamente aplicadas.
4. Revisões constavam do fingerprint mas o carregamento usava o nome do repo
   sem fixar revisão. Agora o caminho local do snapshot é obrigatório e os
   construtores usam `local_files_only=True`; ausência falha sem download.
5. `Qwen3Reranker` referia `self.checkpoint`, atributo inexistente; passa a usar
   `self.spec.checkpoint`. Configuração de checkpoint/instrução ignorada
   silenciosamente agora é rejeitada, mantendo o reranker fixo do protocolo.
6. Saída bf16 não era convertível para NumPy. A conversão do tensor para fp32
   ocorre antes de `.numpy()`, sem alterar a precisão da inferência.
7. Catálogo e schema ainda aceitavam EmbeddingGemma. A opção foi removida;
   tanto `models.embeddings` quanto `experiments.embeddings` rejeitam o modelo.
8. Loaders validam conteúdo/versão/frozen do corpus; parâmetros e estatísticas
   BM25; shape, dimensão nativa, normalização, IDs, revisão e encoding do denso.
9. Índices densos novos incluem `encoding_config` com spec/templates/precisão.
   Índices legados só são aceitos quando esse contrato coincide com hashes
   literais dos defaults originais auditados; mudanças de dtype/template são
   detectadas. BM25 e Colibri existentes não foram regravados.
10. Reutilização de runs agora confere hashes de config/corpus/qrels/prompts/
    perguntas/grupos/revisões/rankings, configurações completas, perguntas
    aprovadas e IDs de chunks. Execuções antigas sem esses dados são recusadas.
11. A cache de vetores de consulta inclui o texto, além de embedding/question_id.
12. Tempos de codificação de consulta são medidos por pergunta e registrados em
    `parameters.query_encoding_seconds`; dense mede busca no vetor em cache.
    O relatório mostra as duas medidas separadamente, sem somar tempo artificial.
13. As proteções de aprovação humana foram preservadas. Retrieval também exige
    validação estrutural do benchmark antes de carregar modelos.
14. O comando de revisão falhava no Windows com saída CP1252 ao imprimir
    caracteres literais da extração, como `ı`. A CLI configura stdout/stderr
    para UTF-8; dois testes em subprocessos com CP1252 reproduzem a condição.
15. A preparação do gold recusa sobrescrever edições humanas posteriores,
    inclusive em perguntas ainda draft, e detecta mudanças concorrentes.

Correções anteriores foram mantidas: import tardio de AppConfig, `nonlocal
table_caption`, `SentenceTransformer(local_files_only=True)` no topo, orçamento
de contexto vazio e exclusão do modelo gated da matriz experimental.

## Benchmark e bloqueio científico

A revisão de evidências consta de `gold_review.md`. Todas as 125 questões seguem
draft. A validação final relatou 0 erros e 130 avisos: 125 `draft`,
2 `empty_required_group`, 2 `missing_evidence_chunks` e 1 `missing_qrels`.
Esses avisos não são ignorados nem convertidos em aprovação pelo agente.
Saída completa preservada em `validate_final.txt`.

Retrieval oficial não executado porque o benchmark ainda aguarda aprovação
humana. Não há RUN_ID, métricas oficiais ou relatório experimental. Os testes
usam fixtures sintéticas e não equivalem a validar inferência real de Qwen/E5.
Geração: `SKIPPED` — Ollama não acessível no PATH, disponibilidade de
`qwen3:14b` não comprovada; nenhum modelo foi baixado.

## Próximas ações

1. Resolver a indexação preexistente com o usuário; após seu término, rodar
   `rag-ptbr index`, que preservará BM25/Colibri e completará somente o faltante.
2. `rag-ptbr review-gold` lista drafts; seguir o helper e `gold_review.md` para
   aprovações humanas explícitas e casos de revisão visual.
3. Após índices completos e gold aprovado: `rag-ptbr validate`, `rag-ptbr retrieve`,
   `rag-ptbr evaluate --run-id <RUN_ID>` e `rag-ptbr report --run-id <RUN_ID>`.

Não houve commit, push, merge, descarte de alterações, exclusão de caches ou
reinicialização do ambiente.
