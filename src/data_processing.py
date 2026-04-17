from __future__ import annotations

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


def load_xls(file) -> pd.DataFrame:
    """Carrega planilha .xls usando xlrd como engine."""
    return pd.read_excel(file, engine="xlrd")


def validate_columns(df: pd.DataFrame) -> ValidationResult:
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    return ValidationResult(is_valid=len(missing) == 0, missing_columns=missing)


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=COLUMN_RENAME_MAP).copy()


def _to_datetime_br(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def _to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def clean_and_enrich(df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Limpa, corrige tipos e cria colunas derivadas."""
    df = standardize_columns(df_raw)

    # Tipos
    df["data_emissao"] = _to_datetime_br(df["data_emissao"])
    df["data_vencimento"] = _to_datetime_br(df["data_vencimento"])

    numeric_cols = ["qtde", "preco_venda_unit", "custo_real", "custo_medio"]
    for col in numeric_cols:
        df[col] = _to_numeric(df[col])

    cat_cols = ["nfe", "forma_pagto", "cod_produto", "cod_cliente", "cod_vendedor", "empresa"]
    for col in cat_cols:
        df[col] = df[col].astype("string").str.strip()

    # Remoções e preenchimentos
    before = len(df)
    df = df.dropna(subset=["data_emissao", "qtde", "preco_venda_unit"])
    removed_missing_critical = before - len(df)

    # Valores inconsistentes
    negative_qty = (df["qtde"] < 0).sum()
    negative_price = (df["preco_venda_unit"] < 0).sum()
    df = df[(df["qtde"] >= 0) & (df["preco_venda_unit"] >= 0)]

    df["custo_real"] = df["custo_real"].fillna(df["custo_medio"])
    df["custo_medio"] = df["custo_medio"].fillna(df["custo_real"])
    df["custo_real"] = df["custo_real"].fillna(0)
    df["custo_medio"] = df["custo_medio"].fillna(0)

    # Derivadas
    df["faturamento"] = df["qtde"] * df["preco_venda_unit"]
    df["custo_total"] = df["qtde"] * df["custo_real"]
    df["margem_bruta"] = df["faturamento"] - df["custo_total"]
    df["margem_percentual"] = np.where(
        df["faturamento"] > 0,
        (df["margem_bruta"] / df["faturamento"]) * 100,
        0,
    )

    iso_calendar = df["data_emissao"].dt.isocalendar()
    df["ano"] = df["data_emissao"].dt.year
    df["mes"] = df["data_emissao"].dt.month
    df["mes_ref"] = df["data_emissao"].dt.to_period("M").astype(str)
    df["semana"] = iso_calendar.week.astype(int)
    df["ano_semana"] = iso_calendar.year.astype(str) + "-W" + iso_calendar.week.astype(str).str.zfill(2)
    df["dia"] = df["data_emissao"].dt.day

    quality = {
        "linhas_entrada": int(before),
        "linhas_saida": int(len(df)),
        "linhas_removidas_criticas": int(removed_missing_critical),
        "qtde_negativa_removida": int(negative_qty),
        "preco_negativo_removido": int(negative_price),
    }
    return df, quality


def date_range(df: pd.DataFrame) -> Tuple[pd.Timestamp, pd.Timestamp]:
    return df["data_emissao"].min(), df["data_emissao"].max()


def filter_by_period(df: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp) -> pd.DataFrame:
    mask = (df["data_emissao"] >= pd.Timestamp(start_date)) & (df["data_emissao"] <= pd.Timestamp(end_date))
    return df.loc[mask].copy()
