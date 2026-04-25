# Hub ERP - Kit merge layer

Este repositório contém uma implementação de referência para mesclagem de kits em dois níveis:

- `kit_family`: agrupa pelos filtros do kit sem `combustivel_2`
- `kit_variant`: separa por `combustivel_2` dentro da família
- `kit_application`: vincula registro original de catálogo à variante

## Arquivos principais

- `models.py`: modelos SQLAlchemy da tabela original e novas tabelas de kit
- `kit_merge.py`: regra de normalização, chave de família/variante, backfill idempotente e consultas
- `scripts/backfill_kits.py`: rotina executável
- `sql/001_create_kit_tables.sql`: SQL equivalente de criação

## Configuração

Variável opcional:

- `INCLUDE_MONTADORA_IN_FAMILY=true|false` (default `true`)

Quando `false`, montadora não participa do `family_key` e o agrupamento pode acontecer entre montadoras.

## Execução

1. Criar tabelas via ORM (automático no script) ou aplicar SQL:

```bash
python scripts/backfill_kits.py
# ou
sqlite3 hub_erp.db < sql/001_create_kit_tables.sql
```

2. Rodar preenchimento idempotente:

```bash
python scripts/backfill_kits.py
```

Pode rodar quantas vezes quiser: famílias/variantes/vínculos são reutilizados por chave única.
