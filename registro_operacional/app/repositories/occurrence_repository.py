from sqlalchemy import text
from registro_operacional.app.models.occurrence import Occurrence

class OccurrenceRepository:
    def __init__(self, session):
        self.session = session

    def create(self, data):
        obj = Occurrence(**data)
        self.session.add(obj)
        self.session.flush()
        return obj

    def get(self, occurrence_id):
        return self.session.get(Occurrence, occurrence_id)

    def list_filtered(self, filters: dict | None = None):
        q = self.session.query(Occurrence).filter_by(is_deleted=False)
        f = filters or {}
        if f.get("status"): q = q.filter(Occurrence.status == f["status"])
        if f.get("category"): q = q.filter(Occurrence.category == f["category"])
        if f.get("priority"): q = q.filter(Occurrence.priority == f["priority"])
        if f.get("owner"): q = q.filter(Occurrence.owner.ilike(f"%{f['owner']}%"))
        if f.get("sector"): q = q.filter(Occurrence.sector.ilike(f"%{f['sector']}%"))
        return q.order_by(Occurrence.created_at.desc()).all()

    def search_ids(self, q):
        return [r[0] for r in self.session.execute(text("SELECT occurrence_id FROM occurrence_fts WHERE occurrence_fts MATCH :q"), {"q": q}).fetchall()]
