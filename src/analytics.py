from __future__ import annotations

from typing import Dict

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    faturamento_total = float(df["faturamento"].sum())
    qtde_total = float(df["qtde"].sum())
    ticket_medio = faturamento_total / max(len(df), 1)
    margem_media = float(df["margem_percentual"].mean()) if len(df) else 0.0

    return {
        "faturamento_total": faturamento_total,
        "quantidade_total": qtde_total,
        "ticket_medio": ticket_medio,
        "margem_media_percentual": margem_media,
    }


def aggregate_revenue(df: pd.DataFrame, by: str, top_n: int = 20) -> pd.DataFrame:
    return (
        df.groupby(by, dropna=False, as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            margem_bruta=("margem_bruta", "sum"),
            qtde=("qtde", "sum"),
            pedidos=("nfe", "nunique"),
        )
        .sort_values("faturamento", ascending=False)
        .head(top_n)
    )


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
