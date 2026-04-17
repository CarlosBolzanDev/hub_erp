from __future__ import annotations

from typing import Dict

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    faturamento_total = float(df["faturamento"].sum())
    qtde_total = float(df["qtde"].sum())
    num_linhas = max(len(df), 1)
    pedidos = max(df["nfe"].nunique(), 1)

    ticket_linha = faturamento_total / num_linhas
    ticket_pedido = faturamento_total / pedidos

    marg_df = df[df["margem_bruta"].notna()]
    margem_bruta_total = float(marg_df["margem_bruta"].sum()) if not marg_df.empty else 0.0
    margem_media = float(marg_df["margem_percentual"].mean()) if not marg_df.empty else 0.0

    return {
        "faturamento_total": faturamento_total,
        "quantidade_total": qtde_total,
        "ticket_medio_linha": float(ticket_linha),
        "ticket_medio_nfe": float(ticket_pedido),
        "ticket_medio": float(ticket_pedido),  # compatibilidade
        "margem_bruta_total": margem_bruta_total,
        "margem_media_percentual": margem_media,
        "pedidos_unicos": float(pedidos),
    }


def aggregate_revenue(df: pd.DataFrame, by: str, top_n: int | None = 20) -> pd.DataFrame:
    out = (
        df.groupby(by, dropna=False, as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            margem_bruta=("margem_bruta", "sum"),
            qtde=("qtde", "sum"),
            pedidos=("nfe", "nunique"),
            linhas=("nfe", "count"),
        )
        .sort_values("faturamento", ascending=False)
    )
    if top_n is not None:
        out = out.head(top_n)
    return out


def monthly_revenue(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("mes_ref", as_index=False)
        .agg(faturamento=("faturamento", "sum"), margem=("margem_bruta", "sum"), qtde=("qtde", "sum"))
        .sort_values("mes_ref")
    )


def payment_usage(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("forma_pagto", as_index=False)
        .agg(transacoes=("nfe", "count"), faturamento=("faturamento", "sum"))
        .sort_values("transacoes", ascending=False)
    )


def margin_analysis(df: pd.DataFrame, by: str, top_n: int = 20) -> pd.DataFrame:
    grouped = (
        df.groupby(by, as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            custo_total=("custo_total", "sum"),
            margem_bruta=("margem_bruta", "sum"),
            margem_percentual_media=("margem_percentual", "mean"),
        )
        .sort_values("margem_bruta", ascending=False)
    )
    return grouped.head(top_n)


def concentration_share(df: pd.DataFrame, dimension: str, top_n: int = 10) -> float:
    grouped = aggregate_revenue(df, dimension, top_n=None)
    total = grouped["faturamento"].sum()
    if total <= 0:
        return 0.0
    return float(grouped.head(top_n)["faturamento"].sum() / total * 100)


def abc_pareto(df: pd.DataFrame, dimension: str) -> pd.DataFrame:
    grouped = aggregate_revenue(df, dimension, top_n=None)
    total = grouped["faturamento"].sum()
    grouped["participacao"] = grouped["faturamento"] / total if total > 0 else 0
    grouped["participacao_acumulada"] = grouped["participacao"].cumsum()

    def classify(x: float) -> str:
        if x <= 0.80:
            return "A"
        if x <= 0.95:
            return "B"
        return "C"

    grouped["classe_abc"] = grouped["participacao_acumulada"].apply(classify)
    return grouped
