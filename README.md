# Projeto de Análise Inteligente de Vendas (.XLS)

Aplicação em Python + Streamlit para analisar planilhas históricas de vendas em `.XLS`, com foco em valor de negócio, IA aplicada e comparação de períodos equivalentes.

## ✅ O que a solução faz

- Lê arquivos `.XLS` com `xlrd`
- Valida as colunas obrigatórias do layout
- Trata datas BR, tipos, ausências e inconsistências
- Cria métricas derivadas (faturamento, custo, margem e calendário)
- Permite analisar **uma planilha** ou **comparar duas planilhas**
- Compara períodos equivalentes em dias (não por quantidade de linhas)
- Gera análises de movimentação de produtos:
  - crescimento/queda em volume e faturamento
  - produtos novos, ausentes e recorrentes
  - variação percentual de quantidade/faturamento/margem
  - mudança de ranking
  - estabilidade x instabilidade
  - frequência de venda
  - concentração dos principais itens
- Mantém e amplia ML:
  - clusterização de clientes
  - agrupamento de produtos por comportamento
  - detecção de anomalias
  - previsão de faturamento semanal/mensal
- Exibe tudo via Streamlit com filtros, KPIs, gráficos e tabelas
- Salva CSVs, gráficos e relatório executivo em `/outputs`

## Estrutura do projeto

```bash
hub_erp/
├── app.py
├── requirements.txt
├── README.md
├── outputs/
└── src/
    ├── __init__.py
    ├── data_processing.py
    ├── analytics.py
    ├── comparison.py
    ├── ml_models.py
    └── reporting.py
```

## Colunas esperadas na entrada

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

## Fluxo de uso

1. Upload da **Base A** (obrigatória)
2. Upload da **Base B** (opcional, para comparação)
3. Escolha de períodos e filtros por dimensão
4. Visualização de:
   - visão geral da Base A
   - modelos de ML
   - comparação de períodos equivalentes (se Base B existir)
   - movimentação de produtos
   - relatório executivo automático

## Saídas em `/outputs`

Exemplos de saídas geradas:

- `base_a_faturamento_mes.png`
- `base_a_previsao_faturamento.png` (quando houver dados)
- `base_a_faturamento_mensal.csv`
- `base_a_faturamento_por_produto.csv`
- `base_a_clusters_clientes.csv`
- `base_a_clusters_produtos.csv`
- `comparacao_cod_produto.csv` (se houver Base B)
- `comparacao_movimentacao_produtos.csv` (se houver Base B)
- `concentracao_produtos_base_a.csv`
- `concentracao_produtos_base_b.csv` (se houver Base B)
- `relatorio_executivo.md`

## Observações técnicas

- A comparação é feita por **janelas equivalentes em dias**, com recorte automático para evitar vieses por períodos desiguais.
- Modelos mantidos simples e explicáveis para facilitar adoção no negócio.
- Recomenda-se validar os resultados com amostras reais antes de decisões críticas.
