# Pacote de revisão humana do gold

Preparação de candidatos por IA. **Nenhuma questão foi aprovada.** READY_FOR_HUMAN_REVIEW significa pronta para inspeção humana, não gold validado. As 125 questões permanecem `draft`.

| Indicador | Quantidade |
| --- | ---: |
| Total de perguntas | 125 |
| Prontas para revisão | 119 |
| Com conflito | 2 |
| Ambíguas | 3 |
| Sem evidência | 0 |
| Dependentes de revisão visual | 1 |
| Evidências com quote literal e página verificada | 176 |
| Evidências com chunks mapeados | 174 |
| Perguntas com qrels candidatos | 124 |
| Qrels positivos candidatos únicos | 157 |
| Grupos obrigatórios | 62 |
| Grupos sem chunks | 2 |

Corpus: `8532bd1f3284ec8ce5446943020b7c894b306fbf7b11795d4d891423c2dd9743`; 224 chunks congelados. As páginas são números físicos do PDF (marcadores PAGE da extração, conferidos com provenance); não foram inferidas pela seção.

## Método e limites

Perguntas, respostas, seções e notas da pré-anotação foram lidas contra Markdown/provenance e conteúdo dos chunks. Os scripts preservados contêm seleções explícitas de trechos. A correspondência literal resolve IDs de chunks somente depois da seleção semântica; nenhuma similaridade lexical determinou relevância. Qrels positivos também podem representar um componente necessário de respostas compostas. Não são exaustivos: não se produziram negativos pela ausência de anotação. Nenhum método de retrieval foi usado para favorecer seus resultados.

As citações preservam exatamente acentos corrompidos, hifenizações e espaços da extração. Os nomes de seção foram apresentados de forma legível quando o chunker interpretou incorretamente títulos/linhas. A evidência nunca foi reconstruída a partir da resposta esperada. Figuras/tabelas foram substituídas por prosa somente quando essa prosa explicita a informação solicitada; isso prepara a resposta, mas não demonstra competência visual do retriever. A modalidade/tipo original das perguntas foi preservada.

Cada grupo representa uma informação necessária; IDs dentro dele são alternativas OR, grupos distintos são AND. Algumas perguntas rotuladas multi_evidence pedem apenas um fato composto (por exemplo, líder e suas métricas), sendo suficiente um grupo. Listas com componentes separadamente verificáveis podem ter vários grupos, inclusive satisfeitos pelo mesmo chunk. A granularidade editorial deve ser confirmada na revisão humana. Não foram criados grupos por sobreposição de chunks. Cabeçalhos e linha de tabela separados podem ser informações complementares necessárias, como em q-005-m05.

O JSON paralelo preserva notas/evidências originais, status por pergunta, qrels, grupos e alterações de resposta antes/depois. As instruções antigas para executar chunk foram substituídas, pois o corpus já está congelado. Nenhum ReviewRecord de aprovação humana foi fabricado.

## Alterações de expected_answer

Nenhuma resposta esperada foi alterada nesta preparação.

## Questões que exigem adjudicação

- **q-001-t15 — SOURCE_CONTRADICTION**: A narrativa afirma superioridade em precisão e F1 nas duas classes, mas a Tabela 3 empata F1 de legislação (FLAIR/TensorFlow: 0,89) e precisão de jurisprudência (FLAIR/spaCy: 0,78). A resposta foi preservada para adjudicação humana; o qrel candidato sustenta a afirmação narrativa, não resolve a contradição.
- **q-001-t20 — AMBIGUOUS_EVIDENCE**: O início da contribuição (produção de nova base de petições) foi interpretado pelo chunker como section, enquanto text conserva apenas primeira base deste tipo anotada manualmente. Indexação/reranking/geração usam text e não section. Não há suporte integral no conteúdo de um chunk; quote/página verificáveis na fonte, sem qrel. Não foi alterado o corpus congelado.
- **q-001-m05 — AMBIGUOUS_EVIDENCE**: Fonte Markdown sustenta a resposta, mas o chunker separou a linha numérica da legislação FLAIR (fim de b0022) do rótulo FLAIR (section de b0023). Nenhum chunk isolado preserva a associação inequívoca modelo/linha; grupo FLAIR fica sem chunk. Corpus congelado preservado. Não tratar mera proximidade como qrel suficiente.
- **q-003-t17 — AMBIGUOUS_EVIDENCE**: O artigo chama a métrica de Erro Quadrático Médio (RMSE), e a explicação da seção 4 descreve média de diferenças quadráticas sem raiz. RMSE e MSE são conceitualmente diferentes; preservada a resposta que reproduz o artigo, exigindo adjudicação da nomenclatura sem inferir código externo.
- **q-003-m03 — MANUAL_VISUAL_REVIEW_REQUIRED**: A resposta pré-anotada diz uma localidade/outra sem atribuir a melhora a Campo Verde ou Maracaju. A prosa sustenta heterogeneidade e dificuldade de ajuste, mas a comparação cidade a cidade das Figuras 2/3 depende das barras não extraídas. Grupos textuais são candidatos parciais; confirmar atribuição visual antes de aprovar.
- **q-004-t18 — SOURCE_CONTRADICTION**: Conflito interno da fonte: o resumo (p.1) registra 24,81% de RDB mínimo em baixa incidência de XT; a conclusão e a Tabela 4 (p.12) registram 24,87%. A resposta e o número da pergunta coincidem com conclusão/tabela e foram preservados, sem resolver arbitrariamente a divergência. Mantido draft. Trecho conflitante literal do resumo: "de bloqueio de requisic¸a˜o (PBR) e de ao menos 24,81% em termos de raza˜o de
dados bloqueados (RDB)."

## Artigo art-001

### q-001-t01

**Pergunta:** Qual é a tarefa de processamento de linguagem natural investigada pelo artigo no domínio jurídico?

**Expected answer:** Reconhecimento de entidades nomeadas (REN/NER) em textos jurídicos

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t01-e1 — página 2; seção 1. Introdução:**

```text
Neste sentido, este trabalho propo˜e uma avaliac¸a˜o de te´cnicas de extrac¸a˜o de
informac¸a˜o chamada de reconhecimento de entidades nomeadas (do ingleˆs, Named
Entity Recognition - NER) [YadavandBethard2019] para o contexto jur´ıdico bra-
sileiro. Estas te´cnicas consistem em localizar em um texto palavras e classifica-
las de acordo com ro´tulos previamente definidos. Aplicac¸o˜es comuns de NER
```

**Chunk IDs:** `art-001-b0004-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0004-c000`

### q-001-t02

**Pergunta:** Quais dois tipos de entidades o trabalho busca extrair das petições iniciais?

**Expected answer:** Legislação e jurisprudência

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t02-e1 — página 2; seção 1. Introdução:**

```text
de aplicac¸a˜o de me´todos de PLN na resoluc¸a˜o de problema do setor jur´ıdico. O presente
trabalho se propo˜e a extrair legislac¸o˜es e jurisprudeˆncias como entidades nomeadas de
petic¸o˜es iniciais. Duas bases de dados foram avaliadas: a base de dados LeNER-br,
```

**Chunk IDs:** `art-001-b0004-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0004-c001`

### q-001-t03

**Pergunta:** Que tipo de documento jurídico compõe exclusivamente a base proprietária proposta?

**Expected answer:** Petições iniciais de processos da primeira instância da Justiça brasileira

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t03-e1 — página 2; seção 1. Introdução:**

```text
proposta originalmente por [Luz de Araujo et al. 2018] e uma base de dados proprieta´ria,
produzida neste trabalho, a qual consiste de petic¸o˜es iniciais de processos que tramitaram
na primeira instaˆncia da justic¸a Brasileira. Esta base e´ composta por 1676 trechos
de petic¸o˜es iniciais, contendo um total de 3825 anotac¸o˜es das entidades legislac¸a˜o e
```

**Chunk IDs:** `art-001-b0004-c002`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0004-c002`

### q-001-t04

**Pergunta:** Quais são as duas bases de dados avaliadas pelos autores?

**Expected answer:** LeNER-Br e uma base proprietária construída a partir de petições iniciais

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t04-e1 — página 2; seção 1. Introdução:**

```text
proposta originalmente por [Luz de Araujo et al. 2018] e uma base de dados proprieta´ria,
produzida neste trabalho, a qual consiste de petic¸o˜es iniciais de processos que tramitaram
na primeira instaˆncia da justic¸a Brasileira. Esta base e´ composta por 1676 trechos
```

**Chunk IDs:** `art-001-b0004-c002`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0004-c002`

### q-001-t05

**Pergunta:** Qual biblioteca é apresentada como voltada à aplicação industrial de técnicas de PLN?

**Expected answer:** spaCy

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t05-e1 — página 6; seção 5. Metodologia Experimental:**

```text
se de bibliotecas para processamento de linguagens naturais de propostas opostas. En-
quanto o FLAIR tem o foco em facilitar a execuc¸a˜o de experimentos para trabalhos ci-
ent´ıficos por pesquisadores, o Spacy se concentra na aplicac¸a˜o industrial de te´cnicas
PLN. Neste artigo, foram treinados, avaliados e comparados treˆs redes neurais: duas
```

**Chunk IDs:** `art-001-b0014-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0014-c000`

### q-001-t06

**Pergunta:** Qual biblioteca é caracterizada como focada em facilitar experimentos científicos para pesquisadores?

**Expected answer:** FLAIR

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t06-e1 — página 6; seção 5. Metodologia Experimental:**

```text
se de bibliotecas para processamento de linguagens naturais de propostas opostas. En-
quanto o FLAIR tem o foco em facilitar a execuc¸a˜o de experimentos para trabalhos ci-
ent´ıficos por pesquisadores, o Spacy se concentra na aplicac¸a˜o industrial de te´cnicas
PLN. Neste artigo, foram treinados, avaliados e comparados treˆs redes neurais: duas
```

**Chunk IDs:** `art-001-b0014-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0014-c000`

### q-001-t07

**Pergunta:** Quais três arquiteturas ou implementações de redes neurais foram comparadas?

**Expected answer:** A CNN do spaCy, uma BiLSTM-CRF implementada em TensorFlow e uma BiLSTM-CRF do FLAIR com FLAIR embeddings

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t07-e1 — página 7; seção 6. Resultados:**

```text
Comopodeserobservado,omodeloSpacyutilizaumaCNN(ConvolutionalNeu-
ral Network com conexo˜es residuais e usa Bloom Embeddings para representar palavras.
OFLAIR,porsuavez,usaumaBiLSTM-CRF(BidirectionalLong-ShortTermMemory-
Conditional Random Fields), que e´ o modelo que domina o estado-da-arte para tarefas
desequencelabeling,segundo[Akbiketal. 2018]. Asconfigurac¸o˜esutilizadasnotreina-
mento do modelo do FLAIR seguiram as recomendac¸o˜es de configurac¸o˜es do modelo de
maior desempenho apresentado por esse mesmo trabalho: uma combinac¸a˜o de BiLSTM
comumaCRFlayereFLAIRembeddings,forwardebackward,paragerac¸a˜odosvetores
depalavras.
```

**Chunk IDs:** `art-001-b0021-c000`.
**Grupo:** Não aplicável.

**Evidência q-001-t07-e2 — página 8; seção 6. Resultados:**

```text
Por outro lado, para reproduzir o modelo apresentado por
[LuzdeAraujoetal. 2018], empregou-se o uso do TensorFlow [Abadietal. 2015],
uma biblioteca para aprendizagem de ma´quina publicada e distribu´ıda pelo Google. A
arquitetura utilizada consiste no mesmo modelo proposto por [Lampleetal. 2016], o
qual consiste e uma BiLSTM combinada com um algoritmo probabil´ıstico, o CRF, e
incorporac¸o˜esdepalavras(i.e.,embeddings)a` n´ıveldecaractere.
```

**Chunk IDs:** `art-001-b0022-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0021-c000`, `art-001-b0022-c000`

### q-001-t08

**Pergunta:** Qual é a pergunta de pesquisa formulada pelos autores?

**Expected answer:** Identificar qual arquitetura escolhida tem melhor precisão, recall e F1 na tarefa de REN no domínio jurídico

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t08-e1 — página 4; seção 3. Pergunta de Pesquisa:**

```text
PERGUNTA DE PESQUISA: Das arquiteturas escolhidas, qual possui
a melhor performance em termos de precisa˜o, recall e F score na tarefa
1
dereconhecimentodeentidadesnomeadasnodom´ıniojur´ıdico?
```

**Chunk IDs:** `art-001-b0009-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0009-c000`

### q-001-t09

**Pergunta:** Por que a arquitetura BiLSTM-CRF é considerada híbrida no artigo?

**Expected answer:** Porque combina uma BiLSTM com o modelo probabilístico Conditional Random Fields (CRF)

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t09-e1 — página 4; seção 4.1. BiLSTM-CRF:**

```text
Essaarquiteturacombinaumaredeneuralbidirectionallong-shorttermmemorycomum
modelobaseadoemprobabilidade,oconditionalrandomfields[Lampleetal. 2016]. Ela
foi usada em [LuzdeAraujoetal. 2018] para avaliar o desempenho do dataset proposto
e, tambe´m, e´ arquitetura padra˜o empregada pelo FLAIR. A proposta dele e´ utilizar um
algoritmo que leve em conta uma quantidade virtualmente infinita de contexto e passar
seus resultados para uma camada CRF, que por sua vez, se encarregara´ do rotulac¸a˜o das
sequeˆnciasdepalavras,capturandoasdependeˆnciasaolongodosro´tulos.
```

**Chunk IDs:** `art-001-b0011-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0011-c000`

### q-001-t10

**Pergunta:** Qual arquitetura interna o artigo atribui ao modelo de NER treinado pelo spaCy?

**Expected answer:** Uma CNN com conexões residuais

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t10-e1 — página 7; seção 6. Resultados:**

```text
Comopodeserobservado,omodeloSpacyutilizaumaCNN(ConvolutionalNeu-
ral Network com conexo˜es residuais e usa Bloom Embeddings para representar palavras.
```

**Chunk IDs:** `art-001-b0021-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0021-c000`

### q-001-t11

**Pergunta:** Que recurso foi usado para extrair o conteúdo textual das páginas das petições da base proprietária?

**Expected answer:** OCR

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t11-e1 — página 6; seção 5.1. Base de Dados:**

```text
Abasededadosfoiextra´ıdade74petic¸o˜esiniciaisdeprocessosquetramitaramnajustic¸a
brasileira, de acesso acesso privado, fazendo um total de 1676 trechos extra´ıdos. As
pa´ginasdaspetic¸o˜esiniciaisforamsubmetidasa` umprocessodeOCR(opticalcharacter
recognition) para extrac¸a˜o do conteu´do textual que viria ser utilizado na composic¸a˜o do
conjunto de treinamento empregado neste trabalho. Em contraste, a base de dados do
```

**Chunk IDs:** `art-001-b0015-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0015-c000`

### q-001-t12

**Pergunta:** Qual foi a proporção de divisão aleatória entre treinamento e teste?

**Expected answer:** 70% para treinamento e 30% para teste

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t12-e1 — página 7; seção 5.2. Medidas de Avaliação:**

```text
O conjunto de dados foi dividido em dois subconjuntos, um para treinamento, composto
por 70% das amostras e outro para teste, composto por 30%, ambas selecionadas aleato-
riamente. Para cada umas das arquiteturas utilizadas foram empregadas as configurac¸o˜es
```

**Chunk IDs:** `art-001-b0019-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0019-c000`

### q-001-t13

**Pergunta:** Quais métricas foram usadas para avaliar as arquiteturas?

**Expected answer:** Precisão, recall e F1 score

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t13-e1 — página 7; seção 5.2. Medidas de Avaliação:**

```text
as especificac¸o˜es trazidas em [LuzdeAraujoetal. 2018]. Como medidas de avaliac¸a˜o
foramusadasasme´tricasdeprecisa˜o,recalleF score,descritasaseguir:
1
```

**Chunk IDs:** `art-001-b0019-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0019-c000`

### q-001-t14

**Pergunta:** Por que o F1 score é considerado confiável para a avaliação da base proposta?

**Expected answer:** Porque a base é desbalanceada e o F1 equilibra precisão e recall

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t14-e1 — página 6; seção 5.1. Base de Dados:**

```text
conjuntodetreinoedeteste. poss´ıvelnotarpormeiodessasfigurasqueabasededados
encontra-se desbalanceada, o que torna o F score uma me´trica bastante confia´vel para
1
medirodesempenhodosmodelosaseremtreinados.
```

**Chunk IDs:** `art-001-b0016-c000`.
**Grupo:** Não aplicável.

**Evidência q-001-t14-e2 — página 7; seção 5.2. Medidas de Avaliação:**

```text
positivos sa˜o de fato positivos. O F score, por fim, mostra uma relac¸a˜o harmoˆnica entre
1
precisa˜o e recall para que possa-se reconhecer qual modelo possui o melhor balancea-
mentoentreessasduasme´tricas.
```

**Chunk IDs:** `art-001-b0019-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0016-c000`, `art-001-b0019-c000`

### q-001-t15

**Pergunta:** Qual modelo apresentou desempenho superior em precisão e F1 score nas duas categorias de entidades?

**Expected answer:** BiLSTM-CRF com FLAIR embeddings, treinado com a biblioteca FLAIR

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `SOURCE_CONTRADICTION`.

**Observações:** A narrativa afirma superioridade em precisão e F1 nas duas classes, mas a Tabela 3 empata F1 de legislação (FLAIR/TensorFlow: 0,89) e precisão de jurisprudência (FLAIR/spaCy: 0,78). A resposta foi preservada para adjudicação humana; o qrel candidato sustenta a afirmação narrativa, não resolve a contradição.

**Evidência q-001-t15-e1 — página 8; seção 6. Resultados:**

```text
Pode-se observar que, de acordo com os resultados apresentados na Tabela 3 o
modelo BiLSTM-CRF com FLAIR embeddings treinado com aux´ılio da biblioteca para
PLN FLAIR apresentou resultados superiores com relac¸a˜o a` precisa˜o e F score em am-
1
bas as categorias de entidades anotadas na base de dados analisada. Entretanto, o melhor
```

**Chunk IDs:** `art-001-b0023-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0023-c000`

### q-001-t16

**Pergunta:** Qual modelo obteve o melhor recall segundo a discussão dos resultados?

**Expected answer:** A BiLSTM-CRF implementada em TensorFlow, reproduzida a partir de Luz de Araujo et al

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Pergunta explicitamente limitada à discussão: ela atribui melhor recall ao TensorFlow. A Tabela 3 limita essa vantagem à legislação (0,87 versus 0,85); jurisprudência favorece FLAIR (0,53 versus 0,44). Não interpretar como superioridade em ambas as classes.

**Evidência q-001-t16-e1 — página 8; seção 6. Resultados:**

```text
bas as categorias de entidades anotadas na base de dados analisada. Entretanto, o melhor
score para recall na˜o foi alcanc¸ado por ele, mas sim pelo modelo BiLSTM-CRF usado
por [LuzdeAraujoetal. 2018] em seus pro´prios experimentos. Contudo, vale ressaltar
que a diferenc¸a entre as pontuac¸o˜es adquiridas pelo modelo do FLAIR e do TensorFlow
na˜o foram ta˜o distantes uma da outra, o que, como pode ser visto pelo seu F score,
```

**Chunk IDs:** `art-001-b0023-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0023-c000`

### q-001-t17

**Pergunta:** Qual foi o modelo de pior desempenho geral entre os comparados?

**Expected answer:** A CNN com conexões residuais do spaCy

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t17-e1 — página 8; seção 6. Resultados:**

```text
torna o modelo BiLSTM-CRF com FLAIR embeddings o modelo com melhor equil´ıbrio
entre precisa˜o e recall. O modelo CNN com conexo˜es residuais, por sua vez, mostrou-
se ter a pior performance entre seus pares. Quando comparado com o modelo treinado
pelo FLAIR, ele na˜o conseguiu se sobressair em nenhuma me´trica. E´ importante notar,
```

**Chunk IDs:** `art-001-b0023-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0023-c000`

### q-001-t18

**Pergunta:** Qual característica dos FLAIR embeddings é citada como capaz de melhorar os scores do modelo?

**Expected answer:** A geração de vetores de palavras usados como entrada para a rede neural

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t18-e1 — página 8; seção 6. Resultados:**

```text
Ale´m disso, eles mostram que o uso de FLAIR embeddings na gerac¸a˜o dos vetores de
palavras,quesera˜oentreguescomoinputparaumaredeneural,podeproverumamelhora
substancial nos scores do modelo a ser treinado. Os resultados, tambe´m, reafirmam a
```

**Chunk IDs:** `art-001-b0023-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0023-c001`

### q-001-t19

**Pergunta:** Qual sistema operacional foi usado nos experimentos?

**Expected answer:** Ubuntu 18.04

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-t19-e1 — página 7; seção 5.3. Recursos de Hardware e Software:**

```text
Os experimentos foram realizados em um computador com processador Ryzen 5 2600x,
16GB ram DDR4. O sistema operacional utilizado foi o Ubuntu 18.04. As bibliotecas
utilizadas foram, Tensorflow versa˜o 1.15.0, Keras versa˜o 2.3.1, Numpy versa˜o 1.18.3,
```

**Chunk IDs:** `art-001-b0020-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-001-b0020-c000`

### q-001-t20

**Pergunta:** Qual foi uma das duas contribuições declaradas do artigo além da avaliação das arquiteturas?

**Expected answer:** A produção de uma nova base de petições iniciais anotada manualmente

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `AMBIGUOUS_EVIDENCE`.

**Observações:** O início da contribuição (produção de nova base de petições) foi interpretado pelo chunker como section, enquanto text conserva apenas primeira base deste tipo anotada manualmente. Indexação/reranking/geração usam text e não section. Não há suporte integral no conteúdo de um chunk; quote/página verificáveis na fonte, sem qrel. Não foi alterado o corpus congelado.

**Evidência q-001-t20-e1 — página 3; seção 1. Introdução / contribuições:**

```text
2. a produc¸a˜o de uma nova base de dados, baseada em petic¸o˜es iniciais, sendo a
primeira base de dados deste tipo de documento jur´ıdico anotada manualmente
ate´ opresentemomento;
```

**Chunk IDs:** Nenhum: suporte no corpus congelado não resolvido..
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** Nenhum.

### q-001-m01

**Pergunta:** Considerando a descrição da BiLSTM-CRF e a Figura 1, qual é o papel da camada CRF após o processamento da BiLSTM?

**Expected answer:** Rotular as sequências de palavras, capturando dependências entre rótulos a partir das saídas da BiLSTM

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A prosa explicita integralmente a função pedida; não se inferiu a estrutura visual da Figura 1. A pergunta demanda uma única informação apesar do tipo multi_evidence pré-anotado; um único grupo é semanticamente correto.

**Evidência q-001-m01-e1 — página 4; seção 4.1. BiLSTM-CRF:**

```text
Essaarquiteturacombinaumaredeneuralbidirectionallong-shorttermmemorycomum
modelobaseadoemprobabilidade,oconditionalrandomfields[Lampleetal. 2016]. Ela
foi usada em [LuzdeAraujoetal. 2018] para avaliar o desempenho do dataset proposto
e, tambe´m, e´ arquitetura padra˜o empregada pelo FLAIR. A proposta dele e´ utilizar um
algoritmo que leve em conta uma quantidade virtualmente infinita de contexto e passar
seus resultados para uma camada CRF, que por sua vez, se encarregara´ do rotulac¸a˜o das
sequeˆnciasdepalavras,capturandoasdependeˆnciasaolongodosro´tulos.
```

**Chunk IDs:** `art-001-b0011-c000`.
**Grupo:** `q-001-m01-g1`

**Qrels propostos (relevance = 1):** `art-001-b0011-c000`

**Grupos obrigatórios:**

- `q-001-m01-g1`: Função da CRF: rotular sequências e capturar dependências entre rótulos após o processamento contextual. Alternativas OR: `art-001-b0011-c000`.

### q-001-m02

**Pergunta:** Comparando a Tabela 1 com a explicação da Seção 5.1, qual base possui mais trechos e qual possui menos classes?

**Expected answer:** LeNER-Br possui mais trechos (10.392); a base proposta possui menos classes (2)

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Tabela extraída perdeu alinhamento da coluna Proposto; os valores e a comparação são recuperáveis na prosa contígua. Não se usou o chunk isolado da coluna sem cabeçalhos.

**Evidência q-001-m02-e1 — página 6; seção 5.1. Base de Dados / Tabela 1:**

```text
Abasededadosfoiextra´ıdade74petic¸o˜esiniciaisdeprocessosquetramitaramnajustic¸a
brasileira, de acesso acesso privado, fazendo um total de 1676 trechos extra´ıdos. As
pa´ginasdaspetic¸o˜esiniciaisforamsubmetidasa` umprocessodeOCR(opticalcharacter
recognition) para extrac¸a˜o do conteu´do textual que viria ser utilizado na composic¸a˜o do
conjunto de treinamento empregado neste trabalho. Em contraste, a base de dados do
LeNER-BR conta com um nu´mero um pouco menor de documentos, pore´m maior em
relac¸a˜o a` sentenc¸as anotadas. Ademais, a base de dados de [LuzdeAraujoetal. 2018] e´
menos espec´ıfico quanto ao tipo de texto jur´ıdico que o compo˜e, sendo o apresentando
nestetrabalhocompostoapenasporpetic¸o˜esiniciais.
Tabela1. Caracter´ısticasdabasededados.
Propriedade LeNER-BR
Documentos 70
Classes 6
Trechos 10.392
```

**Chunk IDs:** `art-001-b0015-c000`.
**Grupo:** `q-001-m02-g1`

**Evidência q-001-m02-e2 — página 6; seção 5.1. Base de Dados:**

```text
A Tabela 1 apresenta outras informac¸o˜es sobre a base de dados. A base de dados
proposta suporta dois tipo de classes: Legislac¸a˜o e Jurisprudeˆncia. Em contraste com o
LeNER-BR,quepossuimaisclasses,nestapesquisaoptou-sepordarfocoa`sduasclasses,
entre as seis do LeNER-BR, que sa˜o mais relevantes para petic¸o˜es iniciais. Percebe-se,
```

**Chunk IDs:** `art-001-b0015-c000`.
**Grupo:** `q-001-m02-g2`

**Qrels propostos (relevance = 1):** `art-001-b0015-c000`

**Grupos obrigatórios:**

- `q-001-m02-g1`: Comparação de trechos: proposta 1.676, LeNER-BR 10.392. Alternativas OR: `art-001-b0015-c000`.
- `q-001-m02-g2`: A base proposta usa duas classes, menos que LeNER-BR. Alternativas OR: `art-001-b0015-c000`.

### q-001-m03

**Pergunta:** Como a distribuição mostrada na Tabela 2 sustenta a escolha do F1 score explicada na Seção 5.2?

**Expected answer:** Há muito mais ocorrências de jurisprudência que de legislação nos conjuntos de treino e teste, caracterizando desbalanceamento; por isso o F1 é usado para equilibrar precisão e recall

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-001-m03-e1 — página 6; seção 5.1. Base de Dados / Tabela 2:**

```text
Tabela2. Distribuic¸a˜odasentidadesnosconjuntosdetreinoeteste
Conjunto Jurisprudeˆncia Legislac¸a˜o
Treino 9011 1341
Teste 3398 427
```

**Chunk IDs:** `art-001-b0016-c000`.
**Grupo:** `q-001-m03-g1`

**Evidência q-001-m03-e2 — página 7; seção 5.2. Medidas de Avaliação:**

```text
positivos sa˜o de fato positivos. O F score, por fim, mostra uma relac¸a˜o harmoˆnica entre
1
precisa˜o e recall para que possa-se reconhecer qual modelo possui o melhor balancea-
mentoentreessasduasme´tricas.
```

**Chunk IDs:** `art-001-b0019-c000`.
**Grupo:** `q-001-m03-g2`

**Qrels propostos (relevance = 1):** `art-001-b0016-c000`, `art-001-b0019-c000`

**Grupos obrigatórios:**

- `q-001-m03-g1`: Contagens por classe/partição comprovam predominância de jurisprudência. Alternativas OR: `art-001-b0016-c000`.
- `q-001-m03-g2`: F1 sintetiza harmonicamente precisão e recall. Alternativas OR: `art-001-b0019-c000`.

### q-001-m04

**Pergunta:** Com base na Tabela 3 e na discussão dos resultados, qual modelo deve ser escolhido se o objetivo for o melhor equilíbrio entre precisão e recall para jurisprudência?

**Expected answer:** FLAIR BiLSTM-CRF, pois apresenta F1 de 0,63 e também o maior recall para jurisprudência entre os modelos listados

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** O rótulo FLAIR é section do primeiro chunk. A comparação requer dois grupos: resultado FLAIR e resultados concorrentes; não são evidências independentes criadas por sobreposição.

**Evidência q-001-m04-e1 — página 8; seção 6. Resultados / Tabela 3:**

```text
Jurisprudeˆncia 0.78 0.53 0.63
Pode-se observar que, de acordo com os resultados apresentados na Tabela 3 o
modelo BiLSTM-CRF com FLAIR embeddings treinado com aux´ılio da biblioteca para
PLN FLAIR apresentou resultados superiores com relac¸a˜o a` precisa˜o e F score em am-
1
bas as categorias de entidades anotadas na base de dados analisada. Entretanto, o melhor
score para recall na˜o foi alcanc¸ado por ele, mas sim pelo modelo BiLSTM-CRF usado
por [LuzdeAraujoetal. 2018] em seus pro´prios experimentos. Contudo, vale ressaltar
que a diferenc¸a entre as pontuac¸o˜es adquiridas pelo modelo do FLAIR e do TensorFlow
na˜o foram ta˜o distantes uma da outra, o que, como pode ser visto pelo seu F score,
1
torna o modelo BiLSTM-CRF com FLAIR embeddings o modelo com melhor equil´ıbrio
entre precisa˜o e recall. O modelo CNN com conexo˜es residuais, por sua vez, mostrou-
```

**Chunk IDs:** `art-001-b0023-c000`.
**Grupo:** `q-001-m04-g1`

**Evidência q-001-m04-e2 — página 8; seção 6. Resultados / Tabela 3:**

```text
Tabela3. Acura´cia,precisa˜o,recalleF scoredosmodelosparacadaentidade.
1
Biblioteca/
Framework Modelo Entidade Precisa˜o Recall F score
1
Legislac¸a˜o 0.79 0.44 0.56
Spacy CNN
Jurisprudeˆncia 0.78 0.11 0.20
Legislac¸a˜o 0.91 0.87 0.89
TensorFlow BiLSTM-CRF
Jurisprudeˆncia 0.74 0.44 0.55
```

**Chunk IDs:** `art-001-b0022-c000`.
**Grupo:** `q-001-m04-g2`

**Qrels propostos (relevance = 1):** `art-001-b0022-c000`, `art-001-b0023-c000`

**Grupos obrigatórios:**

- `q-001-m04-g1`: FLAIR: jurisprudência F1 0,63 e recall 0,53; prosa explica equilíbrio. Alternativas OR: `art-001-b0023-c000`.
- `q-001-m04-g2`: Concorrentes em jurisprudência: TensorFlow F1 0,55/recall 0,44 e spaCy F1 0,20/recall 0,11. Alternativas OR: `art-001-b0022-c000`.

### q-001-m05

**Pergunta:** Usando a Tabela 3 e a conclusão, qual diferença de desempenho explica a afirmação de que o spaCy foi inferior ao FLAIR para legislação?

**Expected answer:** O spaCy tem F1 de 0,56 e recall de 0,44, enquanto o FLAIR tem F1 de 0,89 e recall de 0,85 para legislação

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `AMBIGUOUS_EVIDENCE`.

**Observações:** Fonte Markdown sustenta a resposta, mas o chunker separou a linha numérica da legislação FLAIR (fim de b0022) do rótulo FLAIR (section de b0023). Nenhum chunk isolado preserva a associação inequívoca modelo/linha; grupo FLAIR fica sem chunk. Corpus congelado preservado. Não tratar mera proximidade como qrel suficiente.

**Evidência q-001-m05-e1 — página 8; seção 6. Resultados / Tabela 3:**

```text
Tabela3. Acura´cia,precisa˜o,recalleF scoredosmodelosparacadaentidade.
1
Biblioteca/
Framework Modelo Entidade Precisa˜o Recall F score
1
Legislac¸a˜o 0.79 0.44 0.56
Spacy CNN
Jurisprudeˆncia 0.78 0.11 0.20
```

**Chunk IDs:** `art-001-b0022-c000`.
**Grupo:** `q-001-m05-g1`

**Evidência q-001-m05-e2 — página 8; seção 6. Resultados / Tabela 3:**

```text
Legislac¸a˜o 0.93 0.85 0.89
FLAIR BiLSTM-CRF
```

**Chunk IDs:** Nenhum: suporte no corpus congelado não resolvido..
**Grupo:** `q-001-m05-g2`

**Evidência q-001-m05-e3 — página 9; seção 7. Conclusão:**

```text
Por outro lado, o modelo com pior performance foi o CNN com conexo˜es resi-
duais, treinado no Spacy, que, quando comparado ao modelo de melhor desempenho,
mostrou-se ser inferior em todos os aspectos considerados. De certa forma este resul-
```

**Chunk IDs:** `art-001-b0025-c000`.
**Grupo:** `q-001-m05-g3`

**Qrels propostos (relevance = 1):** `art-001-b0022-c000`, `art-001-b0025-c000`

**Grupos obrigatórios:**

- `q-001-m05-g1`: spaCy em legislação: recall 0,44 e F1 0,56. Alternativas OR: `art-001-b0022-c000`.
- `q-001-m05-g2`: FLAIR em legislação: recall 0,85 e F1 0,89, associado inequivocamente ao modelo. Alternativas OR: **SEM CHUNK — pendente**.
- `q-001-m05-g3`: Conclusão identifica CNN/spaCy como modelo de pior desempenho. Alternativas OR: `art-001-b0025-c000`.


## Artigo art-002

### q-002-t01

**Pergunta:** Qual desfecho clínico a abordagem proposta busca prever?

**Expected answer:** Mortalidade hospitalar de pacientes internados em UTIs

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t01-e1 — página 12; seção 5. Considerações Finais:**

```text
Este trabalho teve como contribuição central à concepção de uma abordagem explorando
Aprendizado de Máquina para predição da mortalidade hospitalar utilizando dados cole-
tados durante as primeiras 48 horas de internação nas UTIs. O MIMIC-III foi utilizado
comobancodedadosdeinformaçõesclínicascoletadasdomundoreal.
```

**Chunk IDs:** `art-002-b0037-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0037-c000`

### q-002-t02

**Pergunta:** Qual banco de dados foi usado para formar a coorte do estudo?

**Expected answer:** MIMIC-III

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t02-e1 — página 5; seção 3.2. Banco de Dados e População Estudada:**

```text
A coorte de pacientes relevantes para o desenvolvimento do modelo foi extraída do Me-
dical Information Mart for Intensive Care (MIMIC-III) baseado no código fornecido por
[Harutyunyanetal. 2019]. O MIMIC-III [Johnsonandatal. 2016] é um repositório de
acesso público criado a partir de dados clínicos de pacientes do Beth Israel Deaconess
MedicalCenter (BIDMC),queéumhospitaluniversitáriodaHarvardMedicalSchool.
```

**Chunk IDs:** `art-002-b0018-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0018-c000`

### q-002-t03

**Pergunta:** Quantos pacientes compõem a coorte inicial utilizada no desenvolvimento do modelo?

**Expected answer:** 17.734 pacientes

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t03-e1 — página 5; seção 3.2. Banco de Dados e População Estudada:**

```text
Para o desenvolvimento do modelo foram incluídos apenas registros de pacientes
com 18 anos ou mais e que permaneceram internados em UTIs por um período mínimo
de 48 horas. Isso resultou em uma coorte de 17.734 pacientes e 1.456.610 observações.
Desses pacientes, 15.328 sobreviveram e 2.406 morreram, resultando em uma taxa de
mortalidadede13,57%.
```

**Chunk IDs:** `art-002-b0018-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0018-c000`

### q-002-t04

**Pergunta:** Quantas variáveis preditoras de entrada foram consideradas?

**Expected answer:** 12 variáveis

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t04-e1 — página 11; seção 4. Análise de Performance:**

```text
O modelo é baseado em 12 variáveis preditoras de entrada, sendo 7 sinais vitais (DBP,
SBP,MAP,BT,RR,HR,SpO2),2dadosdemográficos(sexoeidade),2resultadosdela-
boratório(glicoseepH)eumsistemadepontuação(GCS).Estessinaisvitaisusualmente
```

**Chunk IDs:** `art-002-b0036-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0036-c000`

### q-002-t05

**Pergunta:** Quais janelas após a admissão na UTI foram comparadas?

**Expected answer:** 24 e 48 horas

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t05-e1 — página 5; seção 3.1. Discussão do Problema de Pesquisa:**

```text
Oobjetivodomodelodesenvolvidoporestetrabalhoéidentificaroriscodemorte
duranteainternaçãodepacientesemUTIsconsiderandocomobaseosdadosdoMIMIC-
III. Foram comparadas as performances de vários métodos de Aprendizado de Máquina,
utilizando para isso dados de uma mesma coorte de pacientes coletados em janelas de
tempo de 24 e 48 horas após a admissão nas UTIs. As janelas de tempo foram estabe-
lecidas através de uma avaliação empírica inicial, que mostrou que com esses intervalos
de tempo já é possível uma estimativa de risco de mortalidade suficientemente precisa.
```

**Chunk IDs:** `art-002-b0017-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0017-c000`

### q-002-t06

**Pergunta:** Quais critérios de inclusão foram aplicados aos pacientes da coorte?

**Expected answer:** Ter 18 anos ou mais e permanência mínima de 48 horas na UTI

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t06-e1 — página 5; seção 3.2. Banco de Dados e População Estudada:**

```text
Para o desenvolvimento do modelo foram incluídos apenas registros de pacientes
com 18 anos ou mais e que permaneceram internados em UTIs por um período mínimo
de 48 horas. Isso resultou em uma coorte de 17.734 pacientes e 1.456.610 observações.
```

**Chunk IDs:** `art-002-b0018-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0018-c000`

### q-002-t07

**Pergunta:** Qual foi a taxa de mortalidade da coorte inicial?

**Expected answer:** 13,57%

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t07-e1 — página 5; seção 3.2. Banco de Dados e População Estudada:**

```text
de 48 horas. Isso resultou em uma coorte de 17.734 pacientes e 1.456.610 observações.
Desses pacientes, 15.328 sobreviveram e 2.406 morreram, resultando em uma taxa de
mortalidadede13,57%.
```

**Chunk IDs:** `art-002-b0018-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0018-c000`

### q-002-t08

**Pergunta:** Por que os autores não imputaram valores ausentes?

**Expected answer:** Para evitar a geração de viés no modelo

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t08-e1 — página 9; seção 3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes:**

```text
Como estratégia para evitar a geração de viés no modelo, os dados ausentes não
foram substituídos por valores estimados. A abordagem utilizada foi incluir apenas
pacientes com um alto percentual de informações completas, sendo então selecionados
pacientes onde todas as variáveis foram registradas pelo menos uma vez em três horários
diferentes dentro da janela de tempo de medição. Esta imposição resultou em um con-
```

**Chunk IDs:** `art-002-b0029-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0029-c000`

### q-002-t09

**Pergunta:** Como as séries temporais foram agregadas para obter representação mais densa?

**Expected answer:** Em intervalos de uma hora, calculando a mediana

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t09-e1 — página 9; seção 3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes:**

```text
Os modelos de Aprendizado de Máquina aplicados a séries temporais têm uma
performancedeclassificaçãomelhorquandorecebemcomoentradadadoscomrepresen-
tações de tempo discretizadas [Facelietal. 2021]. Dessa forma, com o objetivo de obter
umarepresentaçãomaisdensadosdadosfisiológicosdeformaaoportunizarumamelhor
inferência pelos algoritmos, as observações de cada série temporal foram agregadas em
intervalosdehoraemhoraatravésdocálculodamediana.
```

**Chunk IDs:** `art-002-b0029-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0029-c000`

### q-002-t10

**Pergunta:** Quais estatísticas resumidas foram calculadas para cada variável na construção de recursos?

**Expected answer:** Mínimo, máximo, desvio padrão, variância, média e mediana

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t10-e1 — página 9; seção 3.5. Construção de Recursos:**

```text
A construção de recursos aborda o problema de encontrar a transformação de variáveis
quepossuamamaiorquantidadedeinformaçõesúteis. Comoassériestemporaispresen-
tesnobancodedadosutilizadonessetrabalhocontémumgrandenúmerodeinformações
ausentes,omodelopropostocalculaosdadosestatísticosresumidos(valormínimo,valor
máximo, desvio padrão, variância, média e mediana) de cada uma das variáveis dentro
da janela de tempo estipulada (24 ou 48 horas). Esta estratégia reduz a complexidade do
modelo,poisutilizainformaçõesmaisrelevantescomoentradaparaatarefadeprevisão.
```

**Chunk IDs:** `art-002-b0030-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0030-c000`

### q-002-t11

**Pergunta:** Qual estratégia de balanceamento de classes foi escolhida para o modelo?

**Expected answer:** Random oversampling da classe minoritária

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t11-e1 — página 9; seção 3.6. Balanceamento das Classes:**

```text
Nestetrabalhoforamexperimentadastrêsdiferentesestratégiasdebalanceamento
entre as classes: (i) random oversampling: sobreamostragem aleatória da classe minori-
tária (método escolhido); (ii) random downsampling: seleciona e remove aleatoriamente
amostras da classe majoritária; e, (iii) SMOTE (Synthetic Minority Oversampling Techni-
que): geraçãodeexemplossintéticosdetreinamentodaclasseminoritária.
```

**Chunk IDs:** `art-002-b0031-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0031-c000`

### q-002-t12

**Pergunta:** Qual método de normalização foi utilizado?

**Expected answer:** Min-max, transformando valores para a escala de zero a um

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t12-e1 — página 10; seção 3.7. Normalização:**

```text
Muitos métodos de Aprendizado de Máquina exigem que as variáveis selecionadas este-
jamnamesmaescalaparaumdesempenhoideal[Facelietal. 2021]. Ométodochamado
“min-max”foiescolhido,atravésdoqualosvaloresforamtransformadosparaumaescala
mínimo-zeroemáximo-um.
```

**Chunk IDs:** `art-002-b0032-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0032-c000`

### q-002-t13

**Pergunta:** O que a sensibilidade mede na avaliação dos classificadores?

**Expected answer:** A capacidade de prever corretamente os pacientes que morreram, a classe positiva

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t13-e1 — página 10; seção 4. Análise de Performance:**

```text
Asensibilidade,tambémchamadadeTaxadeVerdadeirosPositivos(TPR),indica
a capacidade do método de classificação em prever corretamente os pacientes que mor-
reram (classe positiva). A especificidade indica a capacidade do método de classificação
```

**Chunk IDs:** `art-002-b0033-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0033-c000`

### q-002-t14

**Pergunta:** O que a especificidade mede na avaliação dos classificadores?

**Expected answer:** A capacidade de prever corretamente os pacientes que sobreviveram, a classe negativa

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t14-e1 — página 10; seção 4. Análise de Performance:**

```text
reram (classe positiva). A especificidade indica a capacidade do método de classificação
em prever corretamente os pacientes que sobreviveram (classe negativa). F1 score é uma
média harmônica calculada com base na precisão e na sensibilidade [Facelietal. 2021].
```

**Chunk IDs:** `art-002-b0033-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0033-c000`

### q-002-t15

**Pergunta:** Por que a AUC foi escolhida para a comparação com trabalhos relacionados?

**Expected answer:** Porque a literatura a aponta como métrica relevante para medir desempenho na predição de mortalidade hospitalar

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t15-e1 — página 11; seção 4. Análise de Performance:**

```text
A comparação do desempenho da abordagem proposta com outros trabalhos da
literatura será feita tendo como base a Tabela 1. A métrica AUC foi empregada para essa
comparação por ser apontada pela literatura como a mais relevante para medição de de-
sempenho quando da predição de mortalidade hospitalar [Muralitharanandatal. 2021].
Como referência será utilizado o resultado obtido pelo método GBC, desenvolvido pelo
presentetrabalho,oqualalcançouamelhorperformancedeclassificação(AUCde0,85).
```

**Chunk IDs:** `art-002-b0036-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0036-c000`

### q-002-t16

**Pergunta:** Qual método obteve a melhor performance na janela de 24 horas?

**Expected answer:** MLP

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t16-e1 — página 10; seção 4. Análise de Performance:**

```text
Na janela de tempo de 24 horas, o método MLP teve melhor performance con-
siderando simultaneamente os indicadores F1 score e AUC, com valores de 0,51 e 0,83,
respectivamente. O algoritmo GBC teve performance similar, mas com o valor de F1
score um pouco inferior. Considerando a Figura 2(a), que apresenta as curvas ROC dos
```

**Chunk IDs:** `art-002-b0034-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0034-c000`

### q-002-t17

**Pergunta:** Qual método obteve a melhor performance na janela de 48 horas?

**Expected answer:** Gradient Boosting Classifier (GBC)

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t17-e1 — página 10; seção 4. Análise de Performance:**

```text
Já na janela de tempo de 48 horas, o método GBC teve uma performance ligei-
ramente superior em ambos indicadores F1 score e AUC, com valores de 0,53 e 0,85,
respectivamente. As curvas ROC dos modelos nesta janela de tempo estão apresentadas
```

**Chunk IDs:** `art-002-b0034-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0034-c000`

### q-002-t18

**Pergunta:** Quais sinais vitais fazem parte das 12 variáveis usadas pela abordagem proposta?

**Expected answer:** DBP, SBP, MAP, temperatura corporal, frequência respiratória, frequência cardíaca e SpO2

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t18-e1 — página 11; seção 4. Análise de Performance:**

```text
O modelo é baseado em 12 variáveis preditoras de entrada, sendo 7 sinais vitais (DBP,
SBP,MAP,BT,RR,HR,SpO2),2dadosdemográficos(sexoeidade),2resultadosdela-
boratório(glicoseepH)eumsistemadepontuação(GCS).Estessinaisvitaisusualmente
sãoregistradosautomaticamentepormonitoresmultiparamétricosemambientesdeUTIs,
simplificandoassimacoletadestesdadosfisiológicos.
```

**Chunk IDs:** `art-002-b0036-c000`.
**Grupo:** Não aplicável.

**Evidência q-002-t18-e2 — página 6; seção Tabela 1 / descrição de siglas:**

```text
Descriçãodasvariáveis:HR-frequênciacardíaca;SBP-pressãoarterialsistólica;DBP-pressãoarterialdiastólica;MAP-pressão
arterialmédia;RR-frequênciarespiratória;SpO2-saturaçãoperiféricadeoxigênio;BT-temperaturacorporal;GCS-escalade
comadeGlasgow;FiO2-fraçãoinspiradadeoxigênio;PaO2-pressãoarterialdeoxigênio;WBC-contagemdecélulasbrancas;
AIDS-SíndromedaImunodeficiênciaHumana;pH-potencialhidrogeniônico.
```

**Chunk IDs:** `art-002-b0021-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0021-c000`, `art-002-b0036-c000`

### q-002-t19

**Pergunta:** Quantas observações extremas foram removidas pelas regras de limpeza?

**Expected answer:** 7.471 observações, equivalentes a 0,51%

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t19-e1 — página 8; seção 3.4.1. Limpeza de Dados:**

```text
No modelo proposto, cada variável numérica está associada a limites superior e
inferior para detectar valores inutilizáveis (outliers). O valor observado será excluído se
estiver fora desses limites. Ao aplicar essas regras para gerar a coorte do modelo foram
removidas7.471observações(0,51%)classificadascomovaloresatípicosextremos.
```

**Chunk IDs:** `art-002-b0026-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0026-c000`

### q-002-t20

**Pergunta:** Qual perspectiva de continuidade é apontada ao final do artigo?

**Expected answer:** Otimizar a performance preditiva para possibilitar uso em ambiente clínico real como apoio à decisão

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-002-t20-e1 — página 12; seção 5. Considerações Finais:**

```text
Como perspectiva de continuidade da pesquisa, a expectativa é que esta aborda-
gemtenhasuaperformancepreditivaotimizada,naexpectativaquesejapossívelempregar
a mesma em um ambiente clínico real, como apoio à tomada de decisões considerando a
celeridadeinerenteaosambientesdecuidadointensivos.
```

**Chunk IDs:** `art-002-b0037-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-002-b0037-c000`

### q-002-m01

**Pergunta:** Usando a Tabela 2 e a explicação sobre dados ausentes, quais três variáveis apresentam as menores incidências e quais são seus percentuais?

**Expected answer:** pH (8%), GCS (11%) e glicose (17%)

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A Tabela 2 extraída tem colunas colapsadas; a prosa transcreve inequivocamente as três variáveis e incidências. Um grupo corresponde à única comparação pedida, não a três grupos artificiais por número.

**Evidência q-002-m01-e1 — página 9; seção 3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes:**

```text
esparsas. A Tabela 2 apresenta a quantidade de observações com dados não nulos por
variável. Conforme pode-se observar, existem poucas medições das variáveis Potencial
Hidrogeniônico, Escala de Coma de Glasgow e Glicose, com incidências em 8%, 11% e
17%dasobservações,respectivamente.
```

**Chunk IDs:** `art-002-b0029-c000`.
**Grupo:** `q-002-m01-g1`

**Qrels propostos (relevance = 1):** `art-002-b0029-c000`

**Grupos obrigatórios:**

- `q-002-m01-g1`: Variáveis de menor incidência: pH 8%, GCS 11%, glicose 17%. Alternativas OR: `art-002-b0029-c000`.

### q-002-m02

**Pergunta:** Com base na Tabela 3 e na discussão da Seção 4, qual método lidera em F1 e AUC após 48 horas e quais são os valores?

**Expected answer:** GBC, com F1 de 0,53 e AUC de 0,85

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Tabela 3 perdeu rótulos/valores de 48h na extração; discussão textual preserva integralmente método, janela e métricas. Não se atribui relevância ao chunk da tabela mutilada.

**Evidência q-002-m02-e1 — página 10; seção 4. Análise de Performance:**

```text
Já na janela de tempo de 48 horas, o método GBC teve uma performance ligei-
ramente superior em ambos indicadores F1 score e AUC, com valores de 0,53 e 0,85,
respectivamente. As curvas ROC dos modelos nesta janela de tempo estão apresentadas
```

**Chunk IDs:** `art-002-b0034-c000`.
**Grupo:** `q-002-m02-g1`

**Qrels propostos (relevance = 1):** `art-002-b0034-c000`

**Grupos obrigatórios:**

- `q-002-m02-g1`: GBC lidera em 48 horas com F1 0,53 e AUC 0,85. Alternativas OR: `art-002-b0034-c000`.

### q-002-m03

**Pergunta:** Relacione a Figura 2 à Tabela 3: por que modelos com AUC semelhante ainda podem levar a escolhas diferentes de classificador?

**Expected answer:** Porque as curvas ROC mostram comportamentos distintos conforme o limiar de decisão; a escolha depende do equilíbrio desejado entre especificidade e sensibilidade

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A discussão da Figura 2(a) explica explicitamente o fenômeno pedido; não se afirma um limiar numérico ou curva que dependa de leitura visual.

**Evidência q-002-m03-e1 — página 10; seção 4. Análise de Performance:**

```text
score um pouco inferior. Considerando a Figura 2(a), que apresenta as curvas ROC dos
modelos de 24 horas, pode-se observar que apesar dos métodos MLP, LR, RF, GBC e
Adaboost apresentarem valores semelhantes em relação a métrica AUC, eles se compor-
tam de maneira diferente dependendo do limiar de decisão a ser escolhido. Portanto a
escolhadoclassificadormaisadequadodependerádopontodeequilíbriodesejadoparaa
especificidadeesensibilidade.
```

**Chunk IDs:** `art-002-b0034-c000`.
**Grupo:** `q-002-m03-g1`

**Evidência q-002-m03-e2 — página 10; seção 4. Análise de Performance:**

```text
A AUC é uma grandeza escalar entre 0 e 1 que representa a área abaixo da curva ROC e
mede a qualidade das previsões do modelo independentemente do ponto de operação do
classificador[Bradley1997].
```

**Chunk IDs:** `art-002-b0033-c000`.
**Grupo:** `q-002-m03-g2`

**Qrels propostos (relevance = 1):** `art-002-b0033-c000`, `art-002-b0034-c000`

**Grupos obrigatórios:**

- `q-002-m03-g1`: AUCs semelhantes podem acompanhar diferentes sensibilidades/especificidades conforme limiar. Alternativas OR: `art-002-b0034-c000`.
- `q-002-m03-g2`: AUC resume a área da ROC independentemente do ponto de operação. Alternativas OR: `art-002-b0033-c000`.

### q-002-m04

**Pergunta:** Comparando a linha da abordagem proposta na Tabela 1 com a descrição da Seção 4, quais recursos tornam o GBC mais simples de implementar do que alguns trabalhos com AUC maior?

**Expected answer:** Usa 12 variáveis, com sete sinais vitais geralmente registrados automaticamente, dois dados demográficos, dois exames e GCS total; trabalhos com AUC maior usam 17 variáveis, mais exames ou componentes individuais de GCS

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A discussão explicita os valores da comparação da Tabela 1, mantendo os cabeçalhos semânticos que faltam em partes da tabela extraída.

**Evidência q-002-m04-e1 — página 11; seção 4. Análise de Performance:**

```text
O modelo é baseado em 12 variáveis preditoras de entrada, sendo 7 sinais vitais (DBP,
SBP,MAP,BT,RR,HR,SpO2),2dadosdemográficos(sexoeidade),2resultadosdela-
boratório(glicoseepH)eumsistemadepontuação(GCS).Estessinaisvitaisusualmente
sãoregistradosautomaticamentepormonitoresmultiparamétricosemambientesdeUTIs,
simplificandoassimacoletadestesdadosfisiológicos.
```

**Chunk IDs:** `art-002-b0036-c000`.
**Grupo:** `q-002-m04-g1`

**Evidência q-002-m04-e2 — página 11; seção 4. Análise de Performance:**

```text
A performance AUC de 0,85 alcançada é superior ao trabalho de
[Alghatanietal. 2021], que obteve AUC de 0,78. Por sua vez, os trabalhos
[Purushothamandatal. 2018] (AUC de 0,87), [Pirracchioandatal. 2015] (AUC
de 0,88) e [Harutyunyanetal. 2019] (AUC de 0,87) apresentam melhor performance,
entretanto exigem ao total 17 variáveis preditoras, dependem de até 6 exames laborato-
riais ou requerem os valores individuais dos 4 critérios da escala de Glasgow, da qual
muitas vezes é registrado somente o valor total. Estes aspectos podem dificultar sua
```

**Chunk IDs:** `art-002-b0036-c000`.
**Grupo:** `q-002-m04-g2`

**Qrels propostos (relevance = 1):** `art-002-b0036-c000`

**Grupos obrigatórios:**

- `q-002-m04-g1`: Proposta usa 12 variáveis: 7 sinais vitais, 2 dados demográficos, 2 exames e GCS; sinais coletados automaticamente. Alternativas OR: `art-002-b0036-c000`.
- `q-002-m04-g2`: Comparadores com AUC maior requerem 17 variáveis, até 6 exames ou componentes de GCS. Alternativas OR: `art-002-b0036-c000`.

### q-002-m05

**Pergunta:** Considerando a Figura 1 e as Seções 3.4 a 3.7, quais etapas de preparação ocorrem antes da comparação dos classificadores?

**Expected answer:** Limpeza de dados, agregação horária e tratamento de ausentes, construção de recursos, balanceamento de classes e normalização

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Cada etapa necessária tem grupo próprio. A sequência está explicitada nas subseções; não se inventaram setas ou detalhes visuais da Figura 1.

**Evidência q-002-m05-e1 — página 8; seção 3.4.1. Limpeza de Dados:**

```text
Os dados extraídos do MIMIC-III possuem valores errôneos devido a ruídos, registros
incorretos, erros tipográficos e imputação de informações ou unidades inconsistentes
[Purushothamandatal. 2018]. Paratratardessesvaloresdiscrepantespresentesnobanco
de dados foram utilizadas as especificações constantes no repositório de código-fonte de
[Harutyunyanetal. 2019], as quais foram definidas por especialistas clínicos com base
emseuconhecimentodeintervalosdemedidasválidas.
No modelo proposto, cada variável numérica está associada a limites superior e
inferior para detectar valores inutilizáveis (outliers). O valor observado será excluído se
estiver fora desses limites. Ao aplicar essas regras para gerar a coorte do modelo foram
removidas7.471observações(0,51%)classificadascomovaloresatípicosextremos.
```

**Chunk IDs:** `art-002-b0026-c000`.
**Grupo:** `q-002-m05-g1`

**Evidência q-002-m05-e2 — página 9; seção 3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes:**

```text
Os modelos de Aprendizado de Máquina aplicados a séries temporais têm uma
performancedeclassificaçãomelhorquandorecebemcomoentradadadoscomrepresen-
tações de tempo discretizadas [Facelietal. 2021]. Dessa forma, com o objetivo de obter
umarepresentaçãomaisdensadosdadosfisiológicosdeformaaoportunizarumamelhor
inferência pelos algoritmos, as observações de cada série temporal foram agregadas em
intervalosdehoraemhoraatravésdocálculodamediana.
Como estratégia para evitar a geração de viés no modelo, os dados ausentes não
foram substituídos por valores estimados. A abordagem utilizada foi incluir apenas
pacientes com um alto percentual de informações completas, sendo então selecionados
pacientes onde todas as variáveis foram registradas pelo menos uma vez em três horários
diferentes dentro da janela de tempo de medição. Esta imposição resultou em um con-
juntodedadoscom6.184pacientesnajaneladetempode48he4.979pacientesnajanela
de24h.
```

**Chunk IDs:** `art-002-b0029-c000`.
**Grupo:** `q-002-m05-g2`

**Evidência q-002-m05-e3 — página 9; seção 3.5. Construção de Recursos:**

```text
A construção de recursos aborda o problema de encontrar a transformação de variáveis
quepossuamamaiorquantidadedeinformaçõesúteis. Comoassériestemporaispresen-
tesnobancodedadosutilizadonessetrabalhocontémumgrandenúmerodeinformações
ausentes,omodelopropostocalculaosdadosestatísticosresumidos(valormínimo,valor
máximo, desvio padrão, variância, média e mediana) de cada uma das variáveis dentro
da janela de tempo estipulada (24 ou 48 horas). Esta estratégia reduz a complexidade do
modelo,poisutilizainformaçõesmaisrelevantescomoentradaparaatarefadeprevisão.
```

**Chunk IDs:** `art-002-b0030-c000`.
**Grupo:** `q-002-m05-g3`

**Evidência q-002-m05-e4 — página 9; seção 3.6. Balanceamento das Classes:**

```text
Nestetrabalhoforamexperimentadastrêsdiferentesestratégiasdebalanceamento
entre as classes: (i) random oversampling: sobreamostragem aleatória da classe minori-
tária (método escolhido); (ii) random downsampling: seleciona e remove aleatoriamente
amostras da classe majoritária; e, (iii) SMOTE (Synthetic Minority Oversampling Techni-
que): geraçãodeexemplossintéticosdetreinamentodaclasseminoritária.
```

**Chunk IDs:** `art-002-b0031-c000`.
**Grupo:** `q-002-m05-g4`

**Evidência q-002-m05-e5 — página 10; seção 3.7. Normalização:**

```text
Muitos métodos de Aprendizado de Máquina exigem que as variáveis selecionadas este-
jamnamesmaescalaparaumdesempenhoideal[Facelietal. 2021]. Ométodochamado
“min-max”foiescolhido,atravésdoqualosvaloresforamtransformadosparaumaescala
mínimo-zeroemáximo-um.
```

**Chunk IDs:** `art-002-b0032-c000`.
**Grupo:** `q-002-m05-g5`

**Qrels propostos (relevance = 1):** `art-002-b0026-c000`, `art-002-b0029-c000`, `art-002-b0030-c000`, `art-002-b0031-c000`, `art-002-b0032-c000`

**Grupos obrigatórios:**

- `q-002-m05-g1`: Limpeza de valores discrepantes. Alternativas OR: `art-002-b0026-c000`.
- `q-002-m05-g2`: Agregação horária pela mediana e seleção por completude sem imputação. Alternativas OR: `art-002-b0029-c000`.
- `q-002-m05-g3`: Construção de estatísticas resumidas. Alternativas OR: `art-002-b0030-c000`.
- `q-002-m05-g4`: Balanceamento por random oversampling. Alternativas OR: `art-002-b0031-c000`.
- `q-002-m05-g5`: Normalização min-max. Alternativas OR: `art-002-b0032-c000`.


## Artigo art-003

### q-003-t01

**Pergunta:** Qual fungo causa a ferrugem asiática abordada pelo artigo?

**Expected answer:** Phakopsora pachyrhizi

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t01-e1 — página 1; seção Resumo:**

```text
Resumo. A ferrugem asia´tica e´ uma doenc¸a causada pelo fungo Phakopsora
pachyrhizi; tendo a soja como um de seus hospedeiros, e seu aparecimento de-
```

**Chunk IDs:** `art-003-b0000-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0000-c000`

### q-003-t02

**Pergunta:** Qual variável-alvo os modelos procuram prever?

**Expected answer:** A severidade da ferrugem asiática em lavouras de soja

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t02-e1 — página 1; seção Resumo:**

```text
pendente de mu´ltiplas varia´veis do ambiente. Este trabalho propo˜e o uso de
modelos de aprendizado de ma´quina estado-da-arte para prever a severidade
da ferrugem asia´tica em lavouras de soja. Combinamos dados geolo´gicos e
```

**Chunk IDs:** `art-003-b0000-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0000-c000`

### q-003-t03

**Pergunta:** Como a severidade é quantificada no conjunto de dados principal?

**Expected answer:** Como média percentual da área afetada nas folhas remanescentes, com 100% para copas completamente desfolhadas

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t03-e1 — página 3; seção 3.1. Coleta de Dados:**

```text
Noestudo,aseveridadee´ quantificadacomoumame´diapercentualparaolotede
cultivo,levandoemconsiderac¸a˜oaporcentagemdaa´reaafetadapelaferrugemnasfolhas
remanescentesdasplantas,sendoatribu´ıdoovalorde100%emcasosdecopascompleta-
mente desfolhadas [Barroandet. al. 2021]. Adicionalmente, sa˜o fornecidas informac¸o˜es
```

**Chunk IDs:** `art-003-b0006-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0006-c000`

### q-003-t04

**Pergunta:** Qual é a principal fonte dos dados de plantação e fungicidas?

**Expected answer:** Testes cooperativos de fungicidas coordenados pelo Consórcio Antiferrugem

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t04-e1 — página 3; seção 3.1. Coleta de Dados:**

```text
Os dados de plantac¸o˜es utilizados para determinar a severidade da ferrugem asia´tica fo-
ram obtidos de testes cooperativos de fungicidas coordenados pelo Conso´rcio Antiferru-
gem [Barroandet. al. 2021]. Esses dados abrangem 10 estados brasileiros (Bahia [BA],
DistritoFederal[DF],Tocantins[TO],Goia´s[GO],MinasGerais[MG],MatoGrossodo
Sul [MS], Mato Grosso [MT], Sa˜o Paulo [SP], Parana´ [PR], e Rio Grande do Sul [RS]),
comcolheitasdasafrade2014/15ate´ 2019/20.
```

**Chunk IDs:** `art-003-b0006-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0006-c000`

### q-003-t05

**Pergunta:** Em quantos estados brasileiros foram coletados os dados de plantação?

**Expected answer:** Dez estados

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Resposta reproduz a contagem declarada pelo artigo. A enumeração inclui o Distrito Federal entre os dez; editorialmente são nove estados e o DF, não corrigimos silenciosamente o texto-fonte.

**Evidência q-003-t05-e1 — página 3; seção 3.1. Coleta de Dados:**

```text
gem [Barroandet. al. 2021]. Esses dados abrangem 10 estados brasileiros (Bahia [BA],
DistritoFederal[DF],Tocantins[TO],Goia´s[GO],MinasGerais[MG],MatoGrossodo
Sul [MS], Mato Grosso [MT], Sa˜o Paulo [SP], Parana´ [PR], e Rio Grande do Sul [RS]),
comcolheitasdasafrade2014/15ate´ 2019/20.
```

**Chunk IDs:** `art-003-b0006-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0006-c000`

### q-003-t06

**Pergunta:** Quais safras são cobertas pelos dados de plantação?

**Expected answer:** De 2014/15 até 2019/20

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t06-e1 — página 3; seção 3.1. Coleta de Dados:**

```text
gem [Barroandet. al. 2021]. Esses dados abrangem 10 estados brasileiros (Bahia [BA],
DistritoFederal[DF],Tocantins[TO],Goia´s[GO],MinasGerais[MG],MatoGrossodo
Sul [MS], Mato Grosso [MT], Sa˜o Paulo [SP], Parana´ [PR], e Rio Grande do Sul [RS]),
comcolheitasdasafrade2014/15ate´ 2019/20.
```

**Chunk IDs:** `art-003-b0006-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0006-c000`

### q-003-t07

**Pergunta:** Quais meses de dados climáticos foram selecionados e por quê?

**Expected answer:** Novembro e dezembro, por corresponderem ao período de pré-colheita

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t07-e1 — página 3; seção 3.1. Coleta de Dados:**

```text
valores clima´ticos referentes aos meses de novembro e dezembro do ano da safra, uma
vezqueessee´ oper´ıodoreferenteapre´-colheita.
```

**Chunk IDs:** `art-003-b0006-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0006-c001`

### q-003-t08

**Pergunta:** Qual pacote da linguagem R forneceu os dados climáticos usados no enriquecimento?

**Expected answer:** brclimr

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t08-e1 — página 3; seção 3.1. Coleta de Dados:**

```text
Entre os dados utilizados para enriquecimento foram utilizados dados clima´ticos
relacionadosaoper´ıododasafradecadacidade. Osdadosesta˜odispon´ıveisnopacoteda
linguagem R, brclimr [Saldanhaetal. 2023]. Foram utilizados o desvio padra˜o e valores
ma´ximos, m´ınimos e me´dios mensais de precipitac¸a˜o, evapotranspirac¸a˜o, temperatura
m´ınima, temperatura ma´xima, radiac¸a˜o solar, e umidade relativa do ar. Foram usados os
```

**Chunk IDs:** `art-003-b0006-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0006-c000`

### q-003-t09

**Pergunta:** Qual identificador foi utilizado na fusão dos dados do brclimr com a base de severidade?

**Expected answer:** O código de município atribuído pelo IBGE

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t09-e1 — página 4; seção 3.2. Tratamento de Dados:**

```text
dados obtidos do pacote brclimr, foi usado o co´digo dos mu-
nic´ıpios(atribuidospeloIBGE)ondeasplantac¸o˜esocorreram. Foramseparadoosvalores
de desvio padra˜o e valores ma´ximos, m´ınimos e me´dios para cada diferente combinac¸a˜o
demunic´ıpio,meˆseano. Foramselecionadososvaloresreferentesapre´-colheitadecada
safra, nos meses de novembro e dezembro, e os valores foram acrescentados ao conjunto
dedadosdeseveridade.
```

**Chunk IDs:** `art-003-b0007-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0007-c001`

### q-003-t10

**Pergunta:** Que formato de arquivo foi usado pelo IBGE para disponibilizar dados de características climáticas regionais?

**Expected answer:** Arquivos .shp

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t10-e1 — página 4; seção 3.2. Tratamento de Dados:**

```text
Dados referente a`s caracter´ısticas clima´ticas de uma regia˜o foram obtidos nos re-
posito´riosdoIBGE.Essesconjuntossa˜odisponibilizadosemarquivosnoformato“.shp”
que e´ um tipo de arquivo comumente utilizado por sistemas de informac¸o˜es geogra´ficas.
A informac¸a˜o contida dentro desse tipo de arquivo sa˜o descric¸o˜es de como desenhar de-
terminadasregio˜esedepoisquaisasinformac¸o˜esrelacionadasadeterminadaregia˜o.
```

**Chunk IDs:** `art-003-b0007-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0007-c000`

### q-003-t11

**Pergunta:** Quais três modelos baseados em árvores foram utilizados no estudo?

**Expected answer:** Random Forest, XGBoost e CatBoost

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t11-e1 — página 5; seção 3.3. Modelos Utilizados:**

```text
Outros modelos utilizados baseados em A´rvores de Decisa˜o sa˜o o XGBoost e o
CatBoost. A diferenc¸a desses dois para o Random Forest e´ que eles utilizam te´cnicas
mais robustas para a combinac¸a˜o dos resultados dos diferentes Weak Learners, cha-
mada de descida de gradiente. Essa te´cnica usa ca´lculos matema´ticos para reajustar os
paraˆmetros dos Weak Learner para tentar melhorar o valor da previsa˜o. Ale´m disso, as
capacidades de explicabilidade desses dois modelos sa˜o similares aos de Random Fo-
rest[ChenandGuestrin2016][Dorogushetal. 2018]. Comoexemplo,naFigura1e´ mos-
tradaumadasA´rvoresdeDecisa˜ousadasinternamentepelomodelodoCatBoost.
```

**Chunk IDs:** `art-003-b0009-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0009-c000`

### q-003-t12

**Pergunta:** Que característica dos modelos foi priorizada além de encontrar padrões não lineares?

**Expected answer:** Explicabilidade

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t12-e1 — página 4; seção 3.3. Modelos Utilizados:**

```text
Durante esse estudo, foram realizados testes com diferentes modelos com a intenc¸a˜o de
encontrar quais conseguiriam obter os melhores resultados. As caracter´ısticas mais de-
seja´veisdosmodelose´ acapacidadedeencontrarcomportamentosna˜olinearesnosdados
e de serem explica´veis, pois esse tipo de modelo oferece mecanismos para conseguirmos
interpretarseusresultadoseentendermosporquefoifeitadeterminadaprevisa˜o.
```

**Chunk IDs:** `art-003-b0008-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0008-c000`

### q-003-t13

**Pergunta:** Qual técnica de explicabilidade é citada para observar o impacto dos atributos no resultado final?

**Expected answer:** SHAP

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** O nome SHAP é literal. A expansão inglesa usada pelo artigo não foi validada externamente e não é necessária para a resposta.

**Evidência q-003-t13-e1 — página 4; seção 3.3. Modelos Utilizados:**

```text
Ale´m disso, esse modelo tem grandes capacidades de explicabilidade. Com ele
e´ poss´ıvel obter informac¸o˜es como a importaˆncia de cada paraˆmetro e exportar uma
representac¸a˜o visual de cada um dos Weak Learners. Isso possibilita visualizar os ca-
minhos tomados pelo modelo para chegar em uma decisa˜o. Finalmente, pode-se utilizar
uma te´cnica conhecida como SHAP (sampling-based approximation approach) que per-
miteobservaroquantoumatributodosdadosesta´ impactandooresultadofinal.
```

**Chunk IDs:** `art-003-b0008-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0008-c000`

### q-003-t14

**Pergunta:** Qual tipo de modelo, além dos modelos de árvores, também foi testado?

**Expected answer:** Rede neural

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t14-e1 — página 5; seção 3.3. Modelos Utilizados:**

```text
OutromodeloutilizadonesteestudofoiaRedeNeuralpoistambe´mapresentaboa
capacidadedeencontrarpadro˜esna˜olinearesemdados,entretantoseufuncionamentona˜o
e´ baseadoemA´rvoresdedecisa˜ocomoosanteriores. Asredesneuraisforamcriadaspen-
```

**Chunk IDs:** `art-003-b0009-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0009-c000`

### q-003-t15

**Pergunta:** Quais etapas de pré-processamento foram aplicadas antes do treinamento?

**Expected answer:** Limpeza de duplicatas, normalização de colunas, eliminação de valores faltantes e combinação das fontes de dados

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t15-e1 — página 5; seção 3.4. Passo a passo do treinamento:**

```text
No nosso pipeline de treinamento de modelos, adotamos um processo de pre´-
processamento de dados, incluindo a limpeza de duplicatas, a normalizac¸a˜o de colunas
e a eliminac¸a˜o de valores faltantes, com o objetivo de garantir a qualidade dos dados uti-
lizados no treinamento. Ale´m disso, o processo de pre´-processamento e´ responsa´vel pela
combinac¸a˜o das diferentes fontes de dados para enriquecer e ampliar a diversidade das
informac¸o˜es utilizadas no treinamento do modelo. Para otimizac¸a˜o de hiperparaˆmetros,
```

**Chunk IDs:** `art-003-b0010-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0010-c000`

### q-003-t16

**Pergunta:** Qual método de otimização de hiperparâmetros foi utilizado?

**Expected answer:** Grid search

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t16-e1 — página 6; seção 3.4. Passo a passo do treinamento:**

```text
utilizamos o me´todo de grid search, que nos permitiu explorar diversas combinac¸o˜es de
hiperparaˆmetros e selecionar aquela que resultou no melhor desempenho. Vale ressaltar
que a me´trica que utilizamos foi o Erro Quadra´tico Me´dio (RMSE), o qual nos forneceu
umamedidadaqualidadedonossomodeloempreverosvaloresdeseveridade.
```

**Chunk IDs:** `art-003-b0011-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0011-c000`

### q-003-t17

**Pergunta:** Qual métrica foi usada para escolher a melhor combinação de hiperparâmetros?

**Expected answer:** Erro Quadrático Médio (RMSE)

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `AMBIGUOUS_EVIDENCE`.

**Observações:** O artigo chama a métrica de Erro Quadrático Médio (RMSE), e a explicação da seção 4 descreve média de diferenças quadráticas sem raiz. RMSE e MSE são conceitualmente diferentes; preservada a resposta que reproduz o artigo, exigindo adjudicação da nomenclatura sem inferir código externo.

**Evidência q-003-t17-e1 — página 6; seção 3.4. Passo a passo do treinamento:**

```text
utilizamos o me´todo de grid search, que nos permitiu explorar diversas combinac¸o˜es de
hiperparaˆmetros e selecionar aquela que resultou no melhor desempenho. Vale ressaltar
que a me´trica que utilizamos foi o Erro Quadra´tico Me´dio (RMSE), o qual nos forneceu
umamedidadaqualidadedonossomodeloempreverosvaloresdeseveridade.
```

**Chunk IDs:** `art-003-b0011-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0011-c000`

### q-003-t18

**Pergunta:** O que um RMSE menor significa no contexto do trabalho?

**Expected answer:** Que o modelo está melhor ajustado e as previsões estão mais próximas dos valores reais

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t18-e1 — página 6; seção 4. Resultados:**

```text
No eixo Y e´ poss´ıvel observar valor do RMSE dos modelos estudados. Como no
nosso trabalho estamos utilizando a te´cnica de regressa˜o, esse valor e´ calculado obtendo
a me´dia das diferenc¸as ao quadrado entre o valor previsto pelo modelo e o valor real, e
quanto menor o valor, significa que o modelo esta´ melhor ajustado e que as previso˜es
esta˜opro´ximasdosvaloresreais.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0013-c000`

### q-003-t19

**Pergunta:** O que representa a letra B nas combinações de dados apresentadas nos gráficos?

**Expected answer:** A base de dados sem acréscimos

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t19-e1 — página 6; seção 4. Resultados:**

```text
Nosgra´ficosaseguir,“T”representaosdadosdopacotebrclimr,“S”representam
os dados de solo retirados do IBGE, “C” representa a base de dados de caracter´ısticas
clima´ticas retirados do IBGE, “A” representa a altitude da localidade da plantac¸a˜o e “B”
e´ abasededadossemacre´scimos.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0013-c000`

### q-003-t20

**Pergunta:** Qual fonte de dados mostrou importância geral para reduzir o erro dos modelos?

**Expected answer:** Os dados climáticos do pacote brclimr

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.

**Evidência q-003-t20-e1 — página 6; seção 4. Resultados:**

```text
Ao analisar o gra´fico, percebemos que o acre´scimo dos dados provenientes do
pacotebrclimr melhoramsignificativamenteoerrodetodososmodelosutilizados. Ale´m
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-003-b0013-c000`

### q-003-m01

**Pergunta:** Considerando a explicação dos modelos e a Figura 1, qual modelo de árvores é ilustrado e o que a figura torna possível interpretar?

**Expected answer:** CatBoost; a visualização de um weak learner permite observar caminhos de decisão do modelo

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A identidade da árvore e a capacidade interpretativa estão na prosa e legenda. A pergunta não pede ler nós, valores ou caminhos específicos da imagem.

**Evidência q-003-m01-e1 — página 5; seção 3.3. Modelos Utilizados / Figura 1:**

```text
Outros modelos utilizados baseados em A´rvores de Decisa˜o sa˜o o XGBoost e o
CatBoost. A diferenc¸a desses dois para o Random Forest e´ que eles utilizam te´cnicas
mais robustas para a combinac¸a˜o dos resultados dos diferentes Weak Learners, cha-
mada de descida de gradiente. Essa te´cnica usa ca´lculos matema´ticos para reajustar os
paraˆmetros dos Weak Learner para tentar melhorar o valor da previsa˜o. Ale´m disso, as
capacidades de explicabilidade desses dois modelos sa˜o similares aos de Random Fo-
rest[ChenandGuestrin2016][Dorogushetal. 2018]. Comoexemplo,naFigura1e´ mos-
tradaumadasA´rvoresdeDecisa˜ousadasinternamentepelomodelodoCatBoost.
Figura1. Visualizac¸a˜odeumWeakLearner domodeloCatBoost
```

**Chunk IDs:** `art-003-b0009-c000`.
**Grupo:** `q-003-m01-g1`

**Evidência q-003-m01-e2 — página 4; seção 3.3. Modelos Utilizados:**

```text
Ale´m disso, esse modelo tem grandes capacidades de explicabilidade. Com ele
e´ poss´ıvel obter informac¸o˜es como a importaˆncia de cada paraˆmetro e exportar uma
representac¸a˜o visual de cada um dos Weak Learners. Isso possibilita visualizar os ca-
minhos tomados pelo modelo para chegar em uma decisa˜o. Finalmente, pode-se utilizar
```

**Chunk IDs:** `art-003-b0008-c000`.
**Grupo:** `q-003-m01-g2`

**Qrels propostos (relevance = 1):** `art-003-b0008-c000`, `art-003-b0009-c000`

**Grupos obrigatórios:**

- `q-003-m01-g1`: A árvore ilustrada na Figura 1 é um weak learner do CatBoost. Alternativas OR: `art-003-b0009-c000`.
- `q-003-m01-g2`: A visualização de weak learners permite interpretar caminhos até decisões. Alternativas OR: `art-003-b0008-c000`.

### q-003-m02

**Pergunta:** Usando a legenda da Figura 2 e a explicação da Seção 4, o que o eixo Y mede e o que significam as letras T, S, C e A nas combinações?

**Expected answer:** Mede RMSE; T são dados brclimr, S dados de solo do IBGE, C características climáticas do IBGE e A altitude da localidade

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Eixo e legenda são explicados textualmente; nenhuma altura de barra foi inferida. A definição matemática de RMSE na fonte é imprecisa, como registrado em q-003-t17.

**Evidência q-003-m02-e1 — página 6; seção 4. Resultados:**

```text
No eixo Y e´ poss´ıvel observar valor do RMSE dos modelos estudados. Como no
nosso trabalho estamos utilizando a te´cnica de regressa˜o, esse valor e´ calculado obtendo
a me´dia das diferenc¸as ao quadrado entre o valor previsto pelo modelo e o valor real, e
quanto menor o valor, significa que o modelo esta´ melhor ajustado e que as previso˜es
esta˜opro´ximasdosvaloresreais.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** `q-003-m02-g1`

**Evidência q-003-m02-e2 — página 6; seção 4. Resultados:**

```text
Nosgra´ficosaseguir,“T”representaosdadosdopacotebrclimr,“S”representam
os dados de solo retirados do IBGE, “C” representa a base de dados de caracter´ısticas
clima´ticas retirados do IBGE, “A” representa a altitude da localidade da plantac¸a˜o e “B”
e´ abasededadossemacre´scimos.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** `q-003-m02-g2`

**Qrels propostos (relevance = 1):** `art-003-b0013-c000`

**Grupos obrigatórios:**

- `q-003-m02-g1`: O eixo Y representa RMSE. Alternativas OR: `art-003-b0013-c000`.
- `q-003-m02-g2`: T=brclimr, S=solo IBGE, C=clima IBGE, A=altitude. Alternativas OR: `art-003-b0013-c000`.

### q-003-m03

**Pergunta:** Comparando as Figuras 2 e 3 com a discussão textual, como o efeito da combinação de fontes de dados difere entre Campo Verde e Maracaju?

**Expected answer:** Em uma localidade há melhora significativa, especialmente com dados brclimr, enquanto na outra a combinação de todas as fontes produz pouca melhora; o texto atribui a diferença a dificuldades de ajuste em partes dos dados

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `MANUAL_VISUAL_REVIEW_REQUIRED`.

**Observações:** A resposta pré-anotada diz uma localidade/outra sem atribuir a melhora a Campo Verde ou Maracaju. A prosa sustenta heterogeneidade e dificuldade de ajuste, mas a comparação cidade a cidade das Figuras 2/3 depende das barras não extraídas. Grupos textuais são candidatos parciais; confirmar atribuição visual antes de aprovar.

**Evidência q-003-m03-e1 — página 6; seção 4. Resultados:**

```text
A partir dos testes realizados, foi poss´ıvel realizar algumas ana´lises. A primeira delas e´
comparar os gra´ficos das diferentes combinac¸o˜es para algumas cidades e ver como cada
uma delas se comporta. Nas Figuras 2 e 3 podemos observar como variam os valores do
RMSE para duas localidades diferentes, com uma delas obtendo uma melhora significa-
tiva, principalmente quando adicionando os dados do pacote brclim e outra com pouca
melhora,mesmocomacombinac¸a˜odetodasasfontesdedados.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** `q-003-m03-g1`

**Evidência q-003-m03-e2 — página 7; seção 4. Resultados:**

```text
Outrasituac¸a˜orelevantee´ queomodeloparatodasascidadesna˜oapresentavalo-
res ta˜o baixos como os mostrados em casos como o de Maracaju. Isso e´ por conta de um
fenoˆmenocausadopeloscasoscomoodeCampoVerde,emqueomodeloapresentadifi-
culdadesparaseajustaraalgumaspartesdoconjuntosdedados. Issoafetaaperformance
geral do modelo elevando o valor do RMSE. Tal fenoˆmeno e´ detalhadamente estudado
em[Chungetal. 2019].
```

**Chunk IDs:** `art-003-b0014-c000`.
**Grupo:** `q-003-m03-g2`

**Qrels propostos (relevance = 1):** `art-003-b0013-c000`, `art-003-b0014-c000`

**Grupos obrigatórios:**

- `q-003-m03-g1`: Duas localidades respondem de forma diferente ao enriquecimento, sobretudo brclimr. Alternativas OR: `art-003-b0013-c000`.
- `q-003-m03-g2`: Dificuldade de ajuste em Campo Verde contrasta com erros mais baixos em Maracaju. Alternativas OR: `art-003-b0014-c000`.
- `q-003-m03-g3`: Atribuição visual da melhora por combinação a Campo Verde versus Maracaju nas Figuras 2 e 3. Alternativas OR: **SEM CHUNK — pendente**.

### q-003-m04

**Pergunta:** Como a Figura 4 e a análise dos resultados demonstram que adicionar todas as bases não é sempre a melhor escolha?

**Expected answer:** Embora brclimr melhore significativamente o erro em geral, em um caso os dados brclimr sozinhos superam a combinação de todas as bases, indicando que alguns dados podem prejudicar o ajuste

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A prosa descreve diretamente o contraste perguntado; não se identificou arbitrariamente qual modelo ou valor da Figura 4. O segundo trecho é continuação literal da análise da página anterior.

**Evidência q-003-m04-e1 — página 6; seção 4. Resultados:**

```text
Ao analisar o gra´fico, percebemos que o acre´scimo dos dados provenientes do
pacotebrclimr melhoramsignificativamenteoerrodetodososmodelosutilizados. Ale´m
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** `q-003-m04-g1`

**Evidência q-003-m04-e2 — página 7; seção 4. Resultados:**

```text
disso, e´ poss´ıvel observar que em um dos casos, os dados do pacote brclimr sozinhos
tiveram resultados melhores do que com todas as bases unidas, mostrando que alguns
dadospodemestaratrapalhandoosmodelosseajustaremcorretamente.
```

**Chunk IDs:** `art-003-b0014-c000`.
**Grupo:** `q-003-m04-g2`

**Qrels propostos (relevance = 1):** `art-003-b0013-c000`, `art-003-b0014-c000`

**Grupos obrigatórios:**

- `q-003-m04-g1`: brclimr reduz significativamente o erro dos modelos em geral. Alternativas OR: `art-003-b0013-c000`.
- `q-003-m04-g2`: Em um caso brclimr sozinho supera todas as bases combinadas. Alternativas OR: `art-003-b0014-c000`.

### q-003-m05

**Pergunta:** Combinando a descrição das fontes de dados com os gráficos de resultados, qual é a cadeia de informação usada para explicar por que uma previsão pode variar entre cidades?

**Expected answer:** Dados de severidade e fungicidas são enriquecidos por município/ano com dados meteorológicos, solo, clima regional e altitude; os gráficos mostram que essas combinações afetam o RMSE de forma diferente conforme a cidade

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A cadeia de dados e a variação qualitativa entre localidades são explicitadas na prosa. Diferentemente de m03, não é necessário atribuir uma barra/cidade específica.

**Evidência q-003-m05-e1 — página 4; seção 3.2. Tratamento de Dados:**

```text
Os dados passaram por processos de tratamento, para que apenas os dados necessa´rios e
relacionadosa`slocalidadesdesejadasfossemobtidos. Apo´sisso,essasinformac¸o˜esforam
fundidas com o conjunto de dados principal da Embrapa de forma que fossem mantidas
as relac¸o˜es de localidade e ano, assim, ao final desse processo, e´ obtido um conjunto de
dados que relacionam solo, dados clima´ticos e agroto´xicos utilizados com a severidade
daferrugemasia´tica.
```

**Chunk IDs:** `art-003-b0007-c000`.
**Grupo:** `q-003-m05-g1`

**Evidência q-003-m05-e2 — página 4; seção 3.2. Tratamento de Dados:**

```text
nic´ıpios(atribuidospeloIBGE)ondeasplantac¸o˜esocorreram. Foramseparadoosvalores
de desvio padra˜o e valores ma´ximos, m´ınimos e me´dios para cada diferente combinac¸a˜o
demunic´ıpio,meˆseano. Foramselecionadososvaloresreferentesapre´-colheitadecada
safra, nos meses de novembro e dezembro, e os valores foram acrescentados ao conjunto
dedadosdeseveridade.
```

**Chunk IDs:** `art-003-b0007-c001`.
**Grupo:** `q-003-m05-g2`

**Evidência q-003-m05-e3 — página 6; seção 4. Resultados:**

```text
Nosgra´ficosaseguir,“T”representaosdadosdopacotebrclimr,“S”representam
os dados de solo retirados do IBGE, “C” representa a base de dados de caracter´ısticas
clima´ticas retirados do IBGE, “A” representa a altitude da localidade da plantac¸a˜o e “B”
e´ abasededadossemacre´scimos.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** `q-003-m05-g3`

**Evidência q-003-m05-e4 — página 6; seção 4. Resultados:**

```text
A partir dos testes realizados, foi poss´ıvel realizar algumas ana´lises. A primeira delas e´
comparar os gra´ficos das diferentes combinac¸o˜es para algumas cidades e ver como cada
uma delas se comporta. Nas Figuras 2 e 3 podemos observar como variam os valores do
RMSE para duas localidades diferentes, com uma delas obtendo uma melhora significa-
tiva, principalmente quando adicionando os dados do pacote brclim e outra com pouca
melhora,mesmocomacombinac¸a˜odetodasasfontesdedados.
```

**Chunk IDs:** `art-003-b0013-c000`.
**Grupo:** `q-003-m05-g4`

**Qrels propostos (relevance = 1):** `art-003-b0007-c000`, `art-003-b0007-c001`, `art-003-b0013-c000`

**Grupos obrigatórios:**

- `q-003-m05-g1`: Severidade, agroquímicos, solo e clima são integrados mantendo localidade e ano. Alternativas OR: `art-003-b0007-c000`.
- `q-003-m05-g2`: Dados meteorológicos brclimr são associados pelo código municipal e safra. Alternativas OR: `art-003-b0007-c001`.
- `q-003-m05-g3`: Combinações também incluem altitude da localidade. Alternativas OR: `art-003-b0013-c000`.
- `q-003-m05-g4`: Efeitos sobre RMSE variam entre localidades. Alternativas OR: `art-003-b0013-c000`.


## Artigo art-004

### q-004-t01

**Pergunta:** Qual tipo de rede óptica é o foco do artigo?

**Expected answer:** Redes ópticas elásticas com multiplexação por divisão espacial, ou SDM-EONs, usando fibras multinúcleo

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t01-e1 — página 1; seção Resumo:**

```text
Resumo. Redes o´pticas ela´sticas com multiplexac¸a˜o por divisa˜o espacial
(SDM-EON), usando fibras multi-nu´cleos (MCF), sa˜o promissoras para as fu-
turas redes de transporte.
```

**Chunk IDs:** `art-004-b0001-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t01-e2 — página 1; seção Seção 1:**

```text
A rede o´ptica ela´stica com multiplexac¸a˜o por divisa˜o espacial (spatial-division multi-
plexing elastic optical network - SDM-EON), em particular usando fibras multi-nu´cleo
(multi-core fiber - MCF)
```

**Chunk IDs:** `art-004-b0002-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0001-c000`, `art-004-b0002-c000`

### q-004-t02

**Pergunta:** Que novo problema de alocação de recursos surge nas fibras multinúcleo?

**Expected answer:** A alocação do núcleo da fibra

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t02-e1 — página 1; seção Resumo:**

```text
Em MCFs, surge uma nova dimensa˜o no problema
dealocac¸a˜oderecursos: aalocac¸a˜odonu´cleo.
```

**Chunk IDs:** `art-004-b0001-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0001-c000`

### q-004-t03

**Pergunta:** O que significa a sigla AMN?

**Expected answer:** Algoritmo com aprendizado de máquina para escolha de núcleo

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t03-e1 — página 6; seção Seção 4:**

```text
Neste artigo e´ proposto o algoritmo com aprendizado de ma´quina para escolha de nu´cleo
(AMN) em SDM-EONs.
```

**Chunk IDs:** `art-004-b0018-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0018-c000`

### q-004-t04

**Pergunta:** Qual fenômeno de interferência entre núcleos é um desafio central em SDM-EONs?

**Expected answer:** Crosstalk inter-núcleo (XT)

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t04-e1 — página 2; seção Seção 1:**

```text
Um destes desafios e´ o crosstalk (XT) inter-nu´cleo [Hayashietal. 2011]. O XT e´
um tipo de interfereˆncia que ocorre quando a mesma faixa de frequeˆncia e´ utilizada por
doisnu´cleospro´ximos. Quantomenoradistaˆnciaentreosnu´cleos,maioroefeitodoXT.
```

**Chunk IDs:** `art-004-b0003-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0003-c000`

### q-004-t05

**Pergunta:** Quais são os quatro subproblemas do RMSCA apresentados no artigo?

**Expected answer:** Roteamento, escolha de modulação, escolha de núcleo e alocação de espectro

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t05-e1 — página 2; seção Seção 1:**

```text
O problema RMSCA consiste em quatro subproblemas: i) rotea-
mento,queconsisteemescolherumarotaentreumno´ deorigemO eumno´ dedestinoD
na rede; ii) escolha da modulac¸a˜o, que consiste em definir qual o formato de modulac¸a˜o
sera´ usadopelocaminhoo´ptico. Amodulac¸a˜oe´ aformadecodificac¸a˜odainformac¸a˜o(re-
presentada por bits) em sinais digitais [TanenbaumandWetherall2011]; iii) escolha do
nu´cleo, onde o plano de controle deve escolher qual dos nu´cleos da fibra sera´ usado pelo
caminhoo´ptico;eiv)alocac¸a˜odeespectro,queconsistedefinirqualporc¸a˜oespectralsera´
usadapelocaminhoo´ptico.
```

**Chunk IDs:** `art-004-b0003-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0003-c000`

### q-004-t06

**Pergunta:** Qual largura tem cada slot de frequência do espectro óptico na rede descrita?

**Expected answer:** 12,5 GHz

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t06-e1 — página 2; seção Seção 1:**

```text
Oespectroo´ptico,emumaredeo´pticaela´stica,e´ divididoem
porc¸o˜esde12,5GHzdenominadasslotsdefrequeˆncia[ITU-TG.694.12020].
```

**Chunk IDs:** `art-004-b0003-c001`.
**Grupo:** Não aplicável.

**Evidência q-004-t06-e2 — página 8; seção Seção 5:**

```text
Cada
nu´cleoe´ divididoem320slotsdefrequeˆncia,emquecadaslotpossui12,5GHz.
```

**Chunk IDs:** `art-004-b0028-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0003-c001`, `art-004-b0028-c000`

### q-004-t07

**Pergunta:** Qual é a diferença entre estratégias XT-aware e XT-avoid?

**Expected answer:** XT-aware usa níveis de crosstalk em tempo real; XT-avoid tenta evitá-lo sem conhecer seus valores em tempo real

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t07-e1 — página 2; seção Seção 2:**

```text
As estrate´gias XT-aware sa˜o cientes de crosstalk e utilizam
os valores e n´ıveis de crosstalk em tempo real para a tomada de decisa˜o no problema
RMSCA. Ja´ as estrate´gias XT-avoid buscam alocar os recursos da rede de forma a evitar
o crosstalk sem possuir os valores em tempo real.
```

**Chunk IDs:** `art-004-b0004-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0004-c000`

### q-004-t08

**Pergunta:** Qual tipo de estratégia de crosstalk é adotada pelo artigo?

**Expected answer:** XT-avoid

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t08-e1 — página 3; seção Seção 2:**

```text
Buscando eficieˆncia e baixo custo computacional, este artigo aborda o problema de
alocac¸a˜oderecursosemSDM-EONatrave´sdeme´todosXT-avoid.
```

**Chunk IDs:** `art-004-b0005-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t08-e2 — página 4; seção Seção 2:**

```text
deste artigo, que propo˜e o uso de redes neurais para definir o melhor nu´cleo a ser usado,
semoconhecimentodosn´ıveisdeXT(istoe´,XT-avoid),emSDM-EONs.
```

**Chunk IDs:** `art-004-b0007-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0005-c000`, `art-004-b0007-c000`

### q-004-t09

**Pergunta:** Quais três fatores de limitação da camada física são considerados?

**Expected answer:** Ruído ASE, efeitos não lineares e crosstalk inter-núcleo

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t09-e1 — página 4; seção Seção 3:**

```text
Neste artigo sa˜o considerados treˆs
fatores limitadores de desempenho pela camada f´ısica: i) o ru´ıdo de emissa˜o espontaˆnea
amplificada (amplified spontaneous emission - ASE); ii) os efeitos na˜o-lineares; e iii) o
crosstalk inter-nu´cleo.
```

**Chunk IDs:** `art-004-b0008-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0008-c000`

### q-004-t10

**Pergunta:** Qual relação é usada como critério de qualidade de transmissão além do XT?

**Expected answer:** OSNR, relação sinal-ruído óptico

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t10-e1 — página 4; seção Seção 3:**

```text
Umamaneirademedirosn´ıveisdeQoTdaredee´ pormeiodarelac¸a˜osinal-ru´ıdo
o´ptico (optical signal to noise ratio - OSNR). A OSNR estabelece uma relac¸a˜o entre a
PSDdocaminhoo´pticoeaPSDdoru´ıdoASEedainterfereˆnciana˜olinearesqueoafeta.
AOSNRe´ usadacomoumdoscrite´riosdeQoTnesteartigoee´ dadapor
```

**Chunk IDs:** `art-004-b0009-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0009-c000`

### q-004-t11

**Pergunta:** De qual algoritmo o AMN aprende o comportamento para a escolha de núcleo?

**Expected answer:** CBA-SBA

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t11-e1 — página 6; seção Seção 4:**

```text
Oalgoritmoutilizadopara acriac¸a˜odabasededadose´ oCBA-SBA
[LacerdaJretal. 2021].
```

**Chunk IDs:** `art-004-b0019-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t11-e2 — página 12; seção Seção 6:**

```text
OAMNutilizaumaredeneuralparaaprenderocomportamento
de outro algoritmo, o CBA-SBA, e extrair caracter´ısticas-chave e predizer qual o melhor
nu´cleoparaseralocadoparacadarequisic¸a˜oemumdeterminadoestadodarede.
```

**Chunk IDs:** `art-004-b0066-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0019-c000`, `art-004-b0066-c000`

### q-004-t12

**Pergunta:** Quais são os três passos do fluxo de funcionamento do AMN?

**Expected answer:** Gerar a base de dados, treinar a rede neural e executar a rede treinada para escolher o núcleo

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t12-e1 — página 6; seção Seção 4:**

```text
O fluxo de funcionamento do AMN e´ composto de
treˆs passos: o primeiro passo constitui a criac¸a˜o de uma base de dados, o segundo passo
corresponde ao treinamento da RNA e o terceiro passo constitui a execuc¸a˜o do AMN
duranteafasedefuncionamentodarede.
```

**Chunk IDs:** `art-004-b0018-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t12-e2 — página 7; seção Seção 4:**

```text
Os passos um e dois ocorrem em um momento offline da rede. Ja´ o passo treˆs e´
executado durante o funcionamento da rede para a alocac¸a˜o de nu´cleo. Nesta etapa, para
cadarequisic¸a˜odenovocaminhoo´pticoquechegaaoplanodecontrole,oAMNalimenta
asuaRNAcomosdezesseteatributos(estadoatualdarede)eexecutaaRNAja´ treinada.
No processo de execuc¸a˜o da RNA, a mesma retorna o nu´cleo a ser escolhido.
```

**Chunk IDs:** `art-004-b0023-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0018-c000`, `art-004-b0023-c000`

### q-004-t13

**Pergunta:** Aproximadamente quantos registros são gerados na base de dados usada no treinamento do AMN?

**Expected answer:** Aproximadamente 800.000 registros

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A aproximação de 800.000 consta na Figura 1; o texto informa exatamente 844.631 registros gerados (e 675.704 usados no treino, com divisão 80/20). A resposta pré-anotada aproximada foi preservada, pois a pergunta trata da base gerada. Mantido draft.

**Evidência q-004-t13-e1 — página 6; seção Figura 1 / Seção 4:**

```text
Passo 1.Gerar uma base Passo 2.Treinar a rede Passo 3.Executar a rede
de dados com ≈ 800.000 neural para aprender o neural treinada para
registros. comportamento da base. escolha do núcleo.
```

**Chunk IDs:** `art-004-b0018-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t13-e2 — página 6; seção Seção 4:**

```text
A base gerada a partir do CBA-SBA possui 844.631 registros, que correspondem
as requisic¸o˜es na˜o bloqueadas de um total de 1.000.000 de requisic¸o˜es geradas em dife-
rentes pontos de carga da rede.
```

**Chunk IDs:** `art-004-b0019-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0018-c000`, `art-004-b0019-c001`

### q-004-t14

**Pergunta:** Quais topologias são consideradas nas simulações?

**Expected answer:** NSFNet e EURO28

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t14-e1 — página 8; seção Seção 5:**

```text
Astopologiasconsideradasnassimulac¸o˜essa˜oaNSFNeteaEURO28(Figura3).
```

**Chunk IDs:** `art-004-b0026-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0026-c000`

### q-004-t15

**Pergunta:** Quais duas métricas de desempenho são usadas para avaliar o AMN?

**Expected answer:** Probabilidade de bloqueio de requisição (PBR) e razão de dados bloqueados (RDB)

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t15-e1 — página 8; seção Seção 5:**

```text
Osalgoritmossa˜oavaliadosemtermosdeprobabilidadedebloqueioderequisic¸a˜o
(PBR) e raza˜o de dados bloqueados (RDB).
```

**Chunk IDs:** `art-004-b0028-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0028-c000`

### q-004-t16

**Pergunta:** Quais cinco pontos de carga são usados para calcular o ganho médio?

**Expected answer:** 900, 1000, 1100, 1200 e 1300 Erlangs

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t16-e1 — página 12; seção Seção 5:**

```text
O ganho me´dio
consistename´diaentreosganhosobtidosnoscincopontosdecargadecadagra´fico(900,
1000,1100,1200e1300Erlangs).
```

**Chunk IDs:** `art-004-b0064-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0064-c000`

### q-004-t17

**Pergunta:** Em qual cenário o AMN apresenta ganhos médios de pelo menos 8,16% em PBR e 9,28% em RDB?

**Expected answer:** No cenário de alta incidência de XT

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Os percentuais constam no resumo e na conclusão para alta incidência de XT; a Tabela 4 e discussão excluem implicitamente NSFNet versus CBA-SBA por equivalência no intervalo de confiança (1,17% e 1,36%). O cenário pedido está suportado; ressalva preservada para revisão humana.

**Evidência q-004-t17-e1 — página 12; seção Seção 6:**

```text
O AMN alcanc¸ou, em um cena´rio com alta incideˆncia de XT,
ganhosme´diosemrelac¸a˜oaoutrosalgoritmosXT-avoiddepelomenos8,16%emtermos
de PBR e de pelo menos 9,28% em termos de RDB.
```

**Chunk IDs:** `art-004-b0066-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t17-e2 — página 1; seção Resumo:**

```text
Em cena´rio de alta incideˆncia de crosstalk, o AMN
obteveganhosdeaomenos8,16%paraPBRedeaomenos9,28%paraRDB.
```

**Chunk IDs:** `art-004-b0001-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0001-c001`, `art-004-b0066-c000`

### q-004-t18

**Pergunta:** Em qual cenário o AMN alcança ganhos médios de pelo menos 25,35% em PBR e 24,87% em RDB?

**Expected answer:** No cenário de baixa incidência de XT

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `SOURCE_CONTRADICTION`.

**Observações:** Conflito interno da fonte: o resumo (p.1) registra 24,81% de RDB mínimo em baixa incidência de XT; a conclusão e a Tabela 4 (p.12) registram 24,87%. A resposta e o número da pergunta coincidem com conclusão/tabela e foram preservados, sem resolver arbitrariamente a divergência. Mantido draft. Trecho conflitante literal do resumo: "de bloqueio de requisic¸a˜o (PBR) e de ao menos 24,81% em termos de raza˜o de
dados bloqueados (RDB)."

**Evidência q-004-t18-e1 — página 12; seção Seção 6:**

```text
Ja´ no cena´rio de baixa incideˆncia de
XT,oAMNatingiuumganhome´diodepelomenos25,35%emtermosdePBRe24,87%
emtermosdeRDBemrelac¸a˜oaoutrosalgoritmos.
```

**Chunk IDs:** `art-004-b0066-c000`.
**Grupo:** Não aplicável.

**Evidência q-004-t18-e2 — página 12; seção Tabela 4 / Seção 5:**

```text
|  | PBR |  |  |  | RDB |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | NSFNet |  | EURO28 |  | NSFNet |  | EURO28 |  |
|  | AXT | BXT | AXT | BXT | AXT | BXT | AXT | BXT |
| CPRF | 94,52% | 99,94% | 88,70% | 89,10% | 92,40% | 99,90% | 85,81% | 89,01% |
| ADEIN | 86,98% | 96,82% | 74,11% | 25,35% | 84,82% | 95,57% | 71,76% | 24,87% |
```

**Chunk IDs:** `art-004-b0067-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0066-c000`, `art-004-b0067-c000`

### q-004-t19

**Pergunta:** Por que o desempenho do AMN e do CBA-SBA converge no cenário de alta incidência de XT na NSFNet?

**Expected answer:** Porque o AMN foi treinado a partir do CBA-SBA, e seus resultados ficam sobrepostos pelo intervalo de confiança nesse cenário

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t19-e1 — página 12; seção Seção 5:**

```text
Nos cena´rios com alta incideˆncia de XT, o desempenho do
AMN e´ equivalente ao CBA-SBA na topologia NSFNet. Neste caso espec´ıfico, os resul-
tados esta˜o sobrepostos pelo intervalo de confianc¸a (marcado com um “*” na Tabela 4).
Na topologia EURO28, o ganho me´dio do AMN (em relac¸a˜o ao CBA-SBA) e´ de 8,16%
emtermosdePBR.AsimilaridadeentreoAMNeoCBA-SBAnestecena´riodar-sepelo
fato do AMN ser treinado a partir do CBA-SBA, o que acarreta em uma convergeˆncia de
desempenhonocena´riodeAXT.
```

**Chunk IDs:** `art-004-b0065-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0065-c000`

### q-004-t20

**Pergunta:** Qual possibilidade de trabalho futuro é citada para aprimorar a tomada de decisão do AMN?

**Expected answer:** Investigar outras bases de treinamento e outras técnicas de ML, além de integrá-lo a outros subproblemas do RMSCA

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-004-t20-e1 — página 12; seção Seção 6:**

```text
Para trabalhos futuros pretende-se investigar o desempenho do AMN sendo trei-
nadoporoutrasbasesdedados,ale´mdabasegeradapeloalgoritmoCBA-SBA.Tambe´m
pretende-se estudar o uso de outras te´cnicas de ML para auxiliar na tomada de decisa˜o
da escolha de nu´cleo. Por fim, pretende-se aprofundar a investigac¸a˜o e utilizar a aborda-
gem de ML para tratar a alocac¸a˜o de nu´cleo em conjunto com outros subproblemas do
RMSCA,comoalocac¸a˜odeespectroouroteamento.
```

**Chunk IDs:** `art-004-b0066-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-004-b0066-c000`

### q-004-m01

**Pergunta:** Usando a Figura 1 e a descrição do algoritmo, em qual etapa a RNA é usada para escolher o núcleo durante a operação da rede?

**Expected answer:** No terceiro passo, após o treinamento, quando a rede neural treinada é executada para escolher o núcleo

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A informação solicitada da Figura 1 está explicitamente representada no texto das pp.6–7. Uma única informação necessária; os dois chunks são alternativas OR, sem grupos artificiais por sobreposição. Mantido draft.

**Evidência q-004-m01-e1 — página 6; seção Seção 4 / Figura 1:**

```text
corresponde ao treinamento da RNA e o terceiro passo constitui a execuc¸a˜o do AMN
duranteafasedefuncionamentodarede.
```

**Chunk IDs:** `art-004-b0018-c000`.
**Grupo:** `q-004-m01-g1`

**Evidência q-004-m01-e2 — página 7; seção Seção 4:**

```text
Os passos um e dois ocorrem em um momento offline da rede. Ja´ o passo treˆs e´
executado durante o funcionamento da rede para a alocac¸a˜o de nu´cleo. Nesta etapa, para
cadarequisic¸a˜odenovocaminhoo´pticoquechegaaoplanodecontrole,oAMNalimenta
asuaRNAcomosdezesseteatributos(estadoatualdarede)eexecutaaRNAja´ treinada.
No processo de execuc¸a˜o da RNA, a mesma retorna o nu´cleo a ser escolhido.
```

**Chunk IDs:** `art-004-b0023-c000`.
**Grupo:** `q-004-m01-g1`

**Qrels propostos (relevance = 1):** `art-004-b0018-c000`, `art-004-b0023-c000`

**Grupos obrigatórios:**

- `q-004-m01-g1`: Terceiro passo: execução da RNA treinada durante a operação para escolher o núcleo. Alternativas OR: `art-004-b0018-c000`, `art-004-b0023-c000`.

### q-004-m02

**Pergunta:** Compare a Tabela 1 com a estratégia adotada pelo AMN: qual característica comum aos trabalhos XT-avoid justifica a escolha metodológica do artigo?

**Expected answer:** Eles evitam crosstalk sem depender de seus valores em tempo real; o AMN segue essa abordagem para reduzir custo computacional

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A Tabela 1 está parcialmente fragmentada na extração: referências e tipos de XT aparecem em blocos distintos. A característica e a justificativa pedidas estão explícitas no texto da Seção 2, pp.2–3. Nenhuma correspondência de linha da tabela foi inventada; os dois grupos usam suporte textual suficiente. Mantido draft.

**Evidência q-004-m02-e1 — página 2; seção Seção 2:**

```text
Ja´ as estrate´gias XT-avoid buscam alocar os recursos da rede de forma a evitar
o crosstalk sem possuir os valores em tempo real.
```

**Chunk IDs:** `art-004-b0004-c000`.
**Grupo:** `q-004-m02-g1`

**Evidência q-004-m02-e2 — página 3; seção Seção 2:**

```text
Buscando eficieˆncia e baixo custo computacional, este artigo aborda o problema de
alocac¸a˜oderecursosemSDM-EONatrave´sdeme´todosXT-avoid.
```

**Chunk IDs:** `art-004-b0005-c000`.
**Grupo:** `q-004-m02-g2`

**Qrels propostos (relevance = 1):** `art-004-b0004-c000`, `art-004-b0005-c000`

**Grupos obrigatórios:**

- `q-004-m02-g1`: XT-avoid evita crosstalk sem conhecer seus valores em tempo real. Alternativas OR: `art-004-b0004-c000`.
- `q-004-m02-g2`: O artigo escolhe XT-avoid buscando eficiência e baixo custo computacional. Alternativas OR: `art-004-b0005-c000`.

### q-004-m03

**Pergunta:** Considerando a Figura 3 e a Seção 5, quais topologias são representadas e para qual finalidade elas são usadas?

**Expected answer:** NSFNet e EURO28; são as topologias usadas nas simulações de avaliação do AMN

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Identidade das topologias e finalidade estão em uma frase textual que referencia a Figura 3; não se infere grafo, enlaces ou topologia visual pela legenda. Mantido draft.

**Evidência q-004-m03-e1 — página 8; seção Seção 5 / Figura 3:**

```text
Astopologiasconsideradasnassimulac¸o˜essa˜oaNSFNeteaEURO28(Figura3).
```

**Chunk IDs:** `art-004-b0026-c000`.
**Grupo:** `q-004-m03-g1`

**Evidência q-004-m03-e2 — página 8; seção Seção 5 / Figura 3:**

```text
Astopologiasconsideradasnassimulac¸o˜essa˜oaNSFNeteaEURO28(Figura3).
```

**Chunk IDs:** `art-004-b0026-c000`.
**Grupo:** `q-004-m03-g2`

**Qrels propostos (relevance = 1):** `art-004-b0026-c000`

**Grupos obrigatórios:**

- `q-004-m03-g1`: As topologias representadas são NSFNet e EURO28. Alternativas OR: `art-004-b0026-c000`.
- `q-004-m03-g2`: Essas topologias são usadas nas simulações de avaliação de desempenho do AMN. Alternativas OR: `art-004-b0026-c000`.

### q-004-m04

**Pergunta:** Usando a Figura 4 e a explicação dos resultados, em qual carga são relatados os ganhos de 87,19% e 80,64% do AMN em PBR sobre o CPRF, e em quais topologias?

**Expected answer:** Na carga de 1300 Erlangs, na NSFNet (87,19%) e na EURO28 (80,64%), no cenário de alta incidência de XT

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Valores, carga, topologias e cenário constam no texto das pp.9–10; curvas ilegíveis na extração não foram reconstruídas. Mantido draft.

**Evidência q-004-m04-e1 — página 10; seção Seção 5 / Figura 4:**

```text
O ganho do AMN em relac¸a˜o ao CPRF com uma carga de 1300 Erlangs
(u´ltimo ponto de carga) foi de 87,19% na topologia NSFNet (Figura 4 (a)) e 80,64% na
topologia EURO28 (Figura 4 (b)).
```

**Chunk IDs:** `art-004-b0039-c000`.
**Grupo:** `q-004-m04-g1`

**Evidência q-004-m04-e2 — página 10; seção Seção 5 / Figura 4:**

```text
O ganho do AMN em relac¸a˜o ao CPRF com uma carga de 1300 Erlangs
(u´ltimo ponto de carga) foi de 87,19% na topologia NSFNet (Figura 4 (a)) e 80,64% na
topologia EURO28 (Figura 4 (b)).
```

**Chunk IDs:** `art-004-b0039-c000`.
**Grupo:** `q-004-m04-g2`

**Evidência q-004-m04-e3 — página 10; seção Seção 5 / Figura 4:**

```text
O ganho do AMN em relac¸a˜o ao CPRF com uma carga de 1300 Erlangs
(u´ltimo ponto de carga) foi de 87,19% na topologia NSFNet (Figura 4 (a)) e 80,64% na
topologia EURO28 (Figura 4 (b)).
```

**Chunk IDs:** `art-004-b0039-c000`.
**Grupo:** `q-004-m04-g3`

**Evidência q-004-m04-e4 — página 9; seção Seção 5:**

```text
A avaliac¸a˜o de desempenho e´ realizado em dois cena´rios: um com alta in-
cideˆncia de XT (AXT) e um com baixa incideˆncia de XT (BXT). Para simular estes
dois cena´rios, o coeficiente de acoplamento de poteˆncia da fibra (h ) e´ ajustado para
l
6,4×10−9 m−1 no cena´rio de AXT [Lobatoetal. 2019] e 1,5×10−9 m−1 no cena´rio de
BXT[Lobatoetal. 2019]. Estaabordagemverificaodesempenhodaspropostasemdife-
rentestiposdeMCFs. AFigura4apresentaosresultadosdePBRparaocena´rioAXT.
```

**Chunk IDs:** `art-004-b0032-c001`.
**Grupo:** `q-004-m04-g4`

**Qrels propostos (relevance = 1):** `art-004-b0032-c001`, `art-004-b0039-c000`

**Grupos obrigatórios:**

- `q-004-m04-g1`: Os ganhos relatados são medidos na carga de 1300 Erlangs. Alternativas OR: `art-004-b0039-c000`.
- `q-004-m04-g2`: O ganho de PBR do AMN sobre CPRF na NSFNet é 87,19%. Alternativas OR: `art-004-b0039-c000`.
- `q-004-m04-g3`: O ganho de PBR do AMN sobre CPRF na EURO28 é 80,64%. Alternativas OR: `art-004-b0039-c000`.
- `q-004-m04-g4`: Figura 4 apresenta PBR no cenário de alta incidência de XT (AXT). Alternativas OR: `art-004-b0032-c001`.

### q-004-m05

**Pergunta:** A partir da Tabela 4 e da discussão subsequente, em qual caso o ganho médio do AMN sobre CBA-SBA é marcado como equivalente pelo intervalo de confiança?

**Expected answer:** Em PBR e RDB na topologia NSFNet sob alta incidência de XT, com 1,17% e 1,36% marcados por asterisco

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Cabeçalhos hierárquicos PBR/RDB, topologia e AXT/BXT preservados na tabela extraída permitem interpretar os valores. Significado do asterisco confirmado no parágrafo subsequente. Mantido draft.

**Evidência q-004-m05-e1 — página 12; seção Tabela 4 / Seção 5:**

```text
|  | PBR |  |  |  | RDB |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | NSFNet |  | EURO28 |  | NSFNet |  | EURO28 |  |
|  | AXT | BXT | AXT | BXT | AXT | BXT | AXT | BXT |
| CPRF | 94,52% | 99,94% | 88,70% | 89,10% | 92,40% | 99,90% | 85,81% | 89,01% |
| ADEIN | 86,98% | 96,82% | 74,11% | 25,35% | 84,82% | 95,57% | 71,76% | 24,87% |
| CBA-SBA | 1,17%* | 99,98% | 8,16% | 98,83% | 1,36%* | 99,97% | 9,28% | 98,72% |
```

**Chunk IDs:** `art-004-b0067-c000`.
**Grupo:** `q-004-m05-g1`

**Evidência q-004-m05-e2 — página 12; seção Tabela 4 / Seção 5:**

```text
|  | PBR |  |  |  | RDB |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | NSFNet |  | EURO28 |  | NSFNet |  | EURO28 |  |
|  | AXT | BXT | AXT | BXT | AXT | BXT | AXT | BXT |
| CPRF | 94,52% | 99,94% | 88,70% | 89,10% | 92,40% | 99,90% | 85,81% | 89,01% |
| ADEIN | 86,98% | 96,82% | 74,11% | 25,35% | 84,82% | 95,57% | 71,76% | 24,87% |
| CBA-SBA | 1,17%* | 99,98% | 8,16% | 98,83% | 1,36%* | 99,97% | 9,28% | 98,72% |
```

**Chunk IDs:** `art-004-b0067-c000`.
**Grupo:** `q-004-m05-g2`

**Evidência q-004-m05-e3 — página 12; seção Seção 5:**

```text
Nos cena´rios com alta incideˆncia de XT, o desempenho do
AMN e´ equivalente ao CBA-SBA na topologia NSFNet. Neste caso espec´ıfico, os resul-
tados esta˜o sobrepostos pelo intervalo de confianc¸a (marcado com um “*” na Tabela 4).
```

**Chunk IDs:** `art-004-b0065-c000`.
**Grupo:** `q-004-m05-g3`

**Qrels propostos (relevance = 1):** `art-004-b0065-c000`, `art-004-b0067-c000`

**Grupos obrigatórios:**

- `q-004-m05-g1`: Na NSFNet/AXT, o ganho médio de PBR sobre CBA-SBA é 1,17% com asterisco. Alternativas OR: `art-004-b0067-c000`.
- `q-004-m05-g2`: Na NSFNet/AXT, o ganho médio de RDB sobre CBA-SBA é 1,36% com asterisco. Alternativas OR: `art-004-b0067-c000`.
- `q-004-m05-g3`: O asterisco denota equivalência por sobreposição do intervalo de confiança. Alternativas OR: `art-004-b0065-c000`.


## Artigo art-005

### q-005-t01

**Pergunta:** Qual problema clínico os modelos do artigo buscam classificar automaticamente?

**Expected answer:** A presença de câncer peniano em imagens histopatológicas

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t01-e1 — página 10; seção Seção 5:**

```text
Neste estudo, foram propostos dois modelos para o diagnóstico automático de cân-
cerdepênisemimagenshistopatológicas
```

**Chunk IDs:** `art-005-b0022-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0022-c000`

### q-005-t02

**Pergunta:** Qual projeto organizou o conjunto de imagens utilizado?

**Expected answer:** Projeto Câncer de Pênis da Amazônia Legal (PCPAm)

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t02-e1 — página 4; seção Seção 3.1:**

```text
O conjunto de imagens utilizadas para a produção deste trabalho foi organizado
peloProjetoCâncerdePênisdaAmazôniaLegal(PCPAm)emcolaboraçãocomNúcleo
de Computação Aplicada da Universidade Federal do Maranhão.
```

**Chunk IDs:** `art-005-b0009-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0009-c000`

### q-005-t03

**Pergunta:** Quantas imagens compõem o conjunto de dados original?

**Expected answer:** 194 imagens RGB

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t03-e1 — página 4; seção Seção 3.1:**

```text
Este consiste em 194
imagens RGB de resolução 2048×1536 píxeis, organizadas por ampliação e situação
patológicaconformeatabela2.
```

**Chunk IDs:** `art-005-b0009-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0009-c000`

### q-005-t04

**Pergunta:** Quais duas ampliações estão presentes no conjunto original?

**Expected answer:** 40× e 100×

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t04-e1 — página 5; seção Tabela 2 / Seção 3.1:**

```text
Tabela2. Organizaçãodoconjuntodeimagens.
Ampliação Normal Câncer Total
40× 40 57 97
100× 40 57 97
```

**Chunk IDs:** `art-005-b0011-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0011-c000`

### q-005-t05

**Pergunta:** Qual ampliação foi usada nos treinamentos reportados?

**Expected answer:** 100×

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t05-e1 — página 5; seção Seção 3.1:**

```text
Paraaconduçãodesteestudo,optou-seporutilizarapenasaampliaçãode100x. A
decisãodeutilizarexclusivamenteaampliaçãode100xfoibaseadanaescolhadométodo
depré-processamentoquerequerumnúmerosignificativodetreinamentos.
```

**Chunk IDs:** `art-005-b0011-c000`.
**Grupo:** Não aplicável.

**Evidência q-005-t05-e2 — página 11; seção Seção 5:**

```text
Os resultados foram obtidos exclusivamente para a ampliação 100x, devido à
natureza do método Vahadane e a alguns testes preliminares.
```

**Chunk IDs:** `art-005-b0023-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0011-c000`, `art-005-b0023-c000`

### q-005-t06

**Pergunta:** Qual método de pré-processamento foi usado para corrigir variações de cor das imagens?

**Expected answer:** Normalização Vahadane

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t06-e1 — página 6; seção Seção 3.2:**

```text
Para a tarefa de pré-processamento, foi selecionado o método Vahadane, desen-
volvido e apresentado em [Vahadaneetal. 2016]. Este método é uma técnica avançada
utilizadanaanálisedeimagenshistopatológicasparacorrigirvariaçõesdecoretornaras
imagensmaisconsistentesecomparáveis.
```

**Chunk IDs:** `art-005-b0013-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0013-c000`

### q-005-t07

**Pergunta:** Para qual resolução as imagens foram redimensionadas após o pré-processamento?

**Expected answer:** 256 × 192 pixels

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t07-e1 — página 6; seção Seção 3.2:**

```text
Após a aplicação do método Vahadane, as imagens foram
redimensionadasparaaresolução256x192,emvirtudedaslimitaçõescomputacionais.
```

**Chunk IDs:** `art-005-b0013-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0013-c000`

### q-005-t08

**Pergunta:** Quais problemas do conjunto motivaram o uso de augmentation?

**Expected answer:** Desbalanceamento de classes e escassez de imagens para treinamento

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t08-e1 — página 6; seção Seção 3.2:**

```text
Alémdopré-processamento,tambémforamaplicadastécnicasdeAugmentation
paralidarcomdoisproblemaspresentesnoconjuntodeimagens: odesbalanceamentode
classeseaescassezdeimagensparaotreinamento.
```

**Chunk IDs:** `art-005-b0013-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0013-c000`

### q-005-t09

**Pergunta:** Que transformações geométricas foram usadas como augmentation?

**Expected answer:** Rotações de 90°, 180° e 270°, além de inversão horizontal e vertical

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t09-e1 — página 6; seção Seção 3.2:**

```text
Paralidarcomas
poucasimagensdodataset,foramutilizadastransformaçõesgeométricas: rotaçãoem90º,
180ºe270º,inversãohorizontalevertical.
```

**Chunk IDs:** `art-005-b0013-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0013-c001`

### q-005-t10

**Pergunta:** Quais são os dois modelos propostos pelos autores?

**Expected answer:** DenseMSAG e DenseUSAG

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t10-e1 — página 8; seção Seção 4:**

```text
OsmodelosDenseMSAGeDenseUSAGforamimplementados
utilizandoosframeworksKeraseTensorFlow[Josephetal. 2021].
```

**Chunk IDs:** `art-005-b0017-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0017-c000`

### q-005-t11

**Pergunta:** Qual arquitetura DenseNet foi usada como base?

**Expected answer:** DenseNet201

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t11-e1 — página 6; seção Seção 3.3:**

```text
A Figura 3 apresenta a arquitetura da DenseNet201 utilizada neste estudo.
```

**Chunk IDs:** `art-005-b0014-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0014-c000`

### q-005-t12

**Pergunta:** Qual problema de treinamento foi associado à complexidade do DenseMSAG?

**Expected answer:** Um número de parâmetros muito alto, que impediu o uso do mecanismo em todos os blocos densos

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t12-e1 — página 7; seção Seção 3.3:**

```text
Devido à complexidade do MSAG, o número de parâmetros da rede tornou-se
muito elevado, impossibilitandosua utilização em todosos blocos densosda rede, sendo
aplicadoapenasnosblocosdasduasprimeirassucessões.
```

**Chunk IDs:** `art-005-b0015-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0015-c000`

### q-005-t13

**Pergunta:** Qual convolução é mantida pelo USAG após a redução proposta em relação ao MSAG?

**Expected answer:** A convolução 1×1, Point Wise

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t13-e1 — página 7; seção Seção 3.3:**

```text
Este mecanismo de atenção surgiu da
reduçãodonúmerodeconvoluçõesutilizadasnoMSAG,mantendoapenasaconvolução
1x1(PointWise),comoilustradonaFigura5.
```

**Chunk IDs:** `art-005-b0015-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0015-c001`

### q-005-t14

**Pergunta:** Quais frameworks foram usados para implementar DenseMSAG e DenseUSAG?

**Expected answer:** Keras e TensorFlow

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t14-e1 — página 8; seção Seção 4:**

```text
OsmodelosDenseMSAGeDenseUSAGforamimplementados
utilizandoosframeworksKeraseTensorFlow[Josephetal. 2021].
```

**Chunk IDs:** `art-005-b0017-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0017-c000`

### q-005-t15

**Pergunta:** Qual otimizador foi utilizado nos treinamentos?

**Expected answer:** AdamW

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t15-e1 — página 8; seção Seção 4:**

```text
O otimizador AdamW [LoshchilovandHutter2017] foi utilizado devido sua eficiência
computacionalepoucanecessidadedememória.
```

**Chunk IDs:** `art-005-b0017-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0017-c000`

### q-005-t16

**Pergunta:** Quais métricas monitoraram o progresso do treinamento?

**Expected answer:** Acurácia, precisão, sensibilidade e F1-Score

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t16-e1 — página 8; seção Seção 4:**

```text
Para avaliação dos resultados, as métricas adotadas para monitorar o progresso
do treinamento foram a acurácia, a precisão, a sensibilidade e o F1-Score.
```

**Chunk IDs:** `art-005-b0017-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0017-c000`

### q-005-t17

**Pergunta:** Como o conjunto foi dividido na primeira sessão de treinamento?

**Expected answer:** 50% treino, 40% teste e 10% validação

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t17-e1 — página 9; seção Seção 4:**

```text
Inicialmente,oconjuntode
dadosfoidivididoutilizandoométodoHoldout,noqual50%dasimagensforamalocadas
paraoconjuntodetreinamento, 40%paraoconjuntodetestee10%para oconjuntode
validação.
```

**Chunk IDs:** `art-005-b0018-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0018-c000`

### q-005-t18

**Pergunta:** Qual método de validação cruzada foi usado na segunda fase de treinamento?

**Expected answer:** Monte Carlo

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t18-e1 — página 9; seção Seção 4:**

```text
Ométododevalidação
cruzadaescolhidofoioMonteCarlo,noqualoconjuntodedadosédivididoemconjuntos
detreinamento,testeevalidaçãováriasvezesdeformaaleatória,gerandodiversasdivisões
diferentes.
```

**Chunk IDs:** `art-005-b0018-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0018-c001`

### q-005-t19

**Pergunta:** Quantas partições distintas foram realizadas na validação cruzada?

**Expected answer:** Cinco

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t19-e1 — página 9; seção Seção 4:**

```text
Foram
realizadas 5 partições distintas do conjunto de dados, sempre garantindo que a imagem
utilizadaparaopré-processamentoestivessepresentenoconjuntodetreinamento.
```

**Chunk IDs:** `art-005-b0018-c001`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0018-c001`

### q-005-t20

**Pergunta:** Qual limitação do DenseUSAG é destacada na conclusão?

**Expected answer:** Sensibilidade inferior e desvios padrão elevados em suas métricas

**Tipo/modalidade:** `factual` / `text`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-t20-e1 — página 11; seção Seção 5:**

```text
Embora a DenseUSAG tenha resultados
comparáveisàliteratura,elaaindaapresentaalgumaslimitações,comoumasensibilidade
inferior e elevados desvios padrão em suas métricas.
```

**Chunk IDs:** `art-005-b0023-c000`.
**Grupo:** Não aplicável.

**Qrels propostos (relevance = 1):** `art-005-b0023-c000`

### q-005-m01

**Pergunta:** Com base na Tabela 2 e no texto da Seção 3.1, quantas imagens de câncer em 100× estão disponíveis e por que somente essa ampliação foi utilizada?

**Expected answer:** Há 57 imagens de câncer em 100×; foi usada apenas 100× porque o método Vahadane requer número significativo de treinamentos

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.

**Evidência q-005-m01-e1 — página 5; seção Tabela 2 / Seção 3.1:**

```text
Tabela2. Organizaçãodoconjuntodeimagens.
Ampliação Normal Câncer Total
40× 40 57 97
100× 40 57 97
```

**Chunk IDs:** `art-005-b0011-c000`.
**Grupo:** `q-005-m01-g1`

**Evidência q-005-m01-e2 — página 5; seção Seção 3.1:**

```text
Paraaconduçãodesteestudo,optou-seporutilizarapenasaampliaçãode100x. A
decisãodeutilizarexclusivamenteaampliaçãode100xfoibaseadanaescolhadométodo
depré-processamentoquerequerumnúmerosignificativodetreinamentos.
```

**Chunk IDs:** `art-005-b0011-c000`.
**Grupo:** `q-005-m01-g2`

**Evidência q-005-m01-e3 — página 6; seção Seção 3.2:**

```text
Para a tarefa de pré-processamento, foi selecionado o método Vahadane, desen-
volvido e apresentado em [Vahadaneetal. 2016].
```

**Chunk IDs:** `art-005-b0013-c000`.
**Grupo:** `q-005-m01-g3`

**Qrels propostos (relevance = 1):** `art-005-b0011-c000`, `art-005-b0013-c000`

**Grupos obrigatórios:**

- `q-005-m01-g1`: Tabela 2: 57 imagens da classe Câncer na ampliação 100×. Alternativas OR: `art-005-b0011-c000`.
- `q-005-m01-g2`: Uso exclusivo de 100× decorre do número de treinamentos exigido pelo pré-processamento. Alternativas OR: `art-005-b0011-c000`.
- `q-005-m01-g3`: O pré-processamento utilizado é Vahadane. Alternativas OR: `art-005-b0013-c000`.

### q-005-m02

**Pergunta:** Relacionando a Figura 1 às seções metodológicas, qual sequência de etapas forma a abordagem proposta?

**Expected answer:** Aquisição da base, pré-processamento das imagens, desenvolvimento e treinamento das arquiteturas de redes neurais e avaliação dos resultados

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Sequência inteira da Figura 1 está explicitamente descrita no parágrafo da Seção 3; cada grupo representa uma etapa necessária e o mesmo chunk suporta todas elas. Mantido draft.

**Evidência q-005-m02-e1 — página 4; seção Seção 3 / Figura 1:**

```text
AFigura1resumeametodologiapropostaneste
trabalho,composta pelaaquisiçãoda basededados
```

**Chunk IDs:** `art-005-b0007-c000`.
**Grupo:** `q-005-m02-g1`

**Evidência q-005-m02-e2 — página 4; seção Seção 3 / Figura 1:**

```text
pelaetapade pré-processamentodas
imagens
```

**Chunk IDs:** `art-005-b0007-c000`.
**Grupo:** `q-005-m02-g2`

**Evidência q-005-m02-e3 — página 4; seção Seção 3 / Figura 1:**

```text
pelo desenvolvimento e treinamento de arquiteturas de redes neurais
```

**Chunk IDs:** `art-005-b0007-c000`.
**Grupo:** `q-005-m02-g3`

**Evidência q-005-m02-e4 — página 4; seção Seção 3 / Figura 1:**

```text
e finaliza
comaavaliaçãodosresultadosobtidos.
```

**Chunk IDs:** `art-005-b0007-c000`.
**Grupo:** `q-005-m02-g4`

**Qrels propostos (relevance = 1):** `art-005-b0007-c000`

**Grupos obrigatórios:**

- `q-005-m02-g1`: Primeira etapa: aquisição da base de dados. Alternativas OR: `art-005-b0007-c000`.
- `q-005-m02-g2`: Segunda etapa: pré-processamento das imagens. Alternativas OR: `art-005-b0007-c000`.
- `q-005-m02-g3`: Terceira etapa: desenvolvimento e treinamento de arquiteturas neurais. Alternativas OR: `art-005-b0007-c000`.
- `q-005-m02-g4`: Etapa final: avaliação dos resultados. Alternativas OR: `art-005-b0007-c000`.

### q-005-m03

**Pergunta:** A Figura 2 é acompanhada de exemplos visuais do conjunto. De acordo com o texto, por quais dois critérios esses exemplos são organizados?

**Expected answer:** Por classe/situação patológica e por ampliação

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A pergunta solicita expressamente os critérios descritos no texto, que são literais nas pp.4–5. Não requer inferência sobre aparência das imagens. Mantido draft.

**Evidência q-005-m03-e1 — página 5; seção Seção 3.1 / Figura 2:**

```text
A Figura 2 apresenta alguns exemplos de imagens, com identificação do
pacienteedalâminautilizadaparafotografaraamostrarecolhida,organizadasporclassee
ampliação.
```

**Chunk IDs:** `art-005-b0011-c000`.
**Grupo:** `q-005-m03-g1`

**Evidência q-005-m03-e2 — página 4; seção Seção 3.1:**

```text
organizadas por ampliação e situação
patológicaconformeatabela2.
```

**Chunk IDs:** `art-005-b0009-c000`.
**Grupo:** `q-005-m03-g1`

**Evidência q-005-m03-e3 — página 5; seção Seção 3.1 / Figura 2:**

```text
A Figura 2 apresenta alguns exemplos de imagens, com identificação do
pacienteedalâminautilizadaparafotografaraamostrarecolhida,organizadasporclassee
ampliação.
```

**Chunk IDs:** `art-005-b0011-c000`.
**Grupo:** `q-005-m03-g2`

**Evidência q-005-m03-e4 — página 4; seção Seção 3.1:**

```text
organizadas por ampliação e situação
patológicaconformeatabela2.
```

**Chunk IDs:** `art-005-b0009-c000`.
**Grupo:** `q-005-m03-g2`

**Qrels propostos (relevance = 1):** `art-005-b0009-c000`, `art-005-b0011-c000`

**Grupos obrigatórios:**

- `q-005-m03-g1`: Um critério de organização dos exemplos é classe ou situação patológica. Alternativas OR: `art-005-b0009-c000`, `art-005-b0011-c000`.
- `q-005-m03-g2`: Outro critério de organização dos exemplos é ampliação. Alternativas OR: `art-005-b0009-c000`, `art-005-b0011-c000`.

### q-005-m04

**Pergunta:** Combinando a Figura 4 e o texto sobre DenseMSAG, quais três tipos de convolução compõem o MSAG e onde ele é inserido na DenseNet?

**Expected answer:** Convolução 1×1 Point Wise, convolução padrão 3×3 e convolução dilatada 3×3 com dilatação 2; ele é inserido nas concatenações dos blocos densos

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** Composição e ponto de inserção apresentados na Figura 4 estão explicitamente descritos no texto da p.7. O texto também limita MSAG às duas primeiras sucessões de blocos, por excesso de parâmetros; a resposta não deve implicar aplicação a toda a rede. Mantido draft.

**Evidência q-005-m04-e1 — página 7; seção Seção 3.3:**

```text
em três tipos de convoluções: convolução com filtros de tamanho 1x1, conhecida como
PointWise;convoluçõespadrãocomfiltrosdetamanho3x3;econvoluçõesdilatadascom
filtrosdetamanho3x3eumataxadedilataçãoiguala2.
```

**Chunk IDs:** `art-005-b0015-c000`.
**Grupo:** `q-005-m04-g1`

**Evidência q-005-m04-e2 — página 7; seção Seção 3.3:**

```text
em três tipos de convoluções: convolução com filtros de tamanho 1x1, conhecida como
PointWise;convoluçõespadrãocomfiltrosdetamanho3x3;econvoluçõesdilatadascom
filtrosdetamanho3x3eumataxadedilataçãoiguala2.
```

**Chunk IDs:** `art-005-b0015-c000`.
**Grupo:** `q-005-m04-g2`

**Evidência q-005-m04-e3 — página 7; seção Seção 3.3:**

```text
em três tipos de convoluções: convolução com filtros de tamanho 1x1, conhecida como
PointWise;convoluçõespadrãocomfiltrosdetamanho3x3;econvoluçõesdilatadascom
filtrosdetamanho3x3eumataxadedilataçãoiguala2.
```

**Chunk IDs:** `art-005-b0015-c000`.
**Grupo:** `q-005-m04-g3`

**Evidência q-005-m04-e4 — página 7; seção Seção 3.3:**

```text
As adaptações realizadas na arquitetura da DenseNet foram aplicadas em seus
blocos densos, mais especificamente na concatenação. A primeira adaptação, chamada
DenseMSAG, incorpora o Multi-Scale Attention Gate (MSAG) em suas concatenações,
ummecanismodeatençãoapresentadopor [Tangetal. 2023].
```

**Chunk IDs:** `art-005-b0015-c000`.
**Grupo:** `q-005-m04-g4`

**Qrels propostos (relevance = 1):** `art-005-b0015-c000`

**Grupos obrigatórios:**

- `q-005-m04-g1`: O MSAG inclui convolução 1×1 Point Wise. Alternativas OR: `art-005-b0015-c000`.
- `q-005-m04-g2`: O MSAG inclui convolução padrão 3×3. Alternativas OR: `art-005-b0015-c000`.
- `q-005-m04-g3`: O MSAG inclui convolução dilatada 3×3 com taxa de dilatação 2. Alternativas OR: `art-005-b0015-c000`.
- `q-005-m04-g4`: MSAG é inserido nas concatenações dos blocos densos da DenseNet. Alternativas OR: `art-005-b0015-c000`.

### q-005-m05

**Pergunta:** Usando a Tabela 3 e a discussão dos resultados, qual configuração obteve o melhor F1-Score e qual aspecto do resultado ainda exige cautela?

**Expected answer:** DenseUSAG na melhor época, com imagem P35 T, F1 de 93,16% ± 4,63%; a sensibilidade tem desvio padrão elevado e é inferior à de alguns trabalhos relacionados

**Tipo/modalidade:** `multi_evidence` / `mixed`. **Revisão humana:** `draft`.

**Status da análise automática:** `READY_FOR_HUMAN_REVIEW`.

**Observações:** A melhor linha da Tabela 3 foi extraída em bloco de tabela separado dos cabeçalhos e demais linhas. Ambos os chunks são necessários para verificar a coluna F1 e a comparação de máximo; por isso não são alternativas OR. A conclusão de melhor F1 refere-se às configurações propostas da Tabela 3, não ao máximo da literatura/Tabela 4. Mantido draft.

**Evidência q-005-m05-e1 — página 9; seção Tabela 3 / Seção 4:**

```text
| DenseUSAG | Melhorépoca | P35T | 92,30%±4,44% | 95,22%±5,05% | 92,17%±10,83% | 93,16%±4,63% |
| --- | --- | --- | --- | --- | --- | --- |
```

**Chunk IDs:** `art-005-b0020-c000`.
**Grupo:** `q-005-m05-g1`

**Evidência q-005-m05-e2 — página 9; seção Tabela 3 / Seção 4:**

```text
Tabela3. Resultadosobtidospelametodologiaproposta
Trabalhos Estágio ImagemParâm. Acurácia Precisão Sensibilidade F1-Score
DenseMSAG Melhorépoca P49T1 82,56%±4,93% 93,75%±4,16% 75,65%±9,02% 83,45%±5,13%
DenseMSAG Últimaépoca P49T1 80,00%±7,11% 93,97%±4,77% 70,43%±9,91% 80,32%±7,85%
DenseUSAG Últimaépoca P35T 88,20%±6,93% 95,78%±5,81% 84,34%±13,95% 88,95%±7,25%
```

**Chunk IDs:** `art-005-b0019-c000`.
**Grupo:** `q-005-m05-g2`

**Evidência q-005-m05-e3 — página 10; seção Seção 4.1:**

```text
Em relação à sensibilidade, a
DenseUSAGalcançouapenas92,1%±10,8%,valorinferiorquandocomparadoaosoutros
trabalhos. A métrica da sensibilidade é de grande relevância em estudos que tratam do
diagnósticodedoençasaoavaliaromodeloquantoàpresençadefalsosnegativos,osquais
podemrepresentarumafalsapercepçãodesegurança. Essavariaçãoemrelaçãoàsoutras
métricas indica a necessidade de soluções para mitigar os falsos negativos.
```

**Chunk IDs:** `art-005-b0021-c000`.
**Grupo:** `q-005-m05-g3`

**Qrels propostos (relevance = 1):** `art-005-b0019-c000`, `art-005-b0020-c000`, `art-005-b0021-c000`

**Grupos obrigatórios:**

- `q-005-m05-g1`: Configuração DenseUSAG/Melhor época/P35 T obtém F1 de 93,16% ± 4,63%. Alternativas OR: `art-005-b0020-c000`.
- `q-005-m05-g2`: Cabeçalhos e demais linhas da Tabela 3 estabelecem F1 inferior nas outras configurações avaliadas. Alternativas OR: `art-005-b0019-c000`.
- `q-005-m05-g3`: Sensibilidade de 92,1% ± 10,8% é inferior à dos trabalhos comparados e exige cuidado com falsos negativos. Alternativas OR: `art-005-b0021-c000`.

