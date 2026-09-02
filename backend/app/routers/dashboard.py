from typing import Annotated
from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary")
def summary(_: Annotated[User, Depends(get_current_user)]):
    return {"orders": 0, "pending": 0, "picking": 0, "completed": 0}
