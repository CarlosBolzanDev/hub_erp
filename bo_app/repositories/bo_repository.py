from sqlalchemy import text
from bo_app.models import BO

class BORepository:
    def __init__(self, session):
        self.session = session

    def create(self, data):
        bo = BO(**data)
        self.session.add(bo)
        self.session.flush()
        return bo

    def list_all(self):
        return self.session.query(BO).filter_by(is_deleted=False).order_by(BO.created_at.desc()).all()

    def get(self, bo_id:int):
        return self.session.get(BO, bo_id)

    def search(self, term: str):
        return self.session.execute(text("SELECT bo_id FROM bo_search WHERE bo_search MATCH :q"), {"q": term}).fetchall()
