from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CatalogRecord(Base):
    __tablename__ = "catalog_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    montadora = Column(String(255), nullable=True)
    modelo = Column(String(255), nullable=True)
    motor = Column(String(255), nullable=True)
    ano_de = Column(String(30), nullable=True)
    ano_ate = Column(String(30), nullable=True)
    descricao = Column(Text, nullable=True)
    combustivel = Column(String(100), nullable=True)
    local_ar_cabine = Column(String(255), nullable=True)

    ar_cabine = Column(String(255), nullable=True)
    ar_cabine_com_carvao = Column(String(255), nullable=True)
    ar_1 = Column(String(255), nullable=True)
    ar_2 = Column(String(255), nullable=True)
    lubrificante_1 = Column(String(255), nullable=True)
    lubrificante_2 = Column(String(255), nullable=True)
    combustivel_1 = Column(String(255), nullable=True)
    combustivel_2 = Column(String(255), nullable=True)
    cambio_automatico = Column(String(255), nullable=True)
    sedimentador_blindado = Column(String(255), nullable=True)
    sedimentador_com_copo = Column(String(255), nullable=True)
    sedimentador_sem_copo = Column(String(255), nullable=True)
    direcao = Column(String(255), nullable=True)
    transmissao = Column(String(255), nullable=True)
    outros = Column(String(255), nullable=True)
    outros_2 = Column(String(255), nullable=True)
    outros_3 = Column(String(255), nullable=True)

    source_url = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "montadora",
            "modelo",
            "motor",
            "ano_de",
            "ano_ate",
            "descricao",
            "combustivel",
            "local_ar_cabine",
            name="uq_catalog_record_core",
        ),
    )
