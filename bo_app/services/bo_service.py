import csv
import shutil
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab, Image
import pytesseract
import mimetypes
import requests
from bs4 import BeautifulSoup
from bo_app.config import ATTACHMENTS_DIR, EXPORTS_DIR, BACKUPS_DIR, DB_PATH
from bo_app.models import BOEvent, Attachment, LinkItem
from bo_app.repositories.bo_repository import BORepository

class BOService:
    def __init__(self, session):
        self.session = session
        self.repo = BORepository(session)

    def create_bo(self, payload: dict, user="operador"):
        bo = self.repo.create(payload)
        self.add_event(bo.id, "criacao", "BO criado", payload.get("summary", ""), user)
        self._sync_fts(bo.id)
        self.session.commit()
        return bo

    def add_event(self, bo_id, event_type, title, desc, user="operador", metadata="{}"):
        self.session.add(BOEvent(bo_id=bo_id, event_type=event_type, title=title, description=desc, created_by=user, metadata_json=metadata))

    def add_attachment(self, bo_id:int, src_path: str, comment="", do_ocr=True):
        src = Path(src_path)
        target_dir = ATTACHMENTS_DIR / str(bo_id)
        target_dir.mkdir(parents=True, exist_ok=True)
        dst = target_dir / src.name
        shutil.copy2(src, dst)
        mime, _ = mimetypes.guess_type(dst)
        ocr_text = ""
        if do_ocr and (mime or "").startswith("image/"):
            try:
                ocr_text = pytesseract.image_to_string(Image.open(dst))
            except Exception:
                ocr_text = ""
        att = Attachment(bo_id=bo_id, file_name=dst.name, original_name=src.name, file_path=str(dst), file_type="image" if (mime or "").startswith("image/") else "file", mime_type=mime or "application/octet-stream", size_bytes=dst.stat().st_size, ocr_text=ocr_text, comment=comment)
        self.session.add(att)
        self.add_event(bo_id, "anexo", "Anexo incluído", dst.name)
        self._sync_fts(bo_id)
        self.session.commit()

    def add_link(self, bo_id, url, comment=""):
        title = description = ""
        domain = url.split("/")[2] if "//" in url else url
        try:
            r = requests.get(url, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            title = (soup.title.text.strip() if soup.title else "")[:255]
            meta = soup.find("meta", attrs={"name": "description"})
            description = (meta.get("content", "") if meta else "")[:1000]
        except Exception:
            pass
        self.session.add(LinkItem(bo_id=bo_id, url=url, domain=domain, title=title, description=description, fetched_at=datetime.utcnow(), comment=comment))
        self.add_event(bo_id, "link", "Link incluído", url)
        self._sync_fts(bo_id)
        self.session.commit()

    def _sync_fts(self, bo_id):
        bo = self.repo.get(bo_id)
        attachments_text = " ".join(a.ocr_text for a in self.session.query(Attachment).filter_by(bo_id=bo_id).all())
        links_text = " ".join((l.title or "") + " " + (l.description or "") for l in self.session.query(LinkItem).filter_by(bo_id=bo_id).all())
        tags = ""
        content = f"{bo.title} {bo.summary} {bo.observations} {bo.category} {bo.subcategory} {bo.owner} {bo.sector} {tags} {attachments_text} {links_text}"
        from sqlalchemy import text
        self.session.execute(text("DELETE FROM bo_search WHERE bo_id=:id"), {"id": bo_id})
        self.session.execute(text("INSERT INTO bo_search(bo_id, content) VALUES(:id,:c)"), {"id": bo_id, "c": content})

    def export_csv(self):
        out = EXPORTS_DIR / f"bo_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        rows = self.repo.list_all()
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["id", "title", "status", "priority", "owner", "category", "created_at"])
            for bo in rows:
                w.writerow([bo.id, bo.title, bo.status, bo.priority, bo.owner, bo.category, bo.created_at.isoformat()])
        return out

    def backup_db(self):
        dst = BACKUPS_DIR / f"bo_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(DB_PATH, dst)
        return dst
