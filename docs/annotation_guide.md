# Guia de anotação

Como criar perguntas, verificar evidências e aprovar o gold. Todo o benchmark é
de desenvolvimento; rascunhos (`draft`) ficam fora da avaliação por padrão.

## 1. Fluxo

1. Para um corpus novo, rode `rag-ptbr extract` e **revise** `data/processed/extracted/<doc_id>.md`
   (ordem de leitura, seções, tabelas).
2. Para um corpus novo, rode `rag-ptbr chunk` para **congelar** os chunks (gera os `chunk_id`).
   No piloto atual, preserve os 224 chunks já congelados: não regenere durante a anotação.
3. Escreva perguntas em `data/annotations/questions.yaml`.
4. Julgue relevância em `data/annotations/qrels.yaml` e, para multi-evidência,
   em `data/annotations/evidence_groups.yaml`.
5. Rode `rag-ptbr validate` até ficar sem erros.
6. Registre `review_status: approved` somente após revisão humana de cada item,
   usando o helper descrito abaixo.

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

O banco atual possui 125 perguntas: 20 textuais e 5 multimodais por artigo, em
5 artigos. As consultas sempre buscam o corpus inteiro.

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

O pacote `artifacts/review/gold_review.md` organiza os candidatos para revisão.
Citações, qrels e grupos preparados automaticamente continuam candidatos;
`draft` não significa gold aprovado, mesmo quando toda a evidência foi preenchida.

Liste os rascunhos e inspecione uma pergunta, sem alterar arquivos:

```bash
rag-ptbr review-gold
rag-ptbr review-gold --question-id q-001-t01
rag-ptbr review-gold --next
rag-ptbr review-gold --summary
```

`--next` mostra o primeiro `draft` classificado como `READY_FOR_HUMAN_REVIEW`;
quando não há candidatos prontos, mostra o primeiro pendente. `--summary` conta
os estados diretamente no YAML atual. A classificação automática vem das notas,
e não equivale a aprovação. Ambos são somente leitura; uma decisão sempre exige
`--question-id` explícito. As 119 perguntas prontas podem ser decididas pelo
helper sem edição manual de YAML.

Confira pergunta, resposta, trecho literal, página, conteúdo dos chunks, qrels,
grupos e notas contra a fonte. Após a revisão humana, a pessoa revisora registra
sua decisão explicitamente:

```bash
rag-ptbr review-gold --question-id ID_DA_PERGUNTA --decision approve --reviewer "Nome da pessoa revisora" --confirm-human-review --comments "Evidências conferidas na fonte"
rag-ptbr review-gold --question-id ID_DA_PERGUNTA --decision reject --reviewer "Nome da pessoa revisora" --confirm-human-review --comments "Motivo da rejeição"
```

O helper exige identificação e confirmação, valida o corpus congelado e a
estrutura do benchmark antes de aprovar, verifica a citação literal no Markdown
extraído (na página indicada, quando existem marcadores `PAGE`) e grava um
`ReviewRecord` em `data/annotations/reviews/`. Ele não
confirma semanticamente o suporte: essa decisão pertence à pessoa revisora.
Grupos obrigatórios vazios e evidências incompletas impedem a aprovação.
Uma pendência `MANUAL_VISUAL_REVIEW_REQUIRED` precisa ser resolvida na fonte,
com evidência documentada e atualização das notas, antes de aprovar. Outros
status de análise automática devem ser adjudicados e documentados na revisão.
Nenhum campo `review_status` é acrescentado a `EvidenceGroup`.

Depois das decisões, rode `rag-ptbr validate`. Avisos `draft` indicam itens ainda
fora da avaliação; o comando apresenta contagens por categoria. Retrieval e
avaliação oficiais continuam exigindo perguntas humanamente aprovadas.

`rag-ptbr status --json` inclui contagens de evidências, qrels e grupos, os IDs
pendentes e a validação cruzada atual. Além dos IDs e vínculos, o inventário
rejeita evidência/qrel positivo de artigo diferente da origem. Neste piloto,
um grupo obrigatório em pergunta factual exige justificativa nas notas com
`REQUIRED_GROUP_JUSTIFICATION: descrição do motivo`. Grupos vazios em drafts
continuam avisos; a revisão humana precisa resolvê-los antes da aprovação.

Os seis casos especiais estão detalhados em
`artifacts/review/phase2_gold_pending.md`, com resposta preservada, citação,
página, chunks e a ação humana necessária.
