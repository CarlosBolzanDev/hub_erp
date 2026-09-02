from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import BACKEND_DIR, settings

BACKEND_DIR.joinpath("data").mkdir(parents=True, exist_ok=True)
connect_args = {"check_same_thread": False} if settings.database_url_resolved.startswith("sqlite") else {}
engine = create_engine(settings.database_url_resolved, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
