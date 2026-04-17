from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.analytics import aggregate_revenue, compute_kpis, margin_analysis, monthly_revenue, payment_usage
from src.data_processing import clean_and_enrich, date_range, filter_by_period, load_xls, validate_columns
from src.ml_models import (
    customer_clustering,
    detect_outliers,
    forecast_revenue,
    high_low_margin_products,
    product_relevance_rank,
)
from src.reporting import ensure_output_dir, generate_executive_insights, save_dataframe, save_report


st.set_page_config(page_title="Análise Inteligente de Vendas", layout="wide")
st.title("📊 Análise Inteligente de Vendas Históricas")
st.write("Faça upload de uma planilha .XLS para gerar métricas, modelos e insights automáticos.")

uploaded = st.file_uploader("Upload do arquivo .XLS", type=["xls"])

if uploaded:
    try:
        raw_df = load_xls(uploaded)
    except Exception as exc:
        st.error(f"Erro ao ler arquivo .XLS: {exc}")
        st.stop()

    validation = validate_columns(raw_df)
    if not validation.is_valid:
        st.error(f"Colunas ausentes: {validation.missing_columns}")
        st.stop()

    df, quality = clean_and_enrich(raw_df)
    if df.empty:
        st.warning("Após limpeza, não restaram linhas válidas para análise.")
        st.stop()

    min_d, max_d = date_range(df)
    st.sidebar.header("Filtros")
    start_date, end_date = st.sidebar.date_input(
        "Período de emissão",
        value=(min_d.date(), max_d.date()),
        min_value=min_d.date(),
        max_value=max_d.date(),
    )

    df_period = filter_by_period(df, pd.Timestamp(start_date), pd.Timestamp(end_date))

    for col, label in [
        ("empresa", "Empresa"),
        ("cod_vendedor", "Vendedor"),
        ("cod_cliente", "Cliente"),
        ("cod_produto", "Produto"),
        ("forma_pagto", "Forma de pagamento"),
    ]:
        opts = sorted([x for x in df_period[col].dropna().unique().tolist()])
        selected = st.sidebar.multiselect(label, opts)
        if selected:
            df_period = df_period[df_period[col].isin(selected)]

    if df_period.empty:
        st.warning("Nenhum dado para os filtros selecionados.")
        st.stop()

    out_dir = ensure_output_dir()

    kpis = compute_kpis(df_period)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento total", f"R$ {kpis['faturamento_total']:,.2f}")
    c2.metric("Quantidade total", f"{kpis['quantidade_total']:,.0f}")
    c3.metric("Ticket médio", f"R$ {kpis['ticket_medio']:,.2f}")
    c4.metric("Margem média", f"{kpis['margem_media_percentual']:.2f}%")

    monthly = monthly_revenue(df_period)
    top_products = aggregate_revenue(df_period, "cod_produto")
    top_clients = aggregate_revenue(df_period, "cod_cliente")
    top_vendors = aggregate_revenue(df_period, "cod_vendedor")
    top_companies = aggregate_revenue(df_period, "empresa")
    pay = payment_usage(df_period)

    st.subheader("Faturamento por mês")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=monthly, x="mes_ref", y="faturamento", marker="o", ax=ax1)
    ax1.tick_params(axis="x", rotation=45)
    ax1.set_xlabel("Mês")
    ax1.set_ylabel("Faturamento")
    st.pyplot(fig1)
    fig1.savefig(out_dir / "faturamento_por_mes.png", bbox_inches="tight")

    st.subheader("Top produtos por faturamento")
    st.dataframe(top_products, use_container_width=True)

    st.subheader("Top clientes por faturamento")
    st.dataframe(top_clients, use_container_width=True)

    st.subheader("Formas de pagamento")
    st.dataframe(pay, use_container_width=True)

    st.subheader("Análise de margem")
    m_prod = margin_analysis(df_period, "cod_produto")
    m_cli = margin_analysis(df_period, "cod_cliente")
    m_ven = margin_analysis(df_period, "cod_vendedor")
    m_emp = margin_analysis(df_period, "empresa")

    tabs = st.tabs(["Produto", "Cliente", "Vendedor", "Empresa"])
    for t, table in zip(tabs, [m_prod, m_cli, m_ven, m_emp]):
        with t:
            st.dataframe(table, use_container_width=True)

    st.subheader("Machine Learning")
    cluster_df = customer_clustering(df_period)
    outlier_df = detect_outliers(df_period)
    outlier_rate = outlier_df["outlier"].mean() * 100

    st.markdown("**Clusterização de clientes**")
    st.dataframe(cluster_df.head(30), use_container_width=True)

    st.markdown("**Detecção de anomalias (Isolation Forest)**")
    st.write(f"Taxa de outliers no período filtrado: {outlier_rate:.2f}%")
    st.dataframe(
        outlier_df[outlier_df["outlier"] == 1][
            ["nfe", "data_emissao", "cod_cliente", "cod_produto", "qtde", "faturamento", "margem_bruta"]
        ].head(50),
        use_container_width=True,
    )

    freq = st.selectbox("Frequência da previsão", ["Mensal", "Semanal"], index=0)
    horizon = st.slider("Períodos à frente", min_value=1, max_value=12, value=3)
    forecast = forecast_revenue(df_period, frequency=freq, periods_ahead=horizon)

    st.markdown("**Previsão de faturamento (regressão linear)**")
    if forecast.forecast.empty:
        st.info("Dados insuficientes para previsão (mínimo recomendado: 4 períodos).")
    else:
        fig2, ax2 = plt.subplots(figsize=(10, 4))
        sns.lineplot(data=forecast.history, x="periodo", y="y", marker="o", label="Histórico", ax=ax2)
        sns.lineplot(data=forecast.forecast, x="periodo", y="forecast", marker="o", label="Previsão", ax=ax2)
        st.pyplot(fig2)
        fig2.savefig(out_dir / "previsao_faturamento.png", bbox_inches="tight")
        st.write({k: round(v, 4) for k, v in forecast.metrics.items()})

    high_margin, low_margin = high_low_margin_products(df_period)
    relevance = product_relevance_rank(df_period)

    st.markdown("**Produtos de alta margem**")
    st.dataframe(high_margin.head(20), use_container_width=True)
    st.markdown("**Produtos de baixa margem**")
    st.dataframe(low_margin.head(20), use_container_width=True)
    st.markdown("**Ranking de relevância de itens**")
    st.dataframe(relevance.head(30), use_container_width=True)

    report_text = generate_executive_insights(kpis, monthly, top_products, top_clients, outlier_rate)
    st.subheader("Insights automáticos gerados por IA")
    st.markdown(report_text)

    # Salvar saídas
    save_dataframe(monthly, "faturamento_mensal.csv")
    save_dataframe(top_products, "faturamento_por_produto.csv")
    save_dataframe(top_clients, "faturamento_por_cliente.csv")
    save_dataframe(top_vendors, "faturamento_por_vendedor.csv")
    save_dataframe(top_companies, "faturamento_por_empresa.csv")
    save_dataframe(pay, "formas_pagamento.csv")
    save_dataframe(cluster_df, "clusters_clientes.csv")
    save_dataframe(outlier_df, "anomalias.csv")
    save_dataframe(relevance, "ranking_relevancia_produtos.csv")
    save_report(report_text, "relatorio_executivo.md")

    st.success(f"Arquivos gerados em: {Path(out_dir).resolve()}")
    st.caption(f"Qualidade de dados: {quality}")
else:
    st.info("Aguardando upload da planilha .XLS")
