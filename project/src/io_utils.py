from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

LOGGER = logging.getLogger(__name__)

CANONICAL_COLUMNS = {
    "data": ["data", "dt", "date", "emissao"],
    "item": ["item", "produto", "codigo", "sku"],
    "tipo": ["tipo", "movimento", "operacao", "entrada_saida"],
    "qtd": ["qtd", "quantidade", "qtde", "volume"],
    "custo": ["custo", "valor", "preco", "vlr"],
    "fornecedor": ["fornecedor", "supplier", "parceiro"],
    "entrega_dias": ["entrega_dias", "prazo", "lead_time", "dias_entrega"],
    "descricao": ["descricao", "descrição", "nome", "detalhe"],
    "categoria": ["categoria", "grupo", "familia", "família"],
    "fornecedor_padrao": ["fornecedor_padrao", "fornecedor padrão", "forn_padrao"],
    "lead_time": ["lead_time", "prazo", "prazo_dias", "dias"],
    "custo_padrao": ["custo_padrao", "custo padrão", "preco_padrao"],
    "estoque_minimo": ["estoque_minimo", "estoque mínimo", "minimo", "min"],
    "estoque_maximo": ["estoque_maximo", "estoque máximo", "maximo", "max"],
    "estoque_atual": ["estoque_atual", "saldo", "estoque", "quantidade_atual"],
}


def normalize_text(text: object) -> str:
    txt = "" if text is None else str(text)
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode("utf-8")
    txt = txt.lower().strip()
    txt = re.sub(r"\s+", "_", txt)
    txt = re.sub(r"[^a-z0-9_]+", "", txt)
    return txt


def detect_file_types(input_dir: Path, file_cfg: Dict[str, List[str]]) -> Dict[str, Path]:
    excel_files = [*input_dir.glob("*.xls"), *input_dir.glob("*.xlsx")]
    found: Dict[str, Path] = {}

    def pick(keys: List[str]) -> Path | None:
        for p in excel_files:
            stem = normalize_text(p.stem)
            if any(normalize_text(k) in stem for k in keys):
                return p
        return None

    for logical_name, keys in (
        ("vendas", file_cfg.get("vendas_keywords", [])),
        ("produtos", file_cfg.get("produtos_keywords", [])),
        ("estoque", file_cfg.get("estoque_keywords", [])),
    ):
        chosen = pick(keys)
        if chosen:
            found[logical_name] = chosen
    return found


def _score_header_row(row: pd.Series) -> int:
    normalized = [normalize_text(v) for v in row.tolist()]
    aliases = {normalize_text(alias) for values in CANONICAL_COLUMNS.values() for alias in values}
    return sum(1 for v in normalized if v in aliases)


def read_excel_flexible(path: Path) -> pd.DataFrame:
    raw = pd.read_excel(path, header=None)
    if raw.empty:
        return pd.DataFrame()

    scores = raw.head(30).apply(_score_header_row, axis=1)
    header_idx = int(scores.idxmax()) if scores.max() > 0 else 0
    header = raw.iloc[header_idx].tolist()
    df = raw.iloc[header_idx + 1 :].copy()
    df.columns = [normalize_text(c) or f"col_{i}" for i, c in enumerate(header)]
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")
    return df.reset_index(drop=True)


def canonicalize_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    mapping: Dict[str, str] = {}
    existing = {normalize_text(c): c for c in df.columns}

    for canonical, aliases in CANONICAL_COLUMNS.items():
        for alias in aliases:
            n = normalize_text(alias)
            if n in existing:
                mapping[existing[n]] = canonical
                break

    out = df.rename(columns=mapping).copy()
    return out, mapping


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", ".", regex=False), errors="coerce")


def prepare_vendas(df: pd.DataFrame) -> pd.DataFrame:
    df, _ = canonicalize_columns(df)
    required = ["item", "qtd"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Arquivo de vendas sem coluna obrigatoria: {col}")

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce", dayfirst=True)
    else:
        df["data"] = pd.NaT

    df["item"] = df["item"].astype(str).str.strip()
    df = df[df["item"].ne("")]
    df["qtd"] = to_numeric(df["qtd"]).fillna(0)

    if "tipo" not in df.columns:
        df["tipo"] = "SAIDA"
    df["tipo"] = df["tipo"].astype(str).map(normalize_text)
    df["tipo"] = df["tipo"].replace({"entrada": "ENTRADA", "saida": "SAIDA", "": "SAIDA"})
    df["tipo"] = df["tipo"].where(df["tipo"].isin(["ENTRADA", "SAIDA"]), "SAIDA")

    for optional in ["custo", "entrega_dias"]:
        if optional in df.columns:
            df[optional] = to_numeric(df[optional])
    if "fornecedor" in df.columns:
        df["fornecedor"] = df["fornecedor"].astype(str).str.strip()

    return df


def prepare_produtos(df: pd.DataFrame) -> pd.DataFrame:
    df, _ = canonicalize_columns(df)
    if "item" not in df.columns:
        raise ValueError("Arquivo de produtos sem coluna obrigatoria: item")

    df["item"] = df["item"].astype(str).str.strip()
    for col in ["lead_time", "custo_padrao", "estoque_minimo", "estoque_maximo"]:
        if col in df.columns:
            df[col] = to_numeric(df[col])

    return df.dropna(subset=["item"]).drop_duplicates(subset=["item"])


def prepare_estoque(df: pd.DataFrame) -> pd.DataFrame:
    df, _ = canonicalize_columns(df)
    if "item" not in df.columns:
        raise ValueError("Arquivo de estoque sem coluna obrigatoria: item")

    df["item"] = df["item"].astype(str).str.strip()

    if "estoque_atual" in df.columns:
        df["estoque_atual"] = to_numeric(df["estoque_atual"]).fillna(0)
        return df[["item", "estoque_atual"]].groupby("item", as_index=False).sum()

    if {"tipo", "qtd"}.issubset(df.columns):
        df["qtd"] = to_numeric(df["qtd"]).fillna(0)
        df["tipo"] = df["tipo"].astype(str).map(normalize_text)
        df["sinal"] = df["tipo"].map(lambda x: 1 if x == "entrada" else -1)
        df["estoque_atual"] = df["qtd"] * df["sinal"]
        return df[["item", "estoque_atual"]].groupby("item", as_index=False).sum()

    LOGGER.warning("Estoque sem estoque_atual nem movimentacao valida; assumindo zero.")
    return df[["item"]].drop_duplicates().assign(estoque_atual=0.0)
