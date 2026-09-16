# Estrutura do diretório de dados

Este diretório contém os dados do piloto. Os arquivos reais que VOCÊ fornece
começam vazios; os templates ficam em `configs/templates/` e os exemplos
sintéticos (para testes/demo) em `examples/synthetic/`.

```
data/
  raw/articles/          -> coloque os PDFs aqui (data/raw/articles/<nome>.pdf)
  metadata/              -> data/metadata/articles.yaml (metadados dos artigos)
  annotations/           -> perguntas, qrels e grupos de evidência (o "gold")
    reviews/             -> registros opcionais de revisão humana
  processed/             -> GERADO pelo pipeline (não editar manualmente)
    extracted/           -> <doc_id>.md + <doc_id>.provenance.json
    corrections/         -> anotações de correções manuais (opcional)
    chunks/              -> chunks.jsonl + corpus_manifest.json (congelado)
```

## O que é versionado (recomendado) vs. o que é ignorado

- **Versionar para reproduzir**: `data/metadata/articles.yaml` e os arquivos em
  `data/annotations/` (perguntas, qrels, grupos). São o benchmark.
- **Ignorado por padrão** (via `.gitignore`): PDFs, extrações, chunks, caches de
  modelos, índices pesados e saídas em `results/`.

## Convenções

- `doc_id` é estável e usado em chunks e evidências (ex.: `art-001`).
- Nome de PDF sugerido: `art-001_<slug-curto>.pdf` (ex.: `art-001_anemia_ferropriva.pdf`).
