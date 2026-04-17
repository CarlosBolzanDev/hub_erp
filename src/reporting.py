from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd


OUTPUT_DIR = Path("outputs")


def ensure_output_dir() -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def save_dataframe(df: pd.DataFrame, filename: str) -> Path:
    out = ensure_output_dir() / filename
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return out


def build_action_recommendations(
    product_table: pd.DataFrame,
    client_table: pd.DataFrame,
    vendor_table: pd.DataFrame,
    movement_table: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    actions = []

    if not product_table.empty:
        risk_prod = product_table[(product_table["faturamento"] > product_table["faturamento"].median()) & (product_table["margem_bruta"] < 0)]
        if not risk_prod.empty:
            p = risk_prod.iloc[0]
            actions.append({
                "prioridade": "Alta",
                "categoria": "Produto em risco",
                "item": str(p[product_table.columns[0]]),
                "acao": "Revisar preço/custo do item com alto faturamento e margem negativa.",
                "impacto_estimado": float(abs(p["margem_bruta"])),
            })

    if not client_table.empty:
        low_margin_client = client_table.sort_values("margem_bruta", ascending=True).head(1)
        if not low_margin_client.empty:
            c = low_margin_client.iloc[0]
            actions.append({
                "prioridade": "Média",
                "categoria": "Cliente em risco",
                "item": str(c[client_table.columns[0]]),
                "acao": "Executar plano de retenção e revisar mix para recuperar margem do cliente.",
                "impacto_estimado": float(abs(c["margem_bruta"])),
            })

    if not vendor_table.empty:
        vendor_table = vendor_table.copy()
        vendor_table["ticket"] = vendor_table["faturamento"] / vendor_table["pedidos"].replace(0, 1)
        v = vendor_table.sort_values(["ticket", "qtde"], ascending=[True, False]).head(1)
        if not v.empty:
            row = v.iloc[0]
            actions.append({
                "prioridade": "Média",
                "categoria": "Eficiência comercial",
                "item": str(row[vendor_table.columns[0]]),
                "acao": "Revisar mix e estratégia de upsell para elevar ticket médio mantendo volume.",
                "impacto_estimado": float(row["faturamento"] * 0.03),
            })

    if movement_table is not None and not movement_table.empty:
        new_growth = movement_table[(movement_table["status_produto"] == "novo_no_periodo_b")].sort_values(
            "faturamento_b", ascending=False
        )
        if not new_growth.empty:
            n = new_growth.iloc[0]
            actions.append({
                "prioridade": "Alta",
                "categoria": "Oportunidade",
                "item": str(n["cod_produto"]),
                "acao": "Acompanhar produto novo com tração para acelerar distribuição e estoque.",
                "impacto_estimado": float(n["faturamento_b"]),
            })

    if not actions:
        return pd.DataFrame(columns=["prioridade", "categoria", "item", "acao", "impacto_estimado"])

    df = pd.DataFrame(actions)
    priority_order = {"Alta": 0, "Média": 1, "Baixa": 2}
    return df.sort_values(["prioridade", "impacto_estimado"], key=lambda s: s.map(priority_order).fillna(9) if s.name == "prioridade" else -s)


def generate_executive_insights(
    kpis: Dict[str, float],
    monthly: pd.DataFrame,
    top_products: pd.DataFrame,
    top_clients: pd.DataFrame,
    outlier_rate: float,
    comparison_kpis: Optional[pd.DataFrame] = None,
    recommendations: Optional[pd.DataFrame] = None,
) -> str:
    trend = "estável"
    if len(monthly) >= 2:
        delta = monthly["faturamento"].iloc[-1] - monthly["faturamento"].iloc[0]
        trend = "crescimento" if delta > 0 else "queda"

    product = top_products.iloc[0]["cod_produto"] if len(top_products) else "N/A"
    client = top_clients.iloc[0]["cod_cliente"] if len(top_clients) else "N/A"

    comp_section = ""
    if comparison_kpis is not None and not comparison_kpis.empty:
        best = comparison_kpis.sort_values("delta_abs", ascending=False).iloc[0]
        worst = comparison_kpis.sort_values("delta_abs", ascending=True).iloc[0]
        comp_section = (
            "\n## Comparação entre períodos\n"
            f"- Maior ganho absoluto: **{best['indicador']}** ({best['delta_abs']:,.2f}).\n"
            f"- Maior perda absoluta: **{worst['indicador']}** ({worst['delta_abs']:,.2f}).\n"
        )

    rec_section = ""
    if recommendations is not None and not recommendations.empty:
        lines = [f"- ({r['prioridade']}) {r['categoria']}: {r['acao']}" for _, r in recommendations.head(5).iterrows()]
        rec_section = "\n## Ações recomendadas (priorizadas)\n" + "\n".join(lines) + "\n"

    text = f"""
# Relatório Executivo de Vendas

## Resumo
- Faturamento total no período: R$ {kpis['faturamento_total']:,.2f}
- Quantidade total vendida: {kpis['quantidade_total']:,.0f}
- Ticket médio por pedido: R$ {kpis['ticket_medio_nfe']:,.2f}
- Ticket médio por linha: R$ {kpis['ticket_medio_linha']:,.2f}
- Margem percentual média (linhas com custo válido): {kpis['margem_media_percentual']:.2f}%

## Insights automáticos
1. A tendência geral de faturamento no período analisado indica **{trend}**.
2. O produto de maior faturamento foi **{product}**.
3. O cliente de maior faturamento foi **{client}**.
4. A taxa de anomalias identificadas é de **{outlier_rate:.2f}%** das linhas analisadas.
5. Foque em itens de alto volume com margem fraca para proteger rentabilidade.
{comp_section}
{rec_section}
## Recomendações gerais
- Reforçar campanhas para clientes com alto potencial de margem.
- Criar plano de ação para itens com margem baixa recorrente.
- Monitorar semanalmente outliers para detectar erros de cadastro, preço e quantidade.
""".strip()
    return text


def save_report(text: str, filename: str = "relatorio_executivo.md") -> Path:
    out = ensure_output_dir() / filename
    out.write_text(text, encoding="utf-8")
    return out
