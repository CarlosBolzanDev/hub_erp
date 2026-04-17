from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

EXPECTED_COLUMNS: List[str] = [
    "NFE",
    "Data Emissão",
    "Data Vencimento",
    "Forma Pagto",
    "Código Interno Produto",
    "Qtde",
    "Preço Venda Unit",
    "Código Cliente",
    "Código Vendedor",
    "Custo Real",
    "Custo Médio",
    "Empresa",
]

COLUMN_RENAME_MAP: Dict[str, str] = {
    "NFE": "nfe",
    "Data Emissão": "data_emissao",
    "Data Vencimento": "data_vencimento",
    "Forma Pagto": "forma_pagto",
    "Código Interno Produto": "cod_produto",
    "Qtde": "qtde",
    "Preço Venda Unit": "preco_venda_unit",
    "Código Cliente": "cod_cliente",
    "Código Vendedor": "cod_vendedor",
    "Custo Real": "custo_real",
    "Custo Médio": "custo_medio",
    "Empresa": "empresa",
}


@dataclass
class ValidationResult:
    is_valid: bool
    missing_columns: List[str]
    mapping: Dict[str, str]


def _normalize_name(name: str) -> str:
    n = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    n = n.lower().strip()
    n = re.sub(r"\s+", " ", n)
    n = re.sub(r"[^a-z0-9]+", "", n)
    return n


def _resolve_column_mapping(columns: List[str]) -> Tuple[Dict[str, str], List[str]]:
    normalized_incoming = {_normalize_name(c): c for c in columns}
    mapping: Dict[str, str] = {}
    missing: List[str] = []

    for expected in EXPECTED_COLUMNS:
        key = _normalize_name(expected)
        if key in normalized_incoming:
            mapping[normalized_incoming[key]] = expected
        else:
            missing.append(expected)
    return mapping, missing


def load_xls(file) -> pd.DataFrame:
    """Carrega planilha .xls usando xlrd como engine."""
    return pd.read_excel(file, engine="xlrd")


def validate_columns(df: pd.DataFrame) -> ValidationResult:
    mapping, missing = _resolve_column_mapping(df.columns.tolist())
    return ValidationResult(is_valid=len(missing) == 0, missing_columns=missing, mapping=mapping)


def standardize_columns(df: pd.DataFrame, mapping: Dict[str, str] | None = None) -> pd.DataFrame:
    if mapping is None:
        mapping, _ = _resolve_column_mapping(df.columns.tolist())
    canonical = df.rename(columns=mapping)
    return canonical.rename(columns=COLUMN_RENAME_MAP).copy()


def _to_datetime_br(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _normalize_categorical(series: pd.Series, default_value: str = "NA") -> pd.Series:
    return series.astype("string").str.strip().replace({"": pd.NA, "nan": pd.NA, "None": pd.NA}).fillna(default_value)


def clean_and_enrich(df_raw: pd.DataFrame, mapping: Dict[str, str] | None = None) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Limpa, corrige tipos e cria colunas derivadas com foco em consistência analítica."""
    df = standardize_columns(df_raw, mapping=mapping)

    df["data_emissao"] = _to_datetime_br(df["data_emissao"])
    df["data_vencimento"] = _to_datetime_br(df["data_vencimento"])

    for col in ["qtde", "preco_venda_unit", "custo_real", "custo_medio"]:
        df[col] = _to_numeric(df[col])

    for col in ["nfe", "forma_pagto", "cod_produto", "cod_cliente", "cod_vendedor", "empresa"]:
        df[col] = _normalize_categorical(df[col])

    before = len(df)
    df = df.dropna(subset=["data_emissao", "qtde", "preco_venda_unit"])
    removed_missing_critical = before - len(df)

    negative_qty = int((df["qtde"] < 0).sum())
    negative_price = int((df["preco_venda_unit"] < 0).sum())
    df = df[(df["qtde"] >= 0) & (df["preco_venda_unit"] >= 0)].copy()

    # Custos: não força custo zero quando ausente
    custo_ref = df["custo_real"].fillna(df["custo_medio"])
    custo_missing_mask = custo_ref.isna()
    custo_inconsistent_mask = custo_ref < 0
    custo_valid_mask = ~(custo_missing_mask | custo_inconsistent_mask)

    df["status_custo"] = np.select(
        [custo_valid_mask, custo_missing_mask, custo_inconsistent_mask],
        ["valido", "ausente", "inconsistente"],
        default="ausente",
    )
    df["custo_ref"] = custo_ref.where(custo_valid_mask, np.nan)

    # Winsorização leve apenas para visualizações
    for col in ["qtde", "preco_venda_unit"]:
        low, high = df[col].quantile([0.001, 0.999])
        df[col] = df[col].clip(lower=low, upper=high)

    df["faturamento"] = df["qtde"] * df["preco_venda_unit"]
    df["custo_total"] = np.where(df["custo_ref"].notna(), df["qtde"] * df["custo_ref"], np.nan)
    df["margem_bruta"] = np.where(df["custo_total"].notna(), df["faturamento"] - df["custo_total"], np.nan)
    df["margem_percentual"] = np.where(
        (df["faturamento"] > 0) & (df["margem_bruta"].notna()),
        (df["margem_bruta"] / df["faturamento"]) * 100,
        np.nan,
    )

    iso_calendar = df["data_emissao"].dt.isocalendar()
    df["ano"] = df["data_emissao"].dt.year
    df["trimestre"] = df["data_emissao"].dt.quarter
    df["mes"] = df["data_emissao"].dt.month
    df["mes_ref"] = df["data_emissao"].dt.to_period("M").astype(str)
    df["semana"] = iso_calendar.week.astype(int)
    df["ano_semana"] = iso_calendar.year.astype(str) + "-W" + iso_calendar.week.astype(str).str.zfill(2)
    df["dia"] = df["data_emissao"].dt.day
    df["periodo_comparacao"] = "base"

    quality = {
        "linhas_entrada": int(before),
        "linhas_validas": int(len(df)),
        "linhas_removidas": int(before - len(df)),
        "linhas_removidas_criticas": int(removed_missing_critical),
        "qtde_negativa_removida": negative_qty,
        "preco_negativo_removido": negative_price,
        "custos_validos": int((df["status_custo"] == "valido").sum()),
        "custos_ausentes": int((df["status_custo"] == "ausente").sum()),
        "custos_inconsistentes": int((df["status_custo"] == "inconsistente").sum()),
    }
    return df, quality


def date_range(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    return df["data_emissao"].min(), df["data_emissao"].max()


def filter_by_period(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    mask = (df["data_emissao"] >= pd.Timestamp(start_date)) & (df["data_emissao"] <= pd.Timestamp(end_date))
    return df.loc[mask].copy()


def align_equivalent_periods(
    df_a: pd.DataFrame,
    df_b: pd.DataFrame,
    start_a: pd.Timestamp,
    end_a: pd.Timestamp,
    start_b: pd.Timestamp,
    end_b: pd.Timestamp,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, int]]:
    a = filter_by_period(df_a, start_a, end_a)
    b = filter_by_period(df_b, start_b, end_b)

    if a.empty or b.empty:
        return a, b, {"dias_a": 0, "dias_b": 0, "dias_comparados": 0}

    days_a = int((a["data_emissao"].max() - a["data_emissao"].min()).days) + 1
    days_b = int((b["data_emissao"].max() - b["data_emissao"].min()).days) + 1
    days = max(1, min(days_a, days_b))

    end_a_eff = a["data_emissao"].max()
    end_b_eff = b["data_emissao"].max()
    start_a_eff = end_a_eff - pd.Timedelta(days=days - 1)
    start_b_eff = end_b_eff - pd.Timedelta(days=days - 1)

    a_eq = a[a["data_emissao"].between(start_a_eff, end_a_eff)].copy()
    b_eq = b[b["data_emissao"].between(start_b_eff, end_b_eff)].copy()

    return a_eq, b_eq, {"dias_a": days_a, "dias_b": days_b, "dias_comparados": days}
