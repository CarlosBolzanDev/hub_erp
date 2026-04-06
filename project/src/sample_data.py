from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_sample_data(input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    np.random.seed(42)

    items = ["ITEM_A", "ITEM_B", "ITEM_C", "ITEM_D", "ITEM_E"]
    fornecedores = ["Fornecedor X", "Fornecedor Y", "Fornecedor Z"]

    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=120, freq="D")
    rows = []
    for d in dates:
        for item in items:
            if np.random.rand() < 0.7:
                rows.append(
                    {
                        "Data": d,
                        "Produto": item,
                        "Tipo": "SAIDA",
                        "Quantidade": int(np.random.randint(1, 8)),
                        "Custo": round(float(np.random.uniform(8, 20)), 2),
                        "Fornecedor": np.random.choice(fornecedores),
                        "Prazo": int(np.random.randint(2, 12)),
                    }
                )
            if np.random.rand() < 0.25:
                rows.append(
                    {
                        "Data": d,
                        "Produto": item,
                        "Tipo": "ENTRADA",
                        "Quantidade": int(np.random.randint(4, 15)),
                        "Custo": round(float(np.random.uniform(7, 18)), 2),
                        "Fornecedor": np.random.choice(fornecedores),
                        "Prazo": int(np.random.randint(2, 12)),
                    }
                )

    vendas = pd.DataFrame(rows)
    produtos = pd.DataFrame(
        {
            "item": items,
            "descrição": [f"Produto {x[-1]}" for x in items],
            "categoria": ["Cat1", "Cat2", "Cat1", "Cat3", "Cat2"],
            "fornecedor padrão": ["Fornecedor X", "Fornecedor Y", "Fornecedor Y", "Fornecedor Z", "Fornecedor X"],
            "lead_time": [5, 8, 6, 10, 7],
            "custo padrão": [11.0, 15.0, 13.0, 18.0, 9.0],
            "estoque mínimo": [25, 20, 18, 30, 15],
            "estoque máximo": [120, 90, 80, 150, 70],
        }
    )
    estoque = pd.DataFrame({"item": items, "estoque atual": [40, 12, 75, 20, 9]})

    vendas.to_excel(input_dir / "Vendas.xlsx", index=False)
    produtos.to_excel(input_dir / "Produtos.xlsx", index=False)
    estoque.to_excel(input_dir / "Estoque.xlsx", index=False)
