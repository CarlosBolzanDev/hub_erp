from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_CONFIG: Dict[str, Any] = {
    "input_dir": "project/input",
    "output_dir": "project/output",
    "safety_factor": 1.5,
    "analysis_window_days": 180,
    "risk_coverage_days": 7,
    "low_rotation_days": 30,
    "excess_stock_days": 90,
    "files": {
        "vendas_keywords": ["vendas", "mov", "movimentacao"],
        "produtos_keywords": ["produtos", "cadastro", "itens"],
        "estoque_keywords": ["estoque", "saldo"],
    },
}


def load_config(path: str | Path = "project/config.yaml") -> Dict[str, Any]:
    cfg = DEFAULT_CONFIG.copy()
    cfg["files"] = DEFAULT_CONFIG["files"].copy()

    cfg_path = Path(path)
    if not cfg_path.exists():
        return cfg

    with cfg_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    for key, val in raw.items():
        if key == "files" and isinstance(val, dict):
            cfg["files"].update(val)
        else:
            cfg[key] = val
    return cfg
