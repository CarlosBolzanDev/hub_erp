import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.dependencies.auth import get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import authenticate
router = APIRouter(prefix="/api/auth", tags=["Authentication"]); log=logging.getLogger(__name__)
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session=Depends(get_db)):
    user=authenticate(db,payload.email,payload.password)
    if not user:
        log.warning("Failed login attempt for %s", payload.email)
        raise HTTPException(status_code=401,detail="E-mail ou senha inválidos")
    log.info("User %s logged in", user.id); return TokenResponse(access_token=create_access_token(str(user.id)),user=user)
@router.get("/me", response_model=UserRead)
def me(user=Depends(get_current_user)): return user
@router.post("/logout", status_code=204)
def logout(user=Depends(get_current_user)): log.info("User %s logged out",user.id)
