# Registro Operacional (Ocorrências)

Sistema desktop local-first para gestão de ocorrências operacionais com timeline, anexos, links, RACI, busca FTS5 e auditoria.

## Stack
Python 3.11+, PySide6, SQLite, SQLAlchemy 2.x, Alembic, FTS5, Pillow, pytesseract, requests, BeautifulSoup4, pydantic, loguru, qdarktheme, pytest.

## Executar
```bash
pip install -r requirements.txt
python -m registro_operacional.app.main
```

## Migrações
Estrutura Alembic incluída em `alembic/`. Banco inicializa automaticamente na execução.

## Funcionalidades implementadas
- Abertura, finalização e reabertura de ocorrência com eventos de timeline.
- Busca global via FTS5 (ocorrência, eventos, OCR, links e nomes RACI).
- Anexos por upload, OCR opcional e print via clipboard.
- Links com captura de metadados.
- Aba RACI com associação de pessoas e papéis.
- Exportação JSON e backup de banco.
- UI com abas: Resumo, Timeline, Anexos, Links, RACI, Histórico, Observações.
