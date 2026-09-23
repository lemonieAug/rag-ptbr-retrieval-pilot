import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
chunks = [json.loads(line) for line in (root / 'data/processed/chunks/chunks.jsonl').read_text(encoding='utf8').splitlines()]
sources = {doc: (root / f'data/processed/extracted/{doc}.md').read_text(encoding='utf8') for doc in ('art-004', 'art-005')}
results = []

def ev(index, start=None, end=None, section=None):
    chunk = chunks[index]
    text = chunk['text']
    a = text.index(start) if start else 0
    b = text.index(end, a) + len(end) if end else len(text)
    quote = text[a:b]
    source = sources[chunk['doc_id']]
    assert quote in source, (index, quote)
    pos = source.index(quote)
    page = int(list(re.finditer(r'<!-- PAGE (\d+) -->', source[:pos]))[-1].group(1))
    assert page == chunk['page']
    return dict(doc_id=chunk['doc_id'], page=page, section=section or chunk['section'], quote=quote, chunk_ids=[chunk['chunk_id']], required_group=None)

def add(qid, evidence, status='READY_FOR_HUMAN_REVIEW', observations='', groups=None):
    item = dict(question_id=qid, status=status, observations=observations or 'Suporte literal conferido no Markdown extraído e no chunk congelado; página verificada pelo marcador PAGE da extração. Candidato produzido por IA, permanece draft.', evidence=evidence, groups=[])
    for number, (description, indices) in enumerate(groups or [], 1):
        gid = f'{qid}-g{number}'
        ids = []
        for i in indices:
            evidence[i]['required_group'] = gid
            ids.extend(evidence[i]['chunk_ids'])
        item['groups'].append(dict(group_id=gid, question_id=qid, required=True, description=description, chunk_ids=sorted(set(ids))))
    results.append(item)

add('q-004-t01', [ev(107, 'Resumo. Redes', 'turas redes de transporte.', 'Resumo'), ev(109, 'A rede', '(multi-core fiber - MCF)', 'Seção 1')])
add('q-004-t02', [ev(107, 'Em MCFs, surge', 'aalocac¸a˜odonu´cleo.', 'Resumo')])
add('q-004-t03', [ev(130, 'Neste artigo', '(AMN) em SDM-EONs.', 'Seção 4')])
add('q-004-t04', [ev(110, 'Um destes desafios', 'maioroefeitodoXT.', 'Seção 1')])
add('q-004-t05', [ev(110, 'O problema RMSCA consiste', 'usadapelocaminhoo´ptico.', 'Seção 1')])
add('q-004-t06', [ev(111, 'Oespectroo´ptico', '[ITU-TG.694.12020].', 'Seção 1'), ev(141, 'Cada\nnu´cleo', 'possui12,5GHz.', 'Seção 5')])
add('q-004-t07', [ev(113, 'As estrate´gias XT-aware', 'o crosstalk sem possuir os valores em tempo real.', 'Seção 2')])
add('q-004-t08', [ev(114, 'Buscando eficieˆncia', 'XT-avoid.', 'Seção 2'), ev(118, 'deste artigo, que propo˜e', 'emSDM-EONs.', 'Seção 2')])
add('q-004-t09', [ev(119, 'Neste artigo sa˜o considerados', 'crosstalk inter-nu´cleo.', 'Seção 3')])
add('q-004-t10', [ev(120, 'Umamaneira', 'dadapor', 'Seção 3')])
add('q-004-t11', [ev(131, 'Oalgoritmoutilizadopara', '[LacerdaJretal. 2021].', 'Seção 4'), ev(181, 'OAMNutiliza', 'estadodarede.', 'Seção 6')])
add('q-004-t12', [ev(130, 'O fluxo de funcionamento', 'duranteafasedefuncionamentodarede.', 'Seção 4'), ev(136, 'Os passos um e dois', 'No processo de execuc¸a˜o da RNA, a mesma retorna o nu´cleo a ser escolhido.', 'Seção 4')])
add('q-004-t13', [ev(130, 'Passo 1.Gerar', 'escolha do núcleo.', 'Figura 1 / Seção 4'), ev(132, 'A base gerada', 'rentes pontos de carga da rede.', 'Seção 4')], observations='A aproximação de 800.000 consta na Figura 1; o texto informa exatamente 844.631 registros gerados (e 675.704 usados no treino, com divisão 80/20). A resposta pré-anotada aproximada foi preservada, pois a pergunta trata da base gerada. Mantido draft.')
add('q-004-t14', [ev(139, 'Astopologias', '(Figura3).', 'Seção 5')])
add('q-004-t15', [ev(141, 'Osalgoritmossa˜oavaliados', '(PBR) e raza˜o de dados bloqueados (RDB).', 'Seção 5')])
add('q-004-t16', [ev(179, 'O ganho me´dio', '1000,1100,1200e1300Erlangs).', 'Seção 5')])
add('q-004-t17', [ev(181, 'O AMN alcanc¸ou', 'de PBR e de pelo menos 9,28% em termos de RDB.', 'Seção 6'), ev(108, 'Em cena´rio de alta', '9,28%paraRDB.', 'Resumo')], observations='Os percentuais constam no resumo e na conclusão para alta incidência de XT; a Tabela 4 e discussão excluem implicitamente NSFNet versus CBA-SBA por equivalência no intervalo de confiança (1,17% e 1,36%). O cenário pedido está suportado; ressalva preservada para revisão humana.')
add('q-004-t18', [ev(181, 'Ja´ no cena´rio', 'emtermosdeRDBemrelac¸a˜oaoutrosalgoritmos.', 'Seção 6'), ev(182, '|  | PBR', '| ADEIN | 86,98% | 96,82% | 74,11% | 25,35% | 84,82% | 95,57% | 71,76% | 24,87% |', 'Tabela 4 / Seção 5')], status='SOURCE_CONTRADICTION', observations='Conflito interno da fonte: o resumo (p.1) registra 24,81% de RDB mínimo em baixa incidência de XT; a conclusão e a Tabela 4 (p.12) registram 24,87%. A resposta e o número da pergunta coincidem com conclusão/tabela e foram preservados, sem resolver arbitrariamente a divergência. Mantido draft. Trecho conflitante literal do resumo: "de bloqueio de requisic¸a˜o (PBR) e de ao menos 24,81% em termos de raza˜o de\ndados bloqueados (RDB)."')
add('q-004-t19', [ev(180, 'Nos cena´rios', 'desempenhonocena´riodeAXT.', 'Seção 5')])
add('q-004-t20', [ev(181, 'Para trabalhos futuros', 'RMSCA,comoalocac¸a˜odeespectroouroteamento.', 'Seção 6')])
add('q-004-m01', [ev(130, 'corresponde ao treinamento', 'duranteafasedefuncionamentodarede.', 'Seção 4 / Figura 1'), ev(136, 'Os passos um e dois', 'No processo de execuc¸a˜o da RNA, a mesma retorna o nu´cleo a ser escolhido.', 'Seção 4')], groups=[('Terceiro passo: execução da RNA treinada durante a operação para escolher o núcleo.', [0, 1])], observations='A informação solicitada da Figura 1 está explicitamente representada no texto das pp.6–7. Uma única informação necessária; os dois chunks são alternativas OR, sem grupos artificiais por sobreposição. Mantido draft.')
add('q-004-m02', [ev(113, 'Ja´ as estrate´gias XT-avoid', 'o crosstalk sem possuir os valores em tempo real.', 'Seção 2'), ev(114, 'Buscando eficieˆncia', 'XT-avoid.', 'Seção 2')], groups=[('XT-avoid evita crosstalk sem conhecer seus valores em tempo real.', [0]), ('O artigo escolhe XT-avoid buscando eficiência e baixo custo computacional.', [1])], observations='A Tabela 1 está parcialmente fragmentada na extração: referências e tipos de XT aparecem em blocos distintos. A característica e a justificativa pedidas estão explícitas no texto da Seção 2, pp.2–3. Nenhuma correspondência de linha da tabela foi inventada; os dois grupos usam suporte textual suficiente. Mantido draft.')
add('q-004-m03', [ev(139, 'Astopologias', '(Figura3).', 'Seção 5 / Figura 3')], groups=[('NSFNet e EURO28 são as topologias da Figura 3 usadas nas simulações de avaliação.', [0])], observations='Identidade das topologias e finalidade estão em uma frase textual que referencia a Figura 3; não se infere grafo, enlaces ou topologia visual pela legenda. Mantido draft.')
add('q-004-m04', [ev(153, 'O ganho do AMN em relac¸a˜o ao CPRF', 'topologia EURO28 (Figura 4 (b)).', 'Seção 5 / Figura 4'), ev(146, 'A avaliac¸a˜o de desempenho', 'AFigura4apresentaosresultadosdePBRparaocena´rioAXT.', 'Seção 5')], groups=[('Na carga de 1300 Erlangs, ganhos sobre CPRF são 87,19% na NSFNet e 80,64% na EURO28.', [0]), ('Figura 4 apresenta PBR no cenário de alta incidência de XT (AXT).', [1])], observations='Valores, carga, topologias e cenário constam no texto das pp.9–10; curvas ilegíveis na extração não foram reconstruídas. Mantido draft.')
add('q-004-m05', [ev(182, section='Tabela 4 / Seção 5'), ev(180, 'Nos cena´rios', 'Tabela 4).', 'Seção 5')], groups=[('Tabela 4: CBA-SBA versus AMN na NSFNet/AXT tem 1,17% em PBR e 1,36% em RDB, ambos com asterisco.', [0]), ('O asterisco denota equivalência por sobreposição do intervalo de confiança.', [1])], observations='Cabeçalhos hierárquicos PBR/RDB, topologia e AXT/BXT preservados na tabela extraída permitem interpretar os valores. Significado do asterisco confirmado no parágrafo subsequente. Mantido draft.')

add('q-005-t01', [ev(217, 'Neste estudo', 'cerdepênisemimagenshistopatológicas', 'Seção 5')])
add('q-005-t02', [ev(200, 'O conjunto', 'de Computação Aplicada da Universidade Federal do Maranhão.', 'Seção 3.1')])
add('q-005-t03', [ev(200, 'Este consiste', 'patológicaconformeatabela2.', 'Seção 3.1')])
add('q-005-t04', [ev(202, 'Tabela2.', '100× 40 57 97', 'Tabela 2 / Seção 3.1')])
add('q-005-t05', [ev(202, 'Paraacondução', 'depré-processamentoquerequerumnúmerosignificativodetreinamentos.', 'Seção 3.1'), ev(218, 'Os resultados', 'natureza do método Vahadane e a alguns testes preliminares.', 'Seção 5')])
add('q-005-t06', [ev(204, 'Para a tarefa', 'imagensmaisconsistentesecomparáveis.', 'Seção 3.2')])
add('q-005-t07', [ev(204, 'Após a aplicação', 'redimensionadasparaaresolução256x192,emvirtudedaslimitaçõescomputacionais.', 'Seção 3.2')])
add('q-005-t08', [ev(204, 'Alémdopré-processamento', 'classeseaescassezdeimagensparaotreinamento.', 'Seção 3.2')])
add('q-005-t09', [ev(205, 'Paralidarcomas', '180ºe270º,inversãohorizontalevertical.', 'Seção 3.2')])
add('q-005-t10', [ev(210, 'OsmodelosDenseMSAG', 'utilizandoosframeworksKeraseTensorFlow[Josephetal. 2021].', 'Seção 4')])
add('q-005-t11', [ev(206, 'A Figura 3', 'utilizada neste estudo.', 'Seção 3.3')])
add('q-005-t12', [ev(207, 'Devido à complexidade', 'aplicadoapenasnosblocosdasduasprimeirassucessões.', 'Seção 3.3')])
add('q-005-t13', [ev(208, 'Este mecanismo de atenção', '1x1(PointWise),comoilustradonaFigura5.', 'Seção 3.3')])
add('q-005-t14', [ev(210, 'OsmodelosDenseMSAG', 'utilizandoosframeworksKeraseTensorFlow[Josephetal. 2021].', 'Seção 4')])
add('q-005-t15', [ev(210, 'O otimizador AdamW', 'computacionalepoucanecessidadedememória.', 'Seção 4')])
add('q-005-t16', [ev(210, 'Para avaliação dos resultados', 'do treinamento foram a acurácia, a precisão, a sensibilidade e o F1-Score.', 'Seção 4')])
add('q-005-t17', [ev(211, 'Inicialmente,oconjuntode', 'validação.', 'Seção 4')])
add('q-005-t18', [ev(212, 'Ométododevalidação', 'diferentes.', 'Seção 4')])
add('q-005-t19', [ev(212, 'Foram\nrealizadas', 'utilizadaparaopré-processamentoestivessepresentenoconjuntodetreinamento.', 'Seção 4')])
add('q-005-t20', [ev(218, 'Embora a DenseUSAG', 'inferior e elevados desvios padrão em suas métricas.', 'Seção 5')])
add('q-005-m01', [ev(202, 'Tabela2.', '100× 40 57 97', 'Tabela 2 / Seção 3.1'), ev(202, 'Paraacondução', 'depré-processamentoquerequerumnúmerosignificativodetreinamentos.', 'Seção 3.1'), ev(204, 'Para a tarefa', '[Vahadaneetal. 2016].', 'Seção 3.2')], groups=[('Tabela 2: 57 imagens da classe Câncer na ampliação 100×.', [0]), ('Uso exclusivo de 100× decorre do número de treinamentos exigido pelo pré-processamento.', [1]), ('O pré-processamento utilizado é Vahadane.', [2])])
add('q-005-m02', [ev(198, 'AFigura1resume', 'pelaaquisiçãoda basededados', 'Seção 3 / Figura 1'), ev(198, 'pelaetapade pré-processamentodas', 'imagens', 'Seção 3 / Figura 1'), ev(198, 'pelo desenvolvimento', 'arquiteturas de redes neurais', 'Seção 3 / Figura 1'), ev(198, 'e finaliza', 'comaavaliaçãodosresultadosobtidos.', 'Seção 3 / Figura 1')], groups=[('Primeira etapa: aquisição da base de dados.', [0]), ('Segunda etapa: pré-processamento das imagens.', [1]), ('Terceira etapa: desenvolvimento e treinamento de arquiteturas neurais.', [2]), ('Etapa final: avaliação dos resultados.', [3])], observations='Sequência inteira da Figura 1 está explicitamente descrita no parágrafo da Seção 3; cada grupo representa uma etapa necessária e o mesmo chunk suporta todas elas. Mantido draft.')
add('q-005-m03', [ev(202, 'A Figura 2 apresenta', 'ampliação.', 'Seção 3.1 / Figura 2'), ev(200, 'organizadas por ampliação', 'patológicaconformeatabela2.', 'Seção 3.1')], groups=[('Exemplos organizados por classe ou situação patológica e por ampliação.', [0, 1])], observations='A pergunta solicita expressamente os critérios descritos no texto, que são literais nas pp.4–5. Não requer inferência sobre aparência das imagens. Mantido draft.')
add('q-005-m04', [ev(207, 'em três tipos de convoluções', 'filtrosdetamanho3x3eumataxadedilataçãoiguala2.', 'Seção 3.3'), ev(207, 'As adaptações realizadas', 'ummecanismodeatençãoapresentadopor [Tangetal. 2023].', 'Seção 3.3')], groups=[('MSAG combina convoluções 1×1 Point Wise, padrão 3×3 e dilatada 3×3 com taxa 2.', [0]), ('MSAG é inserido nas concatenações dos blocos densos da DenseNet.', [1])], observations='Composição e ponto de inserção apresentados na Figura 4 estão explicitamente descritos no texto da p.7. O texto também limita MSAG às duas primeiras sucessões de blocos, por excesso de parâmetros; a resposta não deve implicar aplicação a toda a rede. Mantido draft.')
add('q-005-m05', [ev(214, section='Tabela 3 / Seção 4'), ev(213, section='Tabela 3 / Seção 4'), ev(215, 'Em relação à sensibilidade', 'métricas indica a necessidade de soluções para mitigar os falsos negativos.', 'Seção 4.1')], groups=[('Configuração DenseUSAG/Melhor época/P35 T obtém F1 de 93,16% ± 4,63%.', [0]), ('Cabeçalhos e demais linhas da Tabela 3 estabelecem F1 inferior nas outras configurações avaliadas.', [1]), ('Sensibilidade de 92,1% ± 10,8% é inferior à dos trabalhos comparados e exige cuidado com falsos negativos.', [2])], observations='A melhor linha da Tabela 3 foi extraída em bloco de tabela separado dos cabeçalhos e demais linhas. Ambos os chunks são necessários para verificar a coluna F1 e a comparação de máximo; por isso não são alternativas OR. A conclusão de melhor F1 refere-se às configurações propostas da Tabela 3, não ao máximo da literatura/Tabela 4. Mantido draft.')

def separate_facts(qid, old_group_number, descriptions):
    """Split independently required facts; shared supporting chunks stay shared."""
    item = next(r for r in results if r['question_id'] == qid)
    old_group = item['groups'][old_group_number - 1]
    supporting = [dict(e) for e in item['evidence'] if e['required_group'] == old_group['group_id']]
    rebuilt = []
    for group in item['groups']:
        if group is old_group:
            for description in descriptions:
                rebuilt.append((description, [dict(e) for e in supporting]))
        else:
            rebuilt.append((group['description'], [dict(e) for e in item['evidence'] if e['required_group'] == group['group_id']]))
    item['groups'] = []
    item['evidence'] = []
    for n, (description, evidence) in enumerate(rebuilt, 1):
        gid = f'{qid}-g{n}'
        for e in evidence:
            e['required_group'] = gid
        item['evidence'].extend(evidence)
        item['groups'].append(dict(group_id=gid, question_id=qid, required=True, description=description, chunk_ids=sorted({cid for e in evidence for cid in e['chunk_ids']})))

separate_facts('q-004-m03', 1, ['As topologias representadas são NSFNet e EURO28.', 'Essas topologias são usadas nas simulações de avaliação de desempenho do AMN.'])
separate_facts('q-004-m04', 1, ['Os ganhos relatados são medidos na carga de 1300 Erlangs.', 'O ganho de PBR do AMN sobre CPRF na NSFNet é 87,19%.', 'O ganho de PBR do AMN sobre CPRF na EURO28 é 80,64%.'])
separate_facts('q-004-m05', 1, ['Na NSFNet/AXT, o ganho médio de PBR sobre CBA-SBA é 1,17% com asterisco.', 'Na NSFNet/AXT, o ganho médio de RDB sobre CBA-SBA é 1,36% com asterisco.'])
separate_facts('q-005-m03', 1, ['Um critério de organização dos exemplos é classe ou situação patológica.', 'Outro critério de organização dos exemplos é ampliação.'])
separate_facts('q-005-m04', 1, ['O MSAG inclui convolução 1×1 Point Wise.', 'O MSAG inclui convolução padrão 3×3.', 'O MSAG inclui convolução dilatada 3×3 com taxa de dilatação 2.'])

assert len(results) == 50
assert len({r['question_id'] for r in results}) == 50
out = root / 'artifacts/review/gold_proposal_004_005.json'
out.write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'questions': len(results), 'evidence': sum(len(r['evidence']) for r in results), 'groups': sum(len(r['groups']) for r in results)}, ensure_ascii=False))
