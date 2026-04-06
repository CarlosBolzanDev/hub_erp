# Projeto: Análise Automática de Estoque, Compras e Vendas

Este projeto lê automaticamente arquivos Excel (`.xls`/`.xlsx`) de **vendas**, **produtos** e **estoque**, padroniza colunas com tolerância a variações (maiúsculas/minúsculas, acentos, espaços), cruza os dados e gera análises gerenciais em Excel + gráficos + painel Streamlit.

## Estrutura

```text
project/
  input/                # arquivos de entrada
  output/               # resultados (Excel + gráficos)
  src/
    analytics.py
    config_loader.py
    io_utils.py
    reporting.py
    sample_data.py
  main.py
  streamlit_app.py
  requirements.txt
  README.md
  config.yaml
```

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -r project/requirements.txt
```

## Como usar

1. Coloque os arquivos na pasta `project/input` com nomes que contenham palavras como:
   - Vendas: `vendas`, `mov`, `movimentacao`
   - Produtos: `produtos`, `cadastro`, `itens`
   - Estoque: `estoque`, `saldo`

2. Execute:

```bash
python project/main.py
```

3. Saída gerada em `project/output`:
   - `analise_estoque.xlsx`
   - `top_itens_saida.png`
   - `top_itens_risco.png`
   - `estoque_vs_ponto_pedido.png`

## Rodar demonstração com dados fictícios

```bash
python project/main.py --demo
```

Isso cria automaticamente:
- `project/input/Vendas.xlsx`
- `project/input/Produtos.xlsx`
- `project/input/Estoque.xlsx`

Depois gera as análises completas.

## Interface Streamlit (opcional)

```bash
streamlit run project/streamlit_app.py
```

## Regras de negócio implementadas

- Consumo médio diário, semanal e mensal
- Tendência (30/60/90 dias)
- Dias de cobertura de estoque
- Estoque mínimo sugerido
- Ponto de pedido
- Quantidade sugerida de compra
- Risco de ruptura
- Curva ABC/Pareto por giro
- Variação de custo e melhor fornecedor (quando dados disponíveis)
- Alertas de compra, baixa rotatividade e excesso de estoque

## Configuração

Ajuste `project/config.yaml` sem editar código:
- `input_dir`
- `output_dir`
- `safety_factor`
- janelas de análise e regras de alerta

## Tratamento de erros

- arquivo faltando: erro explicativo
- coluna obrigatória faltando: erro explicativo
- formato inconsistente: limpeza tolerante + fallback quando possível
