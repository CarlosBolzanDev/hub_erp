from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: datetime
    last_login: datetime | None
