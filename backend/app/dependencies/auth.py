from typing import Annotated
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import ALGORITHM
from app.models.user import User

bearer_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: Annotated[str, Depends(bearer_scheme)], db: Annotated[Session, Depends(get_db)]) -> User:
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        subject = payload.get("sub")
        if not subject:
            raise credentials_error
        user = db.get(User, int(subject))
    except (jwt.PyJWTError, ValueError):
        raise credentials_error
    if not user or not user.is_active:
        raise credentials_error
    return user
