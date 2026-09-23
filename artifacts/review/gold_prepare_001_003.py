"""Reproduce explicitly selected evidence candidates; no retrieval or approval.

Run from repository root. Line ranges were read and selected by the AI annotator,
not obtained by fuzzy matching. Exact containment only resolves chunk alternatives
for these already selected passages. Pages come from canonical PAGE markers.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/review'
CHUNKS = [json.loads(x) for x in (ROOT / 'data/processed/chunks/chunks.jsonl').read_text(encoding='utf-8').splitlines()]
ROWS = []


def add(doc, suffix, spans, groups=None, status='READY_FOR_HUMAN_REVIEW', note='', answer=None, quote_start=None):
    doc_id = f'art-{doc:03d}'
    qid = f'q-{doc:03d}-{suffix}'
    lines = (ROOT / f'data/processed/extracted/{doc_id}.md').read_text(encoding='utf-8').splitlines()
    provenance = json.loads((ROOT / f'data/processed/extracted/{doc_id}.provenance.json').read_text(encoding='utf-8'))
    evidence = []
    for n, spec in enumerate(spans, 1):
        first, last, section = spec[:3]
        quote = '\n'.join(lines[first-1:last])
        if quote_start is not None:
            # Explicitly selected literal start within the first source line.
            offset = lines[first-1].index(quote_start)
            quote = quote[offset:]
        page = int(re.findall(r'<!-- PAGE (\d+) -->', '\n'.join(lines[:first]))[-1])
        assert page <= provenance['num_pages']
        assert '<!-- PAGE' not in quote
        # A quote may begin with a heading represented in chunk.section.
        # Record this separately so consumers do not mistake it for text content.
        matches = [c for c in CHUNKS if c['doc_id'] == doc_id and c['page'] == page
                   and (quote in c['text'] or quote in ((c['section'] or '') + '\n' + c['text']))]
        if len(spec) > 3:
            allowed = spec[3]
            matches = [c for c in matches if c['chunk_id'] in allowed]
        ids = [c['chunk_id'] for c in matches]
        if not ids:
            print('UNMAPPED', qid, first, last)
        evidence.append(dict(doc_id=doc_id, page=page, section=section, quote=quote,
                             chunk_ids=ids, required_group=f'{qid}-g{n}' if groups else None))
    grp = [dict(group_id=f'{qid}-g{i}', question_id=qid, required=True,
                description=desc, chunk_ids=evidence[i-1]['chunk_ids'])
           for i, desc in enumerate(groups or [], 1)]
    row = dict(question_id=qid, status=status, observations=note,
               evidence=evidence, groups=grp,
               source_spans=[dict(first_line=s[0], last_line=s[1]) for s in spans])
    if answer:
        row['expected_answer'] = answer
    ROWS.append(row)


# Article 1: explicitly reviewed passages, including conflicting source claims.
add(1,'t01',[(62,66,'1. Introdução')])
add(1,'t02',[(82,84,'1. Introdução')])
add(1,'t03',[(85,88,'1. Introdução')])
add(1,'t04',[(85,87,'1. Introdução')])
add(1,'t05',[(215,218,'5. Metodologia Experimental')])
add(1,'t06',[(215,218,'5. Metodologia Experimental')])
add(1,'t07',[(294,302,'6. Resultados'),(306,311,'6. Resultados')])
add(1,'t08',[(169,172,'3. Pergunta de Pesquisa')])
add(1,'t09',[(177,183,'4.1. BiLSTM-CRF')])
add(1,'t10',[(294,295,'6. Resultados')])
add(1,'t11',[(223,227,'5.1. Base de Dados')])
add(1,'t12',[(264,266,'5.2. Medidas de Avaliação')])
add(1,'t13',[(268,270,'5.2. Medidas de Avaliação')])
add(1,'t14',[(245,248,'5.1. Base de Dados'),(279,282,'5.2. Medidas de Avaliação')])
add(1,'t15',[(326,330,'6. Resultados')], status='SOURCE_CONTRADICTION',
    note='A narrativa afirma superioridade em precisão e F1 nas duas classes, mas a Tabela 3 empata F1 de legislação (FLAIR/TensorFlow: 0,89) e precisão de jurisprudência (FLAIR/spaCy: 0,78). A resposta foi preservada para adjudicação humana; o qrel candidato sustenta a afirmação narrativa, não resolve a contradição.')
add(1,'t16',[(330,334,'6. Resultados')],
    note='Pergunta explicitamente limitada à discussão: ela atribui melhor recall ao TensorFlow. A Tabela 3 limita essa vantagem à legislação (0,87 versus 0,85); jurisprudência favorece FLAIR (0,53 versus 0,44). Não interpretar como superioridade em ambas as classes.')
add(1,'t17',[(336,339,'6. Resultados')])
add(1,'t18',[(348,350,'6. Resultados')])
add(1,'t19',[(284,286,'5.3. Recursos de Hardware e Software')])
add(1,'t20',[(101,103,'1. Introdução / contribuições',[])],status='AMBIGUOUS_EVIDENCE',
    note='O início da contribuição (produção de nova base de petições) foi interpretado pelo chunker como section, enquanto text conserva apenas primeira base deste tipo anotada manualmente. Indexação/reranking/geração usam text e não section. Não há suporte integral no conteúdo de um chunk; quote/página verificáveis na fonte, sem qrel. Não foi alterado o corpus congelado.')
add(1,'m01',[(177,183,'4.1. BiLSTM-CRF')],
    ['Função da CRF: rotular sequências e capturar dependências entre rótulos após o processamento contextual.'],
    note='A prosa explicita integralmente a função pedida; não se inferiu a estrutura visual da Figura 1. A pergunta demanda uma única informação apesar do tipo multi_evidence pré-anotado; um único grupo é semanticamente correto.')
add(1,'m02',[(223,236,'5.1. Base de Dados / Tabela 1'),(238,241,'5.1. Base de Dados')],
    ['Comparação de trechos: proposta 1.676, LeNER-BR 10.392.', 'A base proposta usa duas classes, menos que LeNER-BR.'],
    note='Tabela extraída perdeu alinhamento da coluna Proposto; os valores e a comparação são recuperáveis na prosa contígua. Não se usou o chunk isolado da coluna sem cabeçalhos.')
add(1,'m03',[(249,252,'5.1. Base de Dados / Tabela 2'),(279,282,'5.2. Medidas de Avaliação')],
    ['Contagens por classe/partição comprovam predominância de jurisprudência.', 'F1 sintetiza harmonicamente precisão e recall.'])
add(1,'m04',[(325,337,'6. Resultados / Tabela 3'),(312,322,'6. Resultados / Tabela 3')],
    ['FLAIR: jurisprudência F1 0,63 e recall 0,53; prosa explica equilíbrio.', 'Concorrentes em jurisprudência: TensorFlow F1 0,55/recall 0,44 e spaCy F1 0,20/recall 0,11.'],
    note='O rótulo FLAIR é section do primeiro chunk. A comparação requer dois grupos: resultado FLAIR e resultados concorrentes; não são evidências independentes criadas por sobreposição.')
add(1,'m05',[(312,319,'6. Resultados / Tabela 3'),(323,324,'6. Resultados / Tabela 3'),(373,375,'7. Conclusão')],
    ['spaCy em legislação: recall 0,44 e F1 0,56.', 'FLAIR em legislação: recall 0,85 e F1 0,89, associado inequivocamente ao modelo.', 'Conclusão identifica CNN/spaCy como modelo de pior desempenho.'],
    status='AMBIGUOUS_EVIDENCE',
    note='Fonte Markdown sustenta a resposta, mas o chunker separou a linha numérica da legislação FLAIR (fim de b0022) do rótulo FLAIR (section de b0023). Nenhum chunk isolado preserva a associação inequívoca modelo/linha; grupo FLAIR fica sem chunk. Corpus congelado preservado. Não tratar mera proximidade como qrel suficiente.')

# Article 2: tables 2/3 lost columns; use explicit surrounding prose where sufficient.
add(2,'t01',[(440,443,'5. Considerações Finais')])
add(2,'t02',[(220,224,'3.2. Banco de Dados e População Estudada')])
add(2,'t03',[(225,229,'3.2. Banco de Dados e População Estudada')])
add(2,'t04',[(414,416,'4. Análise de Performance')])
add(2,'t05',[(210,216,'3.1. Discussão do Problema de Pesquisa')])
add(2,'t06',[(225,227,'3.2. Banco de Dados e População Estudada')])
add(2,'t07',[(227,229,'3.2. Banco de Dados e População Estudada')])
add(2,'t08',[(322,326,'3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes')])
add(2,'t09',[(316,321,'3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes')])
add(2,'t10',[(330,336,'3.5. Construção de Recursos')])
add(2,'t11',[(350,354,'3.6. Balanceamento das Classes')])
add(2,'t12',[(359,362,'3.7. Normalização')])
add(2,'t13',[(369,371,'4. Análise de Performance')])
add(2,'t14',[(371,373,'4. Análise de Performance')])
add(2,'t15',[(408,413,'4. Análise de Performance')])
add(2,'t16',[(380,383,'4. Análise de Performance')])
add(2,'t17',[(389,391,'4. Análise de Performance')])
add(2,'t18',[(414,418,'4. Análise de Performance'),(239,242,'Tabela 1 / descrição de siglas')])
add(2,'t19',[(294,297,'3.4.1. Limpeza de Dados')])
add(2,'t20',[(448,451,'5. Considerações Finais')])
add(2,'m01',[(312,315,'3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes')],
    ['Variáveis de menor incidência: pH 8%, GCS 11%, glicose 17%.'],
    note='A Tabela 2 extraída tem colunas colapsadas; a prosa transcreve inequivocamente as três variáveis e incidências. Um grupo corresponde à única comparação pedida, não a três grupos artificiais por número.')
add(2,'m02',[(389,391,'4. Análise de Performance')],
    ['GBC lidera em 48 horas com F1 0,53 e AUC 0,85.'],
    note='Tabela 3 perdeu rótulos/valores de 48h na extração; discussão textual preserva integralmente método, janela e métricas. Não se atribui relevância ao chunk da tabela mutilada.')
add(2,'m03',[(383,388,'4. Análise de Performance'),(374,376,'4. Análise de Performance')],
    ['AUCs semelhantes podem acompanhar diferentes sensibilidades/especificidades conforme limiar.', 'AUC resume a área da ROC independentemente do ponto de operação.'],
    note='A discussão da Figura 2(a) explica explicitamente o fenômeno pedido; não se afirma um limiar numérico ou curva que dependa de leitura visual.')
add(2,'m04',[(414,418,'4. Análise de Performance'),(419,425,'4. Análise de Performance')],
    ['Proposta usa 12 variáveis: 7 sinais vitais, 2 dados demográficos, 2 exames e GCS; sinais coletados automaticamente.', 'Comparadores com AUC maior requerem 17 variáveis, até 6 exames ou componentes de GCS.'],
    note='A discussão explicita os valores da comparação da Tabela 1, mantendo os cabeçalhos semânticos que faltam em partes da tabela extraída.')
add(2,'m05',[(288,297,'3.4.1. Limpeza de Dados'),(316,328,'3.4.2. Agregação dos Dados por Hora e Tratamento de Dados Ausentes'),(330,336,'3.5. Construção de Recursos'),(350,354,'3.6. Balanceamento das Classes'),(359,362,'3.7. Normalização')],
    ['Limpeza de valores discrepantes.', 'Agregação horária pela mediana e seleção por completude sem imputação.', 'Construção de estatísticas resumidas.', 'Balanceamento por random oversampling.', 'Normalização min-max.'],
    note='Cada etapa necessária tem grupo próprio. A sequência está explicitada nas subseções; não se inventaram setas ou detalhes visuais da Figura 1.')

# Article 3: distinguish statements explicitly available in prose from graph claims.
add(3,'t01',[(23,24,'Resumo')])
add(3,'t02',[(25,27,'Resumo')])
add(3,'t03',[(113,116,'3.1. Coleta de Dados')])
add(3,'t04',[(107,112,'3.1. Coleta de Dados')])
add(3,'t05',[(109,112,'3.1. Coleta de Dados')],
    note='Resposta reproduz a contagem declarada pelo artigo. A enumeração inclui o Distrito Federal entre os dez; editorialmente são nove estados e o DF, não corrigimos silenciosamente o texto-fonte.')
add(3,'t06',[(109,112,'3.1. Coleta de Dados')])
add(3,'t07',[(125,126,'3.1. Coleta de Dados')])
add(3,'t08',[(120,124,'3.1. Coleta de Dados')])
add(3,'t09',[(155,160,'3.2. Tratamento de Dados')], quote_start='dados obtidos')
add(3,'t10',[(142,146,'3.2. Tratamento de Dados')])
add(3,'t11',[(182,189,'3.3. Modelos Utilizados')])
add(3,'t12',[(162,166,'3.3. Modelos Utilizados')])
add(3,'t13',[(173,178,'3.3. Modelos Utilizados')],
    note='O nome SHAP é literal. A expansão inglesa usada pelo artigo não foi validada externamente e não é necessária para a resposta.')
add(3,'t14',[(191,193,'3.3. Modelos Utilizados')])
add(3,'t15',[(206,211,'3.4. Passo a passo do treinamento')])
add(3,'t16',[(215,218,'3.4. Passo a passo do treinamento')])
add(3,'t17',[(215,218,'3.4. Passo a passo do treinamento')],status='AMBIGUOUS_EVIDENCE',
    note='O artigo chama a métrica de Erro Quadrático Médio (RMSE), e a explicação da seção 4 descreve média de diferenças quadráticas sem raiz. RMSE e MSE são conceitualmente diferentes; preservada a resposta que reproduz o artigo, exigindo adjudicação da nomenclatura sem inferir código externo.')
add(3,'t18',[(237,241,'4. Resultados')])
add(3,'t19',[(232,235,'4. Resultados')])
add(3,'t20',[(244,245,'4. Resultados')])
add(3,'m01',[(182,190,'3.3. Modelos Utilizados / Figura 1'),(173,176,'3.3. Modelos Utilizados')],
    ['A árvore ilustrada na Figura 1 é um weak learner do CatBoost.', 'A visualização de weak learners permite interpretar caminhos até decisões.'],
    note='A identidade da árvore e a capacidade interpretativa estão na prosa e legenda. A pergunta não pede ler nós, valores ou caminhos específicos da imagem.')
add(3,'m02',[(237,241,'4. Resultados'),(232,235,'4. Resultados')],
    ['O eixo Y representa RMSE.', 'T=brclimr, S=solo IBGE, C=clima IBGE, A=altitude.'],
    note='Eixo e legenda são explicados textualmente; nenhuma altura de barra foi inferida. A definição matemática de RMSE na fonte é imprecisa, como registrado em q-003-t17.')
add(3,'m03',[(226,231,'4. Resultados'),(254,259,'4. Resultados')],
    ['Duas localidades respondem de forma diferente ao enriquecimento, sobretudo brclimr.', 'Dificuldade de ajuste em Campo Verde contrasta com erros mais baixos em Maracaju.'],
    status='MANUAL_VISUAL_REVIEW_REQUIRED',
    note='A resposta pré-anotada diz uma localidade/outra sem atribuir a melhora a Campo Verde ou Maracaju. A prosa sustenta heterogeneidade e dificuldade de ajuste, mas a comparação cidade a cidade das Figuras 2/3 depende das barras não extraídas. Grupos textuais são candidatos parciais; confirmar atribuição visual antes de aprovar.')
ROWS[-1]['groups'].append(dict(group_id='q-003-m03-g3',question_id='q-003-m03',required=True,description='Atribuição visual da melhora por combinação a Campo Verde versus Maracaju nas Figuras 2 e 3.',chunk_ids=[]))
add(3,'m04',[(244,245,'4. Resultados'),(251,253,'4. Resultados')],
    ['brclimr reduz significativamente o erro dos modelos em geral.', 'Em um caso brclimr sozinho supera todas as bases combinadas.'],
    note='A prosa descreve diretamente o contraste perguntado; não se identificou arbitrariamente qual modelo ou valor da Figura 4. O segundo trecho é continuação literal da análise da página anterior.')
add(3,'m05',[(136,141,'3.2. Tratamento de Dados'),(156,160,'3.2. Tratamento de Dados'),(232,235,'4. Resultados'),(226,231,'4. Resultados')],
    ['Severidade, agroquímicos, solo e clima são integrados mantendo localidade e ano.', 'Dados meteorológicos brclimr são associados pelo código municipal e safra.', 'Combinações também incluem altitude da localidade.', 'Efeitos sobre RMSE variam entre localidades.'],
    note='A cadeia de dados e a variação qualitativa entre localidades são explicitadas na prosa. Diferentemente de m03, não é necessário atribuir uma barra/cidade específica.')

assert len(ROWS) == 75
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'gold_proposal_001_003.json').write_text(json.dumps(ROWS, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Wrote',len(ROWS),'question candidates')
