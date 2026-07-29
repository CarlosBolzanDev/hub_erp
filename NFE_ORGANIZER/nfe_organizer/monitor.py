"""Watchdog integration for continuous input-folder monitoring."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .processor import NFeProcessor, ProcessEvent

EventCallback = Callable[[ProcessEvent], None]


class XMLCreatedHandler(FileSystemEventHandler):
    def __init__(self, processor: NFeProcessor, callback: EventCallback | None = None) -> None:
        self.processor = processor
        self.callback = callback

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".xml":
            return
        result = self.processor.process(path)
        if self.callback:
            self.callback(result)


class FolderMonitor:
    """Start and stop recursive XML monitoring for the input folder."""

    def __init__(self, input_dir: Path, processor: NFeProcessor, callback: EventCallback | None = None) -> None:
        self.input_dir = input_dir
        self.processor = processor
        self.callback = callback
        self.observer: Observer | None = None

    @property
    def is_running(self) -> bool:
        return bool(self.observer and self.observer.is_alive())

    def start(self) -> None:
        if self.is_running:
            return
        self.input_dir.mkdir(parents=True, exist_ok=True)
        handler = XMLCreatedHandler(self.processor, self.callback)
        self.observer = Observer()
        self.observer.schedule(handler, str(self.input_dir), recursive=False)
        self.observer.start()

    def stop(self) -> None:
        if not self.observer:
            return
        self.observer.stop()
        self.observer.join(timeout=5)
        self.observer = None
