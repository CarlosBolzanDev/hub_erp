from sqlalchemy import text
from registro_operacional.app.database.session import engine
from registro_operacional.app.models.base import Base
from registro_operacional.app.models import occurrence  # noqa

def init_db():
    Base.metadata.create_all(engine)
    with engine.begin() as c:
        c.execute(text("CREATE VIRTUAL TABLE IF NOT EXISTS occurrence_fts USING fts5(occurrence_id UNINDEXED, content)"))
