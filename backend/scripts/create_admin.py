"""Create or update the initial administrator after `alembic upgrade head`."""
import getpass
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import select
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

email = os.getenv("ADMIN_EMAIL", "admin@example.com").strip().lower()
name = os.getenv("ADMIN_NAME", "Administrador").strip()
password = os.getenv("ADMIN_PASSWORD") or getpass.getpass("Senha do administrador: ")
if len(password) < 8:
    raise SystemExit("A senha deve ter ao menos 8 caracteres.")

with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        user.name, user.password_hash, user.role, user.is_active = name, hash_password(password), "admin", True
        message = "Administrador atualizado"
    else:
        db.add(User(name=name, email=email, password_hash=hash_password(password), role="admin", is_active=True))
        message = "Administrador criado"
    db.commit()
print(f"{message}: {email}")
