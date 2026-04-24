# Scraper Tecfil (Catálogo de Automóveis)

Projeto em Python para extração automática do catálogo de autopeças da Tecfil e persistência com SQLAlchemy.

## Arquivos

- `scraper.py`: executável principal com scraping (requests + fallback Playwright), paginação, normalização e upsert.
- `db.py`: configuração de conexão por variáveis de ambiente e criação automática do banco.
- `models.py`: modelo ORM e chave única para evitar duplicidade.
- `schema.sql`: script SQL de criação do banco/tabela.
- `requirements.txt`: dependências do projeto.

## Requisitos

- Python 3.11+
- MySQL (padrão) ou SQLite (opcional)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Exemplo de `.env`

```env
# Banco
DB_TYPE=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=senha
DB_NAME=tecfil_catalog

# Alternativa SQLite
# DB_TYPE=sqlite
# SQLITE_PATH=./tecfil_catalog.db

# Scraper
TARGET_URL=https://tecfil-catalago.gruposofape.com.br/CatalogoTecfil/resultadoPorCategoria.xhtml?search-term=categoria-automoveis
REQUEST_TIMEOUT=30
DELAY_MIN=0.8
DELAY_MAX=1.8
HEADLESS=true
LOG_LEVEL=INFO
```

## Execução

```bash
python scraper.py
```

## Como funciona

1. Verifica e cria o banco (MySQL) se não existir.
2. Verifica e cria a tabela com SQLAlchemy (`Base.metadata.create_all`).
3. Tenta scraping via `requests` (sessão com retry/cookies, ViewState e paginação).
4. Se necessário, usa fallback Playwright (headless por padrão).
5. Faz `upsert` (insert/update) para evitar duplicidade de registros.
6. Salva `source_url` em todos os registros.

## Observações

- O mapeamento das colunas é detectado pelo cabeçalho da tabela e normalizado.
- Valores vazios são convertidos para `NULL`.
- Há delay entre páginas e logs de progresso.
