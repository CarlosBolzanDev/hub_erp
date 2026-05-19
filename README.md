# BO Operacional (Desktop)

Aplicativo local em **Python 3.11+** para registro de ocorrências operacionais com timeline, anexos, links e busca avançada (FTS5).

## Requisitos
- Python 3.11+
- SQLite com FTS5
- Dependências:

```bash
pip install -e .[dev]
```

## Execução
```bash
python -m bo_app.main
```

## Inicialização do banco
O banco é criado automaticamente em `data/bo.db` na primeira execução.
Também é possível executar:

```bash
python scripts/init_db.py
```

## Funcionalidades
- Cadastro de BO com campos principais.
- Timeline de eventos auditáveis.
- Anexos com cópia para `data/attachments/<bo_id>/`.
- OCR opcional para imagens (quando pytesseract/tesseract disponível).
- Cadastro de links com metadados (title/description/domain).
- Busca global com FTS5 (texto do BO + anexos OCR + links).
- Filtros por status/categoria/prioridade/setor/responsável/período.
- Exportação CSV simples em `data/exports/`.
- Backups SQLite em `data/backups/`.

## Testes
```bash
pytest
```

## Estrutura
- `bo_app/models`: modelos SQLAlchemy.
- `bo_app/repositories`: acesso a dados.
- `bo_app/services`: regras de negócio.
- `bo_app/ui`: telas PySide6.

## Observação
Captura de tela rápida inclui:
- colar imagem do clipboard;
- importar arquivo de imagem;
- salvar em BO existente ou criar novo BO.
