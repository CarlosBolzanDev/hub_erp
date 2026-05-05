from __future__ import annotations

import logging
from pathlib import Path
from queue import SimpleQueue
from typing import Callable

from utils.file_utils import ensure_directory


class QueueLogHandler(logging.Handler):
    """Logging handler that sends formatted records to the GUI thread queue."""

    def __init__(self, queue: SimpleQueue[str]) -> None:
        super().__init__()
        self.queue = queue

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.queue.put(self.format(record))
        except Exception:
            self.handleError(record)


class CallbackLogHandler(logging.Handler):
    """Small handler available to scripts that need custom log callbacks."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self.callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        self.callback(self.format(record))


class LoggerManager:
    """Configure file and GUI logging for the engine."""

    def __init__(self, log_path: Path, gui_queue: SimpleQueue[str] | None = None) -> None:
        ensure_directory(log_path.parent)
        self.log_path = log_path
        self.gui_queue = gui_queue

    def configure(self) -> logging.Logger:
        logger = logging.getLogger("engine")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.handlers.clear()

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        if self.gui_queue is not None:
            gui_handler = QueueLogHandler(self.gui_queue)
            gui_handler.setLevel(logging.INFO)
            gui_handler.setFormatter(formatter)
            logger.addHandler(gui_handler)

        logger.info("Engine inicializada. Log em: %s", self.log_path)
        return logger
