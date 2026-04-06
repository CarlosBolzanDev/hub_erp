from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class AnalysisConfig:
    safety_factor: float = 1.5
    analysis_window_days: int = 180
    risk_coverage_days: int = 7
    low_rotation_days: int = 30
    excess_stock_days: int = 90


def _safe_div(a: float, b: float) -> float:
    return float(a / b) if b and not np.isnan(b) else 0.0


def compute_metrics(vendas: pd.DataFrame, produtos: pd.DataFrame, estoque: pd.DataFrame, cfg: AnalysisConfig):
    if vendas.empty:
        raise ValueError("Base de vendas vazia apos limpeza.")

    vendas = vendas.copy()
    max_date = vendas["data"].max() if vendas["data"].notna().any() else pd.Timestamp.today().normalize()
    min_date = max_date - pd.Timedelta(days=cfg.analysis_window_days)
    vendas = vendas[(vendas["data"].isna()) | (vendas["data"] >= min_date)]

    vendas["entrada"] = np.where(vendas["tipo"] == "ENTRADA", vendas["qtd"], 0.0)
    vendas["saida"] = np.where(vendas["tipo"] == "SAIDA", vendas["qtd"].abs(), 0.0)

    base = vendas.groupby("item", as_index=False).agg(
        total_entradas=("entrada", "sum"),
        total_saidas=("saida", "sum"),
        data_inicio=("data", "min"),
        data_fim=("data", "max"),
    )

    base = base.merge(estoque, on="item", how="left").fillna({"estoque_atual": 0})
    base = base.merge(produtos, on="item", how="left")

    span_days = (base["data_fim"] - base["data_inicio"]).dt.days.fillna(cfg.analysis_window_days).clip(lower=1)
    base["consumo_medio_diario"] = [
        _safe_div(saidas, dias) for saidas, dias in zip(base["total_saidas"], span_days, strict=False)
    ]
    base["consumo_medio_semanal"] = base["consumo_medio_diario"] * 7
    base["consumo_medio_mensal"] = base["consumo_medio_diario"] * 30

    lead_vendas = (
        vendas.groupby("item", as_index=False)["entrega_dias"].median()
        if "entrega_dias" in vendas.columns
        else pd.DataFrame(columns=["item", "entrega_dias"])
    )
    base = base.merge(lead_vendas, on="item", how="left")
    base["lead_time_final"] = base["lead_time"].fillna(base["entrega_dias"]).fillna(7)

    base["dias_cobertura"] = [
        _safe_div(est, cmd) for est, cmd in zip(base["estoque_atual"], base["consumo_medio_diario"], strict=False)
    ]

    base["estoque_minimo_sugerido"] = (
        base["consumo_medio_diario"] * base["lead_time_final"] * cfg.safety_factor
    )
    base["estoque_seguranca"] = base["estoque_minimo_sugerido"]
    base["ponto_pedido"] = base["consumo_medio_diario"] * base["lead_time_final"] + base["estoque_seguranca"]
    base["qtd_sugerida_compra"] = (base["ponto_pedido"] - base["estoque_atual"]).clip(lower=0)

    b30 = _window_outflow(vendas, max_date, 30)
    b60 = _window_outflow(vendas, max_date, 60)
    b90 = _window_outflow(vendas, max_date, 90)
    trend = b30.merge(b60, on="item", how="outer").merge(b90, on="item", how="outer").fillna(0)
    base = base.merge(trend, on="item", how="left").fillna({"saida_30d": 0, "saida_60d": 0, "saida_90d": 0})

    base["tendencia_consumo"] = np.where(
        base["saida_30d"] / 30 > base["saida_60d"] / 60,
        "Alta",
        np.where(base["saida_30d"] / 30 < base["saida_90d"] / 90, "Queda", "Estavel"),
    )

    base["risco_ruptura"] = np.where(base["dias_cobertura"] <= cfg.risk_coverage_days, "ALTO", "BAIXO")
    base["baixa_rotatividade"] = np.where(base["saida_30d"] <= 0, "SIM", "NAO")
    base["excesso_estoque"] = np.where(base["dias_cobertura"] >= cfg.excess_stock_days, "SIM", "NAO")
    base["alerta_compra"] = np.where(base["estoque_atual"] <= base["ponto_pedido"], "SIM", "NAO")

    base["giro"] = base["total_saidas"]
    base = base.sort_values("giro", ascending=False)
    total_giro = base["giro"].sum()
    base["pareto_acumulado"] = base["giro"].cumsum() / total_giro if total_giro > 0 else 0
    base["classe_abc"] = np.select(
        [base["pareto_acumulado"] <= 0.8, base["pareto_acumulado"] <= 0.95],
        ["A", "B"],
        default="C",
    )

    fornecedores = analyze_suppliers(vendas)
    resumo = build_summary(base)
    alertas = base[(base["alerta_compra"] == "SIM") | (base["risco_ruptura"] == "ALTO")]

    return resumo, base, alertas, fornecedores


def _window_outflow(vendas: pd.DataFrame, max_date: pd.Timestamp, days: int) -> pd.DataFrame:
    ini = max_date - pd.Timedelta(days=days)
    tmp = vendas[(vendas["tipo"] == "SAIDA") & (vendas["data"] >= ini)]
    return tmp.groupby("item", as_index=False)["qtd"].sum().rename(columns={"qtd": f"saida_{days}d"})


def analyze_suppliers(vendas: pd.DataFrame) -> pd.DataFrame:
    cols = set(vendas.columns)
    if not {"item", "fornecedor", "custo"}.issubset(cols):
        return pd.DataFrame(columns=["item", "fornecedor", "custo_medio", "prazo_medio", "score", "melhor_opcao"])

    df = vendas.dropna(subset=["fornecedor", "custo"]).copy()
    if df.empty:
        return pd.DataFrame(columns=["item", "fornecedor", "custo_medio", "prazo_medio", "score", "melhor_opcao"])

    agg = df.groupby(["item", "fornecedor"], as_index=False).agg(
        custo_medio=("custo", "mean"),
        prazo_medio=("entrega_dias", "mean") if "entrega_dias" in df.columns else ("custo", "size"),
    )
    if "entrega_dias" not in df.columns:
        agg["prazo_medio"] = 0

    agg["score"] = _minmax(agg["custo_medio"]) + _minmax(agg["prazo_medio"])
    best_idx = agg.groupby("item")["score"].idxmin()
    agg["melhor_opcao"] = "NAO"
    agg.loc[best_idx, "melhor_opcao"] = "SIM"
    return agg.sort_values(["item", "score"])


def _minmax(series: pd.Series) -> pd.Series:
    smin, smax = series.min(), series.max()
    if smax == smin:
        return pd.Series(np.zeros(len(series)), index=series.index)
    return (series - smin) / (smax - smin)


def build_summary(base: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "itens_total": [base["item"].nunique()],
            "entradas_total": [base["total_entradas"].sum()],
            "saidas_total": [base["total_saidas"].sum()],
            "estoque_total": [base["estoque_atual"].sum()],
            "itens_risco_alto": [(base["risco_ruptura"] == "ALTO").sum()],
            "itens_alerta_compra": [(base["alerta_compra"] == "SIM").sum()],
        }
    )
