from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Análise de Estoque", layout="wide")
st.title("📦 Análise Automática de Estoque")

output_file = Path("project/output/analise_estoque.xlsx")
if not output_file.exists():
    st.warning("Arquivo de saída não encontrado. Execute `python project/main.py --demo` primeiro.")
    st.stop()

analise = pd.read_excel(output_file, sheet_name="Analise_por_Item")
fornecedores = pd.read_excel(output_file, sheet_name="Fornecedores")

item_sel = st.multiselect("Itens", sorted(analise["item"].dropna().unique().tolist()))
cat_sel = st.multiselect("Categoria", sorted(analise.get("categoria", pd.Series(dtype=str)).dropna().unique().tolist()))

filt = analise.copy()
if item_sel:
    filt = filt[filt["item"].isin(item_sel)]
if cat_sel and "categoria" in filt.columns:
    filt = filt[filt["categoria"].isin(cat_sel)]

col1, col2, col3 = st.columns(3)
col1.metric("Itens", int(filt["item"].nunique()))
col2.metric("Itens risco alto", int((filt["risco_ruptura"] == "ALTO").sum()))
col3.metric("Alertas compra", int((filt["alerta_compra"] == "SIM").sum()))

st.subheader("Análise por Item")
st.dataframe(filt, use_container_width=True)

st.subheader("Top Itens por Saída")
st.bar_chart(filt.sort_values("total_saidas", ascending=False).set_index("item")["total_saidas"].head(15))

st.subheader("Fornecedores")
st.dataframe(fornecedores, use_container_width=True)
