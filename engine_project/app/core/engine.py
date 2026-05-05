from __future__ import annotations

import logging
from pathlib import Path
import time
from typing import Any, Callable

from app.core.config import ConfigManager
from app.core.event_bus import Event, EventBus
from app.core.logger import RuntimeLogger
from app.core.resource_manager import ResourceManager
from app.core.script_loader import ScriptLoader


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
        self.ui = None
        self._running = False

        self.services.register("engine_api", self.api)
        self.services.register("config", self.config)

    def add_script(self, script_path: str) -> None:
        path = Path(script_path).expanduser().resolve()
        if not path.exists() or path.suffix.lower() != ".py":
            self.logger.error("Invalid script path: %s", script_path)
            return
        if str(path) not in self.config.selected_scripts:
            self.config.selected_scripts.append(str(path))
        self.script_loader.load_path(path, self.api, auto_activate=False)
        self._refresh_ui_if_present()

    def remove_script(self, name: str) -> None:
        record = self.script_loader.scripts.get(name)
        if record and str(record.path) in self.config.selected_scripts:
            self.config.selected_scripts.remove(str(record.path))
        self.script_loader.unload(name)
        self._refresh_ui_if_present()

    def load_selected_scripts(self, auto_activate: bool = True) -> None:
        if not self.config.selected_scripts:
            self.logger.warning("No selected scripts to load.")
            return
        for script in list(self.config.selected_scripts):
            self.script_loader.load_path(Path(script), self.api, auto_activate=auto_activate)
        self._refresh_ui_if_present()

    def reload_selected_scripts(self) -> None:
        if not self.script_loader.scripts:
            self.logger.warning("No loaded scripts to reload.")
            return
        for name in list(self.script_loader.scripts.keys()):
            self.script_loader.reload(name, self.api)
        self._refresh_ui_if_present()

    def run_headless(self, run_loop: bool = True) -> None:
        self._running = True
        self.logger.info("Starting runtime in headless mode: %s", self.config.runtime_name)
        if self.config.startup.get("autoload_selected", False):
            self.load_selected_scripts(auto_activate=True)
        else:
            self.logger.info("autoload_selected disabled; no scripts were started.")
        if run_loop:
            try:
                while self._running:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                self.logger.info("Headless runtime interrupted by user.")
            finally:
                self.stop()

    def launch_gui(self) -> None:
        from app.ui.main_window import MainWindow

        self._running = True
        try:
            self.ui = MainWindow(self)
        except Exception as exc:
            self.logger.exception("Failed to initialize GUI: %s", exc)
            self._running = False
            raise
        self.log_manager.attach_gui_handler(self.ui.append_log)
        self.ui.set_title(self.config.runtime_name)
        self.logger.info("Starting runtime in GUI mode: %s", self.config.runtime_name)
        # In GUI mode, always load saved scripts into the list; autoload controls activation only.
        self.load_selected_scripts(auto_activate=False)
        if self.config.startup.get("autoload_selected", False):
            for name in list(self.script_loader.scripts.keys()):
                self.script_loader.activate(name)
        self.ui.refresh_scripts()
        self.ui.run()

    def stop(self) -> None:
        if not self._running:
            return
        self.script_loader.shutdown_all()
        self.save_config()
        self._running = False
        self.logger.info("Runtime shutdown complete.")

    def save_config(self) -> None:
        self.config_manager.save()
        self.logger.info("Configuration saved.")

    def _refresh_ui_if_present(self) -> None:
        if self.ui is not None:
            self.ui.refresh_scripts()
