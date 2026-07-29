"""XML parsing and classification rules for Brazilian NF-e documents."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from xml.etree import ElementTree as ET


class NFeType(StrEnum):
    ESTORNO_CREDITO = "ESTORNO_CREDITO"
    DEVOLUCAO = "DEVOLUCAO"
    TRANSFERENCIA = "TRANSFERENCIA"
    SAIDA = "SAIDA"
    DESCONHECIDO = "DESCONHECIDO"


@dataclass(slots=True)
class NFeData:
    number: str | None
    nat_op: str
    tp_nf: str
    fin_nfe: str
    emit_cnpj: str
    dest_cnpj: str
    cfops: list[str]
    product_names: list[str]
    additional_info: str


@dataclass(slots=True)
class ClassificationResult:
    nfe_type: NFeType
    data: NFeData
    reason: str


class NFeParseError(ValueError):
    """Raised when an XML cannot be parsed as a usable NF-e file."""


def normalize_text(value: str | None) -> str:
    """Normalize text for accent-insensitive, case-insensitive matching."""

    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", without_accents).strip().upper()


class NFeClassifier:
    """Read NF-e 4.00 XML files and apply priority-based rules."""

    DEVOLUCAO_CFOPS = ("1202", "2202", "1411", "2411")

    def parse(self, xml_path: Path) -> NFeData:
        try:
            tree = ET.parse(xml_path)
        except ET.ParseError as exc:
            raise NFeParseError(f"XML inválido ou corrompido: {exc}") from exc
        except OSError as exc:
            raise NFeParseError(f"Não foi possível ler o arquivo: {exc}") from exc

        root = tree.getroot()
        number = self._text(root, "nNF")
        return NFeData(
            number=number,
            nat_op=self._text(root, "natOp"),
            tp_nf=self._text(root, "tpNF"),
            fin_nfe=self._text(root, "finNFe"),
            emit_cnpj=self._text_under(root, "emit", "CNPJ"),
            dest_cnpj=self._text_under(root, "dest", "CNPJ"),
            cfops=[value for value in self._texts(root, "CFOP") if value],
            product_names=[value for value in self._texts(root, "xProd") if value],
            additional_info=" ".join(value for value in self._texts(root, "infAdFisco") + self._texts(root, "infCpl") if value),
        )

    def classify(self, xml_path: Path) -> ClassificationResult:
        data = self.parse(xml_path)
        haystack = normalize_text(" ".join([*data.product_names, data.additional_info]))
        nat_op = normalize_text(data.nat_op)

        if any(term in haystack for term in ("ESTORNO DE CREDITO", "E-PTA", "ESTORNO")):
            return ClassificationResult(NFeType.ESTORNO_CREDITO, data, "estorno identificado em produto/informações adicionais")

        if "DEVOLUCAO" in nat_op or data.fin_nfe == "4" or any(cfop.startswith(self.DEVOLUCAO_CFOPS) for cfop in data.cfops):
            return ClassificationResult(NFeType.DEVOLUCAO, data, "regra de devolução atendida")

        if data.fin_nfe == "3" or (data.emit_cnpj and data.emit_cnpj == data.dest_cnpj):
            return ClassificationResult(NFeType.TRANSFERENCIA, data, "finalidade 3 ou mesmo CNPJ emitente/destinatário")

        if data.tp_nf == "1" and ("VENDA" in nat_op or "VENDAS" in nat_op):
            return ClassificationResult(NFeType.SAIDA, data, "tpNF 1 com natureza de venda")

        return ClassificationResult(NFeType.DESCONHECIDO, data, "nenhuma regra atendida")

    def _text(self, root: ET.Element, local_name: str) -> str:
        found = self._find_first(root, local_name)
        return (found.text or "").strip() if found is not None else ""

    def _texts(self, root: ET.Element, local_name: str) -> list[str]:
        return [(element.text or "").strip() for element in root.iter() if self._local_name(element.tag) == local_name]

    def _text_under(self, root: ET.Element, parent_name: str, child_name: str) -> str:
        for parent in root.iter():
            if self._local_name(parent.tag) == parent_name:
                for child in parent:
                    if self._local_name(child.tag) == child_name:
                        return (child.text or "").strip()
        return ""

    def _find_first(self, root: ET.Element, local_name: str) -> ET.Element | None:
        for element in root.iter():
            if self._local_name(element.tag) == local_name:
                return element
        return None

    def _local_name(self, tag: str) -> str:
        return tag.rsplit("}", 1)[-1]
