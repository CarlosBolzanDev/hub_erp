# Hub ERP

Base SaaS local para operações, construída com **FastAPI, SQLAlchemy, Alembic e SQLite** no backend e HTML/CSS/JavaScript puro no frontend. Esta primeira fase inclui login JWT, dashboard, navegação responsiva, tema claro/escuro e páginas preparadas para módulos futuros.

## Estrutura

```text
backend/                 API FastAPI, migrations e testes
frontend/                Interface estática servida por HTTP
backend/data/app.db      Banco SQLite local, criado por migration
```

Não há Docker, containers ou banco de dados externo neste projeto.

## Execução no Windows

### CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r backend\requirements.txt
copy backend\.env.example backend\.env
cd backend
alembic upgrade head
set ADMIN_PASSWORD=uma-senha-segura
PYTHONPATH=. python scripts\create_admin.py
uvicorn app.main:app --reload
```

Em outro terminal, na raiz do projeto:

```cmd
python -m http.server 5500 --directory frontend
```

### PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
Set-Location backend
alembic upgrade head
$env:ADMIN_PASSWORD = "uma-senha-segura"
$env:PYTHONPATH = "."
python scripts\create_admin.py
uvicorn app.main:app --reload
```

Em outro terminal PowerShell, na raiz:

```powershell
python -m http.server 5500 --directory frontend
```

Abra `http://localhost:5500`. A API expõe `http://localhost:8000/docs`, `http://localhost:8000/redoc` e `GET /health`.

> O administrador usa `admin@example.com` por padrão. Personalize-o antes da criação com `ADMIN_EMAIL` e `ADMIN_NAME` se necessário. Nunca versione `backend/.env` nem o banco local.

## Fluxo de dados

O navegador usa a Fetch API para chamar a API FastAPI. A autenticação retorna um JWT, armazenado apenas no navegador. O backend valida o token, executa consultas via SQLAlchemy e é a única camada que acessa o arquivo SQLite.

## Migrations e testes

Execute migrations sempre a partir de `backend`:

```cmd
alembic upgrade head
```

Para testes:

```cmd
pytest
```
