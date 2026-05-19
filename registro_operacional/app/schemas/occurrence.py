from pydantic import BaseModel

class OccurrenceCreate(BaseModel):
    title: str
    summary: str = ""
    category: str = ""
    subcategory: str = ""
    priority: str = "Média"
    sector: str = ""
    owner: str = ""
    tags: str = ""
