# Biply ERP

Base organizada para um SaaS de gestão operacional. O frontend estático consome exclusivamente a API FastAPI; a API acessa o PostgreSQL através de serviços e SQLAlchemy.

## Estrutura

```text
backend/app/{core,models,schemas,routers,services,dependencies,utils}
backend/migrations
backend/tests
frontend/{dashboard,orders,users,settings,picking,assets,components}
```

Os módulos de Pedidos, Usuários, Configurações e Picking estão presentes somente como páginas preparadas. Nesta fase não há CRUD, dados simulados ou APIs para esses módulos.

## Requisitos

- Python 3.12+
- PostgreSQL 16+

## Executar localmente

1. Crie um banco PostgreSQL e um usuário com acesso a ele.
2. Crie o ambiente virtual: `python3 -m venv .venv && source .venv/bin/activate`.
3. Instale as dependências: `pip install -r backend/requirements.txt`.
4. Copie o arquivo de ambiente: `cp backend/.env.example backend/.env`.
5. Em `backend/.env`, defina `DATABASE_URL`, uma `SECRET_KEY` longa e `ADMIN_PASSWORD` seguro.
6. Aplique a migration: `cd backend && alembic upgrade head`.
7. Crie o administrador inicial, uma única vez: `cd backend && PYTHONPATH=. python scripts/create_admin.py`.
8. Inicie a API, a partir de `backend/`: `uvicorn app.main:app --reload`.
9. Em outro terminal, sirva o frontend: `python3 -m http.server 5500 --directory frontend`; abra `http://localhost:5500`.

A documentação da API fica disponível em `http://localhost:8000/docs` e o health check em `http://localhost:8000/health`.

## Testes

Com o ambiente virtual ativo, execute `PYTHONPATH=backend pytest -q backend/tests` a partir da raiz do repositório.
