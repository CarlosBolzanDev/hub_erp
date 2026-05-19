from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from bo_app.config import DB_PATH

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

@event.listens_for(engine, "connect")
def _set_pragma(dbapi_connection, _):
    c = dbapi_connection.cursor()
    c.execute("PRAGMA foreign_keys=ON")
    c.close()
