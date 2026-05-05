from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

from app.core.config import ConfigManager
from app.core.event_bus import Event, EventBus
from app.core.logger import RuntimeLogger
from app.core.resource_manager import ResourceManager
from app.core.script_loader import ScriptLoader
from app.ui.main_window import MainWindow


class ServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[str, Any] = {}

    def register(self, name: str, service: Any) -> None:
        self._services[name] = service

    def get(self, name: str) -> Any:
        return self._services[name]


class EngineAPI:
    def __init__(self, engine: "Engine") -> None:
        self._engine = engine

    def register_service(self, name: str, service: Any) -> None:
        self._engine.services.register(name, service)

    def get_service(self, name: str) -> Any:
        return self._engine.services.get(name)

    def emit_event(self, name: str, payload: dict[str, Any] | None = None) -> None:
        self._engine.events.publish(Event(name=name, payload=payload or {}))

    def on_event(self, name: str, callback: Callable[[Event], None]) -> None:
        self._engine.events.subscribe(name, callback)

    def log(self, message: str, level: str = "INFO") -> None:
        self._engine.logger.log(getattr(logging, level.upper(), logging.INFO), message)

    def execute_script(self, path: str) -> None:
        self._engine.add_script(path)

    def load_selected_scripts(self) -> None:
        self._engine.load_selected_scripts()

    def shutdown_script(self, name: str) -> None:
        self._engine.script_loader.deactivate(name)

    def reload_script(self, name: str) -> None:
        self._engine.script_loader.reload(name, self)


class Engine:
    def __init__(self) -> None:
        self.resources = ResourceManager()
        self.config_manager = ConfigManager(self.resources.resolve("configs", "settings.json"))
        self.config = self.config_manager.load()

        self.log_manager = RuntimeLogger(self.resources.runtime_writable_path("logs", "engine.log"), self.config.log_level)
        self.logger = self.log_manager.instance

        self.events = EventBus()
        self.services = ServiceRegistry()
        self.script_loader = ScriptLoader(self.logger)
        self.api = EngineAPI(self)
        self.ui = MainWindow(self)
        self._running = False

        self.services.register("engine_api", self.api)
        self.services.register("config", self.config)

    def start(self) -> None:
        self._running = True
        self.log_manager.attach_gui_handler(self.ui.append_log)
        self.ui.set_title(self.config.runtime_name)
        self.logger.info("Starting runtime: %s", self.config.runtime_name)
        if self.config.startup.get("autoload_selected", False):
            self.load_selected_scripts()
        self.ui.refresh_scripts()
        self.ui.run()

    def add_script(self, script_path: str) -> None:
        path = Path(script_path).expanduser().resolve()
        if not path.exists() or path.suffix.lower() != ".py":
            self.logger.error("Invalid script path: %s", script_path)
            return
        if str(path) not in self.config.selected_scripts:
            self.config.selected_scripts.append(str(path))
        self.script_loader.load_path(path, self.api)
        self.ui.refresh_scripts()

    def remove_script(self, name: str) -> None:
        record = self.script_loader.scripts.get(name)
        if record and str(record.path) in self.config.selected_scripts:
            self.config.selected_scripts.remove(str(record.path))
        self.script_loader.unload(name)
        self.ui.refresh_scripts()

    def load_selected_scripts(self) -> None:
        for script in list(self.config.selected_scripts):
            self.script_loader.load_path(Path(script), self.api)
        self.ui.refresh_scripts()

    def reload_selected_scripts(self) -> None:
        for name in list(self.script_loader.scripts.keys()):
            self.script_loader.reload(name, self.api)
        self.ui.refresh_scripts()

    def stop(self) -> None:
        if not self._running:
            return
        self.script_loader.shutdown_all()
        self.save_config()
        self._running = False

    def save_config(self) -> None:
        self.config_manager.save()
        self.logger.info("Configuration saved.")
