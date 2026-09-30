# Execução em RunPod Pod (GPU NVIDIA)

Este guia usa **Pods**, não Serverless. Escolha uma GPU NVIDIA, preferencialmente
com pelo menos 24 GiB de VRAM, e monte um volume persistente em `/workspace`.
SSH ou Jupyter são opcionais. A imagem `Dockerfile.runpod` parte de PyTorch com
CUDA 12.4; use um driver NVIDIA compatível com essa versão. O volume guarda o
repositório, o ambiente Python, snapshots e cache entre reinícios.

## Criar o Pod e clonar

Construa `Dockerfile.runpod` como imagem do Pod, ou use uma imagem RunPod com
CUDA, Python e `git`. A imagem do projeto instala `uv` e as ferramentas
básicas; em outra imagem, o setup instala a versão pinada de `uv` via `pip`.
As dependências vêm de `uv.lock`.

```bash
cd /workspace
git clone https://github.com/lemonieAug/rag-ptbr-retrieval-pilot.git
cd rag-ptbr-retrieval-pilot
export HF_HOME=/workspace/hf-cache
# export TRANSFORMERS_CACHE=/workspace/hf-cache  # somente se uma biblioteca antiga exigir
bash scripts/runpod_setup.sh
source /workspace/.venv-rag-ptbr/bin/activate
bash scripts/runpod_smoke_test.sh
```

`HF_HOME` e o cache do `uv` ficam no volume. O modelo Hugging Face não entra na
imagem. `TRANSFORMERS_CACHE` é legado: prefira só `HF_HOME` se houver aviso da
biblioteca instalada. O setup instala Python 3.11.16 conforme `.python-version`, usa
o lock com `--frozen`, valida CUDA, baixa os quatro snapshots pinados e executa
verificações estruturais. Pode ser repetido. Não executa retrieval.

Confira `python -c "import torch; print(torch.cuda.is_available())"`:
deve imprimir `True` no Pod com GPU.

## Artefatos e corpus

O Git contém código, configuração, benchmark aprovado e qrels. O Git ignora os
PDFs, Markdown extraído, chunks congelados, modelos, índices e resultados.
Transfira os artefatos auditados para os caminhos abaixo por um meio de sua
escolha (por exemplo `rsync` ou volume compartilhado). Não rode `extract` ou
`chunk` para recriar o corpus oficial.

| Artefato | Caminho | Necessário para retrieval |
| --- | --- | --- |
| PDFs originais | `data/raw/articles/` | Obrigatórios para reconstrução de corpus ou índices |
| Markdown revisado | `data/processed/extracted/` | Obrigatório para reconstrução do corpus |
| Corpus congelado | `data/processed/chunks/chunks.jsonl` e `corpus_manifest.json` | Sim |
| Snapshots | `artifacts/models/` | Sim; o setup pode baixar |
| Índices | `artifacts/indexes/` | Podem ser reconstruídos |
| Resultados | `results/` | Produzidos após retrieval |

Rode `python scripts/check_artifacts.py` para ver cada classe como `READY`,
`MISSING` ou `INCOMPATIBLE`, com os caminhos relativos esperados. O script usa
`configs/corpus_reference.yaml`, que contém somente nomes e hashes auditados.
A ausência de arquivos ignorados significa que ainda não foram transferidos,
não que o repositório esteja corrompido. Para
esta edição do experimento, espera-se **5 documentos, 224 chunks** e
`corpus_version` **`8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743`**.
O script destaca qualquer divergência do hash; a biblioteca não exige 224
chunks como regra geral. PDFs e Markdown são comparados com a referência
versionada mesmo quando o manifesto ainda não existe. O Markdown usa o hash
do texto UTF-8 decodificado, conforme o comando `chunk` original.
Sem corpus compatível, o inventário mostra os arquivos do benchmark como
presentes e deixa explícito que a validação cruzada com os chunks está pendente.

Um clone novo **não contém** `chunks.jsonl` nem `corpus_manifest.json`.
Transfira esses dois arquivos auditados para `data/processed/chunks/` antes da
execução oficial. Nenhum comando de setup baixa artigos ou cria dados substitutos.
Se os arquivos congelados não estiverem disponíveis, a reconstrução é uma
ação explícita: transfira primeiro os cinco PDFs canônicos para
`data/raw/articles/` e os cinco Markdown revisados para
`data/processed/extracted/`, confira
`python scripts/check_artifacts.py --require-canonical-sources` e só então rode
`bash scripts/rebuild_audited_corpus.sh`. O script recusa sobrescrever um corpus
existente e exige que o resultado tenha a versão e o hash auditados. `extract`
não é chamado automaticamente, pois o Markdown passou por revisão humana.

As revisões de modelos estão em `configs/model_revisions.yaml`. `prepare-models`
passa cada SHA explícito a `snapshot_download`, verifica o snapshot e grava
`artifacts/models/revisions.json`. Carregamento e retrieval rejeitam revisões
divergentes. O lock contém versões e hashes das dependências para Linux x86-64;
o wheel PyTorch é o CUDA 12.4 (`cu124`).

## Validar e executar

```bash
rag-ptbr status
rag-ptbr validate
python scripts/check_artifacts.py --require-ready
rag-ptbr index
rag-ptbr index  # deve imprimir [reuse] para BM25 e os três densos
rag-ptbr status
```

Para rodar todas as 14 configurações e produzir métricas e relatório, execute
**deliberadamente**, depois de conferir o estado:

```bash
bash scripts/run_official_experiment.sh
```

O script captura o `Run ID:` emitido pelo CLI, verifica que o manifesto existe e
grava a saída em `results/<RUN_ID>/`. A sequência manual equivalente é:

```bash
rag-ptbr retrieve
rag-ptbr evaluate --run-id <RUN_ID>
rag-ptbr report --run-id <RUN_ID>
```

Para ajustar memória, copie `configs/default.yaml` para outro YAML e altere
apenas `runtime.embedding_batch_size` e `runtime.reranker_batch_size`; passe
`-c <arquivo>` aos comandos manuais. Os padrões (8, 2, 2 e 8) reproduzem a
execução anterior. A configuração efetiva e os batches entram no manifesto.

## Geração opcional com Ollama

Ollama não é dependência de retrieval ou avaliação. Em um Pod com espaço e
VRAM suficientes, instale Ollama separadamente, inicie `ollama serve`, rode
`ollama pull qwen3:14b`, teste `curl http://127.0.0.1:11434/api/tags` e
confirme uso da GPU com `nvidia-smi` durante uma consulta de teste. Só então
execute `rag-ptbr generate --run-id <RUN_ID>`. O script oficial não chama essa
etapa. Use cache/modelos do Ollama no volume persistente se quiser mantê-los
entre reinícios.

## Problemas comuns

- **CUDA false:** confirme que o Pod tem GPU, que o driver suporta CUDA 12.4 e
  que o container recebeu a GPU; confira `nvidia-smi` e o PyTorch do lock.
- **OOM:** reduza os batches no YAML de execução. Os modelos são carregados em
  sequência; a alteração de batch não muda chunks, ranking ou métricas.
- **Modelo ausente ou snapshot incorreto:** rode `rag-ptbr prepare-models` e
  compare o SHA em `revisions.json` com `configs/model_revisions.yaml`.
- **Cache HF no filesystem efêmero:** exporte `HF_HOME=/workspace/hf-cache` e
  mantenha o repositório no volume persistente. Revise `df -h /workspace`.
- **Índice incompatível:** execute `rag-ptbr index`; o fingerprint seleciona
  reutilização ou reconstrução. A segunda execução deve mostrar `[reuse]`.
- **Corpus incompatível:** transfira os dois arquivos congelados corretos e
  confira o `corpus_version`. Não regenere o gold ou os chunks.
- **Disco cheio:** libere espaço no volume ou aumente a capacidade do Pod;
  evite apagar o corpus e os snapshots auditados.
