from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable


class GuiLogHandler(logging.Handler):
    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        self._callback(self.format(record))


class RuntimeLogger:
    def __init__(self, log_path: Path, level: str = "INFO") -> None:
        self._logger = logging.getLogger("runtime_engine")
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        self._logger.handlers.clear()

        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        self._formatter = formatter

    @property
    def instance(self) -> logging.Logger:
        return self._logger

    def attach_gui_handler(self, callback: Callable[[str], None]) -> None:
        gui_handler = GuiLogHandler(callback)
        gui_handler.setFormatter(self._formatter)
        self._logger.addHandler(gui_handler)
