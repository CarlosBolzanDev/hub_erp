from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.security import verify_password
from app.services.user_service import get_by_email
def authenticate(db: Session, email: str, password: str):
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash) or not user.is_active: return None
    user.last_login = datetime.now(timezone.utc); db.commit(); db.refresh(user); return user
