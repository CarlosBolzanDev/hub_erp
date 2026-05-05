from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.ui.panels import LogPanel, ScriptPanel, StatusPanel


class MainWindow:
    def __init__(self, engine: "Engine") -> None:
        self.engine = engine
        self.root = tk.Tk()
        self.root.geometry("920x620")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build_layout()

    def _build_layout(self) -> None:
        toolbar = ttk.Frame(self.root, padding=8)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Carregar scripts", command=self.engine.reload_scripts).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Recarregar scripts", command=self.engine.reload_scripts).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Iniciar rotina", command=self._start_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Parar rotina", command=self._stop_selected).pack(side="left", padx=4)
        ttk.Button(toolbar, text="Configurações", command=self._open_settings).pack(side="left", padx=4)

        content = ttk.Frame(self.root, padding=8)
        content.pack(fill="both", expand=True)
        content.columnconfigure(0, weight=1)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(1, weight=1)

        self.script_panel = ScriptPanel(content)
        self.script_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 8))

        self.status_panel = StatusPanel(content)
        self.status_panel.grid(row=0, column=1, sticky="nsew")

        self.log_panel = LogPanel(content)
        self.log_panel.grid(row=1, column=1, sticky="nsew", pady=(8, 0))

    def set_title(self, title: str) -> None:
        self.root.title(title)

    def append_log(self, line: str) -> None:
        widget = self.log_panel.text
        widget.configure(state="normal")
        widget.insert("end", f"{line}\n")
        widget.see("end")
        widget.configure(state="disabled")

    def refresh_scripts(self) -> None:
        lb = self.script_panel.listbox
        lb.delete(0, "end")
        for name, record in self.engine.script_loader.scripts.items():
            status = "ativo" if record.active else "erro/inativo"
            lb.insert("end", f"{name} [{status}]")
        self.status_panel.var.set(f"Scripts carregados: {len(self.engine.script_loader.scripts)}")

    def _selected_script_name(self) -> str | None:
        selection = self.script_panel.listbox.curselection()
        if not selection:
            return None
        label = self.script_panel.listbox.get(selection[0])
        return label.split(" [", 1)[0]

    def _start_selected(self) -> None:
        name = self._selected_script_name()
        if not name:
            messagebox.showinfo("Runtime", "Selecione um script para iniciar.")
            return
        self.engine.script_loader.activate(name)
        self.refresh_scripts()

    def _stop_selected(self) -> None:
        name = self._selected_script_name()
        if not name:
            messagebox.showinfo("Runtime", "Selecione um script para parar.")
            return
        self.engine.script_loader.deactivate(name)
        self.refresh_scripts()

    def _open_settings(self) -> None:
        cfg = self.engine.config
        win = tk.Toplevel(self.root)
        win.title("Configurações")
        win.geometry("420x240")

        runtime_name = tk.StringVar(value=cfg.runtime_name)
        scripts_folder = tk.StringVar(value=cfg.scripts_folder)
        log_level = tk.StringVar(value=cfg.log_level)

        ttk.Label(win, text="Nome do runtime").pack(anchor="w", padx=10, pady=(10, 0))
        ttk.Entry(win, textvariable=runtime_name).pack(fill="x", padx=10)

        ttk.Label(win, text="Pasta de scripts").pack(anchor="w", padx=10, pady=(10, 0))
        ttk.Entry(win, textvariable=scripts_folder).pack(fill="x", padx=10)

        ttk.Label(win, text="Nível de log").pack(anchor="w", padx=10, pady=(10, 0))
        ttk.Combobox(win, textvariable=log_level, values=["DEBUG", "INFO", "WARNING", "ERROR"], state="readonly").pack(fill="x", padx=10)

        def save() -> None:
            cfg.runtime_name = runtime_name.get().strip() or cfg.runtime_name
            cfg.scripts_folder = scripts_folder.get().strip() or cfg.scripts_folder
            cfg.log_level = log_level.get().strip() or cfg.log_level
            self.engine.save_config()
            self.set_title(cfg.runtime_name)
            win.destroy()

        ttk.Button(win, text="Salvar", command=save).pack(pady=14)

    def _on_close(self) -> None:
        self.engine.stop()
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
