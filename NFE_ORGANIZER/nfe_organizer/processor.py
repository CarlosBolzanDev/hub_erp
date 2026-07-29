"""File processing, logging, and duplicate-safe movement."""

from __future__ import annotations

import logging
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from .classifier import ClassificationResult, NFeClassifier, NFeParseError, NFeType

DESTINATION_FOLDERS = {
    NFeType.SAIDA: "SAIDA",
    NFeType.DEVOLUCAO: "DEVOLUCAO",
    NFeType.TRANSFERENCIA: "TRANSFERENCIA",
    NFeType.ESTORNO_CREDITO: "ESTORNO_CREDITO",
    NFeType.DESCONHECIDO: "DESCONHECIDOS",
}


@dataclass(slots=True)
class ProcessEvent:
    original_name: str
    nf_number: str
    nfe_type: str
    new_name: str
    destination: str
    status: str
    message: str


class NFeProcessor:
    """Classify, rename, move, and log incoming XML files."""

    def __init__(self, output_dir: Path, logger: logging.Logger) -> None:
        self.output_dir = output_dir
        self.logger = logger
        self.classifier = NFeClassifier()
        self.ensure_directories()

    def ensure_directories(self) -> None:
        for folder in DESTINATION_FOLDERS.values():
            (self.output_dir / folder).mkdir(parents=True, exist_ok=True)

    def process(self, xml_path: Path) -> ProcessEvent:
        original_name = xml_path.name
        self._wait_until_available(xml_path)
        try:
            result = self.classifier.classify(xml_path)
            nf_number = self._require_nf_number(result)
            target_dir = self.output_dir / DESTINATION_FOLDERS[result.nfe_type]
            new_name = self._unique_name(target_dir, f"{nf_number.zfill(6)}.xml")
            destination = target_dir / new_name
            shutil.move(str(xml_path), destination)
            event = ProcessEvent(original_name, nf_number, result.nfe_type.value, new_name, str(target_dir), "OK", result.reason)
            self._log_event(event)
            return event
        except Exception as exc:  # noqa: BLE001 - processing must quarantine any unexpected XML/file issue.
            target_dir = self.output_dir / DESTINATION_FOLDERS[NFeType.DESCONHECIDO]
            new_name = self._unique_name(target_dir, original_name)
            destination = target_dir / new_name
            if xml_path.exists():
                shutil.move(str(xml_path), destination)
            event = ProcessEvent(original_name, "", NFeType.DESCONHECIDO.value, new_name, str(target_dir), "ERRO", str(exc))
            self._log_event(event)
            return event

    def _require_nf_number(self, result: ClassificationResult) -> str:
        number = (result.data.number or "").strip()
        if not number:
            raise NFeParseError("XML sem número NF (<nNF>)")
        return number

    def _unique_name(self, directory: Path, filename: str) -> str:
        directory.mkdir(parents=True, exist_ok=True)
        candidate = Path(filename)
        stem = candidate.stem
        suffix = candidate.suffix or ".xml"
        counter = 0
        while (directory / candidate.name).exists():
            counter += 1
            candidate = Path(f"{stem}_{counter}{suffix}")
        return candidate.name

    def _wait_until_available(self, path: Path, attempts: int = 10, delay: float = 0.5) -> None:
        last_error: OSError | None = None
        for _ in range(attempts):
            try:
                with path.open("rb") as file_obj:
                    file_obj.read(1)
                return
            except OSError as exc:
                last_error = exc
                time.sleep(delay)
        if last_error:
            raise last_error

    def _log_event(self, event: ProcessEvent) -> None:
        self.logger.info(
            "Arquivo: %s | NF: %s | Tipo: %s | Destino: %s | Novo nome: %s | Status: %s | Mensagem: %s",
            event.original_name,
            event.nf_number,
            event.nfe_type,
            event.destination,
            event.new_name,
            event.status,
            event.message,
        )
