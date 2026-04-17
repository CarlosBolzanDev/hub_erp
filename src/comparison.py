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
        ("ticket_medio", "Ticket Médio"),
        ("margem_media_percentual", "Margem Média (%)"),
    ]:
        a = float(kpi_a[key])
        b = float(kpi_b[key])
        delta = b - a
        delta_pct = (delta / a * 100) if a != 0 else np.nan
        rows.append({"indicador": name, label_a: a, label_b: b, "delta_abs": delta, "delta_pct": delta_pct})

    # Margem bruta total explícita
    margem_a = float(df_a["margem_bruta"].sum())
    margem_b = float(df_b["margem_bruta"].sum())
    rows.append(
        {
            "indicador": "Margem Bruta Total",
            label_a: margem_a,
            label_b: margem_b,
            "delta_abs": margem_b - margem_a,
            "delta_pct": ((margem_b - margem_a) / margem_a * 100) if margem_a != 0 else np.nan,
        }
    )

    return pd.DataFrame(rows)


def compare_dimension(df_a: pd.DataFrame, df_b: pd.DataFrame, dimension: str) -> pd.DataFrame:
    a = aggregate_revenue(df_a, dimension, top_n=10).rename(columns={"faturamento": "faturamento_a", "qtde": "qtde_a"})
    b = aggregate_revenue(df_b, dimension, top_n=10).rename(columns={"faturamento": "faturamento_b", "qtde": "qtde_b"})

    merged = a[[dimension, "faturamento_a", "qtde_a"]].merge(
        b[[dimension, "faturamento_b", "qtde_b"]], on=dimension, how="outer"
    )
    merged = merged.fillna(0)
    merged["delta_faturamento"] = merged["faturamento_b"] - merged["faturamento_a"]
    merged["delta_faturamento_pct"] = np.where(
        merged["faturamento_a"] != 0,
        (merged["delta_faturamento"] / merged["faturamento_a"]) * 100,
        np.nan,
    )
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
        )
        .rename(
            columns={
                "qtde": f"qtde_{tag}",
                "faturamento": f"faturamento_{tag}",
                "margem": f"margem_{tag}",
                "dias_com_venda": f"dias_com_venda_{tag}",
                "meses_ativos": f"meses_ativos_{tag}",
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

    # estabilidade por variação relativa de faturamento
    rel = m["delta_faturamento_pct"].abs().fillna(999)
    m["comportamento"] = np.where(rel <= 15, "estavel", np.where(rel <= 40, "moderado", "instavel"))

    # frequência de venda normalizada por mês ativo em cada período
    m["freq_venda_a"] = np.where(m["meses_ativos_a"] > 0, m["dias_com_venda_a"] / m["meses_ativos_a"], 0)
    m["freq_venda_b"] = np.where(m["meses_ativos_b"] > 0, m["dias_com_venda_b"] / m["meses_ativos_b"], 0)

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
