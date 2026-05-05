from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from core.config_manager import ConfigManager, EngineManifest
from core.runtime_bridge import RuntimePaths
from core.script_executor import ScriptExecutionResult, ScriptExecutor
from core.script_loader import ScriptLoader
from ui.log_viewer import LogViewer
from ui.script_manager_widget import ScriptManagerWidget


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
        self.manifest: EngineManifest = config_manager.load()
        self.is_running = False

        self.title("Engine Windows Portátil de Scripts Python")
        self.geometry("1180x720")
        self.minsize(960, 600)
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
        ttk.Label(header, text="Engine portátil para scripts externos", style="Header.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text="Adicione scripts .py por caminho; eles podem estar fora da pasta da engine.").grid(
            row=1, column=0, sticky="w"
        )

        body = ttk.PanedWindow(self, orient="horizontal")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)

        left = ttk.Frame(body)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)
        self.script_manager = ScriptManagerWidget(left)
        self.script_manager.grid(row=0, column=0, sticky="nsew")

        controls = ttk.Frame(left, padding=(0, 8, 0, 0))
        controls.grid(row=1, column=0, sticky="ew")
        for index in range(6):
            controls.columnconfigure(index, weight=1)
        ttk.Button(controls, text="Adicionar script", command=self.add_script).grid(row=0, column=0, sticky="ew", padx=2)
        ttk.Button(controls, text="Remover script", command=self.remove_script).grid(row=0, column=1, sticky="ew", padx=2)
        ttk.Button(controls, text="Recarregar lista", command=self.reload_scripts).grid(row=0, column=2, sticky="ew", padx=2)
        ttk.Button(controls, text="Salvar configuração", command=self.save_manifest).grid(row=0, column=3, sticky="ew", padx=2)
        self.execute_one_button = ttk.Button(controls, text="Executar um script", command=self.execute_one_selected)
        self.execute_one_button.grid(row=0, column=4, sticky="ew", padx=2)
        self.execute_selected_button = ttk.Button(controls, text="Executar selecionados", command=self.execute_active)
        self.execute_selected_button.grid(row=0, column=5, sticky="ew", padx=2)

        args_frame = ttk.LabelFrame(left, text="Argumentos extras", padding=8)
        args_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        args_frame.columnconfigure(0, weight=1)
        self.arguments_var = tk.StringVar(value=self.manifest.default_arguments)
        ttk.Entry(args_frame, textvariable=self.arguments_var).grid(row=0, column=0, sticky="ew")

        right = ttk.Frame(body)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)
        self.status_label = ttk.Label(right, text="Pronto.", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="ew")
        self.log_viewer = LogViewer(right)
        self.log_viewer.grid(row=1, column=0, sticky="nsew")

        body.add(left, weight=3)
        body.add(right, weight=2)

        footer = ttk.Label(self, text=f"Manifesto: {self.config_manager.manifest_path}", padding=(12, 4, 12, 10))
        footer.grid(row=2, column=0, sticky="ew")

    def add_script(self) -> None:
        filename = filedialog.askopenfilename(
            title="Adicionar script Python externo",
            filetypes=(('Scripts Python', '*.py'), ('Todos os arquivos', '*.*')),
        )
        if not filename:
            return
        try:
            script = self.script_loader.add_script(self.manifest, Path(filename))
        except ValueError as exc:
            messagebox.showwarning("Script não adicionado", str(exc))
            self._set_status("warning", str(exc))
            return

        new_name = simpledialog.askstring(
            "Nome amigável",
            "Nome exibido para este script:",
            initialvalue=script.display_name,
            parent=self,
        )
        if new_name:
            script.display_name = new_name.strip() or script.display_name
        self.script_manager.set_scripts(self.manifest.scripts)
        self.save_manifest()
        self._set_status("ok", f"Script adicionado: {script.display_name}.")

    def remove_script(self) -> None:
        selected = self.script_manager.selected_script()
        if selected is None:
            self._set_status("warning", "Selecione um script para remover.")
            return
        if not messagebox.askyesno("Remover script", f"Remover '{selected.display_name}' do manifesto?"):
            return
        self.script_loader.remove_script(self.manifest, selected.id)
        self.script_manager.set_scripts(self.manifest.scripts)
        self.save_manifest()
        self._set_status("ok", "Script removido do manifesto.")

    def reload_scripts(self) -> None:
        self.script_loader.validate_all(self.manifest)
        self.script_manager.set_scripts(self.manifest.scripts)
        self._set_status("ok", f"{len(self.manifest.scripts)} script(s) cadastrado(s) carregado(s).")

    def save_manifest(self) -> None:
        self.manifest.default_arguments = self.arguments_var.get()
        self.config_manager.save(self.manifest)
        self.logger.info("Manifesto salvo com %d script(s).", len(self.manifest.scripts))
        self._set_status("ok", "Configuração salva com sucesso.")

    def execute_active(self) -> None:
        active = self.script_manager.active_scripts()
        if not active:
            self._set_status("warning", "Ative ao menos um script antes de executar.")
            messagebox.showwarning("Nenhum script ativo", "Marque ao menos um script na coluna Ativo.")
            return
        self._start_execution(active)

    def execute_one_selected(self) -> None:
        selected = self.script_manager.selected_script()
        if selected is None:
            self._set_status("warning", "Selecione um script para execução individual.")
            return
        self._start_execution([selected])

    def _start_execution(self, scripts) -> None:
        if self.is_running:
            return
        self.save_manifest()
        self.is_running = True
        self._set_execution_buttons("disabled")
        self._set_status("warning", "Executando script(s)...")
        thread = threading.Thread(target=self._execute_worker, args=(scripts, self.arguments_var.get()), daemon=True)
        thread.start()

    def _execute_worker(self, scripts, arguments: str) -> None:
        results = self.script_executor.execute_many(scripts, self.manifest, arguments)
        self.config_manager.save(self.manifest)
        self.after(0, self._execution_finished, results)

    def _execution_finished(self, results: list[ScriptExecutionResult]) -> None:
        self.is_running = False
        self._set_execution_buttons("normal")
        self.script_manager.set_scripts(self.manifest.scripts)
        errors = [result for result in results if result.status == "error"]
        if errors:
            self._set_status("error", f"Execução finalizada com {len(errors)} erro(s). Consulte os logs.")
        else:
            self._set_status("ok", f"Execução concluída com sucesso ({len(results)} script(s)).")

    def _set_execution_buttons(self, state: str) -> None:
        self.execute_one_button.configure(state=state)
        self.execute_selected_button.configure(state=state)

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
