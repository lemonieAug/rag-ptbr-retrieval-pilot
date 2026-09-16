# Guia de anotação

Como criar perguntas, verificar evidências e aprovar o gold. Todo o benchmark é
de desenvolvimento; rascunhos (`draft`) ficam fora da avaliação por padrão.

## 1. Fluxo

1. Rode `rag-ptbr extract` e **revise** `data/processed/extracted/<doc_id>.md`
   (ordem de leitura, seções, tabelas).
2. Rode `rag-ptbr chunk` para **congelar** os chunks (gera os `chunk_id`).
3. Escreva perguntas em `data/annotations/questions.yaml`.
4. Julgue relevância em `data/annotations/qrels.yaml` e, para multi-evidência,
   em `data/annotations/evidence_groups.yaml`.
5. Rode `rag-ptbr validate` até ficar sem erros.
6. Marque `review_status: approved` após revisão humana de cada item.

## 2. Perguntas (`questions.yaml`)

- `question_id`: estável (ex.: `q-001`).
- `text`: a pergunta como será enviada aos métodos (somente o texto).
- `expected_answer`: resposta de referência.
- `origin_doc_id`: artigo de origem — **apenas** para anotação/avaliação.
- `question_type`: `factual` (uma evidência) ou `multi_evidence` (várias).
- `modality`: `text` | `table` | `visual` | `mixed`.
- `review_status`: `draft` → `approved` (só aprovadas entram nas métricas).
- `evidence`: lista com `evidence_id`, `doc_id`, `page`, `section`, `quote`
  (trecho literal verificável no PDF) e, após o chunk, `chunk_ids`.

Recomendações: 25–40 perguntas no total; misture factuais e multi-evidência do
mesmo artigo; as consultas sempre buscam o corpus inteiro.

## 3. Qrels (`qrels.yaml`)

- Um registro por `(question_id, chunk_id)` com `relevance` 0 ou 1.
- **1 = o chunk dá suporte efetivo à resposta.** Coincidir artigo ou página NÃO
  basta. Dois chunks que repetem a mesma informação são redundantes, não dois
  suportes independentes (isso importa para os grupos).

## 4. Grupos obrigatórios (`evidence_groups.yaml`)

Para respostas que dependem de várias informações:

- Cada grupo = UMA informação necessária.
- `chunk_ids` = alternativas (OR) que satisfazem o mesmo grupo.
- Cobertura completa = satisfazer TODOS os grupos obrigatórios.

Chunks sobrepostos que repetem a mesma informação **não** satisfazem grupos
distintos automaticamente.

## 5. Fluxo manual de julgamento de candidatos

Para encontrar evidências alternativas relevantes que a anotação inicial pode ter
perdido: rode `rag-ptbr retrieve` (ou use rankings existentes), inspecione a
**união** dos candidatos dos métodos por pergunta e adicione ao qrel qualquer
chunk que suporte a resposta. Depois **congele uma versão comum dos qrels** antes
de comparar resultados. Julgamentos incompletos limitam as métricas — registre.

## 6. Prevenção de vazamento

Nunca coloque `expected_answer`, `origin_doc_id`, qrels ou grupos no texto da
pergunta nem no prompt de recuperação. Esses campos são só de avaliação. O
`rag-ptbr validate` e os testes de `benchmark.leakage` ajudam a detectar.

## 7. Revisão humana

Use `configs/templates/reviews.yaml` (ou arquivos em `data/annotations/reviews/`)
para registrar: quem revisou, o quê, o status e comentários. Exija revisão de
**100%** das perguntas/respostas/evidências usadas nas métricas.
