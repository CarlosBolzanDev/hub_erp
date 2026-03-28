# Dashboard Flask + SQLite (local)

## Requisitos
- Python 3.10+
- Banco SQLite real (padrão): `C:\Users\ADM\Desktop\Invex-web\backend_bd\ml_backend.db`

## Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Variável opcional para trocar o banco:
```bash
set ML_BACKEND_DB_PATH=C:\caminho\outro.db
```

## Frontend
Opção 1 (recomendada): servidor estático simples.
```bash
cd frontend
python -m http.server 5500
```
Acesse: `http://127.0.0.1:5500`

## Conexão frontend/backend
- O frontend chama a API em `http://127.0.0.1:5000/api`.
- Você pode alterar em **Configurações** (persistido em `localStorage`).
