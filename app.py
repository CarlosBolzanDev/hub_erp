from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.analytics import (
    abc_pareto,
    aggregate_revenue,
    compute_kpis,
    concentration_share,
    monthly_revenue,
    payment_usage,
)
from src.comparison import (
    analyze_product_movement,
    compare_dimension,
    compare_kpis,
    summarize_product_movement,
)
from src.data_processing import (
    align_equivalent_periods,
    clean_and_enrich,
    date_range,
    filter_by_period,
    load_xls,
    validate_columns,
)
from src.ml_models import (
    customer_clustering,
    detect_outliers,
    forecast_revenue,
    high_low_margin_products,
    product_behavior_clustering,
)
from src.reporting import build_action_recommendations, ensure_output_dir, generate_executive_insights, save_dataframe, save_report

st.set_page_config(page_title="Análise Executiva de Vendas", layout="wide")
st.title("📈 Painel Executivo de Vendas (.XLS)")
st.caption("Foco em decisões acionáveis: qualidade de dados, margem, concentração, comparação e recomendações.")


def _to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def process_file(uploaded_file, tag: str):
    if uploaded_file is None:
        return None, None

    try:
        raw_df = load_xls(uploaded_file)
    except Exception as exc:
        st.error(f"[{tag}] Erro ao ler arquivo .XLS: {exc}")
        return None, None

    validation = validate_columns(raw_df)
    if not validation.is_valid:
        st.error(f"[{tag}] Colunas ausentes: {validation.missing_columns}")
        return None, None

    df, quality = clean_and_enrich(raw_df, mapping=validation.mapping)
    if df.empty:
        st.warning(f"[{tag}] Sem linhas válidas após limpeza.")
        return None, None

    return df, quality


def apply_filters(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    data = df.copy()
    for col, label in [
        ("empresa", "Empresa"),
        ("cod_vendedor", "Vendedor"),
        ("cod_cliente", "Cliente"),
        ("cod_produto", "Produto"),
        ("forma_pagto", "Forma pagamento"),
    ]:
        options = sorted([x for x in data[col].dropna().unique().tolist()])
        selected = st.sidebar.multiselect(f"{label} {prefix}", options)
        if selected:
            data = data[data[col].isin(selected)]
    return data


def plot_bar(data: pd.DataFrame, x: str, y: str, title: str, color: str = "#1f77b4"):
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=data, x=x, y=y, color=color, ax=ax)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)
    return fig


st.sidebar.header("⚙️ Configurações")
uploaded_a = st.sidebar.file_uploader("Base A (.XLS)", type=["xls"], key="base_a")
uploaded_b = st.sidebar.file_uploader("Base B para comparação (.XLS)", type=["xls"], key="base_b")

if not uploaded_a:
    st.info("Carregue a Base A na barra lateral para iniciar.")
    st.stop()

df_a, quality_a = process_file(uploaded_a, "Base A")
if df_a is None:
    st.stop()

min_a, max_a = date_range(df_a)
period_a = st.sidebar.date_input(
    "Período Base A",
    value=(min_a.date(), max_a.date()),
    min_value=min_a.date(),
    max_value=max_a.date(),
)

base_a = filter_by_period(df_a, pd.Timestamp(period_a[0]), pd.Timestamp(period_a[1]))
base_a = apply_filters(base_a, "(A)")
if base_a.empty:
    st.warning("Base A ficou sem dados após filtros.")
    st.stop()

has_comparison = uploaded_b is not None
base_b_eq = pd.DataFrame()
quality_b = None
eq_info = {"dias_a": 0, "dias_b": 0, "dias_comparados": 0}

if has_comparison:
    df_b, quality_b = process_file(uploaded_b, "Base B")
    if df_b is None:
        st.stop()

    min_b, max_b = date_range(df_b)
    period_b = st.sidebar.date_input(
        "Período Base B",
        value=(min_b.date(), max_b.date()),
        min_value=min_b.date(),
        max_value=max_b.date(),
    )
    base_b = filter_by_period(df_b, pd.Timestamp(period_b[0]), pd.Timestamp(period_b[1]))
    base_b = apply_filters(base_b, "(B)")

    base_a_eq, base_b_eq, eq_info = align_equivalent_periods(
        base_a,
        base_b,
        pd.Timestamp(period_a[0]),
        pd.Timestamp(period_a[1]),
        pd.Timestamp(period_b[0]),
        pd.Timestamp(period_b[1]),
    )
    if base_a_eq.empty or base_b_eq.empty:
        st.warning("Não foi possível gerar períodos equivalentes com dados suficientes.")
        has_comparison = False

out_dir = ensure_output_dir()

# ===== Visão Geral =====
st.header("1) Visão geral")
kpis = compute_kpis(base_a)
share_prod = concentration_share(base_a, "cod_produto", top_n=10)
share_cli = concentration_share(base_a, "cod_cliente", top_n=10)
share_ven = concentration_share(base_a, "cod_vendedor", top_n=10)

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Faturamento", f"R$ {kpis['faturamento_total']:,.0f}")
k2.metric("Qtd vendida", f"{kpis['quantidade_total']:,.0f}")
k3.metric("Ticket por pedido", f"R$ {kpis['ticket_medio_nfe']:,.2f}")
k4.metric("Ticket por linha", f"R$ {kpis['ticket_medio_linha']:,.2f}")
k5.metric("Margem média", f"{kpis['margem_media_percentual']:.2f}%")
k6.metric("Pedidos únicos", f"{kpis['pedidos_unicos']:.0f}")

c1, c2, c3 = st.columns(3)
c1.metric("Concentração Top10 Produtos", f"{share_prod:.1f}%")
c2.metric("Concentração Top10 Clientes", f"{share_cli:.1f}%")
c3.metric("Concentração Top10 Vendedores", f"{share_ven:.1f}%")

with st.expander("Qualidade da base", expanded=True):
    q1, q2, q3, q4, q5, q6 = st.columns(6)
    q1.metric("Linhas entrada", quality_a["linhas_entrada"])
    q2.metric("Linhas válidas", quality_a["linhas_validas"])
    q3.metric("Linhas removidas", quality_a["linhas_removidas"])
    q4.metric("Custos ausentes", quality_a["custos_ausentes"])
    q5.metric("Custos inconsistentes", quality_a["custos_inconsistentes"])
    q6.metric("Qtd/preço negativos", quality_a["qtde_negativa_removida"] + quality_a["preco_negativo_removido"])

monthly = monthly_revenue(base_a)
fig_month, ax_month = plt.subplots(figsize=(10, 4))
sns.lineplot(data=monthly, x="mes_ref", y="faturamento", marker="o", color="#1f77b4", ax=ax_month)
ax_month.set_title("Evolução do faturamento")
ax_month.tick_params(axis="x", rotation=45)
st.pyplot(fig_month)
fig_month.savefig(out_dir / "base_a_faturamento_mes.png", bbox_inches="tight")

# ===== Insights e alertas =====
st.header("2) Insights e alertas")
products_full = aggregate_revenue(base_a, "cod_produto", top_n=None)
clients_full = aggregate_revenue(base_a, "cod_cliente", top_n=None)
vendors_full = aggregate_revenue(base_a, "cod_vendedor", top_n=None)

alerts = []
high_rev_low_margin = products_full[(products_full["faturamento"] > products_full["faturamento"].median()) & (products_full["margem_bruta"] < 0)]
if not high_rev_low_margin.empty:
    p = high_rev_low_margin.iloc[0]
    alerts.append(f"🔴 Produto {p['cod_produto']} com alto faturamento e margem negativa: revisar preço/custo.")

if has_comparison:
    comp_clients = compare_dimension(base_a_eq, base_b_eq, "cod_cliente")
    drop_clients = comp_clients[comp_clients["delta_faturamento_pct"] < -30].sort_values("delta_faturamento_pct")
    if not drop_clients.empty:
        c = drop_clients.iloc[0]
        alerts.append(f"🟠 Cliente {c['cod_cliente']} em queda forte ({c['delta_faturamento_pct']:.1f}%): ação de retenção.")

low_ticket_high_volume_vendor = vendors_full.copy()
low_ticket_high_volume_vendor["ticket"] = low_ticket_high_volume_vendor["faturamento"] / low_ticket_high_volume_vendor["pedidos"].replace(0, 1)
low_ticket_high_volume_vendor = low_ticket_high_volume_vendor.sort_values(["ticket", "qtde"], ascending=[True, False])
if not low_ticket_high_volume_vendor.empty:
    v = low_ticket_high_volume_vendor.iloc[0]
    alerts.append(f"🟡 Vendedor {v['cod_vendedor']} com ticket baixo e volume alto: revisar mix comercial.")

for a in alerts[:6]:
    st.markdown(a)

movement = pd.DataFrame()
if has_comparison:
    movement = analyze_product_movement(base_a_eq, base_b_eq)

recs = build_action_recommendations(products_full, clients_full, vendors_full, movement_table=movement if has_comparison else None)
st.subheader("Ações recomendadas (priorizadas)")
st.dataframe(recs, use_container_width=True)

# ===== Produtos =====
st.header("3) Produtos")
top_products = aggregate_revenue(base_a, "cod_produto", top_n=15)
plot_bar(top_products, "cod_produto", "faturamento", "Top produtos por faturamento", color="#4CAF50")

abc_prod = abc_pareto(base_a, "cod_produto")
st.subheader("ABC/Pareto de produtos")
st.dataframe(abc_prod.head(30), use_container_width=True)

high_margin, low_margin = high_low_margin_products(base_a)
with st.expander("Produtos com margem crítica e oportunidades"):
    cma, cmb = st.columns(2)
    with cma:
        st.write("Alta margem")
        st.dataframe(high_margin.head(15), use_container_width=True)
    with cmb:
        st.write("Baixa margem")
        st.dataframe(low_margin.head(15), use_container_width=True)

# ===== Clientes =====
st.header("4) Clientes")
top_clients = aggregate_revenue(base_a, "cod_cliente", top_n=15)
plot_bar(top_clients, "cod_cliente", "faturamento", "Top clientes por faturamento", color="#2196F3")

abc_cli = abc_pareto(base_a, "cod_cliente")
st.subheader("ABC/Pareto de clientes")
st.dataframe(abc_cli.head(30), use_container_width=True)

# ===== Vendedores =====
st.header("5) Vendedores")
top_vendors = aggregate_revenue(base_a, "cod_vendedor", top_n=15)
plot_bar(top_vendors, "cod_vendedor", "faturamento", "Top vendedores por faturamento", color="#FF9800")

# ===== Comparação =====
comparison_kpi_df = pd.DataFrame()
if has_comparison:
    st.header("6) Comparação")
    st.info(
        f"Comparação com períodos equivalentes: {eq_info['dias_comparados']} dias (A={eq_info['dias_a']} / B={eq_info['dias_b']})."
    )

    comparison_kpi_df = compare_kpis(base_a_eq, base_b_eq, "Base A", "Base B")
    st.dataframe(comparison_kpi_df, use_container_width=True)

    with st.expander("Comparação por dimensão (união de itens relevantes)", expanded=False):
        for dim in ["cod_produto", "cod_cliente", "cod_vendedor", "empresa", "forma_pagto"]:
            st.markdown(f"**{dim}**")
            comp = compare_dimension(base_a_eq, base_b_eq, dim)
            st.dataframe(comp.head(50), use_container_width=True)
            save_dataframe(comp, f"comparacao_{dim}.csv")

    st.subheader("Movimentação de produtos")
    movement_summary = summarize_product_movement(movement)
    tabs = st.tabs(["Altas", "Quedas", "Novos", "Ausentes", "Recorrentes"])
    with tabs[0]:
        st.dataframe(movement_summary["crescimento_faturamento"], use_container_width=True)
    with tabs[1]:
        st.dataframe(movement_summary["maior_queda"], use_container_width=True)
    with tabs[2]:
        st.dataframe(movement_summary["novos"], use_container_width=True)
    with tabs[3]:
        st.dataframe(movement_summary["ausentes"], use_container_width=True)
    with tabs[4]:
        st.dataframe(movement_summary["recorrentes"], use_container_width=True)

    st.dataframe(
        movement[
            [
                "cod_produto",
                "status_produto",
                "delta_faturamento",
                "delta_faturamento_pct",
                "delta_qtde",
                "delta_qtde_pct",
                "delta_margem",
                "mudanca_ranking",
                "comportamento",
                "freq_venda_a",
                "freq_venda_b",
                "estabilidade_a",
                "estabilidade_b",
            ]
        ].head(80),
        use_container_width=True,
    )

# ===== ML / Previsão =====
st.header("7) ML / previsão")
cluster_clients = customer_clustering(base_a)
cluster_products = product_behavior_clustering(base_a)
outlier_df = detect_outliers(base_a)
outlier_rate = outlier_df["outlier"].mean() * 100

m1, m2, m3 = st.columns(3)
m1.metric("Outliers", f"{outlier_rate:.2f}%")
m2.metric("Clusters clientes", int(cluster_clients["cluster"].nunique()) if not cluster_clients.empty else 0)
m3.metric("Clusters produtos", int(cluster_products["cluster_produto"].nunique()) if not cluster_products.empty else 0)

with st.expander("Detalhes de clusterização", expanded=False):
    st.write("Clientes")
    st.dataframe(cluster_clients.head(30), use_container_width=True)
    st.write("Produtos")
    st.dataframe(cluster_products.head(30), use_container_width=True)

freq = st.selectbox("Frequência da previsão", ["Mensal", "Semanal"], index=0)
horizon = st.slider("Períodos à frente", min_value=1, max_value=12, value=3)
forecast = forecast_revenue(base_a, frequency=freq, periods_ahead=horizon)

if forecast.forecast.empty:
    st.warning(forecast.message)
else:
    fig_fc, ax_fc = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=forecast.history, x="periodo", y="y", marker="o", label="Histórico", color="#1f77b4", ax=ax_fc)
    sns.lineplot(data=forecast.forecast, x="periodo", y="forecast", marker="o", label="Previsão", color="#2e7d32", ax=ax_fc)
    st.pyplot(fig_fc)
    fig_fc.savefig(out_dir / "base_a_previsao_faturamento.png", bbox_inches="tight")

    st.caption(forecast.message)
    cmod, cbase = st.columns(2)
    cmod.write("**Métricas modelo linear**")
    cmod.json({k: round(v, 4) for k, v in forecast.metrics.items()})
    cbase.write("**Métricas baseline (último valor)**")
    cbase.json({k: round(v, 4) for k, v in forecast.baseline_metrics.items()})

# ===== Relatório e exportação =====
st.header("8) Relatório e exportação")
report_text = generate_executive_insights(
    kpis=kpis,
    monthly=monthly,
    top_products=top_products,
    top_clients=top_clients,
    outlier_rate=outlier_rate,
    comparison_kpis=comparison_kpi_df if has_comparison else None,
    recommendations=recs,
)
st.markdown(report_text)

save_dataframe(monthly, "base_a_faturamento_mensal.csv")
save_dataframe(top_products, "base_a_faturamento_por_produto.csv")
save_dataframe(top_clients, "base_a_faturamento_por_cliente.csv")
save_dataframe(top_vendors, "base_a_faturamento_por_vendedor.csv")
save_dataframe(payment_usage(base_a), "base_a_formas_pagamento.csv")
save_dataframe(cluster_clients, "base_a_clusters_clientes.csv")
save_dataframe(cluster_products, "base_a_clusters_produtos.csv")
save_dataframe(outlier_df, "base_a_anomalias.csv")
save_dataframe(recs, "acoes_recomendadas.csv")
if has_comparison and not movement.empty:
    save_dataframe(movement, "comparacao_movimentacao_produtos.csv")

save_report(report_text, "relatorio_executivo.md")

b1, b2 = st.columns(2)
with b1:
    st.download_button(
        "⬇️ Baixar ações recomendadas (CSV)",
        data=_to_csv_bytes(recs),
        file_name="acoes_recomendadas.csv",
        mime="text/csv",
    )
with b2:
    st.download_button(
        "⬇️ Baixar relatório executivo (MD)",
        data=report_text.encode("utf-8"),
        file_name="relatorio_executivo.md",
        mime="text/markdown",
    )

st.success(f"Arquivos salvos em: {Path(out_dir).resolve()}")
