"""Integrate the explicit AI proposals and build a human review packet.

Never approves questions. Refuses to overwrite human edits, including drafts. The input
snapshot preserves the initial answers/notes for an auditable, idempotent rerun.
Run from the repository: python artifacts/review/gold_integrate.py
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import yaml

from rag_ptbr_pilot.schemas import EvidenceGroup, QrelEntry, Question

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/review'
ANN = ROOT / 'data/annotations'
STATUSES = ['READY_FOR_HUMAN_REVIEW', 'SOURCE_CONTRADICTION', 'AMBIGUOUS_EVIDENCE',
            'MISSING_EVIDENCE', 'MANUAL_VISUAL_REVIEW_REQUIRED']


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


class ReviewDumper(yaml.SafeDumper):
    pass


def literal(dumper, value):
    return dumper.represent_scalar('tag:yaml.org,2002:str', value,
                                   style='|' if '\n' in value else None)


ReviewDumper.add_representer(str, literal)


def write_yaml(path, key, values, comment):
    body = yaml.dump({key: values}, Dumper=ReviewDumper, allow_unicode=True,
                     sort_keys=False, width=100)
    path.write_text(comment+'\n'+body, encoding='utf-8')


def prepared_notes(original, status, observations):
    origin_note = re.search(r'\bA\d\d-[TM]\d\d\b', original.get('notes') or '')
    return ((f"Pré-anotação {origin_note.group(0)}. " if origin_note else '')
            + f"Análise automática: {status}. {observations} Candidato produzido por IA; aguarda revisão humana.")


def assert_safe_annotation_state(current, baseline, previous_packet=None):
    """Accept only the original input or the complete last prepared output."""
    if any(q['review_status'] != 'draft' for q in current['questions']):
        raise RuntimeError('Human decisions already exist; refusing to replace reviewed questions.')
    if current == baseline:
        return
    if previous_packet is not None:
        originals = {q['question_id']: q for q in baseline['questions']}
        previous = {'questions': [], 'qrels': [], 'evidence_groups': []}
        for record in previous_packet['questions']:
            original = originals[record['question_id']]
            question = deepcopy(original)
            question.update(expected_answer=record['expected_answer'], review_status='draft',
                            evidence=record['evidence'],
                            notes=prepared_notes(original, record['automatic_status'], record['observations']))
            previous['questions'].append(question)
            previous['qrels'].extend(record['proposed_qrels'])
            previous['evidence_groups'].extend(record['required_groups'])
        if current == previous:
            return
    raise RuntimeError('Annotations contain edits since the original input or last preparation; '
                       'refusing to overwrite questions, qrels or evidence groups, including drafts.')


def main():
    names = ['questions', 'qrels', 'evidence_groups']
    initial_bytes = {k: (ANN/f'{k}.yaml').read_bytes() for k in names}
    current_state = {k: yaml.safe_load(raw.decode('utf-8'))[k] for k, raw in initial_bytes.items()}
    current = current_state['questions']
    snapshot_path = OUT/'gold_review_input.json'
    if not snapshot_path.exists():
        assert_safe_annotation_state(current_state, current_state)
        write_json(snapshot_path, current_state)
    baseline_state = read_json(snapshot_path)
    packet_path = OUT/'gold_review.json'
    previous_packet = read_json(packet_path) if packet_path.exists() else None
    assert_safe_annotation_state(current_state, baseline_state, previous_packet)
    baseline = baseline_state['questions']
    proposals = read_json(OUT/'gold_proposal_001_003.json') + read_json(OUT/'gold_proposal_004_005.json')
    by_id = {p['question_id']: p for p in proposals}
    assert len(proposals) == len(by_id) == len(baseline) == 125
    assert set(by_id) == {q['question_id'] for q in baseline}
    assert {q['question_id']: q['text'] for q in current} == {q['question_id']: q['text'] for q in baseline}
    chunks_path = ROOT/'data/processed/chunks/chunks.jsonl'
    chunks_hash_before = sha256(chunks_path.read_bytes()).hexdigest()
    chunks = {c['chunk_id']: c for c in map(json.loads, chunks_path.read_text(encoding='utf-8').splitlines())}
    manifest = read_json(ROOT/'data/processed/chunks/corpus_manifest.json')
    docs = {doc: (ROOT/f'data/processed/extracted/{doc}.md').read_text(encoding='utf-8')
            for doc in manifest['doc_ids']}
    pages = {doc: {int(m.group(1)): m.group(2) for m in
                  re.finditer(r'<!-- PAGE (\d+) -->\s*(.*?)(?=<!-- PAGE \d+ -->|\Z)', text, re.S)}
             for doc, text in docs.items()}
    questions, groups, qrels, review, corrections = [], [], [], [], []
    for original in baseline:
        q = deepcopy(original)
        p = by_id[q['question_id']]
        assert p['status'] in STATUSES
        assert original['review_status'] == 'draft'
        q['expected_answer'] = p.get('expected_answer', original['expected_answer'])
        q['review_status'] = 'draft'
        q['evidence'] = []
        for i, ev in enumerate(p['evidence'], 1):
            e = deepcopy(ev)
            e['evidence_id'] = f"{q['question_id']}-e{i}"
            assert e['quote'] and e['quote'] in pages[e['doc_id']][e['page']], e
            for cid in e['chunk_ids']:
                c = chunks[cid]
                assert c['doc_id'] == e['doc_id'] and c['page'] == e['page'], e
                # No source association can be created by near matches.
                assert e['quote'] in c['text'], (q['question_id'], cid, e['quote'])
            q['evidence'].append(e)
        note = p['observations'] or 'Trecho literal, página e suporte nos chunks conferidos automaticamente após seleção semântica por IA.'
        q['notes'] = prepared_notes(original, p['status'], note)
        Question.model_validate(q)
        qgroups = deepcopy(p['groups'])
        for g in qgroups:
            EvidenceGroup.model_validate(g)
            assert g['question_id'] == q['question_id']
            assert set(g['chunk_ids']) <= chunks.keys()
            linked = {cid for e in q['evidence'] if e['required_group'] == g['group_id'] for cid in e['chunk_ids']}
            assert linked == set(g['chunk_ids']), (g, linked)
        assert all(e['required_group'] is None or e['required_group'] in {g['group_id'] for g in qgroups} for e in q['evidence'])
        relevant = sorted({cid for e in q['evidence'] for cid in e['chunk_ids']})
        proposed_qrels = [dict(question_id=q['question_id'],chunk_id=cid,relevance=1) for cid in relevant]
        for rel in proposed_qrels:
            QrelEntry.model_validate(rel)
        change = None
        if q['expected_answer'] != original['expected_answer']:
            change = dict(question_id=q['question_id'],before=original['expected_answer'],after=q['expected_answer'])
            corrections.append(change)
        record = dict(question_id=q['question_id'], text=q['text'],expected_answer=q['expected_answer'],
                      origin_doc_id=q['origin_doc_id'],question_type=q['question_type'],modality=q['modality'],
                      review_status='draft',automatic_status=p['status'],observations=note,
                      original_notes=original.get('notes'),original_evidence=original['evidence'],
                      evidence=q['evidence'],proposed_qrels=proposed_qrels,required_groups=qgroups,
                      answer_change=change)
        review.append(record)
        questions.append(q)
        groups.extend(qgroups)
        qrels.extend(proposed_qrels)
    assert len({g['group_id'] for g in groups}) == len(groups)
    assert len({(r['question_id'],r['chunk_id']) for r in qrels}) == len(qrels)
    counts = Counter(r['automatic_status'] for r in review)
    summary = dict(total_questions=len(questions),
                   statuses={s:counts[s] for s in STATUSES},
                   evidence_refs=sum(len(q['evidence']) for q in questions),
                   evidence_with_literal_quote_and_verified_page=sum(bool(e['quote']) and e['page'] is not None for q in questions for e in q['evidence']),
                   evidence_with_chunk_ids=sum(bool(e['chunk_ids']) for q in questions for e in q['evidence']),
                   questions_with_candidate_qrels=len({r['question_id'] for r in qrels}),
                   qrels=len(qrels),required_groups=len(groups),
                   empty_required_groups=sum(not g['chunk_ids'] for g in groups),
                   approved_questions=0,draft_questions=125,expected_answer_changes=len(corrections))
    packet = dict(schema_version=1,annotation_method='AI candidate preparation; no human approval',
                  corpus_version=manifest['corpus_version'],chunks_sha256=chunks_hash_before,
                  source_hashes={doc:sha256((ROOT/f'data/processed/extracted/{doc}.md').read_bytes()).hexdigest() for doc in docs},
                  summary=summary,answer_changes=corrections,questions=review)
    if any((ANN/f'{k}.yaml').read_bytes() != initial_bytes[k] for k in names):
        raise RuntimeError('Annotations changed during preparation; refusing to overwrite concurrent edits.')
    write_yaml(ANN/'questions.yaml','questions',questions,
               '# 125 candidatos de gold preparados por IA. Todos permanecem draft até revisão humana.\n# Quotes/páginas/chunks auditáveis em artifacts/review/gold_review.md e gold_review.json.\n# Corpus congelado preservado; não regenerar chunks para preencher anotações.')
    write_yaml(ANN/'qrels.yaml','qrels',qrels,
               '# Qrels candidatos positivos; suporte efetivo auditado, sem negativos inferidos.\n# Não constituem gold aprovado. Questões draft continuam excluídas de runs oficiais.')
    write_yaml(ANN/'evidence_groups.yaml','evidence_groups',groups,
               '# Grupos por informação necessária: chunks dentro de cada grupo são alternativas OR.\n# Grupos diferentes são requisitos AND; grupos vazios indicam informação não resolvida.\n# Análise automática documentada no pacote de revisão; não há campo review_status neste schema.')
    write_json(OUT/'gold_review.json',packet)
    md = ['# Pacote de revisão humana do gold','',
          'Preparação de candidatos por IA. **Nenhuma questão foi aprovada.** READY_FOR_HUMAN_REVIEW significa pronta para inspeção humana, não gold validado. As 125 questões permanecem `draft`.', '',
          '| Indicador | Quantidade |','| --- | ---: |',f'| Total de perguntas | {len(questions)} |',
          f'| Prontas para revisão | {counts[STATUSES[0]]} |',f'| Com conflito | {counts[STATUSES[1]]} |',
          f'| Ambíguas | {counts[STATUSES[2]]} |',f'| Sem evidência | {counts[STATUSES[3]]} |',
          f'| Dependentes de revisão visual | {counts[STATUSES[4]]} |',
          f"| Evidências com quote literal e página verificada | {summary['evidence_refs']} |",
          f"| Evidências com chunks mapeados | {summary['evidence_with_chunk_ids']} |",
          f"| Perguntas com qrels candidatos | {summary['questions_with_candidate_qrels']} |",
          f'| Qrels positivos candidatos únicos | {len(qrels)} |',f'| Grupos obrigatórios | {len(groups)} |',
          f"| Grupos sem chunks | {summary['empty_required_groups']} |",'',
          f"Corpus: `{manifest['corpus_version']}`; 224 chunks congelados. As páginas são números físicos do PDF (marcadores PAGE da extração, conferidos com provenance); não foram inferidas pela seção.",'',
          '## Método e limites','',
          'Perguntas, respostas, seções e notas da pré-anotação foram lidas contra Markdown/provenance e conteúdo dos chunks. Os scripts preservados contêm seleções explícitas de trechos. A correspondência literal resolve IDs de chunks somente depois da seleção semântica; nenhuma similaridade lexical determinou relevância. Qrels positivos também podem representar um componente necessário de respostas compostas. Não são exaustivos: não se produziram negativos pela ausência de anotação. Nenhum método de retrieval foi usado para favorecer seus resultados.', '',
          'As citações preservam exatamente acentos corrompidos, hifenizações e espaços da extração. Os nomes de seção foram apresentados de forma legível quando o chunker interpretou incorretamente títulos/linhas. A evidência nunca foi reconstruída a partir da resposta esperada. Figuras/tabelas foram substituídas por prosa somente quando essa prosa explicita a informação solicitada; isso prepara a resposta, mas não demonstra competência visual do retriever. A modalidade/tipo original das perguntas foi preservada.', '',
          'Cada grupo representa uma informação necessária; IDs dentro dele são alternativas OR, grupos distintos são AND. Algumas perguntas rotuladas multi_evidence pedem apenas um fato composto (por exemplo, líder e suas métricas), sendo suficiente um grupo. Listas com componentes separadamente verificáveis podem ter vários grupos, inclusive satisfeitos pelo mesmo chunk. A granularidade editorial deve ser confirmada na revisão humana. Não foram criados grupos por sobreposição de chunks. Cabeçalhos e linha de tabela separados podem ser informações complementares necessárias, como em q-005-m05.', '',
          'O JSON paralelo preserva notas/evidências originais, status por pergunta, qrels, grupos e alterações de resposta antes/depois. As instruções antigas para executar chunk foram substituídas, pois o corpus já está congelado. Nenhum ReviewRecord de aprovação humana foi fabricado.', '',
          '## Alterações de expected_answer','',
          'Nenhuma resposta esperada foi alterada nesta preparação.' if not corrections else '\n'.join(f"- {c['question_id']}: antes `{c['before']}`; depois `{c['after']}`" for c in corrections), '',
          '## Questões que exigem adjudicação','']
    for r in review:
        if r['automatic_status'] != STATUSES[0]:
            md.append(f"- **{r['question_id']} — {r['automatic_status']}**: {r['observations']}")
    current_doc = None
    for r in review:
        if r['origin_doc_id'] != current_doc:
            current_doc = r['origin_doc_id']
            md.extend(['',f'## Artigo {current_doc}',''])
        md.extend([f"### {r['question_id']}",'',f"**Pergunta:** {r['text']}",'',
                   f"**Expected answer:** {r['expected_answer']}",'',
                   f"**Tipo/modalidade:** `{r['question_type']}` / `{r['modality']}`. **Revisão humana:** `draft`.",'',
                   f"**Status da análise automática:** `{r['automatic_status']}`.",'',
                   f"**Observações:** {r['observations']}",''])
        for e in r['evidence']:
            md.extend([f"**Evidência {e['evidence_id']} — página {e['page']}; seção {e['section']}:**",'',
                       '```text',e['quote'],'```','',
                       '**Chunk IDs:** '+(', '.join(f'`{cid}`' for cid in e['chunk_ids']) or 'Nenhum: suporte no corpus congelado não resolvido.')+'.',
                       '**Grupo:** '+(f"`{e['required_group']}`" if e['required_group'] else 'Não aplicável.')+'',''])
        md.extend(['**Qrels propostos (relevance = 1):** '+(', '.join(f"`{x['chunk_id']}`" for x in r['proposed_qrels']) or 'Nenhum.'),''])
        if r['required_groups']:
            md.extend(['**Grupos obrigatórios:**',''])
            for g in r['required_groups']:
                md.append(f"- `{g['group_id']}`: {g['description']} Alternativas OR: "+(', '.join(f'`{cid}`' for cid in g['chunk_ids']) or '**SEM CHUNK — pendente**')+'.')
            md.append('')
    (OUT/'gold_review.md').write_text('\n'.join(md)+'\n', encoding='utf-8')
    assert sha256(chunks_path.read_bytes()).hexdigest() == chunks_hash_before
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
