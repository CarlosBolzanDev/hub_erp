from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_charts(base: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    _bar(
        base.sort_values("total_saidas", ascending=False).head(10),
        x="item",
        y="total_saidas",
        title="Top Itens por Saida",
        path=output_dir / "top_itens_saida.png",
    )

    top_risco = base.sort_values("dias_cobertura").head(10)
    _bar(top_risco, x="item", y="dias_cobertura", title="Top Itens em Risco", path=output_dir / "top_itens_risco.png")

    cmp_df = base.head(15).copy()
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(cmp_df))
    ax.bar(x, cmp_df["estoque_atual"], label="Estoque Atual")
    ax.plot(x, cmp_df["ponto_pedido"], marker="o", color="orange", label="Ponto de Pedido")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cmp_df["item"], rotation=45, ha="right")
    ax.set_title("Estoque Atual vs Ponto de Pedido")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "estoque_vs_ponto_pedido.png", dpi=150)
    plt.close(fig)


def _bar(df: pd.DataFrame, x: str, y: str, title: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df[x].astype(str), df[y])
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def export_excel(
    resumo: pd.DataFrame,
    analise: pd.DataFrame,
    alertas: pd.DataFrame,
    fornecedores: pd.DataFrame,
    movs: pd.DataFrame,
    parametros: pd.DataFrame,
    output_file: Path,
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        resumo.to_excel(writer, index=False, sheet_name="Resumo_Geral")
        analise.to_excel(writer, index=False, sheet_name="Analise_por_Item")
        alertas.to_excel(writer, index=False, sheet_name="Alertas_Compra")
        fornecedores.to_excel(writer, index=False, sheet_name="Fornecedores")
        movs.to_excel(writer, index=False, sheet_name="Movimentacoes_Limpas")
        parametros.to_excel(writer, index=False, sheet_name="Parametros")
