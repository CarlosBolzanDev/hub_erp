from __future__ import annotations

from pathlib import Path
from typing import Any

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


class Engine:
    def __init__(self) -> None:
        self.resources = ResourceManager()
        config_path = self.resources.resolve("configs", "settings.json")
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.load()

        log_path = self.resources.runtime_writable_path("logs", "engine.log")
        self.log_manager = RuntimeLogger(log_path, level=self.config.log_level)
        self.logger = self.log_manager.instance

        self.events = EventBus()
        self.services = ServiceRegistry()
        self.script_loader = ScriptLoader(self.logger)
        self.ui = MainWindow(self)
        self._running = False

        self._register_default_services()

    def _register_default_services(self) -> None:
        self.services.register("events", self.events)
        self.services.register("logger", self.logger)
        self.services.register("config", self.config_manager)
        self.services.register("scripts", self.script_loader)

    def api(self) -> dict[str, Any]:
        return {
            "logger": self.logger,
            "events": self.events,
            "services": self.services,
            "config": self.config,
        }

    def start(self) -> None:
        self._running = True
        self.logger.info("Starting runtime: %s", self.config.runtime_name)
        self.ui.set_title(self.config.runtime_name)
        self.log_manager.attach_gui_handler(self.ui.append_log)

        if self.config.startup.get("autoload_scripts", True):
            self.reload_scripts()

        self.ui.run()

    def reload_scripts(self) -> None:
        scripts_dir = self.resources.resolve(*Path(self.config.scripts_folder).parts)
        self.script_loader.shutdown_all()
        self.script_loader.discover_and_load(scripts_dir, self)
        self.ui.refresh_scripts()
        self.events.publish(Event(name="scripts_reloaded"))

    def stop(self) -> None:
        if not self._running:
            return
        self.script_loader.shutdown_all()
        self._running = False
        self.logger.info("Engine shutdown complete.")
        self.events.publish(Event(name="engine_stopped"))

    def save_config(self) -> None:
        self.config_manager.save()
        self.logger.info("Configuration saved.")
