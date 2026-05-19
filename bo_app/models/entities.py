from datetime import datetime, date
from sqlalchemy import String, Integer, DateTime, Date, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bo_app.models.base import Base

class BO(Base):
    __tablename__ = "bo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(120), default="")
    subcategory: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(60), default="aberto")
    priority: Mapped[str] = mapped_column(String(60), default="media")
    sector: Mapped[str] = mapped_column(String(120), default="")
    owner: Mapped[str] = mapped_column(String(120), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    occurrence_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    summary: Mapped[str] = mapped_column(Text, default="")
    observations: Mapped[str] = mapped_column(Text, default="")
    final_result: Mapped[str] = mapped_column(Text, default="")
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

class BOEvent(Base):
    __tablename__ = "bo_event"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bo_id: Mapped[int] = mapped_column(ForeignKey("bo.id", ondelete="CASCADE"))
    event_type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(String(120), default="system")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

class Attachment(Base):
    __tablename__ = "attachment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bo_id: Mapped[int] = mapped_column(ForeignKey("bo.id", ondelete="CASCADE"))
    file_name: Mapped[str] = mapped_column(String(255))
    original_name: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(80), default="file")
    mime_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ocr_text: Mapped[str] = mapped_column(Text, default="")
    comment: Mapped[str] = mapped_column(Text, default="")
    thumbnail_path: Mapped[str] = mapped_column(String(500), default="")

class LinkItem(Base):
    __tablename__ = "link_item"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bo_id: Mapped[int] = mapped_column(ForeignKey("bo.id", ondelete="CASCADE"))
    url: Mapped[str] = mapped_column(String(1000))
    domain: Mapped[str] = mapped_column(String(255), default="")
    title: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    comment: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)

class BOTag(Base):
    __tablename__ = "bo_tag"
    bo_id: Mapped[int] = mapped_column(ForeignKey("bo.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True)
