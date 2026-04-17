# AGENTS.md

## Objetivo do repositório
Aplicação Streamlit para análise de vendas em `.XLS`, com ETL, analytics, comparação de períodos e ML explicável.

## Regras de execução
- Execute localmente com:
  - `pip install -r requirements.txt`
  - `streamlit run app.py`
- A entrada oficial é `.XLS` (engine `xlrd`).
- Saídas devem continuar sendo gravadas em `outputs/`.

## Estrutura esperada
- `app.py`: interface principal e orquestração.
- `src/data_processing.py`: ingestão, validação, limpeza e enriquecimento.
- `src/analytics.py`: KPIs, agregações, concentração e Pareto.
- `src/comparison.py`: comparação entre períodos e movimentação.
- `src/ml_models.py`: modelos simples, explicáveis, com métricas.
- `src/reporting.py`: relatório executivo e exportações.

## Convenções de mudança
- Priorizar mudanças incrementais e compatíveis com funções existentes.
- Evitar quebrar assinaturas sem necessidade.
- Separar responsabilidades por módulo.
- Manter nomenclatura em português para métricas de negócio.

## Testes mínimos antes de concluir
- `python -m compileall app.py src`
- Teste manual rápido no Streamlit com pelo menos uma base `.XLS`.

## Done criteria
- App inicia sem erros.
- KPIs principais aparecem no topo.
- Qualidade da base é exibida.
- Comparação funciona com 2 arquivos.
- Previsão mostra métricas e baseline quando houver dados suficientes.
- Relatório e CSVs são gerados em `outputs/`.
