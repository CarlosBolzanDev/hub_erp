from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from registro_operacional.app.models.base import Base

class Occurrence(Base):
    __tablename__ = "occurrence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(120), default="")
    subcategory: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(32), default="Aberta")  # Aberta, Em andamento, Pendente, Finalizada, Reaberta
    priority: Mapped[str] = mapped_column(String(32), default="Média")
    sector: Mapped[str] = mapped_column(String(120), default="")
    owner: Mapped[str] = mapped_column(String(120), default="")
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    final_result: Mapped[str] = mapped_column(Text, default="")
    observations: Mapped[str] = mapped_column(Text, default="")
    tags: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

class OccurrenceEvent(Base):
    __tablename__ = "occurrence_event"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(ForeignKey("occurrence.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(120), default="system")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

class Attachment(Base):
    __tablename__ = "attachment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(ForeignKey("occurrence.id", ondelete="CASCADE"))
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(80), default="file")
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    ocr_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    comment: Mapped[str] = mapped_column(Text, default="")
    thumbnail_path: Mapped[str] = mapped_column(String(500), default="")

class LinkItem(Base):
    __tablename__ = "link_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(ForeignKey("occurrence.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(1000))
    domain: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    comment: Mapped[str] = mapped_column(Text, default="")

class RaciPerson(Base):
    __tablename__ = "raci_person"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    role: Mapped[str] = mapped_column(String(120), default="")
    sector: Mapped[str] = mapped_column(String(120), default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class RaciAssignment(Base):
    __tablename__ = "raci_assignment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(ForeignKey("occurrence.id", ondelete="CASCADE"))
    raci_person_id: Mapped[int] = mapped_column(ForeignKey("raci_person.id", ondelete="CASCADE"))
    responsible: Mapped[bool] = mapped_column(Boolean, default=False)
    accountable: Mapped[bool] = mapped_column(Boolean, default=False)
    consulted: Mapped[bool] = mapped_column(Boolean, default=False)
    informed: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
