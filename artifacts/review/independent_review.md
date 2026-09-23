# Verificação das alterações

Verificação por IA, sem aprovação humana do benchmark.

- Conferência integral final: 125 perguntas draft, 176 quotes literais nas
  páginas indicadas, 174 evidências com conteúdo literal em chunks, 157 qrels
  únicos e 62 grupos. Nenhuma resposta esperada foi alterada.
- Conferência semântica adicional: perguntas textuais dos artigos 2 e 3 e
  amostras dos artigos 1, 4 e 5, incluindo perguntas multimodais e tabelas.
  O caso RMSE/MSE permanece ambíguo; q-003-t09 teve a citação ampliada para
  deixar explícita a referência ao código do município.
- Conferência de código: carregamento local por revisão, batches limitados,
  liberação dos modelos, fingerprints, validação de runs, separação entre gold
  e entrada dos recuperadores e confirmação explícita no helper humano.
- A revisão encontrou inconsistências de BM25, rankings incompletos, configuração
  ignorada do reranker e saída Unicode no Windows. Foram corrigidas e cobertas
  por regressões pertinentes.
- A guarda do integrador foi testada sobre cópias temporárias: aceita snapshot
  inicial e último pacote gerado; rejeita edições em resposta, notas, evidência,
  qrels, grupos e estados de revisão sem sobrescrever essas alterações.
- Suíte final: `pytest -o cache_dir=artifacts/review/.pytest_cache` —
  **91 passed em 15,60 s**, sem warnings.
- `rag-ptbr validate`: **0 erros / 130 avisos**; detalhes em
  `validate_final.txt` e `technical_results.json`.
- Corpus, manifesto e arquivos dos índices BM25/Colibri preservados byte a byte.
  Os loaders de retrieval aceitaram esses índices após as mudanças.

Não foram executados retrieval ou métricas oficiais. A inferência real dos
índices Qwen/E5 continua pendente da conclusão ou interrupção autorizada da
indexação que já estava rodando antes desta sessão (PID 12008). Os testes
sintéticos não substituem essa etapa operacional.
