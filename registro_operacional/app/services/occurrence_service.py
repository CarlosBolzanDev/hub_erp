import csv
import json
import shutil
import mimetypes
from datetime import datetime
from pathlib import Path
from sqlalchemy import text
from PIL import ImageGrab, Image, ImageDraw
import pytesseract
import requests
from bs4 import BeautifulSoup
from registro_operacional.app.config.settings import ATTACHMENTS_DIR, EXPORTS_DIR, BACKUPS_DIR, DB_PATH
from registro_operacional.app.logging.logger import logger
from registro_operacional.app.models.occurrence import OccurrenceEvent, Attachment, LinkItem, RaciPerson, RaciAssignment
from registro_operacional.app.repositories.occurrence_repository import OccurrenceRepository

class OccurrenceService:
    def __init__(self, session):
        self.session = session
        self.repo = OccurrenceRepository(session)

    def open_occurrence(self, payload, user="operador"):
        code = f"OC-{datetime.utcnow().strftime('%Y%m%d')}-{int(datetime.utcnow().timestamp())%100000}"
        occ = self.repo.create({**payload, "status": "Aberta", "code": code})
        self._event(occ.id, "abertura", "Ocorrência aberta", occ.summary, user)
        self._sync_fts(occ.id); self.session.commit(); return occ

    def update_status(self, occurrence_id, status, note="", user="operador"):
        occ = self.repo.get(occurrence_id); occ.status = status
        if status == "Finalizada": occ.closed_at = datetime.utcnow(); occ.final_result = note
        self._event(occ.id, "mudanca_status", f"Status alterado para {status}", note, user)
        self._sync_fts(occ.id); self.session.commit()

    def finalize_occurrence(self, occurrence_id, final_result, user="operador"):
        if not final_result.strip(): raise ValueError("Resultado final obrigatório")
        self.update_status(occurrence_id, "Finalizada", final_result, user)

    def reopen_occurrence(self, occurrence_id, reason, user="operador"):
        if not reason.strip(): raise ValueError("Motivo obrigatório")
        occ = self.repo.get(occurrence_id); occ.closed_at = None
        self.update_status(occurrence_id, "Reaberta", reason, user)

    def _event(self, occ_id, t, title, desc, user="operador", meta=None):
        self.session.add(OccurrenceEvent(occurrence_id=occ_id, event_type=t, title=title, description=desc, created_by=user, metadata_json=json.dumps(meta or {})))

    def add_link(self, occ_id, url, comment=""):
        domain = url.split('/')[2] if '//' in url else url; title = description = ""
        try:
            r = requests.get(url, timeout=5); s = BeautifulSoup(r.text, "html.parser")
            title = (s.title.text.strip() if s.title else "")[:255]
            md = s.find("meta", attrs={"name":"description"}); description = (md.get("content","") if md else "")[:1000]
        except Exception as e:
            logger.warning(f"falha metadados link: {e}")
        self.session.add(LinkItem(occurrence_id=occ_id, url=url, domain=domain, title=title, description=description, fetched_at=datetime.utcnow(), comment=comment))
        self._event(occ_id, "link", "Link adicionado", url); self._sync_fts(occ_id); self.session.commit()

    def add_attachment(self, occ_id, source_path, comment="", is_important=False):
        src = Path(source_path); d = ATTACHMENTS_DIR / str(occ_id); d.mkdir(parents=True, exist_ok=True)
        stored = f"{int(datetime.utcnow().timestamp())}_{src.name}"; dst = d / stored; shutil.copy2(src, dst)
        mime, _ = mimetypes.guess_type(dst); ocr = ""
        if (mime or "").startswith("image/"):
            try: ocr = pytesseract.image_to_string(Image.open(dst))
            except Exception: pass
        self.session.add(Attachment(occurrence_id=occ_id, original_name=src.name, stored_name=stored, file_path=str(dst), file_type="image" if (mime or "").startswith("image/") else "file", mime_type=mime or "application/octet-stream", size_bytes=dst.stat().st_size, ocr_text=ocr, comment=comment, is_important=is_important))
        self._event(occ_id, "anexo", "Anexo adicionado", src.name); self._sync_fts(occ_id); self.session.commit()

    def paste_print_from_clipboard(self, occ_id, comment="print colado"):
        img = ImageGrab.grabclipboard()
        if hasattr(img, "save"):
            temp = ATTACHMENTS_DIR / f"_clipboard_{datetime.utcnow().timestamp()}.png"; img.save(temp)
            self.add_attachment(occ_id, str(temp), comment=comment, is_important=True)
            self._event(occ_id, "print_colado", "Print colado", comment); self.session.commit(); return True
        return False

    def add_raci_assignment(self, occ_id, name, role="", sector="", responsible=False, accountable=False, consulted=False, informed=False, note=""):
        p = RaciPerson(name=name, role=role, sector=sector, active=True); self.session.add(p); self.session.flush()
        self.session.add(RaciAssignment(occurrence_id=occ_id, raci_person_id=p.id, responsible=responsible, accountable=accountable, consulted=consulted, informed=informed, note=note))
        self._event(occ_id, "raci", "RACI atualizado", f"{name} associado"); self._sync_fts(occ_id); self.session.commit()

    def _sync_fts(self, occ_id):
        occ = self.repo.get(occ_id)
        ev = " ".join(x.description for x in self.session.query(OccurrenceEvent).filter_by(occurrence_id=occ_id).all())
        at = " ".join(x.ocr_text for x in self.session.query(Attachment).filter_by(occurrence_id=occ_id).all())
        lk = " ".join((x.title or "") + " " + (x.description or "") for x in self.session.query(LinkItem).filter_by(occurrence_id=occ_id).all())
        rc = " ".join(x.name for x in self.session.query(RaciPerson).join(RaciAssignment, RaciPerson.id==RaciAssignment.raci_person_id).filter(RaciAssignment.occurrence_id==occ_id).all())
        blob = f"{occ.title} {occ.summary} {occ.observations} {occ.tags} {occ.category} {occ.subcategory} {occ.owner} {ev} {at} {lk} {rc}"
        self.session.execute(text("DELETE FROM occurrence_fts WHERE occurrence_id=:i"), {"i": occ_id})
        self.session.execute(text("INSERT INTO occurrence_fts(occurrence_id, content) VALUES(:i,:c)"), {"i": occ_id, "c": blob})

    def export_json(self, occ_id):
        occ = self.repo.get(occ_id)
        out = EXPORTS_DIR / f"ocorrencia_{occ_id}.json"
        out.write_text(json.dumps({"dados": occ.title, "status": occ.status, "resultado_final": occ.final_result}, ensure_ascii=False, indent=2))
        return out

    def export_csv(self, occ_id):
        occ = self.repo.get(occ_id)
        out = EXPORTS_DIR / f"ocorrencia_{occ_id}.csv"
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["id","codigo","titulo","status","resultado_final"]); w.writerow([occ.id, occ.code, occ.title, occ.status, occ.final_result])
        return out

    def export_pdf(self, occ_id):
        out = EXPORTS_DIR / f"ocorrencia_{occ_id}.pdf"
        img = Image.new("RGB", (1200, 1600), "white"); d = ImageDraw.Draw(img); d.text((40, 40), f"Ocorrência {occ_id}", fill="black")
        img.save(out, "PDF")
        return out

    def backup_database(self):
        b = BACKUPS_DIR / f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.db"; shutil.copy2(DB_PATH, b); return b
