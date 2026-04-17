from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler


@dataclass
class ForecastResult:
    history: pd.DataFrame
    forecast: pd.DataFrame
    metrics: Dict[str, float]


def customer_clustering(df: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    features = (
        df.groupby("cod_cliente", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            margem=("margem_bruta", "sum"),
            volume=("qtde", "sum"),
            pedidos=("nfe", "nunique"),
        )
        .fillna(0)
    )

    if len(features) < n_clusters:
        n_clusters = max(1, len(features))

    scaler = StandardScaler()
    x = scaler.fit_transform(features[["faturamento", "margem", "volume", "pedidos"]])
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    features["cluster"] = model.fit_predict(x)
    return features


def detect_outliers(df: pd.DataFrame) -> pd.DataFrame:
    work = df[["faturamento", "margem_bruta", "qtde", "preco_venda_unit"]].copy().fillna(0)
    model = IsolationForest(contamination=0.03, random_state=42)
    labels = model.fit_predict(work)
    out = df.copy()
    out["outlier"] = np.where(labels == -1, 1, 0)
    return out


def _prepare_series(df: pd.DataFrame, frequency: str) -> pd.DataFrame:
    if frequency == "Semanal":
        series = (
            df.set_index("data_emissao")["faturamento"]
            .resample("W-MON")
            .sum()
            .reset_index()
            .rename(columns={"data_emissao": "periodo", "faturamento": "y"})
        )
    else:
        series = (
            df.set_index("data_emissao")["faturamento"]
            .resample("MS")
            .sum()
            .reset_index()
            .rename(columns={"data_emissao": "periodo", "faturamento": "y"})
        )

    series["t"] = np.arange(len(series))
    return series


def forecast_revenue(df: pd.DataFrame, frequency: str = "Mensal", periods_ahead: int = 3) -> ForecastResult:
    series = _prepare_series(df, frequency)
    if len(series) < 4:
        return ForecastResult(history=series, forecast=pd.DataFrame(), metrics={})

    split = int(len(series) * 0.8)
    train = series.iloc[:split]
    test = series.iloc[split:]

    model = LinearRegression()
    model.fit(train[["t"]], train["y"])

    test_pred = model.predict(test[["t"]])
    metrics = {
        "mae": float(mean_absolute_error(test["y"], test_pred)),
        "rmse": float(np.sqrt(mean_squared_error(test["y"], test_pred))),
        "r2": float(r2_score(test["y"], test_pred)),
    }

    future_t = np.arange(series["t"].max() + 1, series["t"].max() + 1 + periods_ahead)
    future_y = model.predict(future_t.reshape(-1, 1))

    last_period = series["periodo"].max()
    if frequency == "Semanal":
        future_periods = [last_period + pd.Timedelta(weeks=i) for i in range(1, periods_ahead + 1)]
    else:
        future_periods = [last_period + pd.DateOffset(months=i) for i in range(1, periods_ahead + 1)]

    forecast = pd.DataFrame({"periodo": future_periods, "forecast": future_y})
    return ForecastResult(history=series, forecast=forecast, metrics=metrics)


def product_relevance_rank(df: pd.DataFrame) -> pd.DataFrame:
    rank = (
        df.groupby("cod_produto", as_index=False)
        .agg(
            faturamento=("faturamento", "sum"),
            margem=("margem_bruta", "sum"),
            volume=("qtde", "sum"),
        )
        .fillna(0)
    )
    rank["score_relevancia"] = (
        rank["faturamento"].rank(pct=True) * 0.5
        + rank["margem"].rank(pct=True) * 0.4
        + rank["volume"].rank(pct=True) * 0.1
    )
    return rank.sort_values("score_relevancia", ascending=False)


def high_low_margin_products(df: pd.DataFrame, q: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    grouped = (
        df.groupby("cod_produto", as_index=False)
        .agg(faturamento=("faturamento", "sum"), margem_media=("margem_percentual", "mean"), qtde=("qtde", "sum"))
    )
    low_thr = grouped["margem_media"].quantile(q)
    high_thr = grouped["margem_media"].quantile(1 - q)
    high = grouped[grouped["margem_media"] >= high_thr].sort_values("margem_media", ascending=False)
    low = grouped[grouped["margem_media"] <= low_thr].sort_values("margem_media", ascending=True)
    return high, low
