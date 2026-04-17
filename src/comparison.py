from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd

from src.analytics import aggregate_revenue, compute_kpis


def compare_kpis(df_a: pd.DataFrame, df_b: pd.DataFrame, label_a: str = "Período A", label_b: str = "Período B") -> pd.DataFrame:
    kpi_a = compute_kpis(df_a)
    kpi_b = compute_kpis(df_b)

    rows = []
    for key, name in [
        ("faturamento_total", "Faturamento Total"),
        ("quantidade_total", "Quantidade Total"),
        ("ticket_medio_nfe", "Ticket Médio por Pedido"),
        ("ticket_medio_linha", "Ticket Médio por Linha"),
        ("margem_bruta_total", "Margem Bruta Total"),
        ("margem_media_percentual", "Margem Média (%)"),
    ]:
        a = float(kpi_a[key])
        b = float(kpi_b[key])
        delta = b - a
        delta_pct = (delta / a * 100) if a != 0 else np.nan
        rows.append({"indicador": name, label_a: a, label_b: b, "delta_abs": delta, "delta_pct": delta_pct})

    return pd.DataFrame(rows)


def compare_dimension(df_a: pd.DataFrame, df_b: pd.DataFrame, dimension: str, min_share: float = 0.001) -> pd.DataFrame:
    """Compara dimensão usando união de itens relevantes, sem viés de top10."""
    a = aggregate_revenue(df_a, dimension, top_n=None).rename(
        columns={"faturamento": "faturamento_a", "qtde": "qtde_a", "margem_bruta": "margem_a"}
    )
    b = aggregate_revenue(df_b, dimension, top_n=None).rename(
        columns={"faturamento": "faturamento_b", "qtde": "qtde_b", "margem_bruta": "margem_b"}
    )

    merged = a[[dimension, "faturamento_a", "qtde_a", "margem_a"]].merge(
        b[[dimension, "faturamento_b", "qtde_b", "margem_b"]], on=dimension, how="outer"
    )
    merged = merged.fillna(0)

    total_ref = max(merged["faturamento_a"].sum(), merged["faturamento_b"].sum(), 1)
    merged = merged[
        ((merged["faturamento_a"] + merged["faturamento_b"]).abs() / total_ref >= min_share)
        | ((merged["qtde_a"] + merged["qtde_b"]).abs() > 0)
    ].copy()

    merged["status"] = np.select(
        [
            (merged["faturamento_a"] == 0) & (merged["faturamento_b"] > 0),
            (merged["faturamento_a"] > 0) & (merged["faturamento_b"] == 0),
            (merged["faturamento_a"] > 0) & (merged["faturamento_b"] > 0),
        ],
        ["novo", "ausente", "recorrente"],
        default="sem_movimento",
    )

    for metric in ["faturamento", "qtde", "margem"]:
        merged[f"delta_{metric}"] = merged[f"{metric}_b"] - merged[f"{metric}_a"]
        merged[f"delta_{metric}_pct"] = np.where(
            merged[f"{metric}_a"] != 0,
            merged[f"delta_{metric}"] / merged[f"{metric}_a"] * 100,
            np.nan,
        )

    merged["rank_a"] = merged["faturamento_a"].rank(ascending=False, method="dense")
    merged["rank_b"] = merged["faturamento_b"].rank(ascending=False, method="dense")
    merged["mudanca_ranking"] = merged["rank_a"] - merged["rank_b"]

    return merged.sort_values("delta_faturamento", ascending=False)


def _product_base(df: pd.DataFrame, tag: str) -> pd.DataFrame:
    out = (
        df.groupby("cod_produto", as_index=False)
        .agg(
            qtde=("qtde", "sum"),
            faturamento=("faturamento", "sum"),
            margem=("margem_bruta", "sum"),
            dias_com_venda=("data_emissao", "nunique"),
            meses_ativos=("mes_ref", "nunique"),
            desvio_faturamento=("faturamento", "std"),
        )
        .fillna({"desvio_faturamento": 0})
        .rename(
            columns={
                "qtde": f"qtde_{tag}",
                "faturamento": f"faturamento_{tag}",
                "margem": f"margem_{tag}",
                "dias_com_venda": f"dias_com_venda_{tag}",
                "meses_ativos": f"meses_ativos_{tag}",
                "desvio_faturamento": f"desvio_faturamento_{tag}",
            }
        )
    )
    out[f"rank_faturamento_{tag}"] = out[f"faturamento_{tag}"].rank(ascending=False, method="dense")
    return out


def analyze_product_movement(df_a: pd.DataFrame, df_b: pd.DataFrame) -> pd.DataFrame:
    a = _product_base(df_a, "a")
    b = _product_base(df_b, "b")

    m = a.merge(b, on="cod_produto", how="outer").fillna(0)
    m["status_produto"] = np.select(
        [
            (m["faturamento_a"] == 0) & (m["faturamento_b"] > 0),
            (m["faturamento_a"] > 0) & (m["faturamento_b"] == 0),
            (m["faturamento_a"] > 0) & (m["faturamento_b"] > 0),
        ],
        ["novo_no_periodo_b", "ausente_no_periodo_b", "recorrente"],
        default="sem_movimento",
    )

    for metric in ["qtde", "faturamento", "margem"]:
        m[f"delta_{metric}"] = m[f"{metric}_b"] - m[f"{metric}_a"]
        m[f"delta_{metric}_pct"] = np.where(
            m[f"{metric}_a"] != 0,
            m[f"delta_{metric}"] / m[f"{metric}_a"] * 100,
            np.nan,
        )

    m["mudanca_ranking"] = m["rank_faturamento_a"] - m["rank_faturamento_b"]

    rel = m["delta_faturamento_pct"].abs().fillna(999)
    m["comportamento"] = np.where(rel <= 15, "estavel", np.where(rel <= 40, "moderado", "instavel"))

    m["freq_venda_a"] = np.where(m["meses_ativos_a"] > 0, m["dias_com_venda_a"] / m["meses_ativos_a"], 0)
    m["freq_venda_b"] = np.where(m["meses_ativos_b"] > 0, m["dias_com_venda_b"] / m["meses_ativos_b"], 0)

    m["estabilidade_a"] = np.where(m["faturamento_a"] > 0, m["desvio_faturamento_a"] / m["faturamento_a"], np.nan)
    m["estabilidade_b"] = np.where(m["faturamento_b"] > 0, m["desvio_faturamento_b"] / m["faturamento_b"], np.nan)

    return m.sort_values("delta_faturamento", ascending=False)


def summarize_product_movement(movement: pd.DataFrame, top_n: int = 10) -> Dict[str, pd.DataFrame]:
    recorrentes = movement[movement["status_produto"] == "recorrente"]
    return {
        "crescimento_volume": recorrentes.sort_values("delta_qtde", ascending=False).head(top_n),
        "crescimento_faturamento": recorrentes.sort_values("delta_faturamento", ascending=False).head(top_n),
        "maior_queda": recorrentes.sort_values("delta_faturamento", ascending=True).head(top_n),
        "novos": movement[movement["status_produto"] == "novo_no_periodo_b"].sort_values(
            "faturamento_b", ascending=False
        ).head(top_n),
        "ausentes": movement[movement["status_produto"] == "ausente_no_periodo_b"].sort_values(
            "faturamento_a", ascending=False
        ).head(top_n),
        "recorrentes": recorrentes.sort_values("faturamento_b", ascending=False).head(top_n),
    }


def sales_concentration(df: pd.DataFrame, top_n: int = 10) -> Tuple[pd.DataFrame, float]:
    prod = (
        df.groupby("cod_produto", as_index=False)
        .agg(faturamento=("faturamento", "sum"))
        .sort_values("faturamento", ascending=False)
    )
    total = prod["faturamento"].sum()
    top_share = float(prod.head(top_n)["faturamento"].sum() / total * 100) if total > 0 else 0.0
    return prod, top_share
