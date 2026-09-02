from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.models.user import User

def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user
