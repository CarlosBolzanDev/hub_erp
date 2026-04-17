# Projeto de Análise Inteligente de Vendas (.XLS)

Aplicação Python + Streamlit para análise executiva de vendas em `.XLS`, com foco em **qualidade da base**, **margem**, **concentração**, **comparação entre períodos equivalentes** e **recomendações acionáveis**.

## Principais melhorias (versão atual)

- KPIs mais confiáveis:
  - ticket por pedido (NFE) e ticket por linha;
  - margem calculada separando custos válidos, ausentes e inconsistentes.
- Bloco de qualidade da base:
  - linhas de entrada, válidas, removidas,
  - custos ausentes/inconsistentes,
  - quantidades/preços negativos removidos.
- Indicadores de concentração:
  - participação dos top 10 produtos/clientes/vendedores.
- Tomada de decisão:
  - insights automáticos de negócio,
  - ações recomendadas priorizadas,
  - ABC/Pareto para produtos e clientes.
- Comparação entre períodos mais completa:
  - união de itens relevantes (não apenas top 10),
  - novos/ausentes/recorrentes,
  - deltas de faturamento/quantidade/margem,
  - mudança de ranking, frequência e estabilidade.
- Previsão com avaliação melhor:
  - métricas do modelo linear (MAE, RMSE, MAPE, R²),
  - baseline simples (último valor) para comparação,
  - mensagem mais útil quando há poucos dados.

## Estrutura

```bash
hub_erp/
├── app.py
├── requirements.txt
├── README.md
├── AGENTS.md
├── outputs/
└── src/
    ├── __init__.py
    ├── data_processing.py
    ├── analytics.py
    ├── comparison.py
    ├── ml_models.py
    └── reporting.py
```

## Colunas esperadas

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

> O validador é tolerante a variações de caixa/espaçamento/acentuação nos nomes dessas colunas.

## Execução local

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
streamlit run app.py
```

## Fluxo de uso

1. Upload da **Base A** (`.XLS`) obrigatório.
2. Upload opcional da **Base B** (`.XLS`) para comparação.
3. Escolha de período e filtros na sidebar.
4. Navegação por blocos:
   - Visão geral
   - Insights e alertas
   - Produtos
   - Clientes
   - Vendedores
   - Comparação
   - ML / previsão
   - Relatório e exportação

## Saídas em `/outputs`

Exemplos:
- `base_a_faturamento_mes.png`
- `base_a_previsao_faturamento.png`
- `base_a_faturamento_mensal.csv`
- `base_a_faturamento_por_produto.csv`
- `base_a_clusters_clientes.csv`
- `base_a_clusters_produtos.csv`
- `acoes_recomendadas.csv`
- `comparacao_cod_produto.csv` (se houver Base B)
- `comparacao_movimentacao_produtos.csv` (se houver Base B)
- `relatorio_executivo.md`

## Observações

- A comparação entre bases usa períodos equivalentes em dias para reduzir viés.
- Modelos foram mantidos simples e explicáveis para adoção no negócio.
- Recomenda-se validação com dados reais antes de decisões críticas de preço/estoque.
