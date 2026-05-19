from bo_app.init_db import init_db
from bo_app.db import SessionLocal
from bo_app.services.bo_service import BOService


def test_create_bo_and_search():
    init_db()
    s = SessionLocal()
    svc = BOService(s)
    bo = svc.create_bo({"title": "Falha no servidor", "summary": "queda no setor X", "category": "Infra"})
    assert bo.id > 0
    rows = svc.repo.search("servidor*")
    assert rows


def test_add_link():
    init_db()
    s = SessionLocal()
    svc = BOService(s)
    bo = svc.create_bo({"title": "Teste link"})
    svc.add_link(bo.id, "https://example.com")
    assert True
