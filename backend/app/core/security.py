from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from .config import settings
password_hash = PasswordHash.recommended()
def hash_password(password: str) -> str: return password_hash.hash(password)
def verify_password(password: str, hashed: str) -> bool: return password_hash.verify(password, hashed)
def create_access_token(subject: str) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
def decode_access_token(token: str) -> str:
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])["sub"]
