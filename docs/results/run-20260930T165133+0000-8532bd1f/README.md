# Execução RunPod de 30/09/2026

Esta é a seleção para publicação da execução
`run-20260930T165133+0000-8532bd1f`. O pacote original recebido foi
`run-20260930T165133+0000-8532bd1f.tar.gz`, com SHA-256
`e6645e4b4e924d7a808aa7dbd9e682c2d0b3fa643252685f80193ded398310f5`.
Ele foi extraído localmente em `results/`, que permanece ignorado pelo Git.

O [manifesto original](run_manifest.json) registra a GPU **NVIDIA A40**,
CUDA 12.4, Python 3.11.16, `seed` 42 e a versão do corpus
`8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743`.
A identificação da GPU vem do manifesto, mesmo que o Pod tenha sido descrito
anteriormente como A5000. Foram avaliadas 122 perguntas aprovadas; as outras
3 perguntas do benchmark estão rejeitadas. O estudo é exploratório e não
sustenta alegações de superioridade estatística ou generalização para PT-BR.

## Arquivos selecionados para o GitHub

- [Relatório](report.md): médias, latências medidas e deltas pareados.
- [Resumo das métricas](metrics_summary.json): valores agregados das 14 configurações.
- [Comparações](comparison.json): deltas por pergunta e médias das 15 comparações.
- [Manifesto original](run_manifest.json): hashes, revisões, parâmetros e hardware.
- [`metrics/`](metrics/): 14 arquivos com métricas por pergunta e por artigo.

Os 14 rankings completos (`rankings/*.jsonl`, cerca de 54,6 MB descompactados)
ficam somente no pacote original e em `results/`. O pacote `.tar.gz` também
fica fora do Git. PDFs, Markdown extraído, chunks, índices e modelos continuam
ignorados conforme [o guia de dados](../../../data/README.md).

## Conferências feitas na importação

- Os hashes SHA-256 dos 14 rankings conferem com `run_manifest.json`.
- Cada ranking contém 122 IDs de consulta únicos e a configuração esperada.
- As médias dos 14 arquivos em `metrics/` conferem com `metrics_summary.json`.
- As 15 comparações têm 122 deltas cada.
- `questions_hash` e `evidence_groups_hash` conferem com os blobs LF do Git.
  O checkout Windows anterior usava CRLF e produzia hashes diferentes dos
  bytes do Pod; `.gitattributes` fixa LF para esses dois arquivos.

Os tempos no relatório não incluem carregamento dos modelos. A codificação das
consultas foi medida separadamente da busca vetorial, conforme o
[protocolo](../../protocol.md).
