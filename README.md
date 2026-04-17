# Projeto de Análise Inteligente de Vendas (.XLS)

Aplicação em Python + Streamlit para analisar planilhas de vendas históricas em formato `.XLS`, com foco em valor de negócio: KPIs, segmentações, anomalias, previsão e insights executivos automáticos.

## ✅ O que a solução faz

- Lê planilhas `.XLS` (engine `xlrd`)
- Valida colunas obrigatórias
- Faz tratamento de dados (datas BR, tipos numéricos, ausências e inconsistências)
- Cria métricas derivadas de faturamento, custo e margem
- Permite seleção dinâmica de período conforme dados carregados
- Gera análises descritivas e tabelas agregadas
- Executa modelos de ML simples e explicáveis:
  - Clusterização de clientes (KMeans)
  - Detecção de anomalias (Isolation Forest)
  - Previsão de faturamento semanal/mensal (Regressão Linear)
  - Ranking de relevância de produtos
  - Produtos de alta e baixa margem
- Exibe tudo em interface gráfica interativa (Streamlit)
- Salva gráficos, CSVs e relatório executivo em `/outputs`

## Estrutura do projeto

```bash
hub_erp/
├── app.py
├── requirements.txt
├── README.md
├── outputs/
└── src/
    ├── data_processing.py
    ├── analytics.py
    ├── ml_models.py
    └── reporting.py
```

## Colunas esperadas

A planilha deve conter exatamente estas colunas:

- NFE
- Data Emissão
- Data Vencimento
- Forma Pagto
- Código Interno Produto
- Qtde
- Preço Venda Unit
- Código Cliente
- Código Vendedor
- Custo Real
- Custo Médio
- Empresa

## Como executar localmente

### 1) Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

### 2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 3) Executar aplicação

```bash
streamlit run app.py
```

### 4) Uso na interface

1. Faça upload da planilha `.XLS`
2. Selecione período de análise (intervalo disponível no arquivo)
3. Aplique filtros por empresa, vendedor, cliente, produto e forma de pagamento
4. Analise KPIs, gráficos, tabelas e insights automáticos
5. Consulte arquivos gerados na pasta `/outputs`

## Saídas geradas em `/outputs`

- `faturamento_por_mes.png`
- `previsao_faturamento.png` (quando houver dados suficientes)
- `faturamento_mensal.csv`
- `faturamento_por_produto.csv`
- `faturamento_por_cliente.csv`
- `faturamento_por_vendedor.csv`
- `faturamento_por_empresa.csv`
- `formas_pagamento.csv`
- `clusters_clientes.csv`
- `anomalias.csv`
- `ranking_relevancia_produtos.csv`
- `relatorio_executivo.md`

## Observações de modelagem

- Modelos intencionalmente simples para melhor explicabilidade.
- Recomenda-se monitorar métricas de previsão (`MAE`, `RMSE`, `R²`) antes de usar para tomada de decisão crítica.
- Evite interpretações sem validação de qualidade da base.
