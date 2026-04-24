# Scraper Tecfil (Catálogo de Automóveis) + SQLite local

Projeto Python focado somente em:
1. scraping do catálogo Tecfil;
2. gravação dos dados em banco SQLite local.

Sem dependências de web app, API ou frontend.

## Estrutura

- `scraper.py`: execução principal do scraping e persistência.
- `db.py`: configuração e criação automática do arquivo `.db` local.
- `models.py`: modelo ORM e chave única anti-duplicidade.
- `schema.sql`: criação de tabela/índice único no SQLite.
- `requirements.txt`: dependências mínimas.

## Requisitos

- Python 3.11+

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Exemplo de `.env`

```env
SQLITE_PATH=./data/tecfil_catalog.db
TARGET_URL=https://tecfil-catalago.gruposofape.com.br/CatalogoTecfil/resultadoPorCategoria.xhtml?search-term=categoria-automoveis
REQUEST_TIMEOUT=30
DELAY_MIN=0.8
DELAY_MAX=1.8
LOG_LEVEL=INFO
```

## Execução

```bash
python scraper.py
```

## Comportamento

- Se o arquivo SQLite não existir, ele é criado automaticamente.
- Se a tabela não existir, ela é criada automaticamente.
- O scraper mantém sessão HTTP, trata retry e timeout, processa ViewState/JSF e paginação.
- Valores vazios viram `NULL`.
- Inserção é feita com lógica de upsert para não duplicar registros (com base na chave única definida).
- Cada registro salva também a URL de origem (`source_url`).
