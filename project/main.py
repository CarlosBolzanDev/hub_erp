from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from src.analytics import AnalysisConfig, compute_metrics
from src.config_loader import load_config
from src.io_utils import detect_file_types, prepare_estoque, prepare_produtos, prepare_vendas, read_excel_flexible
from src.reporting import export_excel, save_charts
from src.sample_data import generate_sample_data

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
LOGGER = logging.getLogger("hub_erp")


def run_pipeline(config_path: str, demo: bool = False) -> Path:
    cfg = load_config(config_path)
    input_dir = Path(cfg["input_dir"])
    output_dir = Path(cfg["output_dir"])

    if demo:
        LOGGER.info("Gerando dados ficticios em %s", input_dir)
        generate_sample_data(input_dir)

    files = detect_file_types(input_dir, cfg["files"])
    missing = [name for name in ["vendas", "produtos", "estoque"] if name not in files]
    if missing:
        raise FileNotFoundError(f"Arquivos nao encontrados para: {', '.join(missing)} em {input_dir}")

    vendas = prepare_vendas(read_excel_flexible(files["vendas"]))
    produtos = prepare_produtos(read_excel_flexible(files["produtos"]))
    estoque = prepare_estoque(read_excel_flexible(files["estoque"]))

    analysis_cfg = AnalysisConfig(
        safety_factor=float(cfg["safety_factor"]),
        analysis_window_days=int(cfg["analysis_window_days"]),
        risk_coverage_days=int(cfg["risk_coverage_days"]),
        low_rotation_days=int(cfg["low_rotation_days"]),
        excess_stock_days=int(cfg["excess_stock_days"]),
    )
    resumo, analise, alertas, fornecedores = compute_metrics(vendas, produtos, estoque, analysis_cfg)

    out_excel = output_dir / "analise_estoque.xlsx"
    parametros = pd.DataFrame([cfg])
    export_excel(resumo, analise, alertas, fornecedores, vendas, parametros, out_excel)
    save_charts(analise, output_dir)

    LOGGER.info("Analise finalizada. Arquivo: %s", out_excel)
    return out_excel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analise automatica de estoque, compras e vendas")
    parser.add_argument("--config", default="project/config.yaml", help="Caminho para config.yaml")
    parser.add_argument("--demo", action="store_true", help="Gera dados ficticios e executa pipeline")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.config, demo=args.demo)
