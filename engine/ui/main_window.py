from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from core.config_manager import ConfigManager, EngineSettings
from core.runtime_bridge import RuntimePaths
from core.script_executor import ScriptExecutionResult, ScriptExecutor
from core.script_loader import ScriptLoader
from ui.log_viewer import LogViewer
from ui.script_list_widget import ScriptListWidget


class MainWindow(tk.Tk):
    """Main GUI that connects user actions to engine core services."""

    def __init__(
        self,
        runtime_paths: RuntimePaths,
        config_manager: ConfigManager,
        script_loader: ScriptLoader,
        script_executor: ScriptExecutor,
        logger: logging.Logger,
        log_queue: queue.SimpleQueue[str],
    ) -> None:
        super().__init__()
        self.runtime_paths = runtime_paths
        self.config_manager = config_manager
        self.script_loader = script_loader
        self.script_executor = script_executor
        self.logger = logger
        self.log_queue = log_queue
        self.settings: EngineSettings = config_manager.load()
        self.scripts = []
        self.is_running = False

        self.title("Engine Portátil de Scripts Python")
        self.geometry("980x680")
        self.minsize(820, 560)
        self._configure_style()
        self._build_layout()
        self.reload_scripts()
        self.after(150, self._drain_log_queue)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Status.TLabel", padding=8, font=("Segoe UI", 10, "bold"))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))

    def _build_layout(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, padding=(12, 12, 12, 6))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Engine portátil para execução sob demanda", style="Header.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text=f"Scripts: {self.runtime_paths.scripts_dir}").grid(row=1, column=0, sticky="w")

        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)

        left = ttk.Frame(body)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        self.script_list = ScriptListWidget(left)
        self.script_list.grid(row=0, column=0, sticky="nsew")

        controls = ttk.Frame(left, padding=(0, 8, 0, 0))
        controls.grid(row=1, column=0, sticky="ew")
        for index in range(4):
            controls.columnconfigure(index, weight=1)
        ttk.Button(controls, text="Recarregar", command=self.reload_scripts).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(controls, text="Salvar seleção", command=self.save_selection).grid(row=0, column=1, sticky="ew", padx=2)
        self.execute_button = ttk.Button(controls, text="Executar selecionados", command=self.execute_selected)
        self.execute_button.grid(row=0, column=2, columnspan=2, sticky="ew", padx=2)

        args_frame = ttk.LabelFrame(left, text="Argumentos extras", padding=8)
        args_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        args_frame.columnconfigure(0, weight=1)
        self.arguments_var = tk.StringVar(value=self.settings.default_arguments)
        ttk.Entry(args_frame, textvariable=self.arguments_var).grid(row=0, column=0, sticky="ew")

        right = ttk.Frame(body)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        self.status_label = ttk.Label(right, text="Pronto.", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="ew")
        self.log_viewer = LogViewer(right)
        self.log_viewer.grid(row=1, column=0, sticky="nsew")

        body.add(left, weight=2)
        body.add(right, weight=3)

        footer = ttk.Label(self, text=f"Configuração: {self.config_manager.config_path}", padding=(12, 4, 12, 10))
        footer.grid(row=2, column=0, sticky="ew")

    def reload_scripts(self) -> None:
        self.scripts = self.script_loader.discover()
        self.script_list.set_scripts(self.scripts, self.settings.selected_scripts)
        valid_count = len([script for script in self.scripts if script.valid])
        self._set_status("ok", f"{valid_count} script(s) válido(s) carregado(s).")

    def save_selection(self) -> None:
        self.settings.selected_scripts = self.script_list.selected_scripts()
        self.settings.default_arguments = self.arguments_var.get()
        self.config_manager.save(self.settings)
        self.logger.info("Seleção salva: %s", ", ".join(self.settings.selected_scripts) or "nenhum script")
        self._set_status("ok", "Seleção salva com sucesso.")

    def execute_selected(self) -> None:
        if self.is_running:
            return
        selected = self.script_list.selected_scripts()
        if not selected:
            self._set_status("warning", "Selecione ao menos um script antes de executar.")
            messagebox.showwarning("Nenhum script selecionado", "Selecione ao menos um script válido.")
            return
        self.save_selection()
        self.is_running = True
        self.execute_button.configure(state="disabled")
        self._set_status("warning", "Executando scripts selecionados...")
        thread = threading.Thread(target=self._execute_worker, args=(selected, self.arguments_var.get()), daemon=True)
        thread.start()

    def _execute_worker(self, selected: list[str], arguments: str) -> None:
        results = self.script_executor.execute_many(selected, self.settings, arguments)
        self.after(0, self._execution_finished, results)

    def _execution_finished(self, results: list[ScriptExecutionResult]) -> None:
        self.is_running = False
        self.execute_button.configure(state="normal")
        errors = [result for result in results if result.status == "error"]
        if errors:
            self._set_status("error", f"Execução finalizada com {len(errors)} erro(s). Consulte os logs.")
        else:
            self._set_status("ok", f"Execução concluída com sucesso ({len(results)} script(s)).")

    def _set_status(self, level: str, message: str) -> None:
        colors = {"ok": "#065F46", "warning": "#92400E", "error": "#991B1B"}
        self.status_label.configure(text=message, foreground=colors.get(level, "#111827"))

    def _drain_log_queue(self) -> None:
        while True:
            try:
                message = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log_viewer.append(message)
        self.after(150, self._drain_log_queue)
