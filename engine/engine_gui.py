from __future__ import annotations

import queue
import sys
from pathlib import Path

CURRENT_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
for relative in (".", "core", "ui", "utils", "libs"):
    path = str((CURRENT_DIR / relative).resolve())
    if path not in sys.path:
        sys.path.insert(0, path)

from core.config_manager import ConfigManager
from core.logger_manager import LoggerManager
from core.runtime_bridge import RuntimeBridge
from core.script_executor import ScriptExecutor
from core.script_loader import ScriptLoader
from ui.main_window import MainWindow


def main() -> int:
    bridge = RuntimeBridge(CURRENT_DIR)
    runtime_paths = bridge.prepare()

    log_queue: queue.SimpleQueue[str] = queue.SimpleQueue()
    logger = LoggerManager(runtime_paths.logs_dir / "engine.log", log_queue).configure()
    if not bridge.is_embedded_runtime_available():
        logger.warning(
            "Runtime embutido não encontrado em %s. Em desenvolvimento, a engine usará o Python atual.",
            bridge.python_executable(),
        )

    config_manager = ConfigManager(runtime_paths.config_dir / "engine_manifest.json")
    script_loader = ScriptLoader(runtime_paths, logger)
    script_executor = ScriptExecutor(runtime_paths, logger)

    app = MainWindow(runtime_paths, config_manager, script_loader, script_executor, logger, log_queue)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
