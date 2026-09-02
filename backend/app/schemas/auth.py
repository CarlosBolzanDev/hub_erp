from pydantic import BaseModel, EmailStr
from .user import UserRead
class LoginRequest(BaseModel): email: EmailStr; password: str
class TokenResponse(BaseModel): access_token: str; token_type: str = "bearer"; user: UserRead
