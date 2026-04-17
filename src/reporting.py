from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd


OUTPUT_DIR = Path("outputs")


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def save_dataframe(df: pd.DataFrame, filename: str) -> Path:
    out = ensure_output_dir() / filename
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def generate_executive_insights(
    kpis: Dict[str, float],
    monthly: pd.DataFrame,
    top_products: pd.DataFrame,
    top_clients: pd.DataFrame,
    outlier_rate: float,
) -> str:
    trend = "estável"
    if len(monthly) >= 2:
        delta = monthly["faturamento"].iloc[-1] - monthly["faturamento"].iloc[0]
        trend = "crescimento" if delta > 0 else "queda"

    product = top_products.iloc[0]["cod_produto"] if len(top_products) else "N/A"
    client = top_clients.iloc[0]["cod_cliente"] if len(top_clients) else "N/A"

    text = f"""
# Relatório Executivo de Vendas

## Resumo
- Faturamento total no período: R$ {kpis['faturamento_total']:,.2f}
- Quantidade total vendida: {kpis['quantidade_total']:,.0f}
- Ticket médio por registro: R$ {kpis['ticket_medio']:,.2f}
- Margem percentual média: {kpis['margem_media_percentual']:.2f}%

## Insights automáticos
1. A tendência geral de faturamento no período analisado indica **{trend}**.
2. O produto de maior faturamento foi **{product}**.
3. O cliente de maior faturamento foi **{client}**.
4. A taxa de anomalias identificadas é de **{outlier_rate:.2f}%** das linhas analisadas.
5. Priorize ações comerciais em produtos de alta margem e revise precificação de produtos em baixa margem.

## Recomendações
- Reforçar campanhas para clientes com alto potencial de margem.
- Criar plano de ação para itens com margem baixa recorrente.
- Monitorar semanalmente outliers para detectar erros de cadastro, preço e quantidade.
""".strip()
    return text


def save_report(text: str, filename: str = "relatorio_executivo.md") -> Path:
    out = ensure_output_dir() / filename
    out.write_text(text, encoding="utf-8")
    return out
