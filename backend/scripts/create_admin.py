"""Create the initial administrator from environment variables."""
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.services.user_service import get_by_email


def main() -> None:
    if not settings.admin_password:
        raise SystemExit("Define ADMIN_PASSWORD in backend/.env before creating an administrator.")

    with SessionLocal() as db:
        if get_by_email(db, settings.admin_email):
            raise SystemExit("An administrator with this e-mail already exists.")
        db.add(User(name="Administrador", email=settings.admin_email, password_hash=hash_password(settings.admin_password), role="admin"))
        db.commit()
    print("Administrator created successfully.")


if __name__ == "__main__":
    main()
