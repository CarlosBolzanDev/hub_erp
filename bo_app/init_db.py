from sqlalchemy import text
from bo_app.db import engine
from bo_app.models import Base

def init_db():
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("CREATE VIRTUAL TABLE IF NOT EXISTS bo_search USING fts5(bo_id UNINDEXED, content)"))

if __name__ == "__main__":
    init_db()
