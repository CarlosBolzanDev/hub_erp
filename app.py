from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.analytics import aggregate_revenue, compute_kpis, margin_analysis, monthly_revenue, payment_usage
from src.comparison import (
    analyze_product_movement,
    compare_dimension,
    compare_kpis,
    sales_concentration,
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
    product_relevance_rank,
)
from src.reporting import ensure_output_dir, generate_executive_insights, save_dataframe, save_report

st.set_page_config(page_title="Análise Inteligente de Vendas", layout="wide")
st.title("📊 Análise Inteligente de Vendas Históricas")
st.write("Upload de 1 ou 2 planilhas .XLS para análise detalhada e comparação de períodos equivalentes.")


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

    df, quality = clean_and_enrich(raw_df)
    if df.empty:
        st.warning(f"[{tag}] Sem linhas válidas após limpeza.")
        return None, None

    return df, quality


def apply_dimension_filters(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    data = df.copy()
    for col, label in [
        ("empresa", "Empresa"),
        ("cod_vendedor", "Vendedor"),
        ("cod_cliente", "Cliente"),
        ("cod_produto", "Produto"),
        ("forma_pagto", "Forma de pagamento"),
    ]:
        options = sorted([x for x in data[col].dropna().unique().tolist()])
        selected = st.sidebar.multiselect(f"{label} {prefix}".strip(), options)
        if selected:
            data = data[data[col].isin(selected)]
    return data


uploaded_a = st.file_uploader("Upload planilha principal (.XLS)", type=["xls"], key="base_a")
uploaded_b = st.file_uploader("Upload planilha para comparação (.XLS) - opcional", type=["xls"], key="base_b")

if uploaded_a:
    df_a, quality_a = process_file(uploaded_a, "Base A")
    if df_a is None:
        st.stop()

    min_a, max_a = date_range(df_a)
    st.sidebar.header("Filtros")

    start_a, end_a = st.sidebar.date_input(
        "Período Base A",
        value=(min_a.date(), max_a.date()),
        min_value=min_a.date(),
        max_value=max_a.date(),
    )

    base_a = filter_by_period(df_a, pd.Timestamp(start_a), pd.Timestamp(end_a))
    base_a = apply_dimension_filters(base_a, "(Base A)")
    if base_a.empty:
        st.warning("Nenhum dado na Base A após filtros.")
        st.stop()

    has_comparison = uploaded_b is not None
    if has_comparison:
        df_b, quality_b = process_file(uploaded_b, "Base B")
        if df_b is None:
            st.stop()

        min_b, max_b = date_range(df_b)
        start_b, end_b = st.sidebar.date_input(
            "Período Base B",
            value=(min_b.date(), max_b.date()),
            min_value=min_b.date(),
            max_value=max_b.date(),
        )
        base_b = filter_by_period(df_b, pd.Timestamp(start_b), pd.Timestamp(end_b))
        base_b = apply_dimension_filters(base_b, "(Base B)")

        base_a_eq, base_b_eq, eq_info = align_equivalent_periods(
            base_a,
            base_b,
            pd.Timestamp(start_a),
            pd.Timestamp(end_a),
            pd.Timestamp(start_b),
            pd.Timestamp(end_b),
        )

        if base_a_eq.empty or base_b_eq.empty:
            st.warning("Não foi possível formar períodos equivalentes com dados válidos nas duas bases.")
            has_comparison = False
        else:
            st.sidebar.success(
                f"Comparação equivalente: {eq_info['dias_comparados']} dias (A: {eq_info['dias_a']} dias, B: {eq_info['dias_b']} dias)"
            )
    else:
        base_b_eq = pd.DataFrame()

    out_dir = ensure_output_dir()

    # ============================
    # Análise da base principal
    # ============================
    st.header("1) Visão geral da base principal")
    kpis = compute_kpis(base_a)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento total", f"R$ {kpis['faturamento_total']:,.2f}")
    col2.metric("Quantidade total", f"{kpis['quantidade_total']:,.0f}")
    col3.metric("Ticket médio", f"R$ {kpis['ticket_medio']:,.2f}")
    col4.metric("Margem média", f"{kpis['margem_media_percentual']:.2f}%")

    monthly = monthly_revenue(base_a)
    top_products = aggregate_revenue(base_a, "cod_produto")
    top_clients = aggregate_revenue(base_a, "cod_cliente")
    top_vendors = aggregate_revenue(base_a, "cod_vendedor")
    top_companies = aggregate_revenue(base_a, "empresa")
    payments = payment_usage(base_a)

    g1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=monthly, x="mes_ref", y="faturamento", marker="o", ax=ax1)
    ax1.set_title("Faturamento por mês - Base A")
    ax1.tick_params(axis="x", rotation=45)
    st.pyplot(g1)
    g1.savefig(out_dir / "base_a_faturamento_mes.png", bbox_inches="tight")

    t1, t2, t3, t4 = st.tabs(["Produtos", "Clientes", "Vendedores", "Empresas"])
    with t1:
        st.dataframe(top_products, use_container_width=True)
    with t2:
        st.dataframe(top_clients, use_container_width=True)
    with t3:
        st.dataframe(top_vendors, use_container_width=True)
    with t4:
        st.dataframe(top_companies, use_container_width=True)

    st.subheader("Formas de pagamento")
    st.dataframe(payments, use_container_width=True)

    st.subheader("Análise de margem")
    tabs_m = st.tabs(["Produto", "Cliente", "Vendedor", "Empresa"])
    margin_tables = [
        margin_analysis(base_a, "cod_produto"),
        margin_analysis(base_a, "cod_cliente"),
        margin_analysis(base_a, "cod_vendedor"),
        margin_analysis(base_a, "empresa"),
    ]
    for tab, table in zip(tabs_m, margin_tables):
        with tab:
            st.dataframe(table, use_container_width=True)

    # ============================
    # ML
    # ============================
    st.header("2) Aprendizado de máquina")
    cluster_clients = customer_clustering(base_a)
    outlier_df = detect_outliers(base_a)
    outlier_rate = outlier_df["outlier"].mean() * 100
    cluster_products = product_behavior_clustering(base_a)

    st.markdown("**Clusterização de clientes**")
    st.dataframe(cluster_clients.head(30), use_container_width=True)

    st.markdown("**Agrupamento de produtos por comportamento**")
    st.dataframe(cluster_products.head(30), use_container_width=True)

    st.markdown("**Anomalias**")
    st.write(f"Taxa de outliers na Base A: {outlier_rate:.2f}%")
    st.dataframe(
        outlier_df[outlier_df["outlier"] == 1][
            ["nfe", "data_emissao", "cod_cliente", "cod_produto", "qtde", "faturamento", "margem_bruta"]
        ].head(50),
        use_container_width=True,
    )

    freq = st.selectbox("Frequência de previsão", ["Mensal", "Semanal"], index=0)
    horizon = st.slider("Horizonte de previsão", min_value=1, max_value=12, value=3)
    forecast = forecast_revenue(base_a, frequency=freq, periods_ahead=horizon)

    st.markdown("**Previsão de faturamento (Regressão Linear)**")
    if forecast.forecast.empty:
        st.info("Dados insuficientes para previsão (mínimo de 4 períodos).")
    else:
        g2, ax2 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=forecast.history, x="periodo", y="y", marker="o", label="Histórico", ax=ax2)
        sns.lineplot(data=forecast.forecast, x="periodo", y="forecast", marker="o", label="Previsão", ax=ax2)
        st.pyplot(g2)
        g2.savefig(out_dir / "base_a_previsao_faturamento.png", bbox_inches="tight")
        st.write({k: round(v, 4) for k, v in forecast.metrics.items()})

    high_margin, low_margin = high_low_margin_products(base_a)
    relevance = product_relevance_rank(base_a)
    st.markdown("**Produtos de alta margem**")
    st.dataframe(high_margin.head(20), use_container_width=True)
    st.markdown("**Produtos de baixa margem**")
    st.dataframe(low_margin.head(20), use_container_width=True)
    st.markdown("**Ranking de relevância**")
    st.dataframe(relevance.head(30), use_container_width=True)

    # ============================
    # Comparação entre períodos
    # ============================
    comparison_kpi_df = pd.DataFrame()
    if has_comparison:
        st.header("3) Comparação entre períodos equivalentes")

        comparison_kpi_df = compare_kpis(base_a_eq, base_b_eq, "Base A", "Base B")
        st.subheader("KPIs comparativos")
        st.dataframe(comparison_kpi_df, use_container_width=True)

        dim_tabs = st.tabs(["Produtos", "Clientes", "Vendedores", "Empresas", "Pagamento"])
        dims = ["cod_produto", "cod_cliente", "cod_vendedor", "empresa", "forma_pagto"]
        for tab, dim in zip(dim_tabs, dims):
            with tab:
                comp_dim = compare_dimension(base_a_eq, base_b_eq, dim)
                st.dataframe(comp_dim.head(30), use_container_width=True)
                save_dataframe(comp_dim, f"comparacao_{dim}.csv")

        movement = analyze_product_movement(base_a_eq, base_b_eq)
        movement_summary = summarize_product_movement(movement)

        st.header("4) Movimentação dos produtos")
        mov_tabs = st.tabs(
            [
                "Mais cresceram em volume",
                "Mais cresceram em faturamento",
                "Maior queda",
                "Novos",
                "Ausentes",
                "Recorrentes",
            ]
        )
        for tab, key in zip(
            mov_tabs,
            ["crescimento_volume", "crescimento_faturamento", "maior_queda", "novos", "ausentes", "recorrentes"],
        ):
            with tab:
                st.dataframe(movement_summary[key], use_container_width=True)

        st.subheader("Mudança de ranking, estabilidade e frequência")
        st.dataframe(
            movement[
                [
                    "cod_produto",
                    "status_produto",
                    "delta_qtde",
                    "delta_faturamento",
                    "delta_margem",
                    "delta_qtde_pct",
                    "delta_faturamento_pct",
                    "delta_margem_pct",
                    "mudanca_ranking",
                    "comportamento",
                    "freq_venda_a",
                    "freq_venda_b",
                ]
            ].head(100),
            use_container_width=True,
        )

        conc_a, share_a = sales_concentration(base_a_eq)
        conc_b, share_b = sales_concentration(base_b_eq)
        st.write(f"Concentração (Top 10 produtos) - Base A: {share_a:.2f}% | Base B: {share_b:.2f}%")

        save_dataframe(movement, "comparacao_movimentacao_produtos.csv")
        save_dataframe(conc_a, "concentracao_produtos_base_a.csv")
        save_dataframe(conc_b, "concentracao_produtos_base_b.csv")

    # ============================
    # Relatório e exports
    # ============================
    report_text = generate_executive_insights(
        kpis=kpis,
        monthly=monthly,
        top_products=top_products,
        top_clients=top_clients,
        outlier_rate=outlier_rate,
        comparison_kpis=comparison_kpi_df if has_comparison else None,
    )
    st.header("5) Insights automáticos e relatório")
    st.markdown(report_text)

    save_dataframe(monthly, "base_a_faturamento_mensal.csv")
    save_dataframe(top_products, "base_a_faturamento_por_produto.csv")
    save_dataframe(top_clients, "base_a_faturamento_por_cliente.csv")
    save_dataframe(top_vendors, "base_a_faturamento_por_vendedor.csv")
    save_dataframe(top_companies, "base_a_faturamento_por_empresa.csv")
    save_dataframe(payments, "base_a_formas_pagamento.csv")
    save_dataframe(cluster_clients, "base_a_clusters_clientes.csv")
    save_dataframe(cluster_products, "base_a_clusters_produtos.csv")
    save_dataframe(outlier_df, "base_a_anomalias.csv")
    save_dataframe(relevance, "base_a_ranking_relevancia_produtos.csv")
    save_report(report_text, "relatorio_executivo.md")

    st.success(f"Arquivos exportados em: {Path(out_dir).resolve()}")
    st.caption(f"Qualidade Base A: {quality_a}")
    if has_comparison:
        st.caption(f"Qualidade Base B: {quality_b}")
else:
    st.info("Aguardando upload da planilha principal (.XLS)")
