from datetime import date
from pydantic import BaseModel

class BOCreate(BaseModel):
    title: str
    category: str = ""
    subcategory: str = ""
    status: str = "aberto"
    priority: str = "media"
    sector: str = ""
    owner: str = ""
    occurrence_date: date | None = None
    summary: str = ""
    observations: str = ""
