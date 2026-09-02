from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.user import User

def test_login_returns_a_jwt_for_valid_credentials():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    testing_session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with testing_session() as db:
        db.add(User(name="Administrador", email="admin@example.com", password_hash=hash_password("secure-password"), role="admin"))
        db.commit()

    def override_get_db():
        with testing_session() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).post("/api/auth/login", json={"email": "admin@example.com", "password": "secure-password"})
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["email"] == "admin@example.com"
