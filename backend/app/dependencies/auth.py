import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.user_service import get_user
security = HTTPBearer()
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try: user_id = int(decode_access_token(credentials.credentials))
    except (jwt.PyJWTError, KeyError, ValueError): raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada")
    user = get_user(db, user_id)
    if not user or not user.is_active: raise HTTPException(status_code=401, detail="Usuário não autorizado")
    return user
def require_admin(user = Depends(get_current_user)):
    if user.role != "admin": raise HTTPException(status_code=403, detail="Permissão insuficiente")
    return user
