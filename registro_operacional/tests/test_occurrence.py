from registro_operacional.app.database.init_db import init_db
from registro_operacional.app.database.session import SessionLocal
from registro_operacional.app.services.occurrence_service import OccurrenceService


def test_open_and_finalize_occurrence():
    init_db()
    s = SessionLocal()
    svc = OccurrenceService(s)
    occ = svc.open_occurrence({"title":"Teste"})
    assert occ.status == "Aberta"
    svc.finalize_occurrence(occ.id, "Resolvido")
    assert svc.repo.get(occ.id).status == "Finalizada"


def test_search_and_raci_assignment():
    init_db()
    s = SessionLocal()
    svc = OccurrenceService(s)
    occ = svc.open_occurrence({"title":"Falha de rede", "summary":"router"})
    svc.add_raci_assignment(occ.id, name="Ana")
    ids = svc.repo.search_ids("rede*")
    assert occ.id in ids
